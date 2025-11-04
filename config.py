# config.py
# Configuration settings for InterveneR

import os
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class ScoringConfig:
    """Scoring configuration constants."""
    
    # Priority weights
    PRIORITY_WEIGHTS: Dict[str, float] = None
    
    # Environment boost terms and their weights
    ENV_BOOSTS: Dict[str, float] = None
    
    # Minimum threshold for recommendation
    MIN_SCORE_THRESHOLD: float = 0.3
    
    # Top-K recommendations
    DEFAULT_TOP_K: int = 3
    
    def __post_init__(self):
        if self.PRIORITY_WEIGHTS is None:
            self.PRIORITY_WEIGHTS = {
                'High': 0.03,
                'Medium': 0.015,
                'Low': 0.005
            }
        
        if self.ENV_BOOSTS is None:
            self.ENV_BOOSTS = {
                'school': 0.08,
                'curve': 0.08,
                'intersection': 0.07,
                'blind': 0.07,
                'night': 0.06,
                'pedestrian': 0.08,
                'guardrail': 0.05,
                'dark': 0.06,
                'junction': 0.07,
                'residential': 0.06,
                'accident': 0.05,
                'hazard': 0.04
            }

@dataclass
class FileConfig:
    """File path configuration."""
    
    KB_PATH: str = "Seed_interventions__InterveneR.csv"
    OUTPUT_DIR: str = "output"
    PDF_FILENAME: str = "InterveneR_Report.pdf"
    PPTX_FILENAME: str = "InterveneR_Presentation.pptx"
    JSON_FILENAME: str = "InterveneR_Output.json"
    
    def __post_init__(self):
        """Ensure output directory exists."""
        os.makedirs(self.OUTPUT_DIR, exist_ok=True)

@dataclass
class UIConfig:
    """Streamlit UI configuration."""
    
    PAGE_TITLE: str = "InterveneR - Road Safety Intervention GPT"
    PAGE_ICON: str = "ðŸ›£ï¸"
    LAYOUT: str = "wide"
    SIDEBAR_STATE: str = "expanded"
    
    # Color scheme
    PRIMARY_COLOR: str = "#1f4788"
    SECONDARY_COLOR: str = "#2e5f8a"
    ACCENT_COLOR: str = "#667eea"

@dataclass
class APIConfig:
    """FastAPI configuration."""
    
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = True
    LOG_LEVEL: str = "info"

class Settings:
    """Central settings class."""
    
    def __init__(self):
        self.scoring = ScoringConfig()
        self.files = FileConfig()
        self.ui = UIConfig()
        self.api = APIConfig()

# Global settings instance
settings = Settings()