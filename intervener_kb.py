# intervener_kb.py
# Knowledge Base Module for RoadWiseAI - Loads and manages intervention data

import pandas as pd
import json
from typing import List, Dict, Any
import os

class InterventionKB:
    """
    Knowledge Base for road safety interventions.
    Loads interventions from Excel database and provides query access.
    """
    
    def __init__(self, db_path: str = "GPT_Input_DB.xlsx"):
        """
        Initialize the knowledge base from Excel database.
        
        Args:
            db_path (str): Path to interventions Excel database file
        """
        if not os.path.exists(db_path):
            raise FileNotFoundError(f"Database file not found: {db_path}")
            
        # Read Excel file - try different sheet names
        try:
            self.df = pd.read_excel(db_path, sheet_name=0)  # First sheet
        except Exception as e:
            print(f"Error reading Excel file: {e}")
            # Fallback to try CSV if exists
            csv_fallback = db_path.replace('.xlsx', '.csv')
            if os.path.exists(csv_fallback):
                self.df = pd.read_csv(csv_fallback)
            else:
                raise
                
        self.interventions = []
        self._parse_interventions()
    
    def _parse_interventions(self):
        """Parse Excel rows into intervention objects with flexible column mapping."""
        print(f"Database columns: {list(self.df.columns)}")
        print(f"Database shape: {self.df.shape}")
        
        # Create column mapping for flexible parsing
        col_map = self._create_column_mapping()
        
        for idx, row in self.df.iterrows():
            try:
                # Parse list fields with flexible handling
                problem_text = str(row.get(col_map.get('issue_keywords', ''), 'road safety'))
                category_text = str(row.get(col_map.get('road_type_tags', ''), 'general'))
                data_text = str(row.get(col_map.get('intervention', ''), 'Safety intervention'))
                clause_text = str(row.get(col_map.get('reference', ''), 'IRC Standard'))
                type_text = str(row.get(col_map.get('priority', ''), 'Medium'))
                code_text = str(row.get(col_map.get('code', ''), ''))
                
                issue_keywords = self._parse_list_field(problem_text)
                road_type_tags = self._parse_list_field(category_text)
                
                intervention = {
                    'id': int(row.get(col_map.get('id', ''), idx + 1)),
                    'issue_keywords': issue_keywords,
                    'road_type_tags': road_type_tags,
                    'intervention': data_text,
                    'reference': clause_text,
                    'priority': self._determine_priority(type_text, problem_text),
                    'rationale': self._extract_rationale(row, col_map),
                    'assumptions': "Based on IRC standards. Material costs may vary by location.",
                    'cost_estimate': self._extract_cost_estimate(row, col_map),
                    'implementation_time': self._estimate_implementation_time(data_text),
                    'effectiveness': self._estimate_effectiveness(problem_text, data_text),
                    'maintenance': self._estimate_maintenance(data_text),
                    'code': code_text,
                    'problem_description': problem_text,
                    'category': category_text
                }
                self.interventions.append(intervention)
            except Exception as e:
                print(f"Error parsing row {idx}: {e}")
                continue
    
    def _create_column_mapping(self) -> Dict[str, str]:
        """Create flexible column mapping for the Excel database format."""
        columns = [col.lower().strip() for col in self.df.columns]
        col_map = {}
        
        # Map columns based on actual Excel structure: ['S. No.', 'problem', 'category', 'type', 'data', 'code', 'clause']
        mapping_rules = {
            'id': ['s. no.', 'id', 'number', 'no', '#'],
            'issue_keywords': ['problem', 'issue_keywords', 'keywords', 'issues', 'description'],
            'road_type_tags': ['category', 'road_type_tags', 'road_type', 'type'],
            'intervention': ['data', 'intervention', 'solution', 'recommendation', 'action'],
            'reference': ['clause', 'reference', 'source', 'irc', 'standard'],
            'priority': ['type', 'priority', 'urgency', 'importance'],  # Using 'type' column for priority
            'rationale': ['data', 'rationale', 'reason', 'justification', 'explanation'],
            'assumptions': ['assumptions', 'notes', 'conditions'],
            'cost_estimate': ['cost', 'estimate', 'budget', 'price'],
            'implementation_time': ['time', 'duration', 'timeline', 'implementation'],
            'effectiveness': ['effectiveness', 'impact', 'result'],
            'maintenance': ['maintenance', 'upkeep', 'ongoing'],
            'code': ['code', 'identifier', 'ref_code']
        }
        
        for key, variations in mapping_rules.items():
            for variation in variations:
                if variation in columns:
                    col_map[key] = self.df.columns[columns.index(variation)]
                    break
        
        return col_map
    
    def _parse_list_field(self, field_str: str) -> List[str]:
        """Parse list field from CSV string format."""
        try:
            # Handle JSON list format
            if field_str.startswith('['):
                return json.loads(field_str.replace("'", '"'))
            return [field_str]
        except:
            return [field_str]
    
    def _extract_rationale(self, row, col_map: Dict[str, str]) -> str:
        """Extract or generate rationale from row data."""
        # Try to get rationale from database first
        rationale_col = col_map.get('rationale')
        if rationale_col and rationale_col in row and pd.notna(row[rationale_col]):
            return str(row[rationale_col])
        
        # Fallback rationale based on intervention type
        intervention_text = str(row.get(col_map.get('intervention', ''), '')).lower()
        
        if 'sign' in intervention_text:
            return "Improves driver visibility and awareness of hazards through standardized, retroreflective signage."
        elif 'crossing' in intervention_text or 'pedestrian' in intervention_text:
            return "Provides safe, designated crossing points for pedestrians; reduces vehicle-pedestrian conflicts."
        elif 'marking' in intervention_text:
            return "Enhances road markings visibility; improves lane discipline and nighttime safety."
        elif 'curve' in intervention_text or 'chevron' in intervention_text:
            return "Reduces vehicle speed at high-risk curves; improves directional guidance."
        elif 'pavement' in intervention_text or 'repair' in intervention_text:
            return "Restores pavement integrity; prevents water ingress and secondary damage."
        elif 'guardrail' in intervention_text or 'barrier' in intervention_text:
            return "Prevents vehicles from leaving roadway; protects against run-off accidents."
        elif 'light' in intervention_text or 'illumination' in intervention_text:
            return "Improves nighttime visibility; enhances road user awareness after dark."
        elif 'speed' in intervention_text:
            return "Reduces approach speed at critical zones; warns drivers of hazards ahead."
        elif 'vegetation' in intervention_text or 'sight' in intervention_text:
            return "Restores sightlines; improves driver decision-making time."
        elif 'signal' in intervention_text or 'intersection' in intervention_text:
            return "Controls traffic flow at intersections; reduces conflict points."
        else:
            return "Enhances road safety in line with IRC standards and best practices."
    
    def _extract_cost_estimate(self, row, col_map: Dict[str, str]) -> str:
        """Extract cost estimate from database."""
        cost_col = col_map.get('cost_estimate')
        if cost_col and cost_col in row and pd.notna(row[cost_col]):
            return str(row[cost_col])
        return "Cost varies based on scope and location"
    
    def _determine_priority(self, type_text: str, problem_text: str) -> str:
        """Determine priority based on type and problem description."""
        type_lower = type_text.lower()
        problem_lower = problem_text.lower()
        
        # High priority indicators
        if any(word in problem_lower for word in ['accident', 'fatal', 'injury', 'crash', 'collision']):
            return 'High'
        elif any(word in problem_lower for word in ['damaged', 'missing', 'broken', 'failed']):
            return 'High'
        elif any(word in type_lower for word in ['urgent', 'critical', 'immediate']):
            return 'High'
        # Medium priority indicators
        elif any(word in problem_lower for word in ['poor', 'inadequate', 'insufficient', 'worn']):
            return 'Medium'
        elif any(word in type_lower for word in ['standard', 'regular', 'normal']):
            return 'Medium'
        else:
            return 'Medium'
    
    def _estimate_implementation_time(self, intervention_text: str) -> str:
        """Estimate implementation time based on intervention type."""
        text_lower = intervention_text.lower()
        
        if any(word in text_lower for word in ['sign', 'marking', 'paint']):
            return '1-2 weeks'
        elif any(word in text_lower for word in ['guardrail', 'barrier', 'fence']):
            return '2-4 weeks'
        elif any(word in text_lower for word in ['lighting', 'signal', 'electrical']):
            return '3-6 weeks'
        elif any(word in text_lower for word in ['pavement', 'surface', 'construction']):
            return '1-3 months'
        else:
            return '2-6 weeks'
    
    def _estimate_effectiveness(self, problem_text: str, intervention_text: str) -> str:
        """Estimate effectiveness based on problem and intervention match."""
        problem_lower = problem_text.lower()
        intervention_lower = intervention_text.lower()
        
        # High effectiveness for direct matches
        if ('visibility' in problem_lower and any(word in intervention_lower for word in ['sign', 'marking', 'light'])):
            return 'Very High'
        elif ('speed' in problem_lower and any(word in intervention_lower for word in ['bump', 'limit', 'calm'])):
            return 'Very High'
        elif ('accident' in problem_lower and any(word in intervention_lower for word in ['barrier', 'guardrail'])):
            return 'Very High'
        else:
            return 'High'
    
    def _estimate_maintenance(self, intervention_text: str) -> str:
        """Estimate maintenance requirements based on intervention type."""
        text_lower = intervention_text.lower()
        
        if any(word in text_lower for word in ['paint', 'marking']):
            return 'Annual repainting required'
        elif any(word in text_lower for word in ['sign', 'post']):
            return 'Periodic inspection and cleaning'
        elif any(word in text_lower for word in ['lighting', 'electrical']):
            return 'Regular electrical maintenance'
        elif any(word in text_lower for word in ['guardrail', 'barrier']):
            return 'Minimal maintenance, inspect after impacts'
        else:
            return 'Standard maintenance as per IRC guidelines'
    
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