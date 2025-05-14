import os
import traceback
import git
from typing import List, Optional
from fastapi import APIRouter, Request, Form, Response
from fastapi.responses import JSONResponse, StreamingResponse
from typing_extensions import Annotated
import httpx

from olah.proxy.pathsinfo import pathsinfo_generator
from olah.utils.repo_utils import parse_org_repo
from olah.utils.url_utils import clean_path
from olah.utils.rule_utils import check_proxy_rules_hf
from olah.constants import REPO_TYPES_MAPPING
from olah.utils.repo_utils import check_commit_hf, get_commit_hf
from olah.errors import (
    error_page_not_found,
    error_repo_not_found,
    error_revision_not_found,
)
from olah.mirror.repos import LocalMirrorRepo
from olah.logger import LOGGER

router = APIRouter()


# Git Pathsinfo
async def pathsinfo_proxy_common(
    repo_type: str,
    org: str,
    repo: str,
    commit: str,
    paths: List[str],
    method: str,
    authorization: Optional[str],
    request: Request,
) -> Response:
    # TODO: the head method of meta apis
    # FIXME: do not show the private repos to other user besides owner, even though the repo was cached
    paths = [clean_path(path) for path in paths]
    if repo_type not in REPO_TYPES_MAPPING.keys():
        return error_page_not_found()
    if not await check_proxy_rules_hf(request.app, repo_type, org, repo):
        return error_repo_not_found()
    # Check Mirror Path
    for mirror_path in request.app.state.app_settings.config.mirrors_path:
        git_path = os.path.join(mirror_path, repo_type, org, repo)
        try:
            git_path = os.path.join(mirror_path, repo_type, org or "", repo)
            if os.path.exists(git_path):
                local_repo = LocalMirrorRepo(git_path, repo_type, org, repo)
                pathsinfo_data = local_repo.get_pathinfos(commit, paths)
                if pathsinfo_data is None:
                    continue
                return JSONResponse(content=pathsinfo_data)
        except git.exc.InvalidGitRepositoryError:
            LOGGER.warning(f"Local repository {git_path} is not a valid git reposity.")
            continue

    # Proxy the HF File pathsinfo
    try:
        if not request.app.state.app_settings.config.offline:
            if not await check_commit_hf(
                request.app,
                repo_type,
                org,
                repo,
                commit=None,
                authorization=authorization,
            ):
                return error_repo_not_found()
            if not await check_commit_hf(
                request.app,
                repo_type,
                org,
                repo,
                commit=commit,
                authorization=authorization,
            ):
                return error_revision_not_found(revision=commit)
        commit_sha = await get_commit_hf(
            request.app,
            repo_type,
            org,
            repo,
            commit=commit,
            authorization=authorization,
        )
        if commit_sha is None:
            return error_repo_not_found()
        if not request.app.state.app_settings.config.offline and commit_sha != commit:
            generator = pathsinfo_generator(
                app=request.app,
                repo_type=repo_type,
                org=org,
                repo=repo,
                commit=commit,
                paths=paths,
                override_cache=True,
                method=method,
                authorization=authorization,
            )
            async for _ in generator:
                pass
            generator = pathsinfo_generator(
                app=request.app,
                repo_type=repo_type,
                org=org,
                repo=repo,
                commit=commit_sha,
                paths=paths,
                override_cache=True,
                method=method,
                authorization=authorization,
            )
        else:
            generator = pathsinfo_generator(
                request.app,
                repo_type,
                org,
                repo,
                commit_sha,
                paths,
                override_cache=False,
                method=method,
                authorization=authorization,
            )
        status_code = await generator.__anext__()
        headers = await generator.__anext__()
        return StreamingResponse(generator, status_code=status_code, headers=headers)
    except httpx.ConnectTimeout:
        traceback.print_exc()
        return Response(status_code=504)


@router.head("/api/{repo_type}/{org}/{repo}/paths-info/{commit}")
@router.post("/api/{repo_type}/{org}/{repo}/paths-info/{commit}")
async def pathsinfo_proxy_commit2(
    repo_type: str,
    org: str,
    repo: str,
    commit: str,
    paths: Annotated[List[str], Form()],
    request: Request,
):
    return await pathsinfo_proxy_common(
        repo_type=repo_type,
        org=org,
        repo=repo,
        commit=commit,
        paths=paths,
        method=request.method.lower(),
        authorization=request.headers.get("authorization", None),
        request=request,
    )


@router.head("/api/{repo_type}/{org_repo}/paths-info/{commit}")
@router.post("/api/{repo_type}/{org_repo}/paths-info/{commit}")
async def pathsinfo_proxy_commit(
    repo_type: str,
    org_repo: str,
    commit: str,
    paths: Annotated[List[str], Form()],
    request: Request,
):
    org, repo = parse_org_repo(org_repo)
    if org is None and repo is None:
        return error_repo_not_found()

    return await pathsinfo_proxy_common(
        repo_type=repo_type,
        org=org,
        repo=repo,
        commit=commit,
        paths=paths,
        method=request.method.lower(),
        authorization=request.headers.get("authorization", None),
        request=request,
    )
