import numpy as np
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE
from collections import defaultdict
from representations.sequentialembedding import SequentialEmbedding

def get_embeddings(embedding, words):
    """Get embeddings for a list of words from the embedding object."""
    return np.array([embedding.represent(word) for word in words if word in embedding.wi])


def visualize_tsne_centroids(embedding_path, target_word, decades, output_filename, perplexity=30, n_iter=1000):
    """
    Visualize the semantic change of a word across decades using t-SNE with centroids for each unique word (except the target word) and save the plot.

    Parameters:
    - embedding_path (str): Path to the embeddings directory.
    - target_word (str): The word to visualize.
    - decades (range): Range of decades to consider.
    - output_filename (str): Filename for saving the plot.
    - perplexity (int): The perplexity parameter for t-SNE.
    - n_iter (int): The number of iterations for optimization in t-SNE.
    """

    embeddings = SequentialEmbedding.load(embedding_path, decades)
    word_vectors = defaultdict(list)
    target_word_vectors = []

    # Gather embeddings for each word across decades
    for decade in decades:
        embedding = embeddings.get_embed(decade)
        if target_word in embedding.iw:
            neighbors = embedding.closest(target_word, n=10)
            target_word_vectors.append(embedding.represent(target_word))
            for _, neighbor in neighbors:
                if neighbor != target_word:  # Exclude target word from centroids
                    word_vectors[neighbor].append(embedding.represent(neighbor))

    # Calculate centroids for each non-target word
    centroids = {word: np.mean(np.array(vectors), axis=0) for word, vectors in word_vectors.items()}
    labels = list(centroids.keys()) + [f'{target_word} ({decade})' for decade in decades]
    all_vectors = np.array(list(centroids.values()) + target_word_vectors)

    # Apply t-SNE
    tsne_model = TSNE(n_components=2, perplexity=perplexity, n_iter=n_iter, random_state=0)
    reduced_vectors = tsne_model.fit_transform(all_vectors)

    # Plotting
    plt.figure(figsize=(12, 8))
    for i, label in enumerate(labels):
        x, y = reduced_vectors[i, :]
        plt.scatter(x, y)
        plt.annotate(label, xy=(x, y), xytext=(5, 2), textcoords='offset points', ha='right', va='bottom')

    plt.title(f't-SNE visualization of semantic centroids for "{target_word}"')
    plt.xlabel('t-SNE Component 1')
    plt.ylabel('t-SNE Component 2')
    
    # Save the plot
    plt.savefig(output_filename)
    plt.close()

# Example usage
embedding_path = "sgns"
target_word = "broadcast"
decades = range(1800, 2000, 10)
output_filename = "tsne_centroids_visualization.png"

visualize_tsne_centroids(embedding_path, target_word, decades, output_filename)