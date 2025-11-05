# main.py
# Main Application - Streamlit UI for RoadWiseAI

import streamlit as st
import json
from pathlib import Path
from intervener_kb import InterventionKB
from intervener_retrieval import RetrievalEngine
from intervener_explainer import ExplanationLayer
from intervener_reporter import ReportGenerator

# Page configuration
st.set_page_config(
    page_title="RoadWiseAI - Road Safety Intervention GPT",
    page_icon="🛣️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .info-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        border-left: 4px solid #007bff;
    }
    .metric-card {
        background-color: #e9ecef;
        padding: 0.8rem;
        border-radius: 0.3rem;
        text-align: center;
        margin: 0.2rem;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
@st.cache_resource
def load_kb():
    """Load knowledge base from Excel."""
    kb_path = Path("GPT_Input_DB.xlsx")
    if not kb_path.exists():
        st.error(f"Excel database file not found: {kb_path}")
        st.info("Please ensure GPT_Input_DB.xlsx is in the project directory.")
        st.stop()
    return InterventionKB(str(kb_path))

@st.cache_resource
def initialize_modules():
    """Initialize system modules."""
    kb = load_kb()
    retrieval_engine = RetrievalEngine(kb)
    explainer = ExplanationLayer()
    reporter = ReportGenerator()
    return kb, retrieval_engine, explainer, reporter

# Load modules
try:
    kb, retrieval_engine, explainer, reporter = initialize_modules()
    st.success(f"✅ Loaded {len(kb.get_all())} interventions from Excel database")
except Exception as e:
    st.error(f"❌ Error loading database: {e}")
    st.stop()

# Sidebar
st.sidebar.title("🛣️ RoadWiseAI")
st.sidebar.markdown("**Road Safety Intervention GPT**")
st.sidebar.markdown("*AI-Powered Road Safety Solutions*")
st.sidebar.markdown("---")

st.sidebar.info(
    """
    **How it works:**
    1. Describe your road safety issue
    2. Specify road type & environment (optional)
    3. Get IRC-aligned recommendations
    4. Export as PDF or PowerPoint
    """
)

st.sidebar.markdown("---")
st.sidebar.subheader("Database Info")
st.sidebar.write(f"📊 **Interventions:** {len(kb.get_all())}")
st.sidebar.write(f"📁 **Source:** GPT_Input_DB.xlsx")
st.sidebar.write(f"🔧 **Version:** 2.0")

# Main interface
st.title("🛣️ RoadWiseAI")
st.markdown("### AI-Powered Road Safety Intervention System")
st.markdown("*Your intelligent partner for road safety solutions*")
st.markdown("---")

# Input section
st.subheader("🔍 Describe Your Road Safety Issue")

col1, col2 = st.columns(2)

with col1:
    issue_description = st.text_area(
        "Issue Description",
        placeholder="e.g., 'Frequent accidents at sharp curve, poor visibility at night, missing warning signs'",
        height=120,
        help="Describe the road safety problem in detail"
    )

with col2:
    road_type = st.selectbox(
        "Road Type",
        options=["", "Urban", "Highway", "Rural", "Arterial", "Local"],
        format_func=lambda x: "Select (Optional)" if x == "" else x,
        help="Select the applicable road context"
    )
    
    environment = st.text_input(
        "Environment/Context",
        placeholder="e.g., school zone, intersection, curve, bridge",
        help="Additional environmental context (optional)"
    )

# Process button
if st.button("🔍 Get AI Recommendations", type="primary", use_container_width=True):
    
    if not issue_description.strip():
        st.error("Please describe a road safety issue.")
    else:
        with st.spinner("🤖 Analyzing issue and retrieving recommendations..."):
            # Retrieve and rank
            scored_interventions = retrieval_engine.retrieve_and_rank(
                query=issue_description,
                road_type=road_type if road_type else None,
                environment=environment if environment else None,
                top_k=5
            )
            
            # Check threshold
            if not retrieval_engine.check_minimum_threshold(scored_interventions):
                st.warning("⚠️ No sufficient matches found in knowledge base.")
                st.info("Try adjusting your description or being more specific about the safety issue.")
            else:
                # Format recommendations
                recommendations = [
                    explainer.format_recommendation(interv, score)
                    for interv, score in scored_interventions
                ]
                
                # Display recommendations
                st.success(f"✅ Found {len(recommendations)} relevant interventions!")
                st.markdown("---")
                
                st.subheader("📋 AI-Recommended Interventions")
                
                for idx, rec in enumerate(recommendations, 1):
                    with st.container():
                        # Header
                        st.markdown(f"### 🔧 Recommendation #{idx}")
                        st.markdown(f"**{rec['intervention'][:100]}...**" if len(rec['intervention']) > 100 else f"**{rec['intervention']}**")
                        
                        # Create columns for organized information
                        col_left, col_right = st.columns([2, 1])
                        
                        with col_left:
                            st.markdown(f"**📋 Reference:** {rec['reference']}")
                            st.markdown(f"**💡 Rationale:** {rec['rationale']}")
                            st.markdown(f"**📝 Assumptions:** {rec['assumptions']}")
                        
                        with col_right:
                            st.markdown(f"**🎯 Confidence:** {rec['confidence']}")
                            st.markdown(f"**📊 Relevance:** {rec['relevance_score']}%")
                            st.markdown(f"**⚡ Priority:** {rec['priority']}")
                            if 'cost_estimate' in rec:
                                st.markdown(f"**💰 Cost:** {rec['cost_estimate']}")
                            if 'implementation_time' in rec:
                                st.markdown(f"**⏱️ Timeline:** {rec['implementation_time']}")
                        
                        st.markdown("---")

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #666; font-size: 12px;'>
    <p><strong>RoadWiseAI v2.0</strong> | AI Road Safety Intervention System</p>
    <p>🤖 Powered by Advanced AI | 📊 Excel Database Integration</p>
    <p>📚 References: IRC 35, IRC 67, IRC 99, IRC SP:84, IRC SP:87</p>
    <p>⚠️ Cost estimates exclude labor, transport, and taxes</p>
    </div>
    """, unsafe_allow_html=True)

# About section
with st.sidebar:
    st.markdown("---")
    with st.expander("ℹ️ About RoadWiseAI"):
        st.markdown("""
        **🚀 Features:**
        - Natural language processing
        - Excel database integration
        - Fuzzy + semantic matching
        - IRC-aligned recommendations
        - Explainable AI outputs
        - Cost & timeline estimates
        
        **🎯 Mission:**
        Making road safety interventions accessible through AI-powered recommendations based on official IRC standards.
        
        **🏆 Built for:** National Road Safety Hackathon 2025
        """)
