import unittest
from pathlib import Path
from unittest.mock import patch
import launch


class LauncherTests(unittest.TestCase):
    def test_platform_paths(self):
        root = Path('/example/project with spaces')
        self.assertEqual(launch.environment_python(root, 'nt'), root / '.venv/Scripts/python.exe')
        self.assertEqual(launch.environment_python(root, 'posix'), root / '.venv/bin/python')

    @patch('launch.run')
    @patch('launch.environment_python')
    def test_check_does_not_start_server(self, python, run):
        python.return_value = Path(__file__)
        with patch('sys.argv', ['launch.py', '--check']):
            self.assertEqual(launch.main(), 0)
        self.assertEqual(len(run.call_args_list), 2)

    @patch('launch.run')
    @patch('launch.environment_python')
    def test_server_options(self, python, run):
        python.return_value = Path(__file__)
        with patch('sys.argv', ['launch.py', '--no-browser', '--server.port', '8502']):
            self.assertEqual(launch.main(), 0)
        command = run.call_args_list[-1].args[0]
        self.assertEqual(command[-2:], ['--server.port', '8502'])
        self.assertEqual(command[command.index('--server.headless') + 1], 'true')
