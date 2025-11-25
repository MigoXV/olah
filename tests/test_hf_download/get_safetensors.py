"""
生成测试用的大文件（.safetensors 后缀）
用于测试 Olah 镜像服务的大文件下载功能
文件内容为随机二进制数据，不是真正的 safetensors 格式
同时生成模拟 HuggingFace 格式的 model.safetensors.index.json
"""

import json
import os
from pathlib import Path

from tqdm import tqdm

# 硬编码配置
OUTPUT_DIR = Path("model-bin/fake-organization/fake-model")
MODEL_NAME = "test_model"
NUM_SHARDS = 3  # safetensors 分片数量
TARGET_SIZE_GB_PER_SHARD = 4  # 每个分片大小 (GB)


def generate_fake_safetensors(output_path: Path, target_size_gb: float):
    """
    生成指定大小的假 safetensors 文件（随机二进制数据）
    
    Args:
        output_path: 输出文件路径
        target_size_gb: 目标文件大小（GB）
    """
    target_bytes = int(target_size_gb * 1024 * 1024 * 1024)
    chunk_size = 64 * 1024 * 1024  # 64MB 每次写入
    
    # 事先计算需要多少块
    full_chunks = target_bytes // chunk_size
    last_chunk_size = target_bytes % chunk_size
    total_chunks = full_chunks + (1 if last_chunk_size > 0 else 0)
    
    tqdm.write(f"[INFO] 目标文件大小: {target_size_gb} GB ({target_bytes:,} 字节)")
    tqdm.write(f"[INFO] 输出路径: {output_path}")
    tqdm.write(f"[INFO] 块大小: {chunk_size / 1024 / 1024:.0f} MB, 总块数: {total_chunks}")
    tqdm.write(f"[INFO] 生成中...")
    
    with open(output_path, "wb") as f:
        for i in tqdm(range(total_chunks), desc="生成进度", unit="块"):
            # 最后一块可能不足 chunk_size
            size = last_chunk_size if (i == total_chunks - 1 and last_chunk_size > 0) else chunk_size
            # 写入随机数据
            f.write(os.urandom(size))
    
    # 验证文件大小
    file_size = output_path.stat().st_size
    file_size_gb = file_size / 1024 / 1024 / 1024
    tqdm.write(f"[SUCCESS] 文件已生成!")
    tqdm.write(f"[INFO] 实际文件大小: {file_size_gb:.3f} GB ({file_size:,} 字节)")
    
    return output_path


def generate_safetensors_index(output_dir: Path, shard_files: list[Path]) -> Path:
    """
    生成模拟 HuggingFace 格式的 model.safetensors.index.json
    
    Args:
        output_dir: 输出目录
        shard_files: 分片文件路径列表
    
    Returns:
        生成的 index.json 文件路径
    """
    # 模拟权重映射 (weight_map)
    weight_map = {}
    for i, shard_file in enumerate(shard_files):
        # 为每个分片生成一些假的层名
        num_layers_per_shard = 10
        for layer_idx in range(num_layers_per_shard):
            global_layer_idx = i * num_layers_per_shard + layer_idx
            weight_map[f"model.layers.{global_layer_idx}.self_attn.q_proj.weight"] = shard_file.name
            weight_map[f"model.layers.{global_layer_idx}.self_attn.k_proj.weight"] = shard_file.name
            weight_map[f"model.layers.{global_layer_idx}.self_attn.v_proj.weight"] = shard_file.name
            weight_map[f"model.layers.{global_layer_idx}.self_attn.o_proj.weight"] = shard_file.name
            weight_map[f"model.layers.{global_layer_idx}.mlp.gate_proj.weight"] = shard_file.name
            weight_map[f"model.layers.{global_layer_idx}.mlp.up_proj.weight"] = shard_file.name
            weight_map[f"model.layers.{global_layer_idx}.mlp.down_proj.weight"] = shard_file.name
    
    # 计算总大小
    total_size = sum(f.stat().st_size for f in shard_files)
    
    index_data = {
        "metadata": {
            "total_size": total_size,
        },
        "weight_map": weight_map,
    }
    
    index_path = output_dir / "model.safetensors.index.json"
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(index_data, f, indent=2, ensure_ascii=False)
    
    tqdm.write(f"[SUCCESS] index.json 已生成: {index_path}")
    tqdm.write(f"[INFO] 总大小: {total_size / 1024 / 1024 / 1024:.3f} GB")
    tqdm.write(f"[INFO] 权重数量: {len(weight_map)}")
    
    return index_path


def main():
    # 确保输出目录存在
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    shard_files = []
    
    # 生成多个 safetensors 分片
    tqdm.write(f"[INFO] 将生成 {NUM_SHARDS} 个分片，每个 {TARGET_SIZE_GB_PER_SHARD} GB")
    tqdm.write("=" * 50)
    
    for shard_idx in tqdm(range(1, NUM_SHARDS + 1), desc="分片进度", unit="分片"):
        # 命名格式: model-00001-of-00003.safetensors
        shard_name = f"{MODEL_NAME}-{shard_idx:05d}-of-{NUM_SHARDS:05d}.safetensors"
        shard_path = OUTPUT_DIR / shard_name
        
        tqdm.write(f"\n[分片 {shard_idx}/{NUM_SHARDS}] {shard_name}")
        generate_fake_safetensors(
            output_path=shard_path,
            target_size_gb=TARGET_SIZE_GB_PER_SHARD,
        )
        shard_files.append(shard_path)
    
    # 生成 index.json
    tqdm.write("\n" + "=" * 50)
    tqdm.write("[INFO] 生成 model.safetensors.index.json...")
    generate_safetensors_index(OUTPUT_DIR, shard_files)
    
    tqdm.write("\n" + "=" * 50)
    tqdm.write("[DONE] 所有文件生成完成!")


if __name__ == "__main__":
    main()
