# coding=utf-8
# Copyright 2024 XiaHan
#
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.

from urllib.parse import urljoin

import httpx
from fastapi import APIRouter, Request
from fastapi.responses import Response

router = APIRouter()


@router.get("/api/whoami-v2")
async def whoami_v2(request: Request):
    """
    Sensitive Information!!! 
    """
    app = request.app
    new_headers = {k.lower(): v for k, v in request.headers.items()}
    new_headers["host"] = app.state.app_settings.config.hf_netloc
    async with httpx.AsyncClient() as client:
        response = await client.request(
            method="GET",
            url=urljoin(app.state.app_settings.config.hf_url_base(), "/api/whoami-v2"),
            headers=new_headers,
            timeout=10,
        )
    # final_content = decompress_data(response.headers.get("content-encoding", None))
    response_headers = {k.lower(): v for k, v in response.headers.items()}
    if "content-encoding" in response_headers:
        response_headers.pop("content-encoding")
    if "content-length" in response_headers:
        response_headers.pop("content-length")
    return Response(
        content=response.content,
        status_code=response.status_code,
        headers=response_headers,
    )
