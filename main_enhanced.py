# main_clean.py
# main_enhanced.py
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
st.sidebar.markdown("*Now powered by Excel Database*")
st.sidebar.markdown("---")

st.sidebar.info(
    """
    **Enhanced Features:**
    1. Excel database integration
    2. Comprehensive intervention data
    3. Cost estimates & timelines
    4. Implementation guidance
    5. Maintenance requirements
    """
)

st.sidebar.markdown("---")
st.sidebar.subheader("Database Info")
st.sidebar.write(f"📊 **Interventions:** {len(kb.get_all())}")
st.sidebar.write(f"📁 **Source:** GPT_Input_DB.xlsx")
st.sidebar.write(f"🔧 **Version:** 2.0")

# Main interface
st.title("🛣️ RoadWiseAI 2.0")
st.markdown("### AI Road Safety Intervention System")
st.markdown("*Enhanced with comprehensive Excel database*")
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
    
    priority_filter = st.selectbox(
        "Priority Filter",
        options=["", "High", "Medium", "Low"],
        format_func=lambda x: "All Priorities" if x == "" else x,
        help="Filter by intervention priority"
    )

# Process button
if st.button("🔍 Get AI Recommendations", type="primary", use_container_width=True):
    
    if not issue_description.strip():
        st.error("Please describe a road safety issue.")
    else:
        with st.spinner("🤖 Analyzing issue and retrieving recommendations from Excel database..."):
            # Retrieve and rank
            scored_interventions = retrieval_engine.retrieve_and_rank(
                query=issue_description,
                road_type=road_type if road_type else None,
                environment=environment if environment else None,
                top_k=5
            )
            
            # Filter by priority if specified
            if priority_filter:
                scored_interventions = [
                    (interv, score) for interv, score in scored_interventions
                    if interv.get('priority', '').lower() == priority_filter.lower()
                ]
            
            # Check threshold
            if not retrieval_engine.check_minimum_threshold(scored_interventions):
                st.warning("⚠️ No sufficient matches found in knowledge base.")
                st.info("Try adjusting your description or removing filters.")
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
                        st.markdown(f"**{rec['intervention']}**")
                        
                        # Create tabs for organized information
                        tab1, tab2, tab3, tab4 = st.tabs(["📋 Details", "💰 Implementation", "📊 Metrics", "🔗 Reference"])
                        
                        with tab1:
                            st.markdown(f"**Rationale:** {rec['rationale']}")
                            st.markdown(f"**Assumptions:** {rec['assumptions']}")
                        
                        with tab2:
                            col_cost, col_time = st.columns(2)
                            with col_cost:
                                st.markdown(f"**💰 Cost Estimate:**<br>{rec.get('cost_estimate', 'Variable cost')}", 
                                           unsafe_allow_html=True)
                            with col_time:
                                st.markdown(f"**⏱️ Implementation Time:**<br>{rec.get('implementation_time', 'Variable timeline')}", 
                                           unsafe_allow_html=True)
                            
                            st.markdown(f"**🔧 Maintenance:** {rec.get('maintenance', 'Standard maintenance required')}")
                        
                        with tab3:
                            col_metrics = st.columns(4)
                            with col_metrics[0]:
                                st.markdown(f"**Confidence**<br>{rec['confidence']}", unsafe_allow_html=True)
                            with col_metrics[1]:
                                st.markdown(f"**Relevance**<br>{rec['relevance_score']}%", unsafe_allow_html=True)
                            with col_metrics[2]:
                                st.markdown(f"**Priority**<br>{rec['priority']}", unsafe_allow_html=True)
                            with col_metrics[3]:
                                st.markdown(f"**Effectiveness**<br>{rec.get('effectiveness', 'High')}", unsafe_allow_html=True)
                        
                        with tab4:
                            st.markdown(f"**IRC Reference:** {rec['reference']}")
                            st.markdown(f"**Intervention ID:** #{rec['id']}")
                        
                        st.markdown("---")

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #666; font-size: 12px;'>
    <p><strong>RoadWiseAI v2.0</strong> | AI Road Safety Intervention System</p>
    <p>📊 Enhanced with Excel Database | 🤖 AI-Powered Recommendations</p>
    <p>📚 References: IRC 35, IRC 67, IRC 99, IRC SP:84, IRC SP:87</p>
    <p>⚠️ Cost estimates exclude labor, transport, and taxes</p>
    </div>
    """, unsafe_allow_html=True)

# About section
with st.sidebar:
    st.markdown("---")
    with st.expander("ℹ️ About RoadWiseAI 2.0"):
        st.markdown("""
        **🚀 What's New:**
        - Excel database integration
        - Enhanced data fields
        - Better cost estimates
        - Implementation timelines
        - Maintenance guidance
        
        **🔧 Features:**
        - Natural language processing
        - Fuzzy + semantic matching
        - IRC-aligned recommendations
        - Explainable AI outputs
        - Comprehensive reporting
        
        **🏆 Built for:** National Road Safety Hackathon 2025
        """)
