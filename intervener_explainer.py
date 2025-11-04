# intervener_explainer.py
# Explanation Layer - Generates readable, cited recommendations

from typing import Dict, List, Any

class ExplanationLayer:
    """
    Generates human-readable explanations for recommendations.
    Includes IRC references, rationale, and assumptions.
    """
    
    def __init__(self):
        pass
    
    def format_recommendation(self, intervention: Dict[str, Any], score: float) -> Dict[str, str]:
        """
        Format an intervention into an explainable recommendation card.
        
        Args:
            intervention (Dict): Intervention record from KB
            score (float): Relevance score (0-1)
            
        Returns:
            Dict: Formatted recommendation with all fields
        """
        return {
            'id': intervention['id'],
            'intervention': intervention['intervention'],
            'reference': intervention['reference'],
            'rationale': intervention['rationale'],
            'assumptions': intervention['assumptions'],
            'priority': intervention['priority'],
            'relevance_score': round(score * 100, 1),
            'confidence': self._score_to_confidence(score)
        }
    
    def _score_to_confidence(self, score: float) -> str:
        """
        Convert numerical score to confidence label.
        
        Args:
            score (float): Score between 0 and 1
            
        Returns:
            str: Confidence label
        """
        if score >= 0.8:
            return "Very High"
        elif score >= 0.6:
            return "High"
        elif score >= 0.4:
            return "Medium"
        else:
            return "Low"
    
    def generate_report_text(self, recommendations: List[Dict[str, Any]], 
                            query: str, road_type: str = None, 
                            environment: str = None) -> str:
        """
        Generate a textual report from recommendations.
        
        Args:
            recommendations (List): List of formatted recommendations
            query (str): Original user query
            road_type (str): Road type context
            environment (str): Environment context
            
        Returns:
            str: Formatted report text
        """
        report = []
        report.append("=" * 70)
        report.append("INTERVENER - ROAD SAFETY INTERVENTION RECOMMENDATION REPORT")
        report.append("=" * 70)
        report.append("")
        
        # Query summary
        report.append("QUERY DETAILS:")
        report.append(f"  Issue: {query}")
        if road_type:
            report.append(f"  Road Type: {road_type}")
        if environment:
            report.append(f"  Environment: {environment}")
        report.append("")
        
        # Recommendations
        report.append("RECOMMENDED INTERVENTIONS:")
        report.append("-" * 70)
        
        for idx, rec in enumerate(recommendations, 1):
            report.append(f"\n[Recommendation {idx}]")
            report.append(f"Intervention: {rec['intervention']}")
            report.append(f"Reference: {rec['reference']}")
            report.append(f"Rationale: {rec['rationale']}")
            report.append(f"Assumptions: {rec['assumptions']}")
            report.append(f"Confidence: {rec['confidence']} ({rec['relevance_score']}%)")
            report.append("-" * 70)
        
        report.append("")
        report.append("NOTE: All recommendations are material-only estimates.")
        report.append("Labor, transport, and taxes are excluded from cost calculations.")
        report.append("=" * 70)
        
        return "\n".join(report)
    
    def generate_json_output(self, recommendations: List[Dict[str, Any]], 
                            query: str, road_type: str = None, 
                            environment: str = None) -> Dict[str, Any]:
        """
        Generate structured JSON output.
        
        Args:
            recommendations (List): List of formatted recommendations
            query (str): Original query
            road_type (str): Road type
            environment (str): Environment
            
        Returns:
            Dict: JSON-serializable output
        """
        return {
            'status': 'success',
            'query': {
                'issue': query,
                'road_type': road_type or 'urban (default)',
                'environment': environment or 'general'
            },
            'recommendations': recommendations,
            'total_recommendations': len(recommendations),
            'metadata': {
                'system': 'InterveneR v1.0',
                'note': 'Material-only costs; excludes labor and taxes'
            }
        }
    
    def generate_fallback_response(self, query: str) -> Dict[str, Any]:
        """
        Generate response when no sufficient match found.
        
        Args:
            query (str): Original query
            
        Returns:
            Dict: Fallback recommendation
        """
        return {
            'status': 'no_match',
            'message': 'No direct IRC-aligned intervention found in knowledge base.',
            'suggestions': [
                'Refine your query with specific road type (urban/highway/rural)',
                'Add environment context (e.g., curve, school zone, intersection)',
                'Check for alternative terms related to the issue',
                'Contact administrators to expand knowledge base'
            ],
            'fallback_action': 'Please consult road safety engineers or refer to IRC SP:84 and IRC SP:87 for general guidance.'
        }