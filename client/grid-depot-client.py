#!/usr/bin/env python3
from __future__ import annotations
import argparse, datetime as dt, hashlib, json, os, re, shlex, subprocess, sys
from pathlib import Path

REMOTE_ALIAS = os.environ.get('GRID_DEPOT_REMOTE_ALIAS', 'grid-depot-server')
REMOTE_USER = os.environ.get('GRID_DEPOT_REMOTE_USER', '')
REMOTE_HOST = os.environ.get('GRID_DEPOT_REMOTE_HOST', '')
REMOTE_SPEC = os.environ.get('GRID_DEPOT_REMOTE_SPEC', REMOTE_ALIAS)
CLIENT_TAG = os.environ.get('GRID_DEPOT_CLIENT_TAG', 'mac-client')
SSH_BASE = ['ssh', '-o', 'BatchMode=yes', REMOTE_SPEC]
SCP_BASE = ['scp', '-o', 'BatchMode=yes']
REMOTE_INCOMING = os.environ.get('GRID_DEPOT_REMOTE_INCOMING', '/var/lib/grid-depot/incoming')
DEFAULT_EXTS = ['iso','dmg','pkg','img','qcow2','vmdk','gguf','safetensors']
EXT_TYPES = {'.iso':'iso','.dmg':'dmg','.pkg':'pkg','.img':'disk-image','.qcow2':'vm-image','.vmdk':'vm-image','.gguf':'ai-model','.safetensors':'ai-model','.zip':'archive'}
NOISE = {'installer','install','setup','latest','universal','arm64','aarch64','x64','amd64','darwin','mac','macos','osx','signed','stable','release','final','instruct','q4','q5','q6','q8','k','m','gguf','dmg','pkg','iso','zip'}
VERSION_RE = re.compile(r'(?i)(?:^|[-_ .])v?(\d+(?:\.\d+){1,4}(?:[-_.]?(?:alpha|beta|rc|arm64|x64|universal|aarch64|amd64|q\d(?:_[a-z])?))*)')

def run_remote(args, check=True, capture=False):
    cmd = SSH_BASE + ['/usr/local/bin/grid-depot'] + args
    return subprocess.run(cmd, check=check, text=True, capture_output=capture)

def human(n):
    v=float(n)
    for u in ['B','KiB','MiB','GiB','TiB']:
        if v<1024 or u=='TiB': return f'{int(v)} B' if u=='B' else f'{v:.1f} {u}'
        v/=1024

def sha(path):
    h=hashlib.sha256(); size=0
    with open(path,'rb') as f:
        for b in iter(lambda:f.read(8*1024*1024), b''):
            size += len(b); h.update(b)
    return h.hexdigest(), size

def infer_type(path, override=None):
    if override: return override
    return EXT_TYPES.get(Path(path).suffix.lower(), 'raw')

def infer_version(name):
    stem=Path(name).stem
    m=VERSION_RE.search(stem)
    return m.group(1).strip('-_. ') if m else None

def infer_family(name):
    stem=VERSION_RE.sub(' ', Path(name).stem)
    toks=[t for t in re.split(r'[^A-Za-z0-9]+', stem.lower()) if t and t not in NOISE and not t.isdigit()]
    return '-'.join(toks[:6]) or Path(name).stem.lower()

def remote_artifacts():
    p=run_remote(['list','--json'], capture=True)
    return json.loads(p.stdout)

def candidate_files(dirs, exts):
    wanted={e if e.startswith('.') else '.'+e.lower() for e in exts}
    out=[]
    for root in dirs:
        root=Path(root).expanduser()
        if not root.exists(): continue
        for dp,dn,fn in os.walk(root):
            dn[:] = [d for d in dn if d not in {'.git','node_modules'} and not d.endswith('.app')]
            for f in fn:
                lf=f.lower()
                if any(lf.endswith(e) for e in wanted): out.append(Path(dp)/f)
    return sorted(set(out))

def ask_remove(path, assume_yes=False, keep_local=False):
    if keep_local: return
    if assume_yes:
        Path(path).unlink(missing_ok=True); print(f'removed local copy: {path}'); return
    if not sys.stdin.isatty():
        print(f'kept local copy (non-interactive): {path}'); return
    ans=input(f'Remove local copy now that it is in GRID depot? {path} [y/N] ').strip().lower()
    if ans in {'y','yes'}:
        Path(path).unlink(missing_ok=True); print(f'removed local copy: {path}')
    else:
        print(f'kept local copy: {path}')

