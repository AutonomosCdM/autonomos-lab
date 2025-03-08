from typing import List, Dict, Any
import numpy as np
import logging

class EmbeddingMigrator:
    """
    Handles migration of embedding vectors between different models or embedding spaces.
    """
    
    def __init__(self):
        """
        Initialize the EmbeddingMigrator with logging.
        """
        self.logger = logging.getLogger(__name__)
    
    def linear_transform(
        self,
        source_embeddings: List[List[float]], 
        source_model: str, 
        target_model: str
    ) -> List[List[float]]:
        """
        Perform linear transformation between embedding spaces.
        
        :param source_embeddings: Original embeddings
        :param source_model: Source embedding model identifier
        :param target_model: Target embedding model identifier
        :return: Transformed embeddings
        """
        try:
            # Normalize embeddings
            normalized_embeddings = [
                list(np.array(embedding) / np.linalg.norm(np.array(embedding)))
                for embedding in source_embeddings
            ]
            
            # Log migration details
            self.logger.info(f"Migrating embeddings from {source_model} to {target_model}")
            self.logger.info(f"Number of embeddings: {len(source_embeddings)}")
            
            return normalized_embeddings
        
        except Exception as e:
            self.logger.error(f"Embedding migration error: {e}")
            raise
    
    def reduce_dimensionality(
        self, 
        embeddings: List[List[float]], 
        target_dimensions: int
    ) -> List[List[float]]:
        """
        Reduce the dimensionality of embeddings using PCA.
        
        :param embeddings: Input embeddings
        :param target_dimensions: Desired number of dimensions
        :return: Reduced dimensionality embeddings
        """
        try:
            # Convert to numpy array
            embedding_array = np.array(embeddings)
            
            # Perform PCA
            from sklearn.decomposition import PCA
            pca = PCA(n_components=target_dimensions)
            reduced_embeddings = pca.fit_transform(embedding_array)
            
            # Log dimensionality reduction details
            self.logger.info(f"Reduced embeddings from {embedding_array.shape[1]} to {target_dimensions} dimensions")
            self.logger.info(f"Variance explained: {sum(pca.explained_variance_ratio_):.2%}")
            
            return reduced_embeddings.tolist()
        
        except ImportError:
            self.logger.error("scikit-learn is required for dimensionality reduction")
            raise ImportError("Please install scikit-learn to use dimensionality reduction")
        
        except Exception as e:
            self.logger.error(f"Dimensionality reduction error: {e}")
            raise
    
    def compute_embedding_similarity(
        self, 
        embedding1: List[float], 
        embedding2: List[float]
    ) -> float:
        """
        Compute cosine similarity between two embeddings.
        
        :param embedding1: First embedding
        :param embedding2: Second embedding
        :return: Cosine similarity score
        """
        try:
            # Convert to numpy arrays
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            
            # Compute cosine similarity
            similarity = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
            
            return float(similarity)
        
        except Exception as e:
            self.logger.error(f"Embedding similarity computation error: {e}")
            raise
