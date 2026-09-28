"""Cross-platform bootstrap. Run with Python 3.10+; no global pip installs."""
import argparse
import os
from pathlib import Path
import subprocess
import sys
import venv

ROOT = Path(__file__).resolve().parent


def environment_python(root=ROOT, platform=os.name):
    return root / '.venv' / ('Scripts/python.exe' if platform == 'nt' else 'bin/python')


def run(command):
    subprocess.run([str(arg) for arg in command], cwd=ROOT, check=True)


def main():
    parser = argparse.ArgumentParser(description='Launch Mingxi BI on Windows, Linux or macOS')
    parser.add_argument('--check', action='store_true', help='Install/check dependencies without starting the server')
    parser.add_argument('--no-browser', action='store_true', help='Run without opening a browser (SSH/server)')
    args, streamlit_args = parser.parse_known_args()
    if sys.version_info < (3, 10):
        print('Python 3.10 or newer is required.', file=sys.stderr)
        return 1
    python = environment_python()
    if not python.exists():
        print('Creating local .venv ...', flush=True)
        try:
            venv.EnvBuilder(with_pip=True).create(ROOT / '.venv')
        except Exception as exc:
            print(f'Cannot create .venv: {exc}\nOn Debian/Ubuntu, install python3-venv. Do not copy .venv between operating systems.', file=sys.stderr)
            return 1
    try:
        # Pip checks existing versions and installs only missing/outdated requirements.
        run([python, '-m', 'pip', 'install', '--disable-pip-version-check', '-r', ROOT / 'requirements.txt'])
        run([python, '-c', 'import streamlit, pandas, plotly, openpyxl, xlrd, odf'])
        if args.check:
            print('Dependencies ready.')
            return 0
        run([python, '-m', 'streamlit', 'run', ROOT / 'app.py',
             '--server.address', '127.0.0.1', '--browser.gatherUsageStats', 'false',
             '--server.headless', 'true' if args.no_browser else 'false', *streamlit_args])
        return 0
    except subprocess.CalledProcessError as exc:
        print(f'Command failed (exit {exc.returncode}). See details above.', file=sys.stderr)
        return exc.returncode
    except KeyboardInterrupt:
        return 0


if __name__ == '__main__':
    sys.exit(main())
