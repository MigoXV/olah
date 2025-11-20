# coding=utf-8
# Copyright 2024 XiaHan
#
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.

from __future__ import annotations

import dataclasses
import fnmatch
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal, Optional, Union

import toml

from olah.utils.disk_utils import convert_to_bytes

DEFAULT_PROXY_RULES = [
    {"repo": "*", "allow": True, "use_re": False},
    {"repo": "*/*", "allow": True, "use_re": False},
]

DEFAULT_CACHE_RULES = [
    {"repo": "*", "allow": True, "use_re": False},
    {"repo": "*/*", "allow": True, "use_re": False},
]


@dataclass
class OlahRule:
    repo: str = ""
    type: str = "*"
    allow: bool = False
    use_re: bool = False

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "OlahRule":
        return OlahRule(
            repo=data.get("repo", ""),
            type=data.get("type", "*"),
            allow=data.get("allow", False),
            use_re=data.get("use_re", False),
        )

    def match(self, repo_name: str) -> bool:
        if self.use_re:
            return re.match(self.repo, repo_name) is not None
        return fnmatch.fnmatch(repo_name, self.repo)


@dataclass
class OlahRuleList:
    rules: List[OlahRule] = field(default_factory=list)

    @staticmethod
    def from_list(data: List[Dict[str, Any]]) -> "OlahRuleList":
        return OlahRuleList([OlahRule.from_dict(item) for item in data])

    def allow(self, repo_name: str) -> bool:
        allow = False
        for rule in self.rules:
            if rule.match(repo_name):
                allow = rule.allow
        return allow

    def clear(self) -> None:
        self.rules.clear()


@dataclass
class BasicConfig:
    host: Union[List[str], str] = "localhost"
    port: int = 8090
    ssl_key: Optional[str] = None
    ssl_cert: Optional[str] = None
    repos_path: str = "./repos"
    cache_size_limit: Optional[int] = None
    cache_clean_strategy: Literal["LRU", "FIFO", "LARGE_FIRST"] = "LRU"
    hf_scheme: str = "https"
    hf_netloc: str = "huggingface.co"
    hf_lfs_netloc: str = "cdn-lfs.huggingface.co"

    mirror_scheme: str = dataclasses.field(default_factory=lambda: "http")
    mirror_netloc: str = dataclasses.field(default_factory=str)
    mirror_lfs_netloc: str = dataclasses.field(default_factory=str)
    mirrors_path: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.mirror_scheme:
            self.mirror_scheme = "http" if self.ssl_key is None else "https"
        if not self.mirror_netloc:
            self.mirror_netloc = self._default_netloc()
        if not self.mirror_lfs_netloc:
            self.mirror_lfs_netloc = self._default_netloc()

    def _is_specific_addr(self, host: Union[List[str], str]) -> bool:
        if isinstance(host, str):
            return host not in ["0.0.0.0", "::"]
        return False

    def _default_netloc(self) -> str:
        return f"{self.host if self._is_specific_addr(self.host) else 'localhost'}:{self.port}"

    def hf_url_base(self) -> str:
        return f"{self.hf_scheme}://{self.hf_netloc}"

    def hf_lfs_url_base(self) -> str:
        return f"{self.hf_scheme}://{self.hf_lfs_netloc}"

    def mirror_url_base(self) -> str:
        return f"{self.mirror_scheme}://{self.mirror_netloc}"

    def mirror_lfs_url_base(self) -> str:
        return f"{self.mirror_scheme}://{self.mirror_lfs_netloc}"


@dataclass
class S3Config:
    enable: bool = False
    endpoint: Optional[str] = None
    region: str = "us-east-1"
    access_key: Optional[str] = None
    secret_key: Optional[str] = None
    bucket: Optional[str] = None


@dataclass
class ModelBinConfig:
    enable: bool = False
    path: Optional[str] = None


@dataclass
class AccessibilityConfig:
    offline: bool = False
    proxy: OlahRuleList = field(default_factory=lambda: OlahRuleList.from_list(DEFAULT_PROXY_RULES))
    cache: OlahRuleList = field(default_factory=lambda: OlahRuleList.from_list(DEFAULT_CACHE_RULES))


