#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Shared rqamsc runtime initialization helpers for skill scripts.
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RuntimeConfig:
    """
    Runtime configuration loaded from environment variables.

    :param python_executable: Active Python interpreter path.
    :param username: RQAMSC login username.
    :param password: RQAMSC login password.
    :param uri: AMS endpoint URI.
    :param ssl_verify: Whether SSL certificate verification is enabled.
    :param workspace: Optional workspace name to switch to after initialization.
    """

    python_executable: Path
    username: str | None
    password: str | None
    uri: str | None
    ssl_verify: bool
    workspace: str | None


@dataclass(frozen=True)
class RuntimeInitResult:
    """
    Result returned by rqamsc runtime initialization.

    :param python_executable: Active Python interpreter path.
    :param username: RQAMSC login username.
    :param uri: AMS endpoint URI.
    :param workspace_name: Active workspace name after initialization.
    """

    python_executable: Path
    username: str
    uri: str
    workspace_name: str


class RuntimeConfigError(RuntimeError):
    """
    Raised when required RQAMSC environment variables are missing.
    """

    def __init__(self, missing_keys: list[str]) -> None:
        """
        Initialize the configuration error with missing keys.

        :param missing_keys: Required environment variable names that are absent.
        """

        self.missing_keys = missing_keys
        message = f"Missing required env vars: {', '.join(missing_keys)}"
        super().__init__(message)


def parse_ssl_verify(uri: str, raw_value: str | None) -> bool:
    """
    Parse SSL verification behavior from environment variables.

    :param uri: AMS endpoint URI.
    :param raw_value: Raw RQAMSC_SSL_VERIFY value from the environment.
    :return: Parsed SSL verification flag.
    :raises ValueError: Raised when the raw value cannot be interpreted.
    """

    if raw_value is not None and raw_value != "":
        normalized = raw_value.strip().lower()
        if normalized in {"1", "true", "yes", "y"}:
            return True
        if normalized in {"0", "false", "no", "n"}:
            return False
        raise ValueError(f"Unsupported RQAMSC_SSL_VERIFY value: {raw_value}")
    return uri.startswith("https://")


def build_runtime_config() -> RuntimeConfig:
    """
    Load rqamsc runtime configuration from environment variables.

    :return: Parsed runtime configuration.
    :raises ValueError: Raised when SSL verification configuration is invalid.
    """

    username = os.getenv("RQAMSC_USERNAME")
    password = os.getenv("RQAMSC_PASSWORD")
    uri = os.getenv("RQAMSC_URI")
    workspace = os.getenv("RQAMSC_WORKSPACE")
    ssl_verify_raw = os.getenv("RQAMSC_SSL_VERIFY")
    ssl_verify = parse_ssl_verify(uri or "", ssl_verify_raw)

    return RuntimeConfig(
        python_executable=Path(sys.executable),
        username=username,
        password=password,
        uri=uri,
        ssl_verify=ssl_verify,
        workspace=workspace,
    )


def get_missing_required_keys(config: RuntimeConfig) -> list[str]:
    """
    Compute required environment keys that are missing from configuration.

    :param config: Runtime configuration to validate.
    :return: Missing required key names.
    """

    missing_keys: list[str] = []
    if not config.username:
        missing_keys.append("RQAMSC_USERNAME")
    if not config.password:
        missing_keys.append("RQAMSC_PASSWORD")
    if not config.uri:
        missing_keys.append("RQAMSC_URI")
    return missing_keys


def initialize_rqamsc(config: RuntimeConfig | None = None) -> RuntimeInitResult:
    """
    Initialize rqamsc and switch to the configured workspace when provided.

    :param config: Optional prebuilt runtime configuration.
    :return: Structured initialization result.
    :raises RuntimeConfigError: Raised when required environment variables are missing.
    :raises Exception: Propagates rqamsc import and initialization failures.
    """

    runtime_config = config or build_runtime_config()
    missing_keys = get_missing_required_keys(runtime_config)
    if missing_keys:
        raise RuntimeConfigError(missing_keys)

    import rqamsc

    rqamsc.init(
        username=runtime_config.username,
        password=runtime_config.password,
        uri=runtime_config.uri,
        ssl_verify=runtime_config.ssl_verify,
    )

    workspace_name = "<default>"
    if runtime_config.workspace:
        rqamsc.choose_workspace(runtime_config.workspace)
    current_workspace = rqamsc.current_workspace()
    if current_workspace is not None:
        workspace_name = getattr(current_workspace, "name", None) or str(current_workspace)

    return RuntimeInitResult(
        python_executable=runtime_config.python_executable,
        username=runtime_config.username or "",
        uri=runtime_config.uri or "",
        workspace_name=workspace_name,
    )
