# coding=utf-8
# Copyright 2024 XiaHan
#
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Optional

from fastapi.templating import Jinja2Templates

from olah.configs import OlahConfig
from olah.constants import OLAH_CODE_DIR
from olah.utils.logging import build_logger


@dataclass
class AppContext:
    """Container for configuration and shared infrastructure."""

    config: OlahConfig
    logger: logging.Logger
    templates: Jinja2Templates

    @staticmethod
    def build(config_path: Optional[str] = None) -> "AppContext":
        config = OlahConfig.from_toml(config_path)
        logger = build_logger(__name__)
        templates = Jinja2Templates(directory=os.path.join(OLAH_CODE_DIR, "static"))
        return AppContext(config=config, logger=logger, templates=templates)
