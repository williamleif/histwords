from representations.sequentialembedding import SequentialEmbedding
import numpy as np

def find_centroid(embedding, words):
    """Calculate the centroid of the given words in the embedding."""
    vectors = [embedding.represent(word) for word in words if word in embedding.wi]
    return np.mean(vectors, axis=0) if vectors else None

def track_backward_centroid(embedding_path, target_word, base_decade, decades):
    """
    Track the centroid of a given word's neighbors in a base decade and find the closest match in each preceding decade.

    Parameters:
    - embedding_path (str): Path to the embeddings directory.
    - target_word (str): The word to track.
    - base_decade (int): The base decade to start from.
    - decades (range): Range of decades to consider.

    Returns:
    - centroid_tracking (dict): Dictionary where keys are decades, and values are the words closest to the base centroid.
    """
    embeddings = SequentialEmbedding.load(embedding_path, decades)
    centroid_tracking = {}

    if base_decade not in embeddings.embeds:
        print(f"No embeddings found for base decade {base_decade}.")
        return centroid_tracking

    base_neighbors = embeddings.get_embed(base_decade).get_neighbourhood_embed(target_word, n=10)
    base_centroid = find_centroid(embeddings.get_embed(base_decade), base_neighbors)

    for decade in reversed(decades):
        if decade >= base_decade or decade not in embeddings.embeds:
            continue

        closest_word = None
        min_distance = float('inf')
        current_embedding = embeddings.get_embed(decade)

        for word in current_embedding.iw:
            neighbors = current_embedding.get_neighbourhood_embed(word, n=10)
            centroid = find_centroid(current_embedding, neighbors)
            if centroid is not None:
                distance = np.linalg.norm(base_centroid - centroid)
                if distance < min_distance:
                    min_distance = distance
                    closest_word = word

        centroid_tracking[decade] = closest_word

    return centroid_tracking

# Example usage
embedding_path = "sgns"
target_word = "pure"
base_decade = 1980
decades = range(1800, 1990, 10)

centroid_tracking = track_backward_centroid(embedding_path, target_word, base_decade, decades)

# Print the results
for decade, closest_word in centroid_tracking.items():
    print(f"Decade: {decade}, Closest Word to Centroid: {closest_word}")
