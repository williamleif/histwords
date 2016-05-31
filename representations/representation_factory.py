from embedding import SVDEmbedding, Embedding, GigaEmbedding
from explicit import Explicit

def create_representation(rep_type, path, *args, **kwargs):
    if rep_type == 'Explicit':
        return Explicit.load(path, *args, **kwargs)
    elif rep_type == 'SVD':
        return SVDEmbedding(path, *args, **kwargs)
    elif rep_type == 'GIGA':
        return GigaEmbedding(path, *args, **kwargs)
    else:
        return Embedding.load(path, *args, **kwargs)
