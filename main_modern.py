# main.py
# RoadWiseAI - Modern UI Design

import streamlit as st
import json
from pathlib import Path
from datetime import datetime
from intervener_kb import InterventionKB
from intervener_retrieval import RetrievalEngine
from intervener_explainer import ExplanationLayer
from intervener_reporter import ReportGenerator

# Page configuration
st.set_page_config(
    page_title="RoadWiseAI - Smart Road Safety Solutions",
    page_icon="🛣️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Modern CSS styling
st.markdown("""
<style>
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    .stDeployButton {display:none;}
    footer {visibility: hidden;}
    
    /* Custom fonts and colors */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .main {
        font-family: 'Inter', sans-serif;
        padding: 1rem 2rem;
    }
    
    /* Hero section */
    .hero {
        text-align: center;
        padding: 3rem 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        margin-bottom: 2rem;
        color: white;
    }
    
    .hero h1 {
        font-size: 3.5rem;
        font-weight: 700;
        margin-bottom: 1rem;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    
    .hero p {
        font-size: 1.2rem;
        opacity: 0.9;
        max-width: 600px;
        margin: 0 auto;
    }
    
    /* Input section */
    .input-section {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
        border: 1px solid #e0e7ff;
    }
    
    /* Results cards */
    .result-card {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        border-left: 4px solid #667eea;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .result-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 20px rgba(0,0,0,0.12);
    }
    
    .priority-high {
        border-left-color: #ef4444;
    }
    
    .priority-medium {
        border-left-color: #f59e0b;
    }
    
    .priority-low {
        border-left-color: #10b981;
    }
    
    /* Badges */
    .badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 50px;
        font-size: 0.85rem;
        font-weight: 500;
        margin: 0.25rem 0.25rem 0.25rem 0;
    }
    
    .badge-high {
        background: #fee2e2;
        color: #dc2626;
    }
    
    .badge-medium {
        background: #fef3c7;
        color: #d97706;
    }
    
    .badge-low {
        background: #d1fae5;
        color: #059669;
    }
    
    .badge-confidence {
        background: #ede9fe;
        color: #7c3aed;
    }
    
    /* Stats */
    .stat-card {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        margin: 0.5rem;
    }
    
    .stat-number {
        font-size: 2rem;
        font-weight: 700;
        color: #1e293b;
    }
    
    .stat-label {
        color: #64748b;
        font-size: 0.9rem;
        margin-top: 0.5rem;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6);
    }
    
    /* Text areas and inputs */
    .stTextArea > div > div > textarea {
        border-radius: 12px;
        border: 2px solid #e2e8f0;
        font-family: 'Inter', sans-serif;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    .stSelectbox > div > div {
        border-radius: 12px;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem;
        margin-top: 3rem;
        color: #64748b;
        border-top: 1px solid #e2e8f0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
@st.cache_resource
def load_system():
    """Load the complete RoadWiseAI system."""
    try:
        kb_path = Path("GPT_Input_DB.xlsx")
        if not kb_path.exists():
            st.error("📁 Database file not found. Please ensure GPT_Input_DB.xlsx is in the project directory.")
            st.stop()
        
        kb = InterventionKB(str(kb_path))
        retrieval_engine = RetrievalEngine(kb)
        explainer = ExplanationLayer()
        reporter = ReportGenerator()
        
        return kb, retrieval_engine, explainer, reporter
    except Exception as e:
        st.error(f"❌ System initialization failed: {e}")
        st.stop()

# Load system
kb, retrieval_engine, explainer, reporter = load_system()

# Initialize session state
if 'search_performed' not in st.session_state:
    st.session_state.search_performed = False
if 'recommendations' not in st.session_state:
    st.session_state.recommendations = []

# HERO SECTION
st.markdown("""
<div class="hero">
    <h1>🛣️ RoadWiseAI</h1>
    <p>Intelligent road safety solutions powered by AI. Get expert recommendations based on IRC standards in seconds.</p>
</div>
""", unsafe_allow_html=True)

# STATS ROW
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-number">{len(kb.get_all())}</div>
        <div class="stat-label">Safety Interventions</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="stat-card">
        <div class="stat-number">5+</div>
        <div class="stat-label">IRC Standards</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="stat-card">
        <div class="stat-number">AI</div>
        <div class="stat-label">Powered Matching</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="stat-card">
        <div class="stat-number">24/7</div>
        <div class="stat-label">Available</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# INPUT SECTION
st.markdown('<div class="input-section">', unsafe_allow_html=True)

st.markdown("### 🔍 Describe Your Road Safety Challenge")
st.markdown("*Tell us about the safety issue you're facing - be as specific as possible*")

# Two-column layout for inputs
col_left, col_right = st.columns([2, 1])

with col_left:
    issue_description = st.text_area(
        "Issue Description",
        placeholder="Example: 'Sharp curve with poor visibility at night, vehicles going off road, need immediate safety measures for NH-48 near Gurgaon'",
        height=120,
        key="issue_input",
        help="Describe the location, type of accidents, road conditions, and any specific concerns",
        label_visibility="collapsed"
    )

with col_right:
    st.markdown("**Additional Context** *(Optional)*")
    
    road_type = st.selectbox(
        "Road Type",
        options=["Any", "Urban", "Highway", "Rural", "Arterial", "Local"],
        key="road_type"
    )
    
    environment = st.selectbox(
        "Environment",
        options=["Any", "Intersection", "Curve", "Bridge", "School Zone", "Hospital Zone", "Industrial Area"],
        key="environment"
    )
    
    priority_level = st.selectbox(
        "Priority",
        options=["Any", "High", "Medium", "Low"],
        key="priority"
    )

# Search button
st.markdown("<br>", unsafe_allow_html=True)
search_col1, search_col2, search_col3 = st.columns([1, 1, 1])

with search_col2:
    if st.button("🚀 Get AI Recommendations", key="search_btn", use_container_width=True):
        if not issue_description.strip():
            st.error("⚠️ Please describe your road safety challenge first!")
        else:
            with st.spinner("🤖 AI is analyzing your challenge and finding solutions..."):
                # Process the search
                road_filter = None if road_type == "Any" else road_type
                env_filter = None if environment == "Any" else environment
                
                scored_interventions = retrieval_engine.retrieve_and_rank(
                    query=issue_description,
                    road_type=road_filter,
                    environment=env_filter,
                    top_k=6
                )
                
                if priority_level != "Any":
                    scored_interventions = [
                        (interv, score) for interv, score in scored_interventions
                        if interv.get('priority', '').lower() == priority_level.lower()
                    ]
                
                if not retrieval_engine.check_minimum_threshold(scored_interventions):
                    st.warning("🔍 No close matches found. Try rephrasing your description or removing filters.")
                else:
                    recommendations = [
                        explainer.format_recommendation(interv, score)
                        for interv, score in scored_interventions
                    ]
                    
                    st.session_state.recommendations = recommendations
                    st.session_state.search_performed = True
                    st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# RESULTS SECTION
if st.session_state.search_performed and st.session_state.recommendations:
    st.markdown("### 🎯 AI-Recommended Solutions")
    st.markdown(f"*Found {len(st.session_state.recommendations)} relevant interventions for your challenge*")
    
    for idx, rec in enumerate(st.session_state.recommendations, 1):
        priority_class = f"priority-{rec['priority'].lower()}"
        
        st.markdown(f"""
        <div class="result-card {priority_class}">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                <h4 style="margin: 0; color: #1e293b;">#{idx} {rec['intervention'][:80]}{'...' if len(rec['intervention']) > 80 else ''}</h4>
                <div>
                    <span class="badge badge-{rec['priority'].lower()}">{rec['priority']} Priority</span>
                    <span class="badge badge-confidence">{rec['confidence']}</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Create expandable details
        with st.expander("📋 View Full Details", expanded=False):
            detail_col1, detail_col2 = st.columns([2, 1])
            
            with detail_col1:
                st.markdown(f"**📖 Complete Solution:**")
                st.write(rec['intervention'])
                
                st.markdown(f"**💡 Why This Works:**")
                st.write(rec['rationale'])
                
                st.markdown(f"**📋 Reference:** {rec['reference']}")
                
            with detail_col2:
                st.markdown("**📊 Details:**")
                st.write(f"🎯 **Relevance:** {rec['relevance_score']}%")
                st.write(f"⏱️ **Timeline:** {rec.get('implementation_time', 'Variable')}")
                st.write(f"💰 **Cost:** {rec.get('cost_estimate', 'Variable')}")
                st.write(f"🔧 **Maintenance:** {rec.get('maintenance', 'Standard')}")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Export options
    st.markdown("### 📄 Export Your Results")
    export_col1, export_col2, export_col3 = st.columns(3)
    
    with export_col1:
        if st.button("📄 Download PDF Report", use_container_width=True):
            st.info("PDF generation feature coming soon!")
    
    with export_col2:
        if st.button("📊 Download PowerPoint", use_container_width=True):
            st.info("PowerPoint generation feature coming soon!")
    
    with export_col3:
        json_data = {
            "query": issue_description,
            "recommendations": st.session_state.recommendations,
            "timestamp": datetime.now().isoformat()
        }
        st.download_button(
            "💾 Download JSON Data",
            data=json.dumps(json_data, indent=2),
            file_name="roadwise_recommendations.json",
            mime="application/json",
            use_container_width=True
        )

# FOOTER
st.markdown("""
<div class="footer">
    <p><strong>RoadWiseAI v2.0</strong> | Intelligent Road Safety Solutions</p>
    <p>🏆 Built for National Road Safety Hackathon 2025 | 📚 Based on IRC Standards</p>
    <p>⚠️ Recommendations are advisory. Please consult experts for implementation.</p>
</div>
""", unsafe_allow_html=True)
