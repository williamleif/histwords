import numpy as np
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE
from representations.sequentialembedding import SequentialEmbedding

def semantic_similarity(embedding1, embedding2):
    """Calculate cosine similarity between two embeddings."""
    return np.dot(embedding1, embedding2) / (np.linalg.norm(embedding1) * np.linalg.norm(embedding2))

def get_neighbors(embedding, word, n=10):
    """Get the n closest neighbors of a word in the given embedding."""
    return [neighbor for _, neighbor in embedding.closest(word, n)]

def track_word_changes(embedding_path, word, decades):
    embeddings = SequentialEmbedding.load(embedding_path, decades)
    similarities = {}
    neighbor_changes = {}
    all_vectors = []

    for decade in decades:
        embedding = embeddings.get_embed(decade)
        if word not in embedding.iw:
            continue
        word_vector = embedding.represent(word)
        all_vectors.append(word_vector)
        neighbors = get_neighbors(embedding, word)

        # Calculate similarity to the first decade
        if decade != decades[0]:
            base_embedding = embeddings.get_embed(decades[0])
            base_vector = base_embedding.represent(word)
            similarities[decade] = semantic_similarity(word_vector, base_vector)

        neighbor_changes[decade] = neighbors

    # t-SNE visualization
    num_vectors = len(all_vectors)
    if num_vectors < 5:  # Ensuring a minimum number of vectors for t-SNE to work effectively
        print("Not enough data points for meaningful t-SNE visualization.")
        return similarities, neighbor_changes

    perplexity_value = min(30, num_vectors - 1)  # Adjust perplexity based on the number of vectors
    tsne_model = TSNE(n_components=2, perplexity=perplexity_value, n_iter=1000, random_state=0)
    reduced_vectors = tsne_model.fit_transform(np.array(all_vectors))


    plt.figure(figsize=(10, 6))
    for i, decade in enumerate(decades):
        plt.scatter(reduced_vectors[i, 0], reduced_vectors[i, 1], label=f'{decade}')
        plt.annotate(decade, (reduced_vectors[i, 0], reduced_vectors[i, 1]))

    plt.title(f't-SNE of "{word}" embeddings over decades')
    plt.xlabel('t-SNE Component 1')
    plt.ylabel('t-SNE Component 2')
    plt.legend()
    plt.savefig(f"{word}_tsne_plot.png")
    plt.close()

    return similarities, neighbor_changes

# Example usage
embedding_path = "sgns"
word = "faith"
decades = range(1800, 2000, 10)

similarities, neighbor_changes = track_word_changes(embedding_path, word, decades)
print("Semantic Similarities over Decades:")
for decade, similarity in similarities.items():
    print(f"Decade {decade}: {similarity}")

print("\nNeighbor Changes:")
for decade, neighbors in neighbor_changes.items():
    print(f"Decade {decade}: {neighbors}")
