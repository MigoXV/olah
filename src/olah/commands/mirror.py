# coding=utf-8
# Copyright 2024 XiaHan
#
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.

"""
Olah CLI - Mirror 命令

本地 Git 镜像模式，从本地仓库提供文件服务。
"""

from typing import List, Optional

import typer

from olah.commands.factory import MirrorFactory


def mirror(
    host: str = typer.Option("0.0.0.0", help="服务器绑定地址"),
    port: int = typer.Option(8090, help="服务器绑定端口"),
    mirrors_path: List[str] = typer.Option(
        ..., "--mirrors-path", "-m", help="本地 Git 镜像目录列表"
    ),
    repos_path: str = typer.Option(
        "./repos", help="缓存仓库保存目录"
    ),
    hf_scheme: str = typer.Option(
        "https", help="HuggingFace 站点协议 (http/https)"
    ),
    hf_netloc: str = typer.Option("huggingface.co", help="HuggingFace 站点域名"),
    hf_lfs_netloc: str = typer.Option(
        "cdn-lfs.huggingface.co", help="HuggingFace LFS 域名"
    ),
    ssl_key: Optional[str] = typer.Option(None, help="SSL 密钥文件路径"),
    ssl_cert: Optional[str] = typer.Option(None, help="SSL 证书文件路径"),
    offline: bool = typer.Option(
        False, "--offline", help="启用离线模式（不回退到 HuggingFace）"
    ),
    fallback_proxy: bool = typer.Option(
        True,
        "--fallback-proxy/--no-fallback-proxy",
        help="本地找不到时是否回退到代理模式",
    ),
):
    """
    以 MIRROR 模式启动 Olah。

    从本地 Git 镜像仓库提供文件服务。
    可选择本地找不到时是否回退到代理模式。
    """
    factory = MirrorFactory(
        mirrors_path=list(mirrors_path),
        host=host,
        port=port,
        repos_path=repos_path,
        hf_scheme=hf_scheme,
        hf_netloc=hf_netloc,
        hf_lfs_netloc=hf_lfs_netloc,
        ssl_key=ssl_key,
        ssl_cert=ssl_cert,
        offline=offline,
        fallback_proxy=fallback_proxy,
    )
    factory.run()
