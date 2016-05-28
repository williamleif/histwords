from vecanalysis.representations.embedding import Embedding
from sklearn.decomposition import PCA

def reduce_dim(embedding, dim=2, post_normalize=False):
    pca = PCA(n_components=2)
    reduced_vecs = pca.fit_transform(embedding.m)
    return Embedding(reduced_vecs, embedding.iw, normalize=post_normalize)
    
