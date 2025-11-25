# coding=utf-8
# Copyright 2024 XiaHan
#
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.

"""
Olah Router Module

This module aggregates all route handlers for the Olah Huggingface Mirror Server.
"""

from fastapi import APIRouter

from olah.router.meta import router as meta_router
from olah.router.tree import router as tree_router
from olah.router.pathsinfo import router as pathsinfo_router
from olah.router.commits import router as commits_router
from olah.router.files import router as files_router
from olah.router.lfs import router as lfs_router
from olah.router.pages import router as pages_router
from olah.router.auth import router as auth_router

# Main router that includes all sub-routers
router = APIRouter()

# Include all sub-routers
router.include_router(meta_router)
router.include_router(tree_router)
router.include_router(pathsinfo_router)
router.include_router(commits_router)
router.include_router(files_router)
router.include_router(lfs_router)
router.include_router(pages_router)
router.include_router(auth_router)

__all__ = ["router"]