def upload_and_import(path, atype, tags, keep_local=False, yes_remove=False, dry_run=False):
    path=Path(path).expanduser().resolve()
    if not path.is_file():
        print(f'not a file: {path}', file=sys.stderr); return 2
    digest,size=sha(path)
    arts=remote_artifacts()
    by_sha={a.get('sha256'): a for a in arts}
    fam=infer_family(path.name); ver=infer_version(path.name); atype=infer_type(path, atype)
    related=[a for a in arts if a.get('family') == fam and a.get('type') == atype]
    if digest in by_sha:
        a=by_sha[digest]
        prefix = 'DRY RUN duplicate already in GRID depot' if dry_run else 'duplicate already in GRID depot'
        print(f'{prefix}: {path.name} {human(size)} sha256:{digest[:16]} -> {a.get("name")} family:{a.get("family") or fam} version:{a.get("version") or ver or "-"}')
        if not dry_run:
            ask_remove(path, yes_remove, keep_local)
        return 0
    if related:
        print(f'related versions already in GRID depot for family {fam}:')
        for a in related[-8:]:
            print(f'  - {a.get("id")} {a.get("version") or "-":<16} {a.get("human_size",""):>10} {a.get("name")}')
    tag_args=[]
    for t in (tags or ['auto-imported', CLIENT_TAG]): tag_args += ['--tag', t]
    remote_name=f'{CLIENT_TAG}-{dt.datetime.now().strftime("%Y%m%d-%H%M%S")}-{path.name}'
    remote_path=f'{REMOTE_INCOMING}/{remote_name}'
    if dry_run:
        print(f'DRY RUN would upload/import: {path} -> {remote_path} type:{atype} family:{fam} version:{ver or "-"}')
        return 0
    print(f'uploading: {path.name} {human(size)} -> {REMOTE_SPEC}:{remote_path}')
    subprocess.run(SCP_BASE + [str(path), f'{REMOTE_SPEC}:{remote_path}'], check=True)
    run_remote(['import', remote_path, '--type', atype] + tag_args, check=True)
    ask_remove(path, yes_remove, keep_local)
    return 0

def cmd_grid_artifacts(argv):
    if not argv:
        return run_remote(['list']).returncode
    if argv[0] in ('-h','--help','help'):
        print('''grid-artifacts — list and auto-add artifacts to the GRID server depot

Usage:
  grid-artifacts                         List GRID server artifacts
  grid-artifacts --type dmg              List only one type
  grid-artifacts auto-add [FILES...]     Upload/import local files to GRID depot
  grid-artifacts auto-add --scan-downloads
  grid-artifacts families [--multiple]   Show inferred artifact families/versions

Auto-add options:
  --scan-downloads       Scan ~/Downloads and iCloud Downloads
  --dir DIR              Scan a directory; can be repeated
  --ext EXT              Extension for scans; can be repeated, e.g. --ext dmg
  --type TYPE            Type override for explicit files
  --tag TAG              Tag to apply; can be repeated
  --keep-local           Do not ask to remove local files after upload/duplicate
  --yes-remove           Remove local copies without prompting after safe import/duplicate detection
  --dry-run              Show what would be imported

Examples:
  grid-artifacts auto-add ~/Downloads/Foo.dmg --tag macbook
  grid-artifacts auto-add --scan-downloads --ext dmg --ext iso
'''); return 0
    if argv[0] in ('auto-add','auto-import','add'):
        ap=argparse.ArgumentParser(prog='grid-artifacts auto-add', description='Upload/import local Mac files into the GRID server depot with duplicate/version checks.')
        ap.add_argument('files', nargs='*')
        ap.add_argument('--scan-downloads', action='store_true')
        ap.add_argument('--dir', action='append')
        ap.add_argument('--ext', action='append')
        ap.add_argument('--type')
        ap.add_argument('--tag', action='append')
        ap.add_argument('--keep-local', action='store_true')
        ap.add_argument('--yes-remove', action='store_true')
        ap.add_argument('--dry-run', action='store_true')
        ns=ap.parse_args(argv[1:])
        files=[Path(f).expanduser() for f in ns.files]
        dirs=[]
        if ns.scan_downloads or (not files and not ns.dir):
            dirs=[Path.home()/'Downloads', Path.home()/'Library/Mobile Documents/com~apple~CloudDocs/Downloads', Path.home()/'Library/Mobile Documents/com~apple~CloudDocs/iCloud Downloads']
        if ns.dir: dirs += [Path(d).expanduser() for d in ns.dir]
        files += candidate_files(dirs, ns.ext or DEFAULT_EXTS)
        if not files:
            print('No candidate files found.'); return 0
        rc=0
        for f in sorted(set(files)):
            rc=max(rc, upload_and_import(f, ns.type, ns.tag or ['auto-imported', CLIENT_TAG], ns.keep_local, ns.yes_remove, ns.dry_run))
        return rc
    if argv[0] == 'families':
        return run_remote(['families'] + argv[1:]).returncode
    return run_remote(['list'] + argv).returncode

