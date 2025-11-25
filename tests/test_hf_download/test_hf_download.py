"""
简单测试脚本：测试 Olah model-bin 模式是否正常工作
下载本地 fake-orgnazation/fake-model 仓库中的文件
"""

import os
from datetime import datetime
from huggingface_hub import hf_hub_download

# Olah 服务地址
OLAH_HOST = "http://localhost:8090"


def test_download():
    """测试从 Olah 下载本地模型文件"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    cache_dir = os.path.join(os.getcwd(), "tmp-workspace", "output", timestamp)
    os.makedirs(cache_dir, exist_ok=True)
    
    try:
        print(f"[INFO] Olah 服务: {OLAH_HOST}")
        print(f"[INFO] 下载 fake-orgnazation/fake-model/test_model.safetensors ...")
        
        file_path = hf_hub_download(
            repo_id="fake-orgnazation/fake-model",
            filename="test_model.safetensors",
            cache_dir=cache_dir,
            endpoint=OLAH_HOST,
        )
        
        print(f"[SUCCESS] 下载成功: {file_path}")
        print(f"[INFO] 文件大小: {os.path.getsize(file_path)} 字节")
        print(f"[INFO] 已保存至目录: {cache_dir}")
        return True
        
    except Exception as e:
        print(f"[ERROR] 下载失败: {e}")
        return False


if __name__ == "__main__":
    import sys
    success = test_download()
    sys.exit(0 if success else 1)
