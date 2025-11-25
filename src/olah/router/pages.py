# coding=utf-8
# Copyright 2024 XiaHan
#
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.

import glob
import os

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from olah.constants import OLAH_CODE_DIR
from olah.utils.rule_utils import get_org_repo

router = APIRouter()

# Templates
templates = Jinja2Templates(directory=os.path.join(OLAH_CODE_DIR, "static"))


@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    app = request.app
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "scheme": app.state.app_settings.config.mirror_scheme,
            "netloc": app.state.app_settings.config.mirror_netloc,
        },
    )


@router.get("/repos", response_class=HTMLResponse)
async def repos(request: Request):
    app = request.app
    datasets_repos = glob.glob(os.path.join(app.state.app_settings.config.repos_path, "api/datasets/*/*"))
    models_repos = glob.glob(os.path.join(app.state.app_settings.config.repos_path, "api/models/*/*"))
    spaces_repos = glob.glob(os.path.join(app.state.app_settings.config.repos_path, "api/spaces/*/*"))
    datasets_repos = [get_org_repo(*repo.split("/")[-2:]) for repo in datasets_repos]
    models_repos = [get_org_repo(*repo.split("/")[-2:]) for repo in models_repos]
    spaces_repos = [get_org_repo(*repo.split("/")[-2:]) for repo in spaces_repos]

    return templates.TemplateResponse(
        "repos.html",
        {
            "request": request,
            "datasets_repos": datasets_repos,
            "models_repos": models_repos,
            "spaces_repos": spaces_repos,
        },
    )
