# coding=utf-8
# Copyright 2024 XiaHan
#
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.

"""
Olah 应用工厂模块。

提供不同模式的应用工厂类，用于创建和配置 FastAPI 应用。
"""

from abc import ABC, abstractmethod
from typing import Optional, List

import uvicorn

from olah.configs import OlahConfig


class AppFactory(ABC):
    """
    应用工厂抽象基类。
    
    定义创建和运行 Olah 应用的统一接口。
    每个具体的工厂类负责创建特定模式的配置。
    """
    
    @abstractmethod
    def create_config(self) -> OlahConfig:
        """创建配置对象。"""
        pass
    
    def create_app(self):
        """创建并初始化 FastAPI 应用。"""
        from olah.server import app as fastapi_app, AppSettings
        
        config = self.create_config()
        
        # 根据是否配置 SSL 确定镜像协议
        config.basic.mirror_scheme = (
            "http" if config.basic.ssl_key is None else "https"
        )
        
        # 初始化应用状态
        fastapi_app.state.app_settings = AppSettings(config=config)
        fastapi_app.state.s3_client = self._create_s3_client(config)
        
        return fastapi_app, config
    
    def _create_s3_client(self, config: OlahConfig):
        """创建 S3 客户端（如果启用）。"""
        from olah.utils.s3_client import S3Client
        
        if (
            config.s3.enable
            and config.s3.endpoint
            and config.s3.access_key
            and config.s3.secret_key
            and config.s3.bucket
        ):
            return S3Client(
                endpoint=config.s3.endpoint,
                region=config.s3.region,
                access_key=config.s3.access_key,
                secret_key=config.s3.secret_key,
                bucket=config.s3.bucket,
            )
        return None
    
    def run(self):
        """创建应用并启动服务器。"""
        _, config = self.create_app()
        self._run_server(config)
    
    def _run_server(self, config: OlahConfig):
        """使用 uvicorn 启动服务器。"""
        uvicorn.run(
            "olah.server:app",
            host=config.basic.host,
            port=config.basic.port,
            log_level="info",
            reload=False,
            ssl_keyfile=config.basic.ssl_key,
            ssl_certfile=config.basic.ssl_cert,
        )


class ModelBinFactory(AppFactory):
    """
    Model-bin 模式工厂。
    
    纯本地模型文件服务，不访问 HuggingFace。
    目录结构: <model_bin_path>/<org>/<repo>/<file_path>
    """
    
    def __init__(
        self,
        model_bin_path: str,
        host: str = "0.0.0.0",
        port: int = 8090,
        ssl_key: Optional[str] = None,
        ssl_cert: Optional[str] = None,
    ):
        self.model_bin_path = model_bin_path
        self.host = host
        self.port = port
        self.ssl_key = ssl_key
        self.ssl_cert = ssl_cert
    
    def create_config(self) -> OlahConfig:
        config = OlahConfig()
        
        # 基础网络设置
        config.basic.host = self.host
        config.basic.port = self.port
        config.basic.ssl_key = self.ssl_key
        config.basic.ssl_cert = self.ssl_cert
        
        # Model-bin 专用设置
        config.model_bin.enable = True
        config.model_bin.path = self.model_bin_path
        
        # 强制离线模式，禁用所有远程功能
        config.accessibility.offline = True
        config.s3.enable = False
        config.basic.mirrors_path = []
        
        return config
    
    def _create_s3_client(self, config: OlahConfig):
        """Model-bin 模式不需要 S3 客户端。"""
        return None


class ProxyFactory(AppFactory):
    """
    Proxy 模式工厂。
    
    纯代理模式，转发请求到 HuggingFace 并缓存响应。
    """
    
    def __init__(
        self,
        host: str = "0.0.0.0",
        port: int = 8090,
        repos_path: str = "./repos",
        hf_scheme: str = "https",
        hf_netloc: str = "huggingface.co",
        hf_lfs_netloc: str = "cdn-lfs.huggingface.co",
        cache_size_limit: Optional[int] = None,
        cache_clean_strategy: str = "LRU",
        ssl_key: Optional[str] = None,
        ssl_cert: Optional[str] = None,
        offline: bool = False,
    ):
        self.host = host
        self.port = port
        self.repos_path = repos_path
        self.hf_scheme = hf_scheme
        self.hf_netloc = hf_netloc
        self.hf_lfs_netloc = hf_lfs_netloc
        self.cache_size_limit = cache_size_limit
        self.cache_clean_strategy = cache_clean_strategy
        self.ssl_key = ssl_key
        self.ssl_cert = ssl_cert
        self.offline = offline
    
    def create_config(self) -> OlahConfig:
        config = OlahConfig()
        
        # 基础网络设置
        config.basic.host = self.host
        config.basic.port = self.port
        config.basic.repos_path = self.repos_path
        config.basic.ssl_key = self.ssl_key
        config.basic.ssl_cert = self.ssl_cert
        
        # HuggingFace 设置
        config.basic.hf_scheme = self.hf_scheme
        config.basic.hf_netloc = self.hf_netloc
        config.basic.hf_lfs_netloc = self.hf_lfs_netloc
        
        # 缓存设置
        config.basic.cache_size_limit = self.cache_size_limit
        config.basic.cache_clean_strategy = self.cache_clean_strategy
        
        # 访问设置
        config.accessibility.offline = self.offline
        
        # Proxy 模式禁用其他后端
        config.model_bin.enable = False
        config.s3.enable = False
        config.basic.mirrors_path = []
        
        return config


