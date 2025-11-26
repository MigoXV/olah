# coding=utf-8
# Copyright 2024 XiaHan
#
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.

"""
Olah CLI - Model-bin 命令

纯本地模型文件服务模式。
"""

from typing import Optional

import typer

from olah.commands.factory import ModelBinFactory


def model_bin(
    model_bin: str = typer.Option(
        ...,
        envvar="OLAH_MODEL_BIN",
        help="本地模型二进制文件根目录",
    ),
    host: str = typer.Option("0.0.0.0", envvar="OLAH_HOST", help="服务器绑定地址"),
    port: int = typer.Option(8090, envvar="OLAH_PORT", help="服务器绑定端口"),
    ssl_key: Optional[str] = typer.Option(
        None, envvar="OLAH_SSL_KEY", help="SSL 密钥文件路径"
    ),
    ssl_cert: Optional[str] = typer.Option(
        None, envvar="OLAH_SSL_CERT", help="SSL 证书文件路径"
    ),
):
    """
    以 MODEL-BIN 模式启动 Olah（纯本地模式）。

    从本地目录结构提供模型文件服务。
    目录结构: <model_bin_path>/<org>/<repo>/<file_path>
    """
    factory = ModelBinFactory(
        model_bin_path=model_bin,
        host=host,
        port=port,
        ssl_key=ssl_key,
        ssl_cert=ssl_cert,
    )
    factory.run()
