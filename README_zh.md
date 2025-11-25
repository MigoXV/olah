<h1 align="center">Olah</h1>


<p align="center">
<b>自托管的轻量级HuggingFace镜像服务</b>

Olah是开源的自托管轻量级HuggingFace镜像服务。`Olah`来源于丘丘人语，在丘丘人语中意味着`你好`。
Olah真正地实现了huggingface资源的`镜像`功能，而不仅仅是一个简单的`反向代理`。
Olah并不会立刻对huggingface全站进行镜像，而是在用户下载的同时在文件块级别对资源进行镜像（或者我们可以说是缓存）。

## Olah的优势
Olah能够在用户下载的同时分块缓存文件。当第二次下载时，直接从缓存中读取，极大地提升了下载速度并节约了流量。
同时Olah提供了丰富的缓存控制策略，管理员可以通过配置文件设置哪些仓库可以访问，哪些仓库可以缓存。

## 特性
* 数据缓存，减少下载流量
* 模型镜像
* 数据集镜像
* 空间镜像

## 安装

### 方法1：使用pip

```bash
pip install olah
```

或者：

```bash
pip install git+https://github.com/vtuber-plan/olah.git
```

### 方法2：从源代码安装

1. 克隆这个仓库
```bash
git clone https://github.com/vtuber-plan/olah.git
cd olah
```

2. 安装包
```bash
pip install --upgrade pip
pip install -e .
```

## 快速开始
在控制台运行以下命令：
```bash
python -m olah.server
```

