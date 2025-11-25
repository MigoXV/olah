# coding=utf-8
# Copyright 2024 XiaHan
#
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.

"""
Olah CLI 命令的公共工具函数。
"""

import time

import uvicorn

from olah.configs import OlahConfig
from olah.utils.logging import build_logger


def create_app_with_config(config_obj: OlahConfig):
    """
    根据配置创建 FastAPI 应用。
    
    Args:
        config_obj: Olah 配置对象
        
    Returns:
        tuple: (FastAPI 应用实例, 配置对象)
    """
    from olah.server import app as fastapi_app, AppSettings
    from olah.utils.s3_client import S3Client

    logger = build_logger("olah", "olah.log")

    # 如果 host 是逗号分隔的字符串，则拆分为列表
    if isinstance(config_obj.basic.host, str) and "," in config_obj.basic.host:
        config_obj.basic.host = config_obj.basic.host.split(",")

    # 根据是否配置 SSL 密钥来确定镜像站协议
    config_obj.basic.mirror_scheme = (
        "http" if config_obj.basic.ssl_key is None else "https"
    )

    # 如果设置了缓存大小限制，显示警告信息
    if config_obj.basic.cache_size_limit is not None:
        logger.info(
            f"""
======== 警告 ========
由于设置了 cache_size_limit 参数，Olah 将定期删除缓存文件。
请确保 repos_path '{config_obj.basic.repos_path}' 中指定的缓存目录正确。
错误的设置可能导致意外的文件删除和数据丢失！！！
========================="""
        )
        # 延迟 2 秒，确保用户看到警告
        for _ in range(10):
            time.sleep(0.2)

    # 设置应用状态
    fastapi_app.state.app_settings = AppSettings(config=config_obj)

    # 如果启用了 S3 且配置完整，则初始化 S3 客户端
    if (
        config_obj.s3.enable
        and config_obj.s3.endpoint
        and config_obj.s3.access_key
        and config_obj.s3.secret_key
        and config_obj.s3.bucket
    ):
        fastapi_app.state.s3_client = S3Client(
            endpoint=config_obj.s3.endpoint,
            region=config_obj.s3.region,
            access_key=config_obj.s3.access_key,
            secret_key=config_obj.s3.secret_key,
            bucket=config_obj.s3.bucket,
        )
    else:
        fastapi_app.state.s3_client = None

    return fastapi_app, config_obj


def run_server(config_obj: OlahConfig):
    """
    使用 uvicorn 启动服务器。
    
    Args:
        config_obj: Olah 配置对象
    """
    uvicorn.run(
        "olah.server:app",
        host=config_obj.basic.host,
        port=config_obj.basic.port,
        log_level="info",
        reload=False,
        ssl_keyfile=config_obj.basic.ssl_key,
        ssl_certfile=config_obj.basic.ssl_cert,
    )
