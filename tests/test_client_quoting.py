import importlib.util
import pathlib
import unittest
from unittest import mock

ROOT = pathlib.Path(__file__).resolve().parents[1]
CLIENT = ROOT / 'client' / 'grid-depot-client.py'


def load_client():
    spec = importlib.util.spec_from_file_location('grid_depot_client', CLIENT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f'Could not load {CLIENT}')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class RemoteQuotingTests(unittest.TestCase):
    def test_run_remote_quotes_paths_with_spaces(self):
        mod = load_client()
        with mock.patch.object(mod.subprocess, 'run') as run:
            mod.run_remote(['import', '/incoming/Antigravity IDE.dmg', '--type', 'dmg'])
        cmd = run.call_args.args[0]
        self.assertEqual(cmd[:3], ['ssh', '-o', 'BatchMode=yes'])
        remote_cmd = cmd[-1]
        self.assertIn('/usr/local/bin/grid-depot import', remote_cmd)
        self.assertIn("'/incoming/Antigravity IDE.dmg'", remote_cmd)
        self.assertIn('--type dmg', remote_cmd)


if __name__ == '__main__':
    unittest.main()
