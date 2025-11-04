# main.py
# Main Application - Streamlit UI for InterveneR

import streamlit as st
import json
from pathlib import Path
from intervener_kb import InterventionKB
from intervener_retrieval import RetrievalEngine
from intervener_explainer import ExplanationLayer
from intervener_reporter import ReportGenerator

# Page configuration
st.set_page_config(
    page_title="InterveneR - Road Safety Intervention GPT",
    page_icon="ðŸ›£ï¸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
    }
    .recommendation-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
@st.cache_resource
def load_kb():
    """Load knowledge base."""
    kb_path = Path("Seed_interventions__InterveneR.csv")
    if not kb_path.exists():
        st.error(f"Knowledge base file not found: {kb_path}")
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
kb, retrieval_engine, explainer, reporter = initialize_modules()

# Sidebar
st.sidebar.title("ðŸ›£ï¸ InterveneR")
st.sidebar.markdown("**Road Safety Intervention GPT**")
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
st.sidebar.subheader("System Info")
st.sidebar.metric("Interventions in KB", len(kb.get_all()))
st.sidebar.metric("System Version", "1.0")

# Main interface
st.title("ðŸ›£ï¸ InterveneR")
st.markdown("### Intelligent Road Safety Intervention Recommendation System")
st.markdown("---")

# Input section
st.subheader("ðŸ“ Describe Your Road Safety Issue")

col1, col2 = st.columns(2)

with col1:
    issue_description = st.text_area(
        "Issue Description",
        placeholder="e.g., 'Accidents at blind curve, missing chevron signs, poor lighting'",
        height=100,
        label_visibility="collapsed"
    )

with col2:
    road_type = st.selectbox(
        "Road Type",
        options=["", "Urban", "Highway", "Rural"],
        format_func=lambda x: "Select (Optional)" if x == "" else x,
        help="Select the applicable road context"
    )
    
    environment = st.text_input(
        "Environment/Context",
        placeholder="e.g., school zone, intersection, curve",
        help="Additional environmental context (optional)"
    )

# Process button
if st.button("ðŸ” Get Recommendations", type="primary", use_container_width=True):
    
    if not issue_description.strip():
        st.error("Please describe a road safety issue.")
    else:
        with st.spinner("Analyzing issue and retrieving recommendations..."):
            # Retrieve and rank
            scored_interventions = retrieval_engine.retrieve_and_rank(
                query=issue_description,
                road_type=road_type if road_type else None,
                environment=environment if environment else None,
                top_k=3
            )
            
            # Check threshold
            if not retrieval_engine.check_minimum_threshold(scored_interventions):
                st.warning("âš ï¸ No sufficient match found in knowledge base.")
                fallback = explainer.generate_fallback_response(issue_description)
                st.info(fallback['message'])
                st.markdown("**Suggestions:**")
                for sugg in fallback['suggestions']:
                    st.markdown(f"- {sugg}")
            else:
                # Format recommendations
                recommendations = [
                    explainer.format_recommendation(interv, score)
                    for interv, score in scored_interventions
                ]
                
                # Display recommendations
                st.success("âœ… Recommendations retrieved successfully!")
                st.markdown("---")
                
                st.subheader("ðŸ“‹ Recommended Interventions")
                
                for idx, rec in enumerate(recommendations, 1):
                    with st.container():
                        col_idx, col_content = st.columns([0.1, 0.9])
                        
                        with col_idx:
                            st.markdown(f"### {idx}")
                        
                        with col_content:
                            with st.expander(f"**{rec['intervention'][:70]}...**", expanded=(idx==1)):
                                st.markdown(f"**Reference:** {rec['reference']}")
                                st.markdown(f"**Rationale:** {rec['rationale']}")
                                st.markdown(f"**Assumptions:** {rec['assumptions']}")
                                
                                col_conf, col_pri = st.columns(2)
                                with col_conf:
                                    st.metric("Confidence", f"{rec['confidence']} ({rec['relevance_score']}%)")
                                with col_pri:
                                    st.metric("Priority", rec['priority'])
                
                st.markdown("---")
                
                # Export options
                st.subheader("ðŸ“¥ Export Options")
                col_pdf, col_pptx, col_json = st.columns(3)
                
                with col_pdf:
                    if st.button("ðŸ“„ Download PDF Report", use_container_width=True):
                        try:
                            pdf_path = "InterveneR_Report.pdf"
                            reporter.generate_pdf_report(
                                recommendations,
                                issue_description,
                                road_type if road_type else None,
                                environment if environment else None,
                                pdf_path
                            )
                            
                            with open(pdf_path, "rb") as pdf_file:
                                st.download_button(
                                    label="âœ… PDF Ready to Download",
                                    data=pdf_file,
                                    file_name=pdf_path,
                                    mime="application/pdf"
                                )
                        except Exception as e:
                            st.error(f"Error generating PDF: {e}")
                
                with col_pptx:
                    if st.button("ðŸŽ¯ Download PowerPoint Deck", use_container_width=True):
                        try:
                            pptx_path = "InterveneR_Presentation.pptx"
                            reporter.generate_pptx_report(
                                recommendations,
                                issue_description,
                                road_type if road_type else None,
                                environment if environment else None,
                                pptx_path
                            )
                            
                            with open(pptx_path, "rb") as pptx_file:
                                st.download_button(
                                    label="âœ… PPTX Ready to Download",
                                    data=pptx_file,
                                    file_name=pptx_path,
                                    mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
                                )
                        except Exception as e:
                            st.error(f"Error generating PowerPoint: {e}")
                
                with col_json:
                    if st.button("ðŸ“Š Download JSON Data", use_container_width=True):
                        try:
                            json_output = explainer.generate_json_output(
                                recommendations,
                                issue_description,
                                road_type if road_type else None,
                                environment if environment else None
                            )
                            json_str = json.dumps(json_output, indent=2)
                            st.download_button(
                                label="âœ… JSON Ready to Download",
                                data=json_str,
                                file_name="InterveneR_Output.json",
                                mime="application/json"
                            )
                        except Exception as e:
                            st.error(f"Error generating JSON: {e}")
                
                st.markdown("---")
                
                # Full report text
                with st.expander("ðŸ“„ View Full Text Report"):
                    report_text = explainer.generate_report_text(
                        recommendations,
                        issue_description,
                        road_type if road_type else None,
                        environment if environment else None
                    )
                    st.code(report_text, language="text")

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #888; font-size: 12px;'>
    <p>InterveneR v1.0 | Road Safety Intervention GPT</p>
    <p>All recommendations are material-only estimates. Labor, transport, and taxes are excluded.</p>
    <p>References: IRC 35, IRC 67, IRC 99, IRC SP:84, IRC SP:87</p>
    </div>
    """, unsafe_allow_html=True)

# About section
with st.sidebar:
    st.markdown("---")
    with st.expander("â„¹ï¸ About InterveneR"):
        st.markdown("""
        **InterveneR** is an AI-powered tool that recommends road safety interventions based on identified issues, referencing official IRC standards and best practices.
        
        **Features:**
        - Natural language issue input
        - Fuzzy + semantic matching
        - IRC-aligned recommendations
        - Explainable outputs (references, rationale, assumptions)
        - Auto-generated reports (PDF, PPTX, JSON)
        
        **Built for:** National Road Safety Hackathon 2025
        **Developed by:** Your Team Name
        """)