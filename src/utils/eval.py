def compute_recall(correct_uris, retrieved_uris):
    if len(correct_uris) == 0:
        return 0
    else:
        return len(set(correct_uris) & set(retrieved_uris)) / len(correct_uris)

def compute_precision(correct_uris, retrieved_uris):
    if len(retrieved_uris) == 0:
        return 0
    else:
        return len(set(correct_uris) & set(retrieved_uris)) / len(retrieved_uris)