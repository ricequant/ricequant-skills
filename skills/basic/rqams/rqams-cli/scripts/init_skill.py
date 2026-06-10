#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Initialize cached rqams-cli docs and regenerate lightweight indexes when needed.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
import time
from urllib.error import URLError
from urllib.request import urlopen


GITHUB_RAW_BASE = "https://raw.githubusercontent.com/ricequant/rqams-cli/master/docs"
DEFAULT_CACHE_DAYS = 7
DOC_FILES = [
    "rqams_cli_manual.md",
    "commands/analysis.md",
    "commands/auth_workspace.md",
    "commands/balance.md",
    "commands/customized.md",
    "commands/customized_benchmark.md",
    "commands/customized_indicator.md",
    "commands/events.md",
    "commands/paper_trading.md",
    "commands/permissions.md",
    "commands/products.md",
    "commands/reconciliation.md",
    "commands/reports.md",
    "commands/statements_and_valuation.md",
    "commands/trades.md",
]


def skill_root() -> Path:
    return Path(__file__).resolve().parent.parent


def cache_docs_dir() -> Path:
    return skill_root() / "cache" / "docs"


def command_index_path() -> Path:
    return skill_root() / "cache" / "doc_index" / "command_index.md"


def cached_doc_paths() -> list[Path]:
    return [cache_docs_dir() / rel_path for rel_path in DOC_FILES]


def required_cache_paths() -> list[Path]:
    return cached_doc_paths() + [command_index_path()]


def cache_expired(path: Path, cache_days: int = DEFAULT_CACHE_DAYS) -> bool:
    if not path.exists():
        return True
    max_age_seconds = cache_days * 24 * 60 * 60
    return time.time() - path.stat().st_mtime > max_age_seconds


def download_text(url: str, retries: int = 3, timeout_seconds: int = 60) -> str:
    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            with urlopen(url, timeout=timeout_seconds) as response:
                return response.read().decode("utf-8")
        except (OSError, TimeoutError, URLError) as exc:
            last_error = exc
            if attempt < retries:
                time.sleep(attempt)
    raise RuntimeError(f"Failed to download {url}") from last_error


def download_docs(target_dir: Path) -> None:
    for rel_path in DOC_FILES:
        target_path = target_dir / rel_path
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(download_text(f"{GITHUB_RAW_BASE}/{rel_path}"), encoding="utf-8")


def generate_indexes() -> None:
    from generate_indexes import generate_command_index

    generate_command_index(cache_docs_dir(), command_index_path())


def refresh_docs() -> str:
    target_dir = cache_docs_dir()
    target_dir.mkdir(parents=True, exist_ok=True)

    try:
        download_docs(target_dir)
    except RuntimeError as exc:
        raise RuntimeError("Failed to download rqams-cli docs from GitHub") from exc
    return f"GitHub raw: {GITHUB_RAW_BASE}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Initialize rqams-cli skill cache")
    parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Force refresh cached docs and indexes",
    )
    args = parser.parse_args()

    needs_refresh = args.force_refresh or any(cache_expired(path) for path in required_cache_paths())
    if needs_refresh:
        source_description = refresh_docs()
        print(f"[INFO] Refreshed rqams-cli docs cache from {source_description}")
        generate_indexes()
        print("[INFO] Regenerated command index")

    print("Done")
    return 0


if __name__ == "__main__":
    sys.exit(main())
