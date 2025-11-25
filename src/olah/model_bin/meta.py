# coding=utf-8
# Copyright 2024 XiaHan
#
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.

"""
Model-bin 元数据生成模块。

提供为本地 model-bin 仓库生成 HuggingFace 兼容元数据的功能。
"""

import hashlib
from datetime import datetime
from pathlib import Path
from typing import Optional


def generate_meta(
    model_bin_path: str,
    repo_type: str,
    org: str,
    repo: str,
    commit: str
) -> Optional[dict]:
    """
    为 model-bin 模式生成仓库元数据。
    
    由于 model-bin 是纯文件目录，没有 Git 历史，
    我们使用模型名的哈希作为 SHA。
    
    Args:
        model_bin_path: model-bin 根目录路径
        repo_type: 仓库类型 (models, datasets, spaces)
        org: 组织名
        repo: 仓库名
        commit: 请求的 commit/分支名
    
    Returns:
        符合 HuggingFace 格式的元数据字典，如果仓库不存在则返回 None
    """
    repo_path = Path(model_bin_path) / org / repo
    if not repo_path.is_dir():
        return None
    
    # 收集所有文件
    siblings = []
    for file_path in repo_path.rglob("*"):
        if file_path.is_file():
            rel_path = file_path.relative_to(repo_path)
            siblings.append({"rfilename": str(rel_path)})
    
    # 使用模型名生成稳定的伪 commit SHA
    model_id = f"{org}/{repo}"
    fake_sha = hashlib.sha256(model_id.encode()).hexdigest()[:40]
    
    # 如果请求的是 "main" 分支，使用生成的 SHA
    if commit == "main":
        sha = fake_sha
    else:
        sha = commit
    
    # 获取目录的修改时间
    try:
        mtime = repo_path.stat().st_mtime
        last_modified = datetime.fromtimestamp(mtime).strftime("%Y-%m-%dT%H:%M:%S.000Z")
    except:
        last_modified = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")
    
    return {
        "_id": hashlib.sha256(f"{org}/{repo}/{sha}".encode()).hexdigest(),
        "id": model_id,
        "modelId": model_id,
        "author": org,
        "sha": sha,
        "lastModified": last_modified,
        "private": False,
        "gated": False,
        "disabled": False,
        "tags": ["model-bin"],
        "description": "Local model served via model-bin mode",
        "downloads": 0,
        "likes": 0,
        "siblings": siblings,
        "createdAt": last_modified,
    }
