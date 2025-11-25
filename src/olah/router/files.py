# coding=utf-8
# Copyright 2024 XiaHan
#
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.

import os
import traceback

import git
import httpx
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse, Response

from olah.constants import REPO_TYPES_MAPPING
from olah.errors import error_repo_not_found, error_page_not_found
from olah.mirror.repos import LocalMirrorRepo
from olah.model_bin.files import (
    get_file_path as get_model_bin_file_path,
    build_headers as build_model_bin_headers,
    stream_file as stream_model_bin_file,
)
from olah.proxy.files import cdn_file_get_generator, file_get_generator
from olah.utils.logging import build_logger
from olah.utils.repo_utils import (
    check_commit_hf,
    get_commit_hf,
    parse_org_repo,
)
from olah.utils.rule_utils import check_proxy_rules_hf

logger = build_logger("olah.router.files", "olah_router_files.log")

router = APIRouter()


# ======================
# File Head Hooks
# ======================
async def file_head_common(
    app,
    repo_type: str,
    org: str,
    repo: str,
    commit: str,
    file_path: str,
    request: Request
) -> Response:
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
                head = local_repo.get_file_head(commit_hash=commit, path=file_path)
                if head is None:
                    continue
                return Response(headers=head)
        except git.exc.InvalidGitRepositoryError:
            logger.warning(f"Local repository {git_path} is not a valid git reposity.")
            continue

    if (
        repo_type == "models"
        and app.state.app_settings.config.model_bin_enable
        and app.state.app_settings.config.model_bin_path is not None
    ):
        local_path = get_model_bin_file_path(
            app.state.app_settings.config.model_bin_path, org, repo, file_path
        )
        if local_path:
            headers, _ = build_model_bin_headers(
                local_path, request.headers.get("range"), commit
            )
            return Response(headers=headers)

    # Proxy the HF File Head
    try:
        if not app.state.app_settings.config.offline and not await check_commit_hf(
            app,
            repo_type,
            org,
            repo,
            commit=commit,
            authorization=request.headers.get("authorization", None),
        ):
            return error_repo_not_found()
        commit_sha = await get_commit_hf(
            app,
            repo_type,
            org,
            repo,
            commit=commit,
            authorization=request.headers.get("authorization", None),
        )
        if commit_sha is None:
            return error_repo_not_found()
        generator = await file_get_generator(
            app,
            repo_type,
            org,
            repo,
            commit_sha,
            file_path=file_path,
            method="HEAD",
            request=request,
        )
        status_code = await generator.__anext__()
        headers = await generator.__anext__()
        return StreamingResponse(generator, headers=headers, status_code=status_code)
    except httpx.ConnectTimeout:
        traceback.print_exc()
        return Response(status_code=504)


@router.head("/{repo_type}/{org}/{repo}/resolve/{commit}/{file_path:path}")
async def file_head3(
    repo_type: str, org: str, repo: str, commit: str, file_path: str, request: Request
):
    app = request.app
    return await file_head_common(
        app=app,
        repo_type=repo_type,
        org=org,
        repo=repo,
        commit=commit,
        file_path=file_path,
        request=request,
    )


@router.head("/{org_or_repo_type}/{repo_name}/resolve/{commit}/{file_path:path}")
async def file_head2(
    org_or_repo_type: str, repo_name: str, commit: str, file_path: str, request: Request
):
    app = request.app
    if org_or_repo_type in REPO_TYPES_MAPPING.keys():
        repo_type: str = org_or_repo_type
        org, repo = parse_org_repo(repo_name)
        if org is None and repo is None:
            return error_repo_not_found()
    else:
        repo_type: str = "models"
        org, repo = org_or_repo_type, repo_name

    return await file_head_common(
        app=app,
        repo_type=repo_type,
        org=org,
        repo=repo,
        commit=commit,
        file_path=file_path,
        request=request,
    )


@router.head("/{org_repo}/resolve/{commit}/{file_path:path}")
async def file_head(org_repo: str, commit: str, file_path: str, request: Request):
    app = request.app
    repo_type: str = "models"
    org, repo = parse_org_repo(org_repo)
    if org is None and repo is None:
        return error_repo_not_found()
    return await file_head_common(
        app=app,
        repo_type=repo_type,
        org=org,
        repo=repo,
        commit=commit,
        file_path=file_path,
        request=request,
    )


@router.head("/{org_repo}/{hash_file}")
@router.head("/{repo_type}/{org_repo}/{hash_file}")
async def cdn_file_head(org_repo: str, hash_file: str, request: Request, repo_type: str = "models"):
    app = request.app
    org, repo = parse_org_repo(org_repo)
    if org is None and repo is None:
        return error_repo_not_found()

    if not await check_proxy_rules_hf(app, repo_type, org, repo):
        return error_repo_not_found()

    try:
        generator = await cdn_file_get_generator(app, repo_type, org, repo, hash_file, method="HEAD", request=request)
        status_code = await generator.__anext__()
        headers = await generator.__anext__()
        return StreamingResponse(generator, headers=headers, status_code=status_code)
    except httpx.ConnectTimeout:
        return Response(status_code=504)


