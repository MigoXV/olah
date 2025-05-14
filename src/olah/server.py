# coding=utf-8
# Copyright 2024 XiaHan
#
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.

from contextlib import asynccontextmanager
import datetime
import os
import glob
import argparse
import sys
import time
import traceback
from typing import Annotated, List, Literal, Optional, Sequence, Tuple, Union
from urllib.parse import urljoin
from fastapi import FastAPI, Header, Request, Form
from fastapi.responses import (
    FileResponse,
    HTMLResponse,
    StreamingResponse,
    Response,
    JSONResponse,
)
from fastapi.templating import Jinja2Templates
from fastapi_utils.tasks import repeat_every

import git
import httpx

from olah.proxy.commits import commits_generator
from olah.proxy.pathsinfo import pathsinfo_generator
from olah.proxy.tree import tree_generator
from olah.utils.disk_utils import convert_bytes_to_human_readable, convert_to_bytes, get_folder_size, sort_files_by_access_time, sort_files_by_modify_time, sort_files_by_size
from olah.utils.url_utils import clean_path

from olah.configs import OlahConfig
from olah.errors import error_repo_not_found, error_page_not_found, error_revision_not_found
from olah.mirror.repos import LocalMirrorRepo
from olah.proxy.files import cdn_file_get_generator, file_get_generator
from olah.proxy.lfs import lfs_get_generator, lfs_head_generator
from olah.proxy.meta import meta_generator
from olah.utils.rule_utils import check_proxy_rules_hf, get_org_repo
from olah.utils.repo_utils import (
    check_commit_hf,
    get_commit_hf,
    get_newest_commit_hf,
    parse_org_repo,
)
from olah.constants import OLAH_CODE_DIR, REPO_TYPES_MAPPING

from olah.utils.logging import build_logger
from .logger import LOGGER

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

# from pympler import tracker, classtracker
# tr = tracker.SummaryTracker()
# cr = classtracker.ClassTracker()
# from olah.cache.bitset import Bitset
# from olah.cache.olah_cache import OlahCache, OlahCacheHeader
# cr.track_class(Bitset)
# cr.track_class(OlahCacheHeader)
# cr.track_class(OlahCache)

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
code_file_path = os.path.abspath(__file__)
app = FastAPI(lifespan=lifespan, debug=False)
templates = Jinja2Templates(directory=os.path.join(OLAH_CODE_DIR, "static"))

from .settings import AppSettings

# ======================
# Exception handlers
# ======================
@app.exception_handler(404)
async def custom_404_handler(_, __):
    return error_page_not_found()


# ======================
# Web Page Hooks
# ======================

from .routers import auth, commits, resolve, lfs, meta, pathinfo, repository, tree
app.include_router(auth.router, prefix="")
app.include_router(commits.router, prefix="")
app.include_router(resolve.router, prefix="")
app.include_router(lfs.router, prefix="")
app.include_router(meta.router, prefix="")
app.include_router(pathinfo.router, prefix="")
app.include_router(repository.router, prefix="")
app.include_router(tree.router, prefix="")


