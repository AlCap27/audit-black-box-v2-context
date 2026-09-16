"""Run every repository unittest suite in isolation with Python networking denied.

No installation, provider calls or writes to sealed artifacts. Child processes
inherit sitecustomize and PYTHONDONTWRITEBYTECODE, including historic hash-seed
tests. Temporary fixtures are managed by their existing tests.
"""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
GROUPS = [
    'preflight',
    'study/batch-preparation-20260914',
    'study/batch-preparation-20260914/source-protocol',
    'study/confirmatory-design-20260914',
    'study/pilot-expanded-20260910/source-snapshot',
    'study/extension-20260913/source-snapshot',
]
GUARD = '''import socket
def denied(*args, **kwargs):
    raise AssertionError("NETWORK FORBIDDEN IN OFFLINE SUITE")
socket.socket.connect = denied
socket.socket.connect_ex = denied
socket.socket.sendto = denied
socket.create_connection = denied
socket.getaddrinfo = denied
'''
RUN = '''import json,sys,unittest
sys.path.append(sys.argv[1])
suite=unittest.defaultTestLoader.discover('.',pattern='test_*.py')
result=unittest.TextTestRunner(verbosity=2).run(suite)
print('OFFLINE_RESULT '+json.dumps({'tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'skipped':len(result.skipped)}))
raise SystemExit(not result.wasSuccessful())
'''


def main():
    total = {'tests': 0, 'failures': 0, 'errors': 0, 'skipped': 0}
    failed = False
    with tempfile.TemporaryDirectory(prefix='abbv2-offline-guard-') as folder:
        (Path(folder) / 'sitecustomize.py').write_text(GUARD, encoding='utf-8')
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONPATH=folder)
        for group in GROUPS:
            print('SUITE ' + group, flush=True)
            result = subprocess.run([sys.executable, '-B', '-c', RUN,
                                     str(ROOT / 'study/batch-preparation-20260914/source')],
                                    cwd=ROOT / group, env=env, text=True,
                                    stdout=subprocess.PIPE)
            print(result.stdout, end='', flush=True)
            summary = [line for line in result.stdout.splitlines() if line.startswith('OFFLINE_RESULT ')]
            if len(summary) != 1:
                failed = True
                continue
            for key, value in json.loads(summary[0].removeprefix('OFFLINE_RESULT ')).items():
                total[key] += value
            failed |= result.returncode != 0
    print('ALL_SUITES ' + json.dumps(total), flush=True)
    return int(failed)


if __name__ == '__main__':
    raise SystemExit(main())
