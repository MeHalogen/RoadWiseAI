# config.py
# Configuration settings for RoadWiseAI

import os
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class UIConfig:
    """Streamlit UI configuration."""
    
    PAGE_TITLE: str = "RoadWiseAI - Road Safety Intervention GPT"
    PAGE_ICON: str = "🛣️"
    LAYOUT: str = "wide"
    SIDEBAR_STATE: str = "expanded"
    
    # Color scheme
    PRIMARY_COLOR: str = "#1f4788"
    SECONDARY_COLOR: str = "#2e5f8a"
    ACCENT_COLOR: str = "#667eea"

@dataclass
class ScoringConfig:
    """Scoring configuration constants."""
    
    # Priority weights
    PRIORITY_WEIGHTS: Dict[str, float] = None
    
    # Environment boost terms and their weights
    ENV_BOOSTS: Dict[str, float] = None
    
    # Road type weights
    ROAD_TYPE_WEIGHTS: Dict[str, float] = None
    
    # Matching thresholds
    FUZZY_THRESHOLD: float = 70.0
    SEMANTIC_THRESHOLD: float = 0.3
    MINIMUM_SCORE_THRESHOLD: float = 0.2
    
    def __post_init__(self):
        """Initialize default values."""
        if self.PRIORITY_WEIGHTS is None:
            self.PRIORITY_WEIGHTS = {
                "High": 1.0,
                "Medium": 0.7,
                "Low": 0.4
            }
        
        if self.ENV_BOOSTS is None:
            self.ENV_BOOSTS = {
                "intersection": 0.2,
                "curve": 0.15,
                "bridge": 0.1,
                "school": 0.25,
                "hospital": 0.2,
                "urban": 0.1,
                "highway": 0.15
            }
        
        if self.ROAD_TYPE_WEIGHTS is None:
            self.ROAD_TYPE_WEIGHTS = {
                "Urban": 1.0,
                "Highway": 0.9,
                "Rural": 0.8
            }

@dataclass
class FileConfig:
    """File path configuration."""
    
    KB_PATH: str = "GPT_Input_DB.xlsx"
    OUTPUT_DIR: str = "output"
    PDF_FILENAME: str = "RoadWiseAI_Report.pdf"
    PPTX_FILENAME: str = "RoadWiseAI_Presentation.pptx"
    JSON_FILENAME: str = "RoadWiseAI_Output.json"
    
    def __post_init__(self):
        """Create output directory if it doesn't exist."""
        os.makedirs(self.OUTPUT_DIR, exist_ok=True)

@dataclass
class APIConfig:
    """API configuration."""
    
    TITLE: str = "RoadWiseAI API"
    DESCRIPTION: str = "Road Safety Intervention GPT - REST API"
    VERSION: str = "2.0.0"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Response limits
    MAX_RECOMMENDATIONS: int = 10
    DEFAULT_TOP_K: int = 5

@dataclass
class ReportConfig:
    """Report generation configuration."""
    
    REPORT_TITLE: str = "RoadWiseAI Safety Intervention Report"
    ORGANIZATION: str = "Road Safety Authority"
    AUTHOR: str = "RoadWiseAI System"
    
    # Report styling
    HEADER_COLOR: str = "#1f4788"
    ACCENT_COLOR: str = "#667eea"
    
    # PDF settings
    PAGE_SIZE: str = "A4"
    MARGIN: float = 1.0  # inches
    
    # PowerPoint settings
    SLIDE_LAYOUT: int = 1  # Title and content layout