def init():
    parser = argparse.ArgumentParser(
        description="Olah Huggingface Mirror Server."
    )
    parser.add_argument("--config", "-c", type=str, default="")
    parser.add_argument("--host", type=str, default="localhost")
    parser.add_argument("--port", type=int, default=8090)
    parser.add_argument("--hf-scheme", type=str, default="https", help="The scheme of huggingface site (http or https)")
    parser.add_argument("--hf-netloc", type=str, default="huggingface.co")
    parser.add_argument("--hf-lfs-netloc", type=str, default="cdn-lfs.huggingface.co")
    parser.add_argument("--mirror-scheme", type=str, default="http", help="The scheme of mirror site (http or https)")
    parser.add_argument("--mirror-netloc", type=str, default="localhost:8090")
    parser.add_argument("--mirror-lfs-netloc", type=str, default="localhost:8090")
    parser.add_argument("--has-lfs-site", action="store_true")
    parser.add_argument("--ssl-key", type=str, default=None, help="The SSL key file path, if HTTPS is used")
    parser.add_argument("--ssl-cert", type=str, default=None, help="The SSL cert file path, if HTTPS is used")
    parser.add_argument("--repos-path", type=str, default="./repos", help="The folder to save cached repositories")
    parser.add_argument("--cache-size-limit", type=str, default="", help="The limit size of cache. (Example values: '100MB', '2GB', '500KB')")
    parser.add_argument("--cache-clean-strategy", type=str, default="LRU", help="The clean strategy of cache. ('LRU', 'FIFO', 'LARGE_FIRST')")
    parser.add_argument("--log-path", type=str, default="./logs", help="The folder to save logs")
    args = parser.parse_args()
    
    LOGGER = build_logger("olah", "olah.log", logger_dir=args.log_path)
    
    def is_default_value(args, arg_name):
        if hasattr(args, arg_name):
            arg_value = getattr(args, arg_name)
            arg_default = parser.get_default(arg_name)
            return arg_value == arg_default
        return False

    if args.config != "":
        config = OlahConfig(args.config)
    else:
        config = OlahConfig()
        
        if not is_default_value(args, "host"):
            config.host = args.host
        if not is_default_value(args, "port"):
            config.port = args.port
        
        if not is_default_value(args, "ssl_key"):
            config.ssl_key = args.ssl_key
        if not is_default_value(args, "ssl_cert"):
            config.ssl_cert = args.ssl_cert
        
        if not is_default_value(args, "repos_path"):
            config.repos_path = args.repos_path
        if not is_default_value(args, "hf_scheme"):
            config.hf_scheme = args.hf_scheme
        if not is_default_value(args, "hf_netloc"):
            config.hf_netloc = args.hf_netloc
        if not is_default_value(args, "hf_lfs_netloc"):
            config.hf_lfs_netloc = args.hf_lfs_netloc
        if not is_default_value(args, "mirror_scheme"):
            config.mirror_scheme = args.mirror_scheme
        if not is_default_value(args, "mirror_netloc"):
            config.mirror_netloc = args.mirror_netloc
        if not is_default_value(args, "mirror_lfs_netloc"):
            config.mirror_lfs_netloc = args.mirror_lfs_netloc
        if not is_default_value(args, "cache_size_limit"):
            config.cache_size_limit = convert_to_bytes(args.cache_size_limit)
        if not is_default_value(args, "cache_clean_strategy"):
            config.cache_clean_strategy = args.cache_clean_strategy
        else:
            if not args.has_lfs_site and not is_default_value(args, "mirror_netloc"):
                config.mirror_lfs_netloc = args.mirror_netloc

    if is_default_value(args, "host"):
        args.host = config.host
    if is_default_value(args, "port"):
        args.port = config.port
    if is_default_value(args, "ssl_key"):
        args.ssl_key = config.ssl_key
    if is_default_value(args, "ssl_cert"):
        args.ssl_cert = config.ssl_cert
    if is_default_value(args, "repos_path"):
        args.repos_path = config.repos_path
    
    if is_default_value(args, "hf_scheme"):
        args.hf_scheme = config.hf_scheme
    if is_default_value(args, "hf_netloc"):
        args.hf_netloc = config.hf_netloc
    if is_default_value(args, "hf_lfs_netloc"):
        args.hf_lfs_netloc = config.hf_lfs_netloc
    if is_default_value(args, "mirror_scheme"):
        args.mirror_scheme = config.mirror_scheme
    if is_default_value(args, "mirror_netloc"):
        args.mirror_netloc = config.mirror_netloc
    if is_default_value(args, "mirror_lfs_netloc"):
        args.mirror_lfs_netloc = config.mirror_lfs_netloc
    
    if is_default_value(args, "cache_size_limit"):
        args.cache_size_limit = config.cache_size_limit
    if is_default_value(args, "cache_clean_strategy"):
        args.cache_clean_strategy = config.cache_clean_strategy

    # Post processing
    if "," in args.host:
        args.host = args.host.split(",")
    
    args.mirror_scheme = config.mirror_scheme = "http" if args.ssl_key is None else "https"

    print(args)
    # Warnings
    if config.cache_size_limit is not None:
        logger.info(f"""
======== WARNING ========
Due to the cache_size_limit parameter being set, Olah will periodically delete cache files.
Please ensure that the cache directory specified in repos_path '{config.repos_path}' is correct.
Incorrect settings may result in unintended file deletion and loss!!! !!!
=========================""")
        for i in range(10):
            time.sleep(0.2)
    
    # Init app settings
    app.state.app_settings = AppSettings(config=config)
    return args

def main():
    args = init()
    if __name__ == "__main__":
        import uvicorn
        uvicorn.run(
            "olah.server:app",
            host=args.host,
            port=args.port,
            log_level="info",
            reload=False,
            ssl_keyfile=args.ssl_key,
            ssl_certfile=args.ssl_cert
        )

def cli():
    args = init()
    import uvicorn
    uvicorn.run(
        "olah.server:app",
        host=args.host,
        port=args.port,
        log_level="info",
        reload=False,
        ssl_keyfile=args.ssl_key,
        ssl_certfile=args.ssl_cert,
    )

if __name__ in ["olah.server", "__main__"]:
    main()
