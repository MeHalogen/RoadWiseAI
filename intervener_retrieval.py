# intervener_retrieval.py
# Retrieval Engine - Scoring and ranking interventions

from difflib import SequenceMatcher
from rapidfuzz import fuzz
from typing import List, Dict, Any, Tuple
import re

class RetrievalEngine:
    """
    Retrieval Engine: Matches user issues to interventions using hybrid scoring.
    Combines fuzzy matching, keyword overlap, and contextual boosting.
    """
    
    # Priority weights
    PRIORITY_WEIGHTS = {
        'High': 0.03,
        'Medium': 0.015,
        'Low': 0.005
    }
    
    # Environment boosts
    ENV_BOOSTS = {
        'school': 0.08,
        'curve': 0.08,
        'intersection': 0.07,
        'blind': 0.07,
        'night': 0.06,
        'pedestrian': 0.08,
        'guardrail': 0.05,
        'dark': 0.06
    }
    
    def __init__(self, kb: Any):
        """
        Initialize retrieval engine with knowledge base.
        
        Args:
            kb (InterventionKB): Knowledge base instance
        """
        self.kb = kb
    
    def tokenize_query(self, query: str) -> List[str]:
        """
        Tokenize user query into meaningful keywords.
        
        Args:
            query (str): User's natural language issue description
            
        Returns:
            List[str]: Extracted keywords
        """
        query_lower = query.lower()
        # Remove common stop words
        stop_words = {'the', 'a', 'an', 'is', 'are', 'at', 'to', 'for', 'and', 'or', 'in', 'on', 'of'}
        
        # Extract multi-word phrases and individual terms
        tokens = re.findall(r'\b\w+(?:\s+\w+)?\b', query_lower)
        tokens = [t for t in tokens if t not in stop_words]
        return tokens
    
    def calculate_fuzzy_score(self, query: str, target: str) -> float:
        """
        Calculate fuzzy matching score between query and target.
        
        Args:
            query (str): User query token
            target (str): KB entry text
            
        Returns:
            float: Similarity score 0-1
        """
        # Use token_set_ratio for partial matching
        score = fuzz.token_set_ratio(query, target) / 100.0
        return score
    
    def get_environment_boost(self, query: str) -> float:
        """
        Extract environment tags from query and compute boost.
        
        Args:
            query (str): User query
            
        Returns:
            float: Cumulative environment boost
        """
        query_lower = query.lower()
        boost = 0.0
        
        for env_term, boost_val in self.ENV_BOOSTS.items():
            if env_term in query_lower:
                boost += boost_val
        
        return min(boost, 0.25)  # Cap environment boost
    
    def score_intervention(self, query: str, intervention: Dict[str, Any], 
                          road_type: str = None, environment: str = None) -> float:
        """
        Calculate composite relevance score for an intervention.
        
        Score components:
        - Fuzzy match on issue keywords
        - Road type alignment
        - Environment context boost
        - Priority weight
        
        Args:
            query (str): User query
            intervention (Dict): Intervention record
            road_type (str, optional): Specified road type
            environment (str, optional): Specified environment
            
        Returns:
            float: Composite score (0-1)
        """
        tokens = self.tokenize_query(query)
        
        # Base similarity: check against issue keywords
        keyword_scores = []
        for token in tokens:
            max_kw_score = 0.0
            for issue_kw in intervention['issue_keywords']:
                score = self.calculate_fuzzy_score(token, issue_kw)
                max_kw_score = max(max_kw_score, score)
            keyword_scores.append(max_kw_score)
        
        base_similarity = sum(keyword_scores) / len(keyword_scores) if keyword_scores else 0.0
        
        # Road type boost
        road_type_boost = 0.0
        if road_type and road_type.lower() in [rt.lower() for rt in intervention['road_type_tags']]:
            road_type_boost = 0.15
        elif not road_type and 'urban' in [rt.lower() for rt in intervention['road_type_tags']]:
            # Default boost if no road type specified
            road_type_boost = 0.05
        
        # Environment boost
        env_boost = self.get_environment_boost(query)
        if environment:
            env_boost = max(env_boost, 0.08)
        
        # Priority weight
        priority_weight = self.PRIORITY_WEIGHTS.get(intervention['priority'], 0.01)
        
        # Composite score (capped at 1.0)
        composite_score = min(
            base_similarity + road_type_boost + env_boost + priority_weight,
            1.0
        )
        
        return composite_score
    
    def retrieve_and_rank(self, query: str, road_type: str = None, 
                         environment: str = None, top_k: int = 3) -> List[Tuple[Dict[str, Any], float]]:
        """
        Retrieve and rank interventions for a given query.
        
        Args:
            query (str): User issue description
            road_type (str, optional): Road context (urban/highway/rural)
            environment (str, optional): Environmental context
            top_k (int): Number of top interventions to return
            
        Returns:
            List[Tuple]: [(intervention, score), ...] sorted by score descending
        """
        scored_interventions = []
        
        for intervention in self.kb.get_all():
            score = self.score_intervention(query, intervention, road_type, environment)
            scored_interventions.append((intervention, score))
        
        # Sort by score descending, then by priority
        scored_interventions.sort(
            key=lambda x: (x[1], self.PRIORITY_WEIGHTS.get(x[0]['priority'], 0)),
            reverse=True
        )
        
        return scored_interventions[:top_k]
    
    def check_minimum_threshold(self, scored_items: List[Tuple[Dict, float]], 
                               threshold: float = 0.3) -> bool:
        """
        Check if top-ranked intervention meets minimum threshold.
        
        Args:
            scored_items (List): Ranked [(intervention, score), ...] pairs
            threshold (float): Minimum acceptable score
            
        Returns:
            bool: True if best match exceeds threshold
        """
        return len(scored_items) > 0 and scored_items[0][1] >= threshold