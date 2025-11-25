# coding=utf-8
# Copyright 2024 XiaHan
#
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.

"""
Olah CLI - Proxy 命令

纯代理模式，转发请求到 HuggingFace 并缓存响应。
"""

from typing import Optional

import typer

from olah.commands.factory import ProxyFactory
from olah.utils.disk_utils import convert_to_bytes


def proxy(
    host: str = typer.Option("0.0.0.0", help="服务器绑定地址"),
    port: int = typer.Option(8090, help="服务器绑定端口"),
    hf_scheme: str = typer.Option(
        "https", help="HuggingFace 站点协议 (http/https)"
    ),
    hf_netloc: str = typer.Option("huggingface.co", help="HuggingFace 站点域名"),
    hf_lfs_netloc: str = typer.Option(
        "cdn-lfs.huggingface.co", help="HuggingFace LFS 域名"
    ),
    repos_path: str = typer.Option(
        "./repos", help="缓存仓库保存目录"
    ),
    cache_size_limit: Optional[str] = typer.Option(
        None, help="缓存大小限制 (例如: '100MB', '2GB')"
    ),
    cache_clean_strategy: str = typer.Option(
        "LRU", help="缓存清理策略: LRU, FIFO, LARGE_FIRST"
    ),
    ssl_key: Optional[str] = typer.Option(None, help="SSL 密钥文件路径"),
    ssl_cert: Optional[str] = typer.Option(None, help="SSL 证书文件路径"),
    offline: bool = typer.Option(False, "--offline", help="启用离线模式"),
):
    """
    以 PROXY 模式启动 Olah。

    转发所有请求到 HuggingFace 并在本地缓存响应。
    """
    # 转换缓存大小限制
    cache_limit_bytes = None
    if cache_size_limit is not None:
        cache_limit_bytes = convert_to_bytes(cache_size_limit)
    
    factory = ProxyFactory(
        host=host,
        port=port,
        repos_path=repos_path,
        hf_scheme=hf_scheme,
        hf_netloc=hf_netloc,
        hf_lfs_netloc=hf_lfs_netloc,
        cache_size_limit=cache_limit_bytes,
        cache_clean_strategy=cache_clean_strategy,
        ssl_key=ssl_key,
        ssl_cert=ssl_cert,
        offline=offline,
    )
    factory.run()
