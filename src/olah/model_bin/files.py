# coding=utf-8
# Copyright 2024 XiaHan
#
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.

"""
Model-bin 文件服务模块。

提供本地 model-bin 仓库的文件路径解析、HTTP 头构建和流式读取功能。
"""

from pathlib import Path
from typing import AsyncGenerator, List, Optional, Tuple

import aiofiles

from olah.constants import CHUNK_SIZE, HUGGINGFACE_HEADER_X_REPO_COMMIT
from olah.utils.url_utils import get_all_ranges, parse_range_params


def get_file_path(root_path: str, org: str, repo: str, file_path: str) -> Optional[Path]:
    """
    解析并验证 model-bin 文件路径。
    
    该函数会进行路径遍历攻击防护，确保请求的文件在 model-bin 根目录内。
    
    Args:
        root_path: model-bin 根目录路径
        org: 组织名
        repo: 仓库名
        file_path: 请求的文件相对路径
    
    Returns:
        文件的 Path 对象，如果文件不存在或路径非法则返回 None
    """
    root = Path(root_path).resolve()
    # 清理文件路径，移除开头的分隔符
    clean_file_path = file_path.lstrip("/\\")
    candidate = (root / org / repo / clean_file_path).resolve()

    # 路径遍历攻击防护
    try:
        candidate.relative_to(root)
    except ValueError:
        return None

    if candidate.is_file():
        return candidate

    return None


def build_headers(
    path: Path, 
    request_range: Optional[str], 
    commit: Optional[str]
) -> Tuple[dict, List[Tuple[int, int]]]:
    """
    为文件响应构建 HTTP 头。
    
    Args:
        path: 文件 Path 对象
        request_range: HTTP Range 请求头值
        commit: commit SHA（用于 X-Repo-Commit 头）
    
    Returns:
        (headers 字典, ranges 列表)
    """
    stat = path.stat()
    file_size = stat.st_size
    mtime = stat.st_mtime
    
    unit, ranges, suffix = parse_range_params(request_range or f"bytes=0-{file_size-1}")
    all_ranges = get_all_ranges(file_size, unit, ranges, suffix)

    headers = {
        "content-length": str(sum(r[1] - r[0] for r in all_ranges)),
        "content-range": f"bytes {','.join(f'{r[0]}-{r[1]-1}' for r in all_ranges)}/{file_size}"
        if suffix is None
        else f"bytes -{suffix}/{file_size}",
        "etag": f'"{mtime}-{file_size}"',
    }

    if commit is not None:
        headers[HUGGINGFACE_HEADER_X_REPO_COMMIT.lower()] = commit

    return headers, all_ranges


async def stream_file(
    path: Path, 
    ranges: List[Tuple[int, int]]
) -> AsyncGenerator[bytes, None]:
    """
    异步流式读取文件内容。
    
    支持 HTTP Range 请求，可以读取文件的指定范围。
    
    Args:
        path: 文件 Path 对象
        ranges: 要读取的字节范围列表，每个元素为 (start, end) 元组
    
    Yields:
        文件内容的字节块
    """
    async with aiofiles.open(path, "rb") as fp:
        for start, end in ranges:
            await fp.seek(start)
            remaining = end - start
            while remaining > 0:
                chunk = await fp.read(min(CHUNK_SIZE, remaining))
                if not chunk:
                    break
                remaining -= len(chunk)
                yield chunk
