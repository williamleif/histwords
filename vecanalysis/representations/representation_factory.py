from embedding import SVDEmbedding, Embedding
from explicit import Explicit

def create_representation(rep_type, path, **kwargs):
    if rep_type == 'PPMI':
        return Explicit.load(path, **kwargs)
    elif rep_type == 'SVD':
        return SVDEmbedding(path, **kwargs)
    else:
        return Embedding.load(path, **kwargs)
