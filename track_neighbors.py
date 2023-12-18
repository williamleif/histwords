from representations.sequentialembedding import SequentialEmbedding

def track_neighbor_changes(embedding_path, target_word, decades):
    """
    Track changes in neighbors for a given word across decades using SequentialEmbedding.

    Parameters:
    - embedding_path (str): Path to the embeddings directory.
    - target_word (str): The word for which neighbors are compared.
    - decades (range): Range of decades to consider.

    Returns:
    - neighbor_changes (dict): Dictionary where keys are decades, and values are sets of new neighbors.
    """

    # Load embeddings for the specified range of years
    embeddings = SequentialEmbedding.load(embedding_path, decades)

    # Dictionary to store changing neighbors for each decade
    neighbor_changes = {}
    lost_neighbors = {}
    previous_neighbors = set()

    for decade in decades:
        current_neighbors = set()
        current_embedding = embeddings.get_embed(decade)
        
        if target_word in current_embedding.iw:
            for _, neighbor in current_embedding.closest(target_word, n=10):
                current_neighbors.add(neighbor)

            if decade > decades[0]:
                new_neighbors = current_neighbors - previous_neighbors
                neighbors_lost = previous_neighbors - current_neighbors
                neighbor_changes[decade] = new_neighbors
                lost_neighbors[decade] = neighbors_lost
            else:
                neighbor_changes[decade] = current_neighbors

            previous_neighbors = current_neighbors
        else:
            print(f"Word '{target_word}' not present in the vocabulary for the decade {decade}")

    return neighbor_changes, lost_neighbors

# Example usage
if __name__ == "__main__":
    embedding_path = "sgns"
    target_word = "gospel"
    decades = range(1810, 2000, 10)

    neighbor_changes, lost_neighbors = track_neighbor_changes(embedding_path, target_word, decades)

    # Print the results
    print("New Neighbors:")
    for decade, neighbors in neighbor_changes.items():
        print(f"Decade: {decade}, New Neighbors: {neighbors}")

    print("\nLost Neighbors:")
    for decade, neighbors in lost_neighbors.items():
        print(f"Decade: {decade}, Lost Neighbors: {neighbors}")