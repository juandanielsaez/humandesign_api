# SPDX-License-Identifier: AGPL-3.0-or-later OR LicenseRef-DevAIble-Commercial
#
# Human Design API
# Copyright (C) 2026 Dogan Turkuler <dogan.turkuler@gmail.com>
# https://devaible.com
#
# This file is part of Human Design API, available under dual license:
#   - AGPL-3.0 (open source): see LICENSE-AGPL
#   - Commercial License: see LICENSE-COMMERCIAL or contact dogan.turkuler@gmail.com

import tomllib
from pathlib import Path

def get_version() -> str:
    """Reads the project version from pyproject.toml."""
    # Find pyproject.toml in the project root
    # Assuming this file is in src/humandesign/utils/version.py
    # Root is 3 levels up from this file
    current_file = Path(__file__).resolve()
    # Go up: utils -> humandesign -> src -> root
    root_dir = current_file.parent.parent.parent.parent
    pyproject_path = root_dir / "pyproject.toml"

    if pyproject_path.exists():
        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)
            return data.get("project", {}).get("version", "0.0.0")
    
    return "0.0.0"
