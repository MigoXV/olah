# coding=utf-8
# Copyright 2024 XiaHan
#
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.

"""
Olah CLI - Serve 命令

完整模式，从配置文件加载所有设置。
"""

from typing import Optional

import typer

from olah.commands.factory import ServeFactory


def serve(
    config: str = typer.Option(
        ..., "--config", "-c", help="TOML 配置文件路径"
    ),
    host: Optional[str] = typer.Option(None, help="覆盖配置中的 host"),
    port: Optional[int] = typer.Option(None, help="覆盖配置中的 port"),
):
    """
    以 SERVE 模式启动 Olah（完整模式）。

    从 TOML 配置文件加载所有设置，
    启用所有可用后端（代理、镜像、model-bin、S3）。
    """
    factory = ServeFactory(
        config_path=config,
        host=host,
        port=port,
    )
    factory.run()
