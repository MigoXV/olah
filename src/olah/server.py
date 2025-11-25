# coding=utf-8
# Copyright 2024 XiaHan
#
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.

from contextlib import asynccontextmanager
import datetime
import os
import sys
from typing import Sequence, Tuple, Union

from fastapi import FastAPI
from fastapi_utils.tasks import repeat_every

import httpx

from olah.utils.disk_utils import (
    convert_bytes_to_human_readable,
    get_folder_size,
    sort_files_by_access_time,
    sort_files_by_modify_time,
    sort_files_by_size,
)

BASE_SETTINGS = False
if not BASE_SETTINGS:
    try:
        from pydantic import BaseSettings
        BASE_SETTINGS = True
    except ImportError:
        BASE_SETTINGS = False

if not BASE_SETTINGS:
    try:
        from pydantic_settings import BaseSettings
        BASE_SETTINGS = True
    except ImportError:
        BASE_SETTINGS = False

if not BASE_SETTINGS:
    raise Exception("Cannot import BaseSettings from pydantic or pydantic-settings")

from olah.configs import OlahConfig
from olah.errors import error_page_not_found
from olah.router import router


# ======================
# Utilities
# ======================
async def check_connection(url: str) -> bool:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method="HEAD",
                url=url,
                timeout=10,
            )
        if response.status_code != 200:
            return False
        else:
            return True
    except httpx.TimeoutException:
        return False


@repeat_every(seconds=60*5)
async def check_hf_connection() -> None:
    if app.state.app_settings.config.offline:
        return
    scheme = app.state.app_settings.config.hf_scheme
    netloc = app.state.app_settings.config.hf_netloc
    hf_online_status = await check_connection(
        f"{scheme}://{netloc}/datasets/Salesforce/wikitext/resolve/main/.gitattributes"
    )
    if not hf_online_status:
        print("Failed to reach Huggingface Site.", file=sys.stderr)


@repeat_every(seconds=60 * 60)
async def check_disk_usage() -> None:
    if app.state.app_settings.config.offline:
        return
    if app.state.app_settings.config.cache_size_limit is None:
        return

    limit_size = app.state.app_settings.config.cache_size_limit
    current_size = get_folder_size(app.state.app_settings.config.repos_path)

    limit_size_h = convert_bytes_to_human_readable(limit_size)
    current_size_h = convert_bytes_to_human_readable(current_size)

    if current_size < limit_size:
        return
    print(
        f"Cache size exceeded! Limit: {limit_size_h}, Current: {current_size_h}."
    )
    print("Cleaning...")
    files_path = os.path.join(app.state.app_settings.config.repos_path, "files")
    lfs_path = os.path.join(app.state.app_settings.config.repos_path, "lfs")

    files: Sequence[Tuple[str, Union[int, datetime.datetime]]] = []
    if app.state.app_settings.config.cache_clean_strategy == "LRU":
        files = sort_files_by_access_time(files_path) + sort_files_by_access_time(
            lfs_path
        )
        files = sorted(files, key=lambda x: x[1])
    elif app.state.app_settings.config.cache_clean_strategy == "FIFO":
        files = sort_files_by_modify_time(files_path) + sort_files_by_modify_time(
            lfs_path
        )
        files = sorted(files, key=lambda x: x[1])
    elif app.state.app_settings.config.cache_clean_strategy == "LARGE_FIRST":
        files = sort_files_by_size(files_path) + sort_files_by_size(lfs_path)
        files = sorted(files, key=lambda x: x[1], reverse=True)

    for filepath, index in files:
        if current_size < limit_size:
            break
        filesize = os.path.getsize(filepath)
        os.remove(filepath)
        current_size -= filesize
        print(f"Remove file: {filepath}. File Size: {convert_bytes_to_human_readable(filesize)}")

    current_size = get_folder_size(app.state.app_settings.config.repos_path)
    current_size_h = convert_bytes_to_human_readable(current_size)
    print(f"Cleaning finished. Limit: {limit_size_h}, Current: {current_size_h}.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # TODO: Check repo cache path
    await check_hf_connection()
    await check_disk_usage()
    yield


# ======================
# Application
# ======================
app = FastAPI(lifespan=lifespan, debug=False)

# Include router
app.include_router(router)


class AppSettings(BaseSettings):
    # The address of the model controller.
    config: OlahConfig = OlahConfig()


# ======================
# Exception handlers
# ======================
@app.exception_handler(404)
async def custom_404_handler(_, __):
    return error_page_not_found()
