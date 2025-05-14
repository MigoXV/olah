

# ======================
# Repository API Hooks
# ======================

from typing import Optional

from fastapi import APIRouter, Request
router = APIRouter()

@router.route("/api/models", methods=["GET"])
async def list_models(
    search: Optional[str]=None,
    author: Optional[str]=None,
    filter: Optional[str]=None,
    sort: Optional[str]=None,
    direction: Optional[int]=None,
    limit: Optional[int]=None,
    full: Optional[bool]=None,
    config: Optional[bool]=None):
    pass
