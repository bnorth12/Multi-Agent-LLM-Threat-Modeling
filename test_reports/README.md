# Test Reports Directory

All test logs, outputs, and artifacts are stored under this directory in a structured format:

- `test_reports/YYYY-MM-DD/[test_type]/` for all logs and outputs by date and test type.
- Each test run creates a timestamped log file and, if applicable, subfolders for artifacts (screenshots, downloads, etc).

## How to Use

- Configure the test shell environment first (PowerShell):

  ```powershell
  .\scripts\set_test_env.ps1
  ```

  This enforces:
  - `PYTHONIOENCODING=utf-8` for Unicode-safe logs.
  - `RUN_VISIBLE_BROWSER_TESTS=1` for browser smoke runs.
  - A preflight warning when `GROK_API`/`GROK_API_KEY` is missing.

- Use the `scripts/run_and_log.py` wrapper to run any test script and automatically capture logs:

  ```sh
  python scripts/run_and_log.py scripts/verify_sprint_traceability.py --sprint 2026_11
  ```
  This will create a log file in `test_reports/YYYY-MM-DD/verify_sprint_traceability/`.

- For scripts that support a `--log` argument (like `verify_sprint_traceability.py`), you can also run directly:

  ```sh
  python scripts/verify_sprint_traceability.py --sprint 2026_11 --log test_reports/YYYY-MM-DD/verify_sprint_traceability/traceability.log
  ```

- All test artifacts (logs, screenshots, reports) from E2E and smoke tests are also written to subfolders here.

- Browser E2E requirement:
  - One of `GROK_API` or `GROK_API_KEY` must be set for `scripts/live_browser_e2e_smoke.py`.
  - `scripts/run_and_log.py` performs this check and exits with a clear error if missing.

## CI/CD Integration

- Update your CI/CD pipeline to use the `run_and_log.py` wrapper or redirect outputs to this directory.
- This ensures all test artifacts are consistently organized and easy to review.

## .gitignore

- All files in `test_reports/` are ignored by git except this README.md.
- Do not manually add logs or outputs to version control.
