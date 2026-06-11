"""
BGE-M3 模型配置与使用示例
模型路径: models/bge-m3
"""

import os
from sentence_transformers import SentenceTransformer

# ==================== 配置区域 ====================

# 模型本地路径（相对于当前工作目录）
MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "bge-m3", 
                          "models--BAAI--bge-m3", "snapshots", 
                          "5617a9f61b028005a4858fdac845db406aefb181")

# 或者使用 HuggingFace 模型ID（需要联网）
# MODEL_NAME = "BAAI/bge-m3"

# 是否使用 GPU（如果可用）
USE_GPU = False

# 批处理大小（根据内存调整）
BATCH_SIZE = 32

# 嵌入维度（BGE-M3 固定为 1024 维）
EMBEDDING_DIM = 1024

# ==================== 模型加载 ====================

def load_model(model_path=None, use_gpu=USE_GPU):
    """
    加载 BGE-M3 模型
    
    Args:
        model_path: 模型本地路径，默认使用配置中的 MODEL_PATH
        use_gpu: 是否使用 GPU
        
    Returns:
        SentenceTransformer 模型实例
    """
    path = model_path or MODEL_PATH
    
    if not os.path.exists(path):
        raise FileNotFoundError(f"模型路径不存在: {path}")
    
    print(f"正在加载模型: {path}")
    
    device = "cuda" if use_gpu and os.system("python -c 'import torch; print(torch.cuda.is_available())'") == "True" else "cpu"
    model = SentenceTransformer(path, device=device)
    
    print(f"模型加载完成，使用设备: {device}")
    return model

# ==================== 文本嵌入 ====================

def encode_texts(model, texts, batch_size=BATCH_SIZE, normalize=True):
    """
    将文本列表编码为向量
    
    Args:
        model: 加载好的模型
        texts: 文本列表（字符串或字符串列表）
        batch_size: 批处理大小
        normalize: 是否对向量进行 L2 归一化（推荐用于相似度计算）
        
    Returns:
        numpy.ndarray: 嵌入向量数组，形状为 (len(texts), 1024)
    """
    if isinstance(texts, str):
        texts = [texts]
    
    embeddings = model.encode(
        texts,
        batch_size=batch_size,
        normalize_embeddings=normalize,
        show_progress_bar=True
    )
    
    return embeddings

# ==================== 相似度计算 ====================

def compute_similarity(embedding1, embedding2):
    """
    计算两个向量之间的余弦相似度
    
    Args:
        embedding1: 第一个向量
        embedding2: 第二个向量
        
    Returns:
        float: 余弦相似度值，范围 [-1, 1]
    """
    import numpy as np
    
    # 如果已经归一化，点积即为余弦相似度
    similarity = np.dot(embedding1, embedding2)
    return float(similarity)

# ==================== 使用示例 ====================

if __name__ == "__main__":
    # 1. 加载模型
    model = load_model()
    
    # 2. 准备文本
    texts = [
        "这是一个关于人工智能的句子。",
        "This is a sentence about artificial intelligence.",
        "今天天气很好，适合出去散步。",
        "Machine learning is a subset of AI.",
        "深度学习是机器学习的一个分支。"
    ]
    
    # 3. 生成嵌入向量
    print("\n正在编码文本...")
    embeddings = encode_texts(model, texts)
    
    print(f"\n嵌入维度: {embeddings.shape}")
    
    # 4. 计算相似度
    print("\n文本相似度矩阵:")
    print("-" * 60)
    
    for i in range(len(texts)):
        for j in range(i + 1, len(texts)):
            sim = compute_similarity(embeddings[i], embeddings[j])
            print(f"文本 {i+1} <-> 文本 {j+1}: {sim:.4f}")
            print(f"  [{texts[i][:40]}...]")
            print(f"  [{texts[j][:40]}...]")
            print()
    
    # 5. 单条文本编码示例
    query = "什么是深度学习？"
    query_embedding = encode_texts(model, query)
    print(f"查询 '{query}' 的嵌入向量前10个值: {query_embedding[0][:10]}")
