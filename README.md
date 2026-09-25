# Security Scanner

A small security scanning tool with both static and dynamic testing, built to understand how automated vulnerability detection tools (like BreachX's Typhon/PatchZero) work under the hood.

## What it does

**Static analysis (`static/bandit_scan.py`)**
Wraps [Bandit](https://bandit.readthedocs.io/) to scan Python/Flask source code for known vulnerability patterns without running the app. Parses Bandit's JSON output into a clean, severity-grouped report.


**Dynamic testing (`dynamic/attack_test.py`)**
Runs real attacks against a live Flask app to test for:
- SQL injection (login bypass attempt)
- Missing CSRF protection
- Missing rate limiting on login
- Missing security headers (CSP, X-Frame-Options, X-Content-Type-Options)


(Edit the `v1_url`/`v2_url` variables in the file to point at your running app(s).)

## Test subjects

This was built and validated against two versions of a sample Flask app (a basic travel booking app):
- **v1** — built without explicit security hardening
- **v2** — built with hardening: parameterized queries, CSRF protection, rate limiting, security headers, hashed passwords, secure session cookies

## Results

| Test | v1 | v2 |
|---|---|---|
| SQL Injection | Safe | Safe |
| CSRF Protection | Vulnerable | Protected |
| Rate Limiting | Vulnerable | Protected (blocked at attempt 5) |
| Security Headers | Vulnerable (all missing) | Protected (all present) |
| Bandit static scan | 1 High, 2 Medium | 0 High, 2 Medium |

**Note:** SQL injection and IDOR/access-control were expected to be present in v1 based on the original build spec, but testing showed the app's queries were already parameterized and ownership-checked despite the spec asking for no hardening — a good reminder to verify assumptions against actual running code rather than trusting a spec alone.

## Setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

Point it towards python static/bandit_scan.py /path/to/app for defensive scanning, and for the offensive scanning python dynamic/attack_test.py


## Notes

- Only test apps you own or have explicit permission to test. This tool sends real attack payloads (SQL injection strings, brute-force login attempts) to whatever URL you point it at.
