# SPDX-License-Identifier: AGPL-3.0-or-later OR LicenseRef-DevAIble-Commercial
#
# Human Design API
# Copyright (C) 2026 Dogan Turkuler <dogan.turkuler@gmail.com>
# https://devaible.com
#
# This file is part of Human Design API, available under dual license:
#   - AGPL-3.0 (open source): see LICENSE-AGPL
#   - Commercial License: see LICENSE-COMMERCIAL or contact dogan.turkuler@gmail.com

from pydantic import BaseModel, Field
from typing import Dict

class HealthResponse(BaseModel):
    """Schema for the health check response."""
    status: str = Field(..., description="Operational status of the API")
    version: str = Field(..., description="Current version of the API")
    timestamp: str = Field(..., description="ISO 8601 timestamp of the response")
    dependencies: Dict[str, str] = Field(default_factory=dict, description="Status of core dependencies")