然后将环境变量`HF_ENDPOINT`设置为镜像站点(这里是http://localhost:8090/)。

Linux: 
```bash
export HF_ENDPOINT=http://localhost:8090
```

Windows Powershell:
```bash
$env:HF_ENDPOINT = "http://localhost:8090"
```

从现在开始，HuggingFace库中的所有下载操作都将通过此镜像站点代理进行。
```bash
pip install -U huggingface_hub
```

```python
from huggingface_hub import snapshot_download

snapshot_download(repo_id='Qwen/Qwen-7B', repo_type='model',
                  local_dir='./model_dir', resume_download=True,
                  max_workers=8)

```

或者你也可以使用huggingface cli直接下载模型和数据集.

下载GPT2:
```bash
huggingface-cli download --resume-download openai-community/gpt2 --local-dir gpt2
```

下载WikiText:
```bash
huggingface-cli download --repo-type dataset --resume-download Salesforce/wikitext --local-dir wikitext
```

您可以查看路径`./repos`，其中存储了所有数据集和模型的缓存。

## 启动服务器
在控制台运行以下命令：
```bash
olah-cli
```

或者您可以指定主机地址和监听端口：
```bash
olah-cli --host localhost --port 8090
```
**注意：请记得在修改主机和端口时将`--mirror-netloc`和`--mirror-lfs-netloc`更改为镜像站点的实际URL。**

```bash
olah-cli --host 192.168.1.100 --port 8090 --mirror-netloc 192.168.1.100:8090
```

默认的镜像缓存路径是`./repos`，您可以通过`--repos-path`参数进行更改：
```bash
olah-cli --host localhost --port 8090 --repos-path ./hf_mirrors
```

**注意，不同版本之间的缓存数据不能迁移，请删除缓存文件夹后再进行olah的升级**

在实际部署中可能出现下载并发量很大，导致新的连接出现Timeout错误。
可以设置uvicorn的WEB_CONCURRENCY变量以增加worker数量以提升产品场景的并发量。
例如Linux下:
```bash
export WEB_CONCURRENCY=4
```

## 更多配置

更多配置可以通过配置文件进行控制，通过命令参数传入`configs.toml`以设置配置文件路径：
```bash
olah-cli -c configs.toml
```

完整的配置文件内容见[assets/full_configs.toml](https://github.com/vtuber-plan/olah/blob/main/assets/full_configs.toml)

### 配置详解
第一部分basic字段用于对镜像站进行基本设置
```toml
[basic]
host = "localhost"
port = 8090
ssl-key = ""
ssl-cert = ""
repos-path = "./repos"
cache-size-limit = ""
cache-clean-strategy = "LRU"
hf-scheme = "https"
hf-netloc = "huggingface.co"
hf-lfs-netloc = "cdn-lfs.huggingface.co"
mirror-scheme = "http"
mirror-netloc = "localhost:8090"
mirror-lfs-netloc = "localhost:8090"
mirrors-path = ["./mirrors_dir"]
```

- host: 设置olah监听的host地址
- port: 设置olah监听的端口
- ssl-key和ssl-cert: 当需要开启HTTPS时传入key和cert的文件路径
- repos-path: 用于保存缓存数据的目录
- cache-size-limit: 指定缓存大小限制（例如，100G，500GB，2TB）。Olah会每小时扫描缓存文件夹的大小。如果超出限制，Olah会删除一些缓存文件
- cache-clean-strategy: 指定缓存清理策略（可用策略：LRU，FIFO，LARGE_FIRST）
- hf-scheme: huggingface官方站点的网络协议（一般不需要改动）
- hf-netloc: huggingface官方站点的网络位置（一般不需要改动）
- hf-lfs-netloc: huggingface官方站点LFS文件的网络位置（一般不需要改动）
- mirror-scheme: Olah镜像站的网络协议（应当和上面的设置一致，当提供ssl-key和ssl-cert时，应改为https）
- mirror-netloc: Olah镜像站的网络位置（应与host和port设置一致）
- mirror-lfs-netloc: Olah镜像站LFS的网络位置（应与host和port设置一致）
- mirrors-path: 额外的镜像文件目录。当你已经clone了一些git仓库时可以放入该目录下以供下载。此处例子目录为`./mirrors_dir`, 若要添加数据集`Salesforce/wikitext`，可将git仓库放置于`./mirrors_dir/datasets/Salesforce/wikitext`目录。同理，模型放置于`./mirrors_dir/models/organization/repository`下。


第二部分可以对可访问性进行限制
```toml

[accessibility]
offline = false

[[accessibility.proxy]]
repo = "cais/mmlu"
allow = true

[[accessibility.proxy]]
repo = "adept/fuyu-8b"
allow = false

[[accessibility.proxy]]
repo = "mistralai/*"
allow = true

[[accessibility.proxy]]
repo = "mistralai/Mistral.*"
allow = false
use_re = true

[[accessibility.cache]]
repo = "cais/mmlu"
allow = true

[[accessibility.cache]]
repo = "adept/fuyu-8b"
allow = false
```
- offline: 设置Olah镜像站是否进入离线模式，不再向huggingface官方站点发出请求以进行数据更新，但已经缓存的仓库仍可以下载
- proxy: 用于设置该仓库是否可以被代理，默认全部允许，`repo`用于匹配仓库名字; 可使用正则表达式和通配符两种模式，`use_re`用于控制是否使用正则表达式，默认使用通配符; `allow`控制该规则的属性是允许代理还是不允许代理。
- cache: 用于设置该仓库是否会被缓存，默认全部允许，`repo`用于匹配仓库名字; 可使用正则表达式和通配符两种模式，`use_re`用于控制是否使用正则表达式，默认使用通配符; `allow`控制该规则的属性是允许代理还是不允许缓存。

## Model-Bin 模式

Model-Bin 模式是一种纯本地模型文件服务模式，无需访问 HuggingFace，适用于以下场景：
- 内网环境，无法访问外网
- 已下载模型文件，需要本地分发
- 构建离线模型仓库

### 目录结构

Model-Bin 模式要求模型文件按以下结构组织：

```
<model_bin_path>/
├── <org>/
│   └── <repo>/
│       ├── config.json
│       ├── model.safetensors
│       └── tokenizer.json
└── <org2>/
    └── <repo2>/
        └── ...
```

例如，要提供 `Qwen/Qwen-7B` 模型：

```
./model-bin/
└── Qwen/
    └── Qwen-7B/
        ├── config.json
        ├── generation_config.json
        ├── model-00001-of-00008.safetensors
        ├── model-00002-of-00008.safetensors
        ├── ...
        ├── model.safetensors.index.json
        ├── tokenizer.json
        └── tokenizer_config.json
```

### 启动服务

使用 `model-bin` 子命令启动：

```bash
olah-cli model-bin --path ./model-bin
```

完整参数说明：

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--path`, `-p` | 本地模型文件根目录（必填） | - |
| `--host` | 服务器绑定地址 | `0.0.0.0` |
| `--port` | 服务器绑定端口 | `8090` |
| `--ssl-key` | SSL 密钥文件路径 | `None` |
| `--ssl-cert` | SSL 证书文件路径 | `None` |

### 使用示例

#### 1. 准备模型文件

假设你已经下载了模型文件到 `./model-bin` 目录：

```bash
# 目录结构
./model-bin/
├── THUDM/
│   └── chatglm3-6b/
│       ├── config.json
│       ├── model-00001-of-00007.safetensors
│       └── ...
└── Qwen/
    └── Qwen-7B/
        ├── config.json
        └── ...
```

#### 2. 启动 Model-Bin 服务

```bash
olah-cli model-bin --path ./model-bin --port 8090
```

#### 3. 客户端下载

设置环境变量并下载：

```bash
export HF_ENDPOINT=http://localhost:8090

# 使用 huggingface-cli 下载
huggingface-cli download THUDM/chatglm3-6b --local-dir ./chatglm3-6b

# 或使用 Python
from huggingface_hub import snapshot_download
snapshot_download(repo_id='Qwen/Qwen-7B', local_dir='./qwen-7b')
```

### 与其他模式的区别

| 特性 | Proxy 模式 | Mirror 模式 | Model-Bin 模式 |
|------|-----------|-------------|----------------|
| 需要外网 | ✅ | 可选 | ❌ |
| 支持缓存 | ✅ | ✅ | ❌ |
| 支持增量更新 | ✅ | ✅ | ❌ |
| 文件格式 | Git LFS | Git 仓库 | 普通文件 |
| 适用场景 | 代理加速 | 镜像站点 | 离线分发 |

### 注意事项

1. **纯离线模式**：Model-Bin 模式不会访问 HuggingFace，如果请求的文件不存在会返回 404
2. **无版本控制**：不支持 Git 版本控制，只能提供当前目录下的文件
3. **无元数据**：部分 HuggingFace API（如模型信息查询）可能返回有限信息
4. **文件名匹配**：确保文件名与 HuggingFace 仓库中的文件名完全一致

## 许可证

olah采用MIT许可证发布。

## 另请参阅

- [olah-docs](https://github.com/vtuber-plan/olah/tree/main/docs)
- [olah-source](https://github.com/vtuber-plan/olah)

## Star历史

[![Star历史图表]()](https://star-history.com/#vtuber-plan/olah&Date)