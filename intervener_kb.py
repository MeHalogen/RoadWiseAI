# intervener_kb.py
# Knowledge Base Module - Loads and manages intervention data

import pandas as pd
import json
from typing import List, Dict, Any

class InterventionKB:
    """
    Knowledge Base for road safety interventions.
    Loads interventions from CSV and provides query access.
    """
    
    def __init__(self, csv_path: str = "interventions.csv"):
        """
        Initialize the knowledge base from CSV.
        
        Args:
            csv_path (str): Path to interventions CSV file
        """
        self.df = pd.read_csv(csv_path)
        self.interventions = []
        self._parse_interventions()
    
    def _parse_interventions(self):
        """Parse CSV rows into intervention objects."""
        for idx, row in self.df.iterrows():
            # Parse list fields (they are stored as strings in CSV)
            issue_keywords = self._parse_list_field(row['issue_keywords'])
            road_type_tags = self._parse_list_field(row['road_type_tags'])
            
            intervention = {
                'id': int(row['id']),
                'issue_keywords': issue_keywords,
                'road_type_tags': road_type_tags,
                'intervention': str(row['intervention']),
                'reference': str(row['reference']),
                'priority': str(row['priority']),
                'rationale': self._extract_rationale(row),
                'assumptions': "Material-only cost; excludes labor and taxes."
            }
            self.interventions.append(intervention)
    
    def _parse_list_field(self, field_str: str) -> List[str]:
        """Parse list field from CSV string format."""
        try:
            # Handle JSON list format
            if field_str.startswith('['):
                return json.loads(field_str.replace("'", '"'))
            return [field_str]
        except:
            return [field_str]
    
    def _extract_rationale(self, row) -> str:
        """Extract or generate rationale from row data."""
        rationale_map = {
            1: "Improves driver visibility and awareness of hazards through standardized, retroreflective signage.",
            2: "Provides safe, designated crossing points for pedestrians; reduces vehicle-pedestrian conflicts.",
            3: "Enhances road markings visibility; improves lane discipline and nighttime safety.",
            4: "Reduces vehicle speed at high-risk curves; improves directional guidance.",
            5: "Restores pavement integrity; prevents water ingress and secondary damage.",
            6: "Prevents vehicles from leaving roadway; protects against run-off accidents.",
            7: "Improves nighttime visibility; enhances road user awareness after dark.",
            8: "Reduces approach speed at critical zones; warns drivers of hazards ahead.",
            9: "Restores sightlines; improves driver decision-making time.",
            10: "Controls traffic flow at intersections; reduces conflict points.",
            11: "Provides dedicated, tactile infrastructure for vulnerable road users.",
            12: "Restores road delineation; improves night visibility for all users."
        }
        row_id = int(row['id'])
        return rationale_map.get(row_id, "Enhances road safety in line with IRC standards.")
    
    def get_all(self) -> List[Dict[str, Any]]:
        """Return all interventions."""
        return self.interventions
    
    def get_by_id(self, intervention_id: int) -> Dict[str, Any]:
        """Get intervention by ID."""
        for interv in self.interventions:
            if interv['id'] == intervention_id:
                return interv
        return None
    
    def search_by_keywords(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """Search interventions by keywords."""
        results = []
        for interv in self.interventions:
            for kw in keywords:
                if any(kw.lower() in issue_kw.lower() 
                       for issue_kw in interv['issue_keywords']):
                    results.append(interv)
                    break
        return results