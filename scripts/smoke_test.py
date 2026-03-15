"""
Post-deploy smoke tests.
Verifikasi bahwa app berjalan dengan benar setelah deploy.

Usage:
    python3 scripts/smoke_test.py                    # default localhost:8000
    python3 scripts/smoke_test.py https://myapp.com  # custom URL
"""

import json
import sys
import urllib.error
import urllib.request

GREEN = "\033[0;32m"
RED = "\033[0;31m"
YELLOW = "\033[0;33m"
CYAN = "\033[0;36m"
RESET = "\033[0m"

BASE_URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"

results: list[tuple[str, bool, str]] = []


def test(
    name: str,
    method: str,
    path: str,
    body: dict | None = None,
    expect_status: int = 200,
    expect_body_contains: str | None = None,
):
    """Run a single smoke test."""
    url = f"{BASE_URL}{path}"
    try:
        if body:
            data = json.dumps(body).encode("utf-8")
            req = urllib.request.Request(
                url, data=data, method=method, headers={"Content-Type": "application/json"}
            )
        else:
            req = urllib.request.Request(url, method=method)

        with urllib.request.urlopen(req, timeout=10) as resp:
            status = resp.status
            resp_body = resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        status = e.code
        resp_body = e.read().decode("utf-8")
    except Exception as e:
        results.append((name, False, f"Connection error: {e}"))
        return

    passed = status == expect_status
    if passed and expect_body_contains:
        passed = expect_body_contains in resp_body

    detail = f"status={status}"
    if not passed:
        detail += f" (expected {expect_status})"
        if expect_body_contains and expect_body_contains not in resp_body:
            detail += f", body missing '{expect_body_contains}'"

    results.append((name, passed, detail))


def main():
    print()
    print(f"{CYAN}╔══════════════════════════════════════════╗{RESET}")
    print(f"{CYAN}║    🔥 Post-Deploy Smoke Tests            ║{RESET}")
    print(f"{CYAN}║    Target: {BASE_URL:<29s}║{RESET}")
    print(f"{CYAN}╚══════════════════════════════════════════╝{RESET}")
    print()

    # ── Test 1: Health check ──
    test(
        name="Health check",
        method="GET",
        path="/health",
        expect_status=200,
        expect_body_contains='"status"',
    )

    # ── Test 2: Index page ──
    test(
        name="Index page loads",
        method="GET",
        path="/",
        expect_status=200,
        expect_body_contains="html",
    )

    # ── Test 3: Chat API - validation ──
    test(
        name="Chat API rejects empty message",
        method="POST",
        path="/api/chat",
        body={"message": ""},
        expect_status=422,
    )

    # ── Test 4: Chat API - valid request ──
    test(
        name="Chat API accepts valid request",
        method="POST",
        path="/api/chat",
        body={"message": "ping", "history": []},
        expect_status=200,
        expect_body_contains='"reply"',
    )

    # ── Print results ──
    print(f"{'Test':<40s} {'Result':<10s} Details")
    print("─" * 75)

    passed = 0
    failed = 0
    for name, ok, detail in results:
        if ok:
            passed += 1
            print(f"  {GREEN}✔{RESET} {name:<37s} {GREEN}PASS{RESET}     {detail}")
        else:
            failed += 1
            print(f"  {RED}✗{RESET} {name:<37s} {RED}FAIL{RESET}     {detail}")

    print("─" * 75)
    total = passed + failed
    print(f"  Total: {total}  |  Passed: {GREEN}{passed}{RESET}  |  Failed: {RED}{failed}{RESET}")
    print()

    if failed > 0:
        print(f"{RED}✗ Smoke tests failed! Deploy mungkin bermasalah.{RESET}")
        sys.exit(1)
    else:
        print(f"{GREEN}✔ All smoke tests passed! App berjalan normal.{RESET}")


if __name__ == "__main__":
    main()
