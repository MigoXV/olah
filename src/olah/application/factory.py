# coding=utf-8
# Copyright 2024 XiaHan
#
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, Request

from olah.application.context import AppContext


def get_app_context(request: Request) -> AppContext:
    return request.app.state.context


def create_application(config_path: Optional[str] = None) -> FastAPI:
    context = AppContext.build(config_path)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.context = context
        yield

    app = FastAPI(lifespan=lifespan, debug=False)
    app.state.context = context
    return app
