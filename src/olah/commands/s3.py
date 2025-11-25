# coding=utf-8
# Copyright 2024 XiaHan
#
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.

"""
Olah CLI - S3 命令

S3 存储模式，缓存文件到 S3 兼容存储。
"""

from typing import Optional

import typer

from olah.commands.factory import S3Factory


def s3(
    host: str = typer.Option("0.0.0.0", help="服务器绑定地址"),
    port: int = typer.Option(8090, help="服务器绑定端口"),
    endpoint: str = typer.Option(..., "--endpoint", "-e", help="S3 端点 URL"),
    access_key: str = typer.Option(..., "--access-key", "-a", help="S3 访问密钥 ID"),
    secret_key: str = typer.Option(
        ..., "--secret-key", "-s", help="S3 秘密访问密钥"
    ),
    bucket: str = typer.Option(..., "--bucket", "-b", help="S3 存储桶名称"),
    region: str = typer.Option("us-east-1", help="S3 区域"),
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
):
    """
    以 S3 模式启动 Olah。

    缓存并上传模型文件到 S3 兼容存储。
    作为带 S3 后端的代理模式运行。
    """
    factory = S3Factory(
        endpoint=endpoint,
        access_key=access_key,
        secret_key=secret_key,
        bucket=bucket,
        region=region,
        host=host,
        port=port,
        repos_path=repos_path,
        hf_scheme=hf_scheme,
        hf_netloc=hf_netloc,
        hf_lfs_netloc=hf_lfs_netloc,
        ssl_key=ssl_key,
        ssl_cert=ssl_cert,
    )
    factory.run()