@dataclass
class OlahConfig:
    basic: BasicConfig = field(default_factory=BasicConfig)
    accessibility: AccessibilityConfig = field(default_factory=AccessibilityConfig)
    s3: S3Config = field(default_factory=S3Config)
    model_bin: ModelBinConfig = field(default_factory=ModelBinConfig)

    @classmethod
    def from_toml(cls, path: Optional[str]) -> "OlahConfig":
        config = cls()
        if path:
            config.apply_toml(path)
        return config

    def apply_toml(self, path: str) -> None:
        config = toml.load(path)

        if "basic" in config:
            basic = config["basic"]
            self.basic.host = basic.get("host", self.basic.host)
            self.basic.port = basic.get("port", self.basic.port)
            self.basic.ssl_key = self._empty_str(basic.get("ssl-key", self.basic.ssl_key))
            self.basic.ssl_cert = self._empty_str(basic.get("ssl-cert", self.basic.ssl_cert))
            self.basic.repos_path = basic.get("repos-path", self.basic.repos_path)
            self.basic.cache_size_limit = convert_to_bytes(
                basic.get("cache-size-limit", self.basic.cache_size_limit)
            )
            self.basic.cache_clean_strategy = basic.get(
                "cache-clean-strategy", self.basic.cache_clean_strategy
            )
            self.basic.hf_scheme = basic.get("hf-scheme", self.basic.hf_scheme)
            self.basic.hf_netloc = basic.get("hf-netloc", self.basic.hf_netloc)
            self.basic.hf_lfs_netloc = basic.get("hf-lfs-netloc", self.basic.hf_lfs_netloc)
            self.basic.mirror_scheme = basic.get("mirror-scheme", self.basic.mirror_scheme)
            self.basic.mirror_netloc = basic.get("mirror-netloc", self.basic.mirror_netloc)
            self.basic.mirror_lfs_netloc = basic.get(
                "mirror-lfs-netloc", self.basic.mirror_lfs_netloc
            )
            self.basic.mirrors_path = basic.get("mirrors-path", self.basic.mirrors_path)

        if "accessibility" in config:
            accessibility = config["accessibility"]
            self.accessibility.offline = accessibility.get(
                "offline", self.accessibility.offline
            )
            self.accessibility.proxy = OlahRuleList.from_list(
                accessibility.get("proxy", DEFAULT_PROXY_RULES)
            )
            self.accessibility.cache = OlahRuleList.from_list(
                accessibility.get("cache", DEFAULT_CACHE_RULES)
            )

        if "s3" in config:
            s3 = config["s3"]
            self.s3.enable = s3.get("enable", self.s3.enable)
            self.s3.endpoint = self._empty_str(s3.get("endpoint", self.s3.endpoint))
            self.s3.region = s3.get("region", self.s3.region)
            self.s3.access_key = self._empty_str(s3.get("access-key", self.s3.access_key))
            self.s3.secret_key = self._empty_str(s3.get("secret-key", self.s3.secret_key))
            self.s3.bucket = self._empty_str(s3.get("bucket", self.s3.bucket))

        if "model-bin" in config:
            model_bin = config["model-bin"]
            self.model_bin.enable = model_bin.get("enable", self.model_bin.enable)
            self.model_bin.path = self._empty_str(model_bin.get("path", self.model_bin.path))

    @property
    def host(self) -> Union[List[str], str]:
        return self.basic.host

    @property
    def port(self) -> int:
        return self.basic.port

    @property
    def ssl_key(self) -> Optional[str]:
        return self.basic.ssl_key

    @property
    def ssl_cert(self) -> Optional[str]:
        return self.basic.ssl_cert

    @property
    def repos_path(self) -> str:
        return self.basic.repos_path

    @property
    def cache_size_limit(self) -> Optional[int]:
        return self.basic.cache_size_limit

    @property
    def cache_clean_strategy(self) -> Literal["LRU", "FIFO", "LARGE_FIRST"]:
        return self.basic.cache_clean_strategy

    @property
    def hf_scheme(self) -> str:
        return self.basic.hf_scheme

    @property
    def hf_netloc(self) -> str:
        return self.basic.hf_netloc

    @property
    def hf_lfs_netloc(self) -> str:
        return self.basic.hf_lfs_netloc

    @property
    def mirror_scheme(self) -> str:
        return self.basic.mirror_scheme

    @property
    def mirror_netloc(self) -> str:
        return self.basic.mirror_netloc

    @property
    def mirror_lfs_netloc(self) -> str:
        return self.basic.mirror_lfs_netloc

    @property
    def mirrors_path(self) -> List[str]:
        return self.basic.mirrors_path

    @property
    def offline(self) -> bool:
        return self.accessibility.offline

    @property
    def proxy(self) -> OlahRuleList:
        return self.accessibility.proxy

    @property
    def cache(self) -> OlahRuleList:
        return self.accessibility.cache

    @property
    def s3_enable(self) -> bool:
        return self.s3.enable

    @property
    def s3_endpoint(self) -> Optional[str]:
        return self.s3.endpoint

    @property
    def s3_region(self) -> str:
        return self.s3.region

    @property
    def s3_access_key(self) -> Optional[str]:
        return self.s3.access_key

    @property
    def s3_secret_key(self) -> Optional[str]:
        return self.s3.secret_key

    @property
    def s3_bucket(self) -> Optional[str]:
        return self.s3.bucket

    @property
    def model_bin_enable(self) -> bool:
        return self.model_bin.enable

    @property
    def model_bin_path(self) -> Optional[str]:
        return self.model_bin.path

    def hf_url_base(self) -> str:
        return self.basic.hf_url_base()

    def hf_lfs_url_base(self) -> str:
        return self.basic.hf_lfs_url_base()

    def mirror_url_base(self) -> str:
        return self.basic.mirror_url_base()

    def mirror_lfs_url_base(self) -> str:
        return self.basic.mirror_lfs_url_base()

    @staticmethod
    def _empty_str(value: Optional[str]) -> Optional[str]:
        if value == "":
            return None
        return value