class MirrorFactory(AppFactory):
    """
    Mirror 模式工厂。
    
    本地 Git 镜像模式，从本地仓库提供文件服务。
    可选择是否回退到代理模式。
    """
    
    def __init__(
        self,
        mirrors_path: List[str],
        host: str = "0.0.0.0",
        port: int = 8090,
        repos_path: str = "./repos",
        hf_scheme: str = "https",
        hf_netloc: str = "huggingface.co",
        hf_lfs_netloc: str = "cdn-lfs.huggingface.co",
        ssl_key: Optional[str] = None,
        ssl_cert: Optional[str] = None,
        offline: bool = False,
        fallback_proxy: bool = True,
    ):
        self.mirrors_path = mirrors_path
        self.host = host
        self.port = port
        self.repos_path = repos_path
        self.hf_scheme = hf_scheme
        self.hf_netloc = hf_netloc
        self.hf_lfs_netloc = hf_lfs_netloc
        self.ssl_key = ssl_key
        self.ssl_cert = ssl_cert
        self.offline = offline
        self.fallback_proxy = fallback_proxy
    
    def create_config(self) -> OlahConfig:
        config = OlahConfig()
        
        # 基础网络设置
        config.basic.host = self.host
        config.basic.port = self.port
        config.basic.repos_path = self.repos_path
        config.basic.mirrors_path = list(self.mirrors_path)
        config.basic.ssl_key = self.ssl_key
        config.basic.ssl_cert = self.ssl_cert
        
        # HuggingFace 设置
        config.basic.hf_scheme = self.hf_scheme
        config.basic.hf_netloc = self.hf_netloc
        config.basic.hf_lfs_netloc = self.hf_lfs_netloc
        
        # 访问设置：离线或不回退代理时设为 offline
        config.accessibility.offline = self.offline or (not self.fallback_proxy)
        
        # Mirror 模式禁用其他后端
        config.model_bin.enable = False
        config.s3.enable = False
        
        return config


class S3Factory(AppFactory):
    """
    S3 模式工厂。
    
    S3 兼容存储模式，缓存文件到 S3 存储。
    """
    
    def __init__(
        self,
        endpoint: str,
        access_key: str,
        secret_key: str,
        bucket: str,
        region: str = "us-east-1",
        host: str = "0.0.0.0",
        port: int = 8090,
        repos_path: str = "./repos",
        hf_scheme: str = "https",
        hf_netloc: str = "huggingface.co",
        hf_lfs_netloc: str = "cdn-lfs.huggingface.co",
        ssl_key: Optional[str] = None,
        ssl_cert: Optional[str] = None,
    ):
        self.endpoint = endpoint
        self.access_key = access_key
        self.secret_key = secret_key
        self.bucket = bucket
        self.region = region
        self.host = host
        self.port = port
        self.repos_path = repos_path
        self.hf_scheme = hf_scheme
        self.hf_netloc = hf_netloc
        self.hf_lfs_netloc = hf_lfs_netloc
        self.ssl_key = ssl_key
        self.ssl_cert = ssl_cert
    
    def create_config(self) -> OlahConfig:
        config = OlahConfig()
        
        # 基础网络设置
        config.basic.host = self.host
        config.basic.port = self.port
        config.basic.repos_path = self.repos_path
        config.basic.ssl_key = self.ssl_key
        config.basic.ssl_cert = self.ssl_cert
        
        # HuggingFace 设置
        config.basic.hf_scheme = self.hf_scheme
        config.basic.hf_netloc = self.hf_netloc
        config.basic.hf_lfs_netloc = self.hf_lfs_netloc
        
        # S3 设置
        config.s3.enable = True
        config.s3.endpoint = self.endpoint
        config.s3.region = self.region
        config.s3.access_key = self.access_key
        config.s3.secret_key = self.secret_key
        config.s3.bucket = self.bucket
        
        # S3 模式禁用其他后端
        config.model_bin.enable = False
        config.basic.mirrors_path = []
        
        return config


class ServeFactory(AppFactory):
    """
    Serve 模式工厂。
    
    完整模式，从配置文件加载所有设置。
    """
    
    def __init__(
        self,
        config_path: str,
        host: Optional[str] = None,
        port: Optional[int] = None,
    ):
        self.config_path = config_path
        self.host = host
        self.port = port
    
    def create_config(self) -> OlahConfig:
        config = OlahConfig.from_toml(self.config_path)
        
        # 覆盖 host 和 port（如果指定）
        if self.host is not None:
            config.basic.host = self.host
        if self.port is not None:
            config.basic.port = self.port
        
        return config
