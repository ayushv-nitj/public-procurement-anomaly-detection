"""
NLP Module — TF-IDF Similarity Detection
Detects suspiciously similar tender descriptions that may indicate
copy-paste tenders or coordinated bidding.
"""

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def compute_tfidf_matrix(descriptions):
    """
    Vectorize tender descriptions using TF-IDF.
    
    Args:
        descriptions: list or Series of description strings
        
    Returns:
        vectorizer: fitted TfidfVectorizer
        tfidf_matrix: sparse TF-IDF matrix
    """
    vectorizer = TfidfVectorizer(
        max_features=500,
        stop_words="english",
        ngram_range=(1, 2),  # unigrams + bigrams
        min_df=2,
        max_df=0.95
    )
    tfidf_matrix = vectorizer.fit_transform(descriptions)
    return vectorizer, tfidf_matrix


def compute_similarity_scores(tfidf_matrix, threshold=0.8):
    """
    Compute per-contract NLP similarity score.
    
    For each contract, finds the maximum cosine similarity with any other contract.
    High similarity (>threshold) indicates potential copy-paste or collusion.
    
    Returns:
        max_similarities: array of max similarity score per contract
        similar_pairs: list of (i, j, score) tuples exceeding threshold
    """
    # Compute pairwise cosine similarity
    sim_matrix = cosine_similarity(tfidf_matrix)
    
    # Zero out the diagonal (self-similarity = 1.0)
    np.fill_diagonal(sim_matrix, 0)
    
    # Max similarity for each contract
    max_similarities = sim_matrix.max(axis=1)
    
    # Find pairs above threshold
    similar_pairs = []
    n = sim_matrix.shape[0]
    for i in range(n):
        for j in range(i + 1, n):
            if sim_matrix[i, j] >= threshold:
                similar_pairs.append((i, j, round(sim_matrix[i, j], 4)))
    
    return max_similarities, similar_pairs


def run_nlp_analysis(descriptions, threshold=0.8):
    """
    Full NLP pipeline.
    
    Returns:
        nlp_scores: per-contract similarity score (0 to 1)
        similar_pairs: list of suspicious pairs
        vectorizer: fitted TF-IDF vectorizer
    """
    vectorizer, tfidf_matrix = compute_tfidf_matrix(descriptions)
    max_similarities, similar_pairs = compute_similarity_scores(tfidf_matrix, threshold)
    
    print(f"NLP Analysis:")
    print(f"  Vocabulary size: {len(vectorizer.vocabulary_)}")
    print(f"  Contracts with similarity > {threshold}: {sum(max_similarities > threshold)}")
    print(f"  Suspicious pairs found: {len(similar_pairs)}")
    
    return max_similarities, similar_pairs, vectorizer
