# ======================
# Authentication API Hooks
# ======================
from fastapi import APIRouter, Request
from olah.logger import LOGGER
router = APIRouter()

@router.get("/api/whoami-v2")
async def whoami_v2(request: Request):
    """
    Sensitive Information!!! 
    """
    new_headers = {k.lower(): v for k, v in request.headers.items()}
    new_headers["host"] = request.app.state.app_settings.config.hf_netloc
    async with httpx.AsyncClient() as client:
        response = await client.request(
            method="GET",
            url=urljoin(request.app.state.app_settings.config.hf_url_base(), "/api/whoami-v2"),
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
