# coding=utf-8
# Copyright 2024 XiaHan
#
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.

"""
Olah CLI 命令模块

提供以下命令入口:
- proxy: 纯代理模式
- mirror: 本地 Git 镜像模式
- model-bin: 纯本地模型文件模式
- s3: S3 存储后端模式
- serve: 配置文件完整模式
"""

from olah.commands.app import app, main
from olah.commands.factory import (
    AppFactory,
    ModelBinFactory,
    MirrorFactory,
    ProxyFactory,
    S3Factory,
    ServeFactory,
)
from olah.commands.proxy import proxy
from olah.commands.mirror import mirror
from olah.commands.model_bin import model_bin
from olah.commands.s3 import s3
from olah.commands.serve import serve

__all__ = [
    "app",
    "main",
    "AppFactory",
    "ModelBinFactory",
    "MirrorFactory",
    "ProxyFactory",
    "S3Factory",
    "ServeFactory",
    "proxy",
    "mirror",
    "model_bin",
    "s3",
    "serve",
]
