# Security Scanner

A small security scanning tool with both static and dynamic testing, built to understand how automated vulnerability detection tools (like BreachX's Typhon/PatchZero) work under the hood. Coverage now maps to the full OWASP Top 10:2025.

## What it does

**Static analysis (`static/`)**
- `bandit_scan.py` — wraps [Bandit](https://bandit.readthedocs.io/) to scan Python/Flask source code for known vulnerability patterns without running the app. Parses Bandit's JSON output into a clean, severity-grouped report. Also catches weak hashing (A04) and insecure deserialization (A08) for free, no extra code needed.
- `dependency_scan.py` — wraps [pip-audit](https://pypi.org/project/pip-audit/) to check `requirements.txt` for known CVEs in installed packages.
- `crypto_check.py` — checks source for `SESSION_COOKIE_SECURE` and `Talisman()` usage, i.e. whether TLS/cookie enforcement is actually configured.
- `logging_check.py` — checks whether logging is configured at all, then flags security-relevant functions (login, access checks, etc.) that have no adjacent log call.

**Dynamic testing (`dynamic/`)**
Runs real attacks against a live Flask app to test for:
- SQL injection (login bypass attempt) and CSRF/rate-limit/header checks — `attack_test.py`
- Broken access control / IDOR (one user accessing another user's data by guessing an ID) — `idor_test.py`
- Cross-site scripting (stored payload in a text field, checked for whether it survives unescaped) — `xss_test.py`
- Weak password acceptance and session fixation — `auth_test.py`
- Error handling / stack trace leakage on malformed input — `error_leak_test.py`

(Edit the `base_url` / `v1_url` / `v2_url` variables in each file to point at your running app(s).)

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
| Dependency scan (pip-audit) | 0 vulnerabilities | 0 vulnerabilities |
| IDOR / access control | Protected | Protected |
| XSS (stored payload) | Protected (Jinja2 auto-escape only) | Protected (Jinja2 + bleach) |
| Weak password acceptance | Vulnerable (accepts 1-char password) | Protected |
| Session fixation | Protected | Protected |
| Security logging coverage | None configured | Configured, but not wired to security events |
| Error handling / stack trace leakage | Vulnerable (leaks full Werkzeug debugger) | Protected |

**Note:** SQL injection and IDOR/access-control were expected to be present in v1 based on the original build spec, but testing showed the app's queries were already parameterized and ownership-checked despite the spec asking for no hardening — a good reminder to verify assumptions against actual running code rather than trusting a spec alone.

## OWASP Top 10:2025 Coverage

### A01: Broken Access Control
Tested with `dynamic/idor_test.py`. Two users register, one creates a trip, the other tries to view it directly by ID. Both v1 and v2 came back protected (v1 via redirect-with-flash, v2 via 404), though v1 wasn't explicitly built with this hardening in mind.

### A02: Security Misconfiguration
Caught by `static/bandit_scan.py` with no new code needed. Flagged `debug=True` on v1 (B201, High) and bind-all-interfaces on both apps (B104, Medium). The debug flag turned out to matter a lot more than it looks on paper, see A10.

### A03: Software Supply Chain Failures
Tested with `static/dependency_scan.py`, wrapping pip-audit. Validated against a deliberately outdated `Flask==0.12` requirements file (8 raw CVEs, 4 unique) before trusting it against the real apps, which both came back clean.

### A04: Cryptographic Failures
Two-part check. Weak hashing is caught by Bandit (B324), confirmed against a throwaway MD5 test file. Transport/cookie enforcement is checked by `static/crypto_check.py`, which looks for `SESSION_COOKIE_SECURE` and `Talisman()`. v1 has neither, v2 has both.

### A05: Injection
Covered three ways. SQL injection and CSRF are tested in `dynamic/attack_test.py`. Command injection is covered in `vuln-research` (vulnerable/fixed CLI tool). XSS is tested in `dynamic/xss_test.py`; both apps came back protected, but for different reasons worth noting. v1 relies entirely on Jinja2's default auto-escaping, no deliberate sanitization. v2 adds `bleach.clean()` on top, which strips tags outright rather than escaping them.

### A06: Insecure Design
Not automatable. Documented as a manual review checklist instead of code:
- Are authorization checks designed into the data model (e.g. `user_id` ownership columns) or bolted on per-route?
- Is there a single source of truth for "who can access what," or is it re-implemented in each view?
- Are destructive actions (delete trip, delete account) protected by confirmation or re-authentication?
- Does the registration flow allow enumeration of existing usernames?

### A07: Authentication Failures
Two checks in `dynamic/auth_test.py`. Weak password acceptance: v1 accepts a single-character password, v2 rejects it. Session fixation: both apps regenerate the session cookie on login, tested by planting a fake pre-login cookie and confirming it gets replaced.

### A08: Software/Data Integrity Failures
Caught by Bandit with no new code needed (B403, pickle import detection), confirmed against `vuln-research`'s insecure deserialization example.

### A09: Security Logging and Alerting Failures
Tested with `static/logging_check.py`. Checks whether logging is configured at all, then flags security-relevant functions (login, access checks, etc.) with no adjacent log call. v1 has no logging at all. v2 has logging configured, but it's only wired to a generic unhandled-error handler, not to actual security events like failed logins or denied access, so the same functions end up flagged in both apps despite v2 "having logging."

### A10: Mishandling of Exceptional Conditions
Tested with `dynamic/error_leak_test.py`. Sending a POST request missing a required form field crashed v1 with a 500 and served Flask's full interactive debugger, source code and all, because of the `debug=True` flagged under A02. v2 validated the input and rejected it cleanly instead. This is the clearest case in the project of a static finding becoming a concretely exploitable issue once tested dynamically.

## Setup
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Static scans:
```
python3 static/bandit_scan.py /path/to/app
python3 static/dependency_scan.py /path/to/app/requirements.txt
python3 static/crypto_check.py /path/to/app
python3 static/logging_check.py /path/to/app
```

Dynamic tests (point the `base_url`/`v1_url`/`v2_url` variables in each file at your running app first):
```
python3 dynamic/attack_test.py
python3 dynamic/idor_test.py
python3 dynamic/xss_test.py
python3 dynamic/auth_test.py
python3 dynamic/error_leak_test.py
```

## Notes

- Only test apps you own or have explicit permission to test. This tool sends real attack payloads (SQL injection strings, XSS payloads, brute-force login attempts, malformed input designed to trigger crashes) to whatever URL you point it at.