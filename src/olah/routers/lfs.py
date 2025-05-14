
# ======================
# LFS Hooks
# ======================
import httpx
from fastapi.responses import Response, StreamingResponse
from olah.proxy.lfs import lfs_head_generator, lfs_get_generator

from fastapi import APIRouter, Request
from olah.logger import LOGGER
router = APIRouter()

@router.head("/repos/{dir1}/{dir2}/{hash_repo}/{hash_file}")
async def lfs_head(dir1: str, dir2: str, hash_repo: str, hash_file: str, request: Request):
    try:
        generator = await lfs_head_generator(app, dir1, dir2, hash_repo, hash_file, request)
        status_code = await generator.__anext__()
        headers = await generator.__anext__()
        return StreamingResponse(generator, headers=headers, status_code=status_code)
    except httpx.ConnectTimeout:
        return Response(status_code=504)

@router.get("/repos/{dir1}/{dir2}/{hash_repo}/{hash_file}")
async def lfs_get(dir1: str, dir2: str, hash_repo: str, hash_file: str, request: Request):
    try:
        generator = await lfs_get_generator(app, dir1, dir2, hash_repo, hash_file, request)
        status_code = await generator.__anext__()
        headers = await generator.__anext__()
        return StreamingResponse(generator, headers=headers, status_code=status_code)
    except httpx.ConnectTimeout:
        return Response(status_code=504)