def cmd_grid_import(argv):
    if not argv or argv[0] in ('-h','--help','help'):
        print('''grid-import — upload/import local files to the GRID server depot

Usage:
  grid-import FILE [FILE...] [--type TYPE] [--tag TAG...] [--keep-local] [--yes-remove]

Examples:
  grid-import ~/Downloads/App.dmg --type dmg --tag macbook
  grid-import ~/Downloads/model.gguf --type ai-model --tag gguf --tag keep
'''); return 0
    ap=argparse.ArgumentParser(prog='grid-import')
    ap.add_argument('files', nargs='+'); ap.add_argument('--type'); ap.add_argument('--tag', action='append'); ap.add_argument('--keep-local', action='store_true'); ap.add_argument('--yes-remove', action='store_true'); ap.add_argument('--dry-run', action='store_true')
    ns=ap.parse_args(argv)
    rc=0
    for f in ns.files: rc=max(rc, upload_and_import(f, ns.type, ns.tag or ['imported', CLIENT_TAG], ns.keep_local, ns.yes_remove, ns.dry_run))
    return rc

def cmd_grid_audit(argv):
    if argv and argv[0] in ('-h','--help','help'):
        print('''grid-depot-audit — scan this Mac for files that may belong in GRID depot

Usage:
  grid-depot-audit [--dir DIR] [--ext EXT]

This does not import. To import safely:
  grid-artifacts auto-add --scan-downloads
'''); return 0
    ap=argparse.ArgumentParser(prog='grid-depot-audit')
    ap.add_argument('--dir', action='append'); ap.add_argument('--ext', action='append')
    ns=ap.parse_args(argv)
    dirs=[Path.home()/'Downloads', Path.home()/'Library/Mobile Documents/com~apple~CloudDocs/Downloads', Path.home()/'Library/Mobile Documents/com~apple~CloudDocs/iCloud Downloads']
    if ns.dir: dirs=[Path(d).expanduser() for d in ns.dir]
    for p in candidate_files(dirs, ns.ext or DEFAULT_EXTS): print(p)
    return 0

def cmd_grid_get(argv):
    if not argv or argv[0] in ('-h','--help','help'):
        print('''grid-get — download a URL directly on the GRID server and import it

Usage:
  grid-get URL [--type TYPE] [--tag TAG...]

Example:
  grid-get https://example.com/file.iso --type iso --tag keep
'''); return 0
    return run_remote(['get'] + argv).returncode

def cmd_grid_depot(argv):
    if not argv or argv[0] in ('-h','--help','help'):
        return run_remote(['--help']).returncode
    return run_remote(argv).returncode

def cmd_auth_check(argv):
    if argv and argv[0] in ('-h','--help','help'):
        print('grid-depot-auth-check — verify passwordless SSH and GRID depot command access')
        return 0
    print('Checking GRID depot SSH/client access...')
    p=subprocess.run(SSH_BASE + ['echo SSH_OK; /usr/local/bin/grid-depot where; /usr/local/bin/grid-depot list | head -5'], text=True)
    return p.returncode

def main():
    name=Path(sys.argv[0]).name
    argv=sys.argv[1:]
    if name == 'grid-artifacts': raise SystemExit(cmd_grid_artifacts(argv))
    if name == 'grid-import': raise SystemExit(cmd_grid_import(argv))
    if name == 'grid-depot-audit': raise SystemExit(cmd_grid_audit(argv))
    if name == 'grid-get': raise SystemExit(cmd_grid_get(argv))
    if name == 'grid-depot-auth-check': raise SystemExit(cmd_auth_check(argv))
    raise SystemExit(cmd_grid_depot(argv))
if __name__ == '__main__': main()
