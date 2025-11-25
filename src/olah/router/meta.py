# coding=utf-8
# Copyright 2024 XiaHan
#
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.

import os
import traceback
from typing import Literal, Optional

import git
import httpx
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse, Response, JSONResponse

from olah.constants import REPO_TYPES_MAPPING
from olah.errors import error_repo_not_found, error_page_not_found, error_revision_not_found
from olah.mirror.repos import LocalMirrorRepo
from olah.proxy.meta import meta_generator
from olah.utils.logging import build_logger
from olah.utils.repo_utils import (
    check_commit_hf,
    get_commit_hf,
    get_newest_commit_hf,
    parse_org_repo,
)
from olah.utils.rule_utils import check_proxy_rules_hf

logger = build_logger("olah.router.meta", "olah_router_meta.log")

router = APIRouter()


async def meta_proxy_common(
    app,
    repo_type: Literal["models", "datasets", "spaces"],
    org: str,
    repo: str,
    commit: str,
    method: str,
    authorization: Optional[str]
) -> Response:
    # FIXME: do not show the private repos to other user besides owner, even though the repo was cached
    if repo_type not in REPO_TYPES_MAPPING.keys():
        return error_page_not_found()
    if not await check_proxy_rules_hf(app, repo_type, org, repo):
        return error_repo_not_found()
    # Check Mirror Path
    for mirror_path in app.state.app_settings.config.mirrors_path:
        git_path = os.path.join(mirror_path, repo_type, org, repo)
        try:
            git_path = os.path.join(mirror_path, repo_type, org or '', repo)
            if os.path.exists(git_path):
                local_repo = LocalMirrorRepo(git_path, repo_type, org, repo)
                meta_data = local_repo.get_meta(commit)
                if meta_data is None:
                    continue
                return JSONResponse(content=meta_data)
        except git.exc.InvalidGitRepositoryError:
            logger.warning(f"Local repository {git_path} is not a valid git reposity.")
            continue

    # Proxy the HF File Meta
    try:
        if not app.state.app_settings.config.offline:
            if not await check_commit_hf(app, repo_type, org, repo, commit=None,
                authorization=authorization,
            ):
                return error_repo_not_found()
            if not await check_commit_hf(app, repo_type, org, repo, commit=commit,
                authorization=authorization,
            ):
                return error_revision_not_found(revision=commit)
        commit_sha = await get_commit_hf(app, repo_type, org, repo, commit=commit,
            authorization=authorization,
        )
        if commit_sha is None:
            return error_repo_not_found()
        # if branch name and online mode, refresh branch info
        if not app.state.app_settings.config.offline and commit_sha != commit:
            generator = meta_generator(
                app=app,
                repo_type=repo_type,
                org=org,
                repo=repo,
                commit=commit,
                override_cache=True,
                method=method,
                authorization=authorization,
            )
            async for _ in generator:
                pass
            generator = meta_generator(
                app=app,
                repo_type=repo_type,
                org=org,
                repo=repo,
                commit=commit_sha,
                override_cache=True,
                method=method,
                authorization=authorization,
            )
        else:
            generator = meta_generator(
                app=app,
                repo_type=repo_type,
                org=org,
                repo=repo,
                commit=commit_sha,
                override_cache=False,
                method=method,
                authorization=authorization,
            )
        headers = await generator.__anext__()
        return StreamingResponse(generator, headers=headers)
    except httpx.ConnectTimeout:
        traceback.print_exc()
        return Response(status_code=504)


@router.head("/api/{repo_type}/{org_repo}")
@router.get("/api/{repo_type}/{org_repo}")
async def meta_proxy(repo_type: str, org_repo: str, request: Request):
    app = request.app
    org, repo = parse_org_repo(org_repo)
    if org is None and repo is None:
        return error_repo_not_found()
    if not app.state.app_settings.config.offline:
        new_commit = await get_newest_commit_hf(
            app,
            repo_type,
            org,
            repo,
            authorization=request.headers.get("authorization", None),
        )
        if new_commit is None:
            return error_repo_not_found()
    else:
        new_commit = "main"
    return await meta_proxy_common(
        app=app,
        repo_type=repo_type,
        org=org,
        repo=repo,
        commit=new_commit,
        method=request.method.lower(),
        authorization=request.headers.get("authorization", None),
    )


@router.head("/api/{repo_type}/{org}/{repo}")
@router.get("/api/{repo_type}/{org}/{repo}")
async def meta_proxy_org_repo(repo_type: str, org: str, repo: str, request: Request):
    app = request.app
    if not app.state.app_settings.config.offline:
        new_commit = await get_newest_commit_hf(
            app,
            repo_type,
            org,
            repo,
            authorization=request.headers.get("authorization", None),
        )
        if new_commit is None:
            return error_repo_not_found()
    else:
        new_commit = "main"
    return await meta_proxy_common(
        app=app,
        repo_type=repo_type,
        org=org,
        repo=repo,
        commit=new_commit,
        method=request.method.lower(),
        authorization=request.headers.get("authorization", None),
    )


@router.head("/api/{repo_type}/{org}/{repo}/revision/{commit}")
@router.get("/api/{repo_type}/{org}/{repo}/revision/{commit}")
async def meta_proxy_commit2(
    repo_type: str, org: str, repo: str, commit: str, request: Request
):
    app = request.app
    return await meta_proxy_common(
        app=app,
        repo_type=repo_type,
        org=org,
        repo=repo,
        commit=commit,
        method=request.method.lower(),
        authorization=request.headers.get("authorization", None),
    )


@router.head("/api/{repo_type}/{org_repo}/revision/{commit}")
@router.get("/api/{repo_type}/{org_repo}/revision/{commit}")
async def meta_proxy_commit(
    repo_type: str, org_repo: str, commit: str, request: Request
):
    app = request.app
    org, repo = parse_org_repo(org_repo)
    if org is None and repo is None:
        return error_repo_not_found()

    return await meta_proxy_common(
        app=app,
        repo_type=repo_type,
        org=org,
        repo=repo,
        commit=commit,
        method=request.method.lower(),
        authorization=request.headers.get("authorization", None),
    )
