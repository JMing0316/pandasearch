import os
import sys

# 设置 HuggingFace 镜像源
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

# 设置模型下载路径为当前工作目录下的 models/bge-m3
model_name = "BAAI/bge-m3"
local_model_path = os.path.join(os.getcwd(), "models", "bge-m3")

print(f"开始下载模型: {model_name}")
print(f"目标路径: {local_model_path}")
print(f"使用镜像源: {os.environ['HF_ENDPOINT']}")

# 使用 sentence-transformers 下载模型
try:
    from sentence_transformers import SentenceTransformer
    
    # 下载模型到指定路径
    model = SentenceTransformer(model_name, cache_folder=local_model_path)
    
    print(f"\n模型下载完成!")
    print(f"模型路径: {local_model_path}")
    
    # 测试模型加载
    print("\n正在测试模型...")
    test_sentences = ["这是一个测试句子", "This is a test sentence"]
    embeddings = model.encode(test_sentences)
    
    print(f"测试成功!")
    print(f"嵌入维度: {embeddings.shape}")
    print(f"示例嵌入 (前5个值): {embeddings[0][:5]}")
    
except Exception as e:
    print(f"错误: {e}")
    sys.exit(1)