# ======================
# File Get Hooks
# ======================
async def file_get_common(
    app,
    repo_type: str,
    org: str,
    repo: str,
    commit: str,
    file_path: str,
    request: Request
) -> Response:
    if repo_type not in REPO_TYPES_MAPPING.keys():
        return error_page_not_found()
    if not await check_proxy_rules_hf(app, repo_type, org, repo):
        return error_repo_not_found()
    # Check Mirror Path
    for mirror_path in app.state.app_settings.config.mirrors_path:
        try:
            git_path = os.path.join(mirror_path, repo_type, org or '', repo)
            if os.path.exists(git_path):
                local_repo = LocalMirrorRepo(git_path, repo_type, org, repo)
                content_stream = local_repo.get_file(commit_hash=commit, path=file_path)
                if content_stream is None:
                    continue
                return StreamingResponse(content_stream)
        except git.exc.InvalidGitRepositoryError:
            logger.warning(f"Local repository {git_path} is not a valid git reposity.")
            continue

    if (
        repo_type == "models"
        and app.state.app_settings.config.model_bin_enable
        and app.state.app_settings.config.model_bin_path is not None
    ):
        local_path = get_model_bin_file_path(
            app.state.app_settings.config.model_bin_path, org, repo, file_path
        )
        if local_path:
            headers, ranges = build_model_bin_headers(
                local_path, request.headers.get("range"), commit
            )
            return StreamingResponse(
                stream_model_bin_file(local_path, ranges),
                headers=headers,
                status_code=200,
            )
    try:
        if not app.state.app_settings.config.offline and not await check_commit_hf(
            app,
            repo_type,
            org,
            repo,
            commit=commit,
            authorization=request.headers.get("authorization", None),
        ):
            return error_repo_not_found()
        commit_sha = await get_commit_hf(
            app,
            repo_type,
            org,
            repo,
            commit=commit,
            authorization=request.headers.get("authorization", None),
        )
        if commit_sha is None:
            return error_repo_not_found()
        generator = await file_get_generator(
            app,
            repo_type,
            org,
            repo,
            commit_sha,
            file_path=file_path,
            method="GET",
            request=request,
        )
        status_code = await generator.__anext__()
        headers = await generator.__anext__()
        return StreamingResponse(generator, headers=headers, status_code=status_code)
    except httpx.ConnectTimeout:
        traceback.print_exc()
        return Response(status_code=504)


@router.get("/{repo_type}/{org}/{repo}/resolve/{commit}/{file_path:path}")
async def file_get3(
    org: str, repo: str, commit: str, file_path: str, request: Request, repo_type: str
):
    app = request.app
    return await file_get_common(
        app=app,
        repo_type=repo_type,
        org=org,
        repo=repo,
        commit=commit,
        file_path=file_path,
        request=request,
    )


@router.get("/{org_or_repo_type}/{repo_name}/resolve/{commit}/{file_path:path}")
async def file_get2(
    org_or_repo_type: str, repo_name: str, commit: str, file_path: str, request: Request
):
    app = request.app
    if org_or_repo_type in REPO_TYPES_MAPPING.keys():
        repo_type: str = org_or_repo_type
        org, repo = parse_org_repo(repo_name)
        if org is None and repo is None:
            return error_repo_not_found()
    else:
        repo_type: str = "models"
        org, repo = org_or_repo_type, repo_name

    return await file_get_common(
        app=app,
        repo_type=repo_type,
        org=org,
        repo=repo,
        commit=commit,
        file_path=file_path,
        request=request,
    )


@router.get("/{org_repo}/resolve/{commit}/{file_path:path}")
async def file_get(org_repo: str, commit: str, file_path: str, request: Request):
    app = request.app
    repo_type: str = "models"
    org, repo = parse_org_repo(org_repo)
    if org is None and repo is None:
        return error_repo_not_found()

    return await file_get_common(
        app=app,
        repo_type=repo_type,
        org=org,
        repo=repo,
        commit=commit,
        file_path=file_path,
        request=request,
    )


@router.get("/{org_repo}/{hash_file}")
@router.get("/{repo_type}/{org_repo}/{hash_file}")
async def cdn_file_get(
    org_repo: str, hash_file: str, request: Request, repo_type: str = "models"
):
    app = request.app
    org, repo = parse_org_repo(org_repo)
    if org is None and repo is None:
        return error_repo_not_found()

    if not await check_proxy_rules_hf(app, repo_type, org, repo):
        return error_repo_not_found()
    try:
        generator = await cdn_file_get_generator(
            app, repo_type, org, repo, hash_file, method="GET", request=request
        )
        status_code = await generator.__anext__()
        headers = await generator.__anext__()
        return StreamingResponse(generator, headers=headers, status_code=status_code)
    except httpx.ConnectTimeout:
        return Response(status_code=504)
