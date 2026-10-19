"""Safe read-only public deployment checks: python scripts/smoke_test.py URL"""
import json
import sys
import urllib.request
from urllib.error import HTTPError, URLError

base = (sys.argv[1] if len(sys.argv) > 1 else 'http://127.0.0.1:8000').rstrip('/')
for path in ('/', '/health', '/api/meta', '/docs'):
    try:
        with urllib.request.urlopen(base + path, timeout=12) as response:
            payload = response.read()
            print(f'PASS  {response.status}  {path}  ({len(payload)} bytes)')
    except (HTTPError, URLError, TimeoutError) as exc:
        print(f'FAIL {path}  {exc}')
        sys.exit(1)
print('Public smoke test passed. Run pytest for full authentication, RBAC, CSRF and workflow coverage.')
