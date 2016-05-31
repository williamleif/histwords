from embedding import SVDEmbedding, Embedding, GigaEmbedding
from explicit import Explicit

def create_representation(rep_type, path, *args, **kwargs):
    if rep_type == 'Explicit' or rep_type == 'PPMI':
        return Explicit.load(path, *args, **kwargs)
    elif rep_type == 'SVD':
        return SVDEmbedding(path, *args, **kwargs)
    elif rep_type == 'GIGA':
        return GigaEmbedding(path, *args, **kwargs)
    elif rep_type:
        return Embedding.load(path, *args, **kwargs)
