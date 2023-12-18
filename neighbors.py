from representations.sequentialembedding import SequentialEmbedding

def compare_neighbors_over_decades(embedding_path, target_word, decades):
    """
    Compute and compare the sets of neighbors for a given word across decades.

    Parameters:
    - embedding_path (str): Path to the embeddings directory.
    - target_word (str): The word for which neighbors are compared.
    - decades (range): Range of decades to consider.

    Returns:
    - neighbors_over_decades (dict): Dictionary where keys are decades, and values are sets of neighbors.
    """

    # Load embeddings for the specified range of years
    embeddings = SequentialEmbedding.load(embedding_path, decades)

    # Dictionary to store neighbors for each decade
    neighbors_over_decades = {}

    # Compute neighbors for the target word for each decade
    for decade in decades:
        neighbors = set(embeddings.get_embed(decade).get_neighbourhood_embed(target_word, n=10))
        neighbors_over_decades[decade] = neighbors

    return neighbors_over_decades

if __name__ == "__main__":
    # Example usage
    embedding_path = "sgns"
    target_word = "covenant"
    decades = range(1800, 2000, 10)

    neighbors_over_decades = compare_neighbors_over_decades(embedding_path, target_word, decades)

    # Print the results
    for decade, neighbors in neighbors_over_decades.items():
        print(f"Decade: {decade}, Neighbors: {neighbors}")
