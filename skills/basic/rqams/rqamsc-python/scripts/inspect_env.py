#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Inspect rqamsc runtime environment and print concise initialization context.
"""

from __future__ import annotations

from rqamsc_runtime import RuntimeConfigError, build_runtime_config, initialize_rqamsc


def main() -> int:
    config = build_runtime_config()
    print(f"Python: {config.python_executable}")

    try:
        result = initialize_rqamsc(config)
        print(f"Account: {result.username}")
        print(f"AMS URI: {result.uri}")
        print(f"Workspace: {result.workspace_name}")
        return 0
    except RuntimeConfigError as exc:
        print("RQAMSC env: incomplete")
        print(f"Missing: {' / '.join(exc.missing_keys)}")
        return 0
    except Exception as exc:
        print(f"RQAMSC init failed: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
