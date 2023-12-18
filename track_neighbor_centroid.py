from representations.sequentialembedding import SequentialEmbedding
import numpy as np

def find_closest_word(embedding, target_vector):
    """Find the closest word in the embedding to the given target vector."""
    closest_word = None
    min_distance = float('inf')

    for word in embedding.iw:
        word_vector = embedding.represent(word)
        distance = np.linalg.norm(target_vector - word_vector)
        if distance < min_distance:
            min_distance = distance
            closest_word = word

    return closest_word

def track_centroid_neighbors(embedding_path, target_word, decades):
    """
    Track the centroid of the 10 nearest neighbors of a word from the first decade and find the closest word to this centroid in subsequent decades.

    Parameters:
    - embedding_path (str): Path to the embeddings directory.
    - target_word (str): The word to track.
    - decades (range): Range of decades to consider.

    Returns:
    - closest_words (dict): Dictionary where keys are decades, and values are words closest to the initial centroid.
    """

    embeddings = SequentialEmbedding.load(embedding_path, decades)
    first_decade = decades[0]

    # Get the embedding for the first decade and find the centroid of the 10 nearest neighbors
    first_embedding = embeddings.get_embed(first_decade)
    if target_word not in first_embedding.iw:
        raise ValueError(f"Word '{target_word}' not present in the vocabulary for the decade {first_decade}.")

    neighbors = first_embedding.closest(target_word, n=10)
    neighbor_vectors = [first_embedding.represent(neighbor) for _, neighbor in neighbors]
    centroid = np.mean(neighbor_vectors, axis=0)

    closest_words = {}
    for decade in decades:
        current_embedding = embeddings.get_embed(decade)
        closest_word = find_closest_word(current_embedding, centroid)
        closest_words[decade] = closest_word

    return closest_words

# Example usage
if __name__ == "__main__":
    embedding_path = "sgns"
    target_word = "pure"
    decades = range(1800, 2000, 10)

    closest_words = track_centroid_neighbors(embedding_path, target_word, decades)

    # Print the results
    for decade, word in closest_words.items():
        print(f"Decade: {decade}, Closest Word to Initial Centroid: {word}")
