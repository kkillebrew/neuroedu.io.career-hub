"""
=============================================================================
MODULE: pages/2_mentorship_app.py
AUTHOR: Kyle W. Killebrew, PhD
VERSION: 1.0 (Spoke App)
DESCRIPTION: 
    The Educational Mentorship & Tutoring sub-page for career-hub.neuro-edu.io.
    Utilizes the 1-to-1 mentorship_loader.py.
=============================================================================
"""
import streamlit as st
import os
import sys
import numpy as np

# --- PATH CONFIGURATION ---
# This tells the script to look one folder up to find the 'loaders' directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# --- IMPORT DATA ---
from loaders.mentorship_loader import get_mentorship_data

from career_hub_loader import (
    get_biographic_metadata,
    get_portfolio_metadata
)

from career_hub_sidebar import apply_global_settings, render_sidebar

########################################
#        APPLY GLOBAL SETTINGS         #
########################################
apply_global_settings("Kyle W. Killebrew, PhD | Tutoring and Career Mentorship")

########################################
#  RENDER THE SIDEBAR FOR CAREER-HUB   #
########################################
# Point Python to the root directory so it can find the sidebar file
render_sidebar()

# Initialize the data from the loader
bio = get_biographic_metadata()
_, _, academic = get_portfolio_metadata()

mentorship = get_mentorship_data()

# =============================================================================
# SECTION 1: EDUCATIONAL DESIGN & PHILOSOPHY (Interactive Visual Lessons)
# =============================================================================
st.header("1. Educational Design & Philosophy")
st.write("""
My methodology relies on **cognitive grounding**—showing students how mathematical rules are generated 
conceptually, rather than demanding blind memorization. This maximizes attention capture and structural encoding.
""")

# Create sub-tabs for the interactive child-level lessons
lesson_tab1, lesson_tab2 = st.tabs(["📐 Geometry: Area Generation", "🎲 Probability: Visualizing Chance"])

with lesson_tab1:
    st.subheader("How an Area Function is Born")
    st.write("We teach kids that a triangle's area is $\\frac{1}{2}b \\times h$ by physically derivation from a rectangle.")
    
    # Interactive sliders for dimensions
    # MATLAB Analogy: These act as real-time uisliders that trigger callback updates
    width = st.slider("Adjust Rectangle Width (Base)", min_value=2, max_value=20, value=10, step=1)
    height = st.slider("Adjust Rectangle Height (Height)", min_value=2, max_value=20, value=6, step=1)
    
    # Calculate Areas using standard scalars
    rect_area = width * height
    tri_area = 0.5 * rect_area
    
    # Render interactive visuals using Plotly Express (Exclusive stack preference)
    # This visual demonstrates the exact spatial division rule of shapes
    import plotly.graph_objects as go
    
    fig_geom = go.Figure()
    # Left Triangle half (Blue)
    fig_geom.add_trace(go.Scatter(x=[0, 0, width, 0], y=[0, height, 0, 0], fill="toself", fillcolor="rgba(56, 189, 248, 0.5)", line=dict(color="#38BDF8"), name="Triangle (Half)"))
    # Right complementary half (Muted Grey to complete the rectangle)
    fig_geom.add_trace(go.Scatter(x=[0, width, width, 0], y=[height, height, 0, height], fill="toself", fillcolor="rgba(148, 163, 184, 0.2)", line=dict(color="#94A3B8", dash="dash"), name="Complementary Space"))
    
    fig_geom.update_layout(
        title=f"Visual Proof: Rectangle Area ({rect_area}) vs. Triangle Area ({tri_area})",
        xaxis=dict(range=[-1, width + 1], showgrid=False, zeroline=False, visible=False),
        yaxis=dict(range=[-1, height + 1], showgrid=False, zeroline=False, visible=False),
        height=300, margin=dict(l=20, r=20, t=40, b=20), showlegend=False
    )
    st.plotly_chart(fig_geom, use_container_width=True, config={'scrollZoom': False, 'displayModeBar': False})
    st.caption("Notice how the base triangle naturally cuts the bounded coordinate plane exactly in half: $Area = \\frac{1}{2} \\times b \\times h$.")

with lesson_tab2:
    st.subheader("Visualizing Probability Space")
    st.write("Instead of tracking abstract formulas, children learn better by seeing outcomes populate a frequency plane.")
    
    # Simulating rolling dice or choosing chips
    num_samples = st.selectbox("Select Number of Empirical Trials to Run:", [10, 50, 200, 500])
    
    # Generate uniform synthetic sample points to ensure data consistency without class imbalances
    import numpy as np
    import pandas as pd
    import plotly.express as px
    
    np.random.seed(42)
    x_outcomes = np.random.randint(1, 7, size=num_samples)
    y_outcomes = np.random.randint(1, 7, size=num_samples)
    df_prob = pd.DataFrame({'Die 1': x_outcomes, 'Die 2': y_outcomes})
    df_prob['Sum'] = df_prob['Die 1'] + df_prob['Die 2']
    
    # Group results for distribution layout (MATLAB equivalent: groupsummary)
    df_dist = df_prob['Sum'].value_counts().reset_index().sort_values('Sum')
    
    fig_prob = px.bar(df_dist, x='Sum', y='count', labels={'count': 'Times Rolled', 'Sum': 'Sum of Two Dice'}, title=f"Empirical Frequency Distribution Across {num_samples} Matrix Points")
    fig_prob.update_traces(marker_color='#38BDF8')
    fig_prob.update_layout(height=300, margin=dict(l=20, r=20, t=40, b=20), displayModeBar=False)
    st.plotly_chart(fig_prob, use_container_width=True, config={'displayModeBar': False})

st.divider()

# =============================================================================
# SECTION 2: EDUCATION (Teaching Career History & MAP Performance Metrics)
# =============================================================================
st.header("2. Education & Professional History")
st.write("Tracking quantitative student development, baseline testing improvements, and certified instruction.")

# Define Plotly standard configuration to lock the UI per the Style Guide
PLOTLY_CONFIG = {'scrollZoom': False, 'displayModeBar': False, 'staticPlot': False}
# Get the absolute path to the root directory (career_hub) to reliably find the 'documents' folder
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

for job in mentorship['career_history']:
    with st.container():
        c_left, c_right = st.columns([1, 2], gap="medium")
        with c_left:
            st.markdown(f"#### **{job['school']}**")
            st.markdown(f"*{job['role']}*")
            st.caption(f"🗓️ {job['years']}")
            st.write(job['metrics'])
            
        with c_right:
            if job.get('file_path'):
                target_csv = os.path.join(root_dir, job['file_path'])
                
                if os.path.exists(target_csv):
                    # ---------------------------------------------------------
                    # PIPELINE A: 6TH GRADE MAPS DATA
                    # ---------------------------------------------------------
                    if job['dataset_type'] == 'maps':
                        # RAM-First: Explicitly load both scores and percentiles
                        cols_to_load = [
                            "Last Name", "First Name", 
                            "Fall '25", "Fall '25%", 
                            "Winter '25", "Winter '25%", 
                            "Spring '25", "Spring '25%"
                        ]
                        
                        try:
                            df_maps = pd.read_csv(target_csv, usecols=cols_to_load)
                            
                            # MATLAB Analogy: This is equivalent to 'stack' to convert 
                            # wide-format matrices into long-format for grouped Plotly grouping.
                            # We will isolate just the percentiles for the visual distribution.
                            df_melted = df_maps.melt(
                                id_vars=["Last Name", "First Name"], 
                                value_vars=["Fall '25%", "Winter '25%", "Spring '25%"],
                                var_name="Testing Term", 
                                value_name="Percentile"
                            )
                            
                            # Clean the string names for a cleaner x-axis
                            df_melted['Testing Term'] = df_melted['Testing Term'].str.replace("%", "")
                            
                            fig = px.box(
                                df_melted, x="Testing Term", y="Percentile", points="all",
                                title="Longitudinal MAP Percentile Growth",
                                color="Testing Term",
                                color_discrete_sequence=['#94A3B8', '#38BDF8', '#4ADE80'] # Slate to Blue to Green
                            )
                            fig.update_layout(
                                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                                margin=dict(l=10, r=10, t=40, b=10), height=300, showlegend=False,
                                yaxis=dict(title="National Percentile", gridcolor="rgba(148, 163, 184, 0.15)")
                            )
                            st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
                            
                        except Exception as e:
                            st.error(f"Error processing MAPs data: {e}")

                    # ---------------------------------------------------------
                    # PIPELINE B: 7TH GRADE ELA STANDARDS
                    # ---------------------------------------------------------
                    elif job['dataset_type'] == 'ela':
                        # Explicitly map the exact strings from your gradebook
                        myth_components = ['Sequence', 'Techniques', 'Transitions', 'Details', 'Conclusion']
                        core_standards = [
                            'Article Analysis - Citing Evidence (RI.7.1.)', 
                            'Article Analysis - Central Idea (RI.7.1)', 
                            'RI.7.5: Quiz (Text Structure)', 
                            'SLG #3', 
                            'RI.7.6 Transportation', 
                            'Unit Test: Percy Jackson'
                        ]
                        cols_to_load = ["Last Name", "First Name"] + core_standards + myth_components
                        
                        try:
                            df_ela = pd.read_csv(target_csv, usecols=cols_to_load)
                            
                            # Data Cleaning: Convert 'M' (Missing) to np.nan (MATLAB's NaN)
                            df_ela = df_ela.replace({'M': np.nan})
                            
                            # Ensure all assessment columns are floats to allow for mathematical averaging
                            assess_cols = core_standards + myth_components
                            df_ela[assess_cols] = df_ela[assess_cols].apply(pd.to_numeric, errors='coerce')
                            
                            # Calculate the composite "Create Your Own Myth" score
                            # skipna=True mimics 'omitnan' in MATLAB, ensuring an 'M' doesn't tank the average
                            df_ela['Create Your Own Myth'] = df_ela[myth_components].mean(axis=1, skipna=True)
                            
                            # Prepare data for plotting
                            plot_cols = core_standards + ['Create Your Own Myth']
                            df_plot = df_ela[["Last Name", "First Name"] + plot_cols].copy()
                            
                            df_melted_ela = df_plot.melt(
                                id_vars=["Last Name", "First Name"],
                                value_vars=plot_cols,
                                var_name="Standard / Assessment",
                                value_name="Score (0-4)"
                            )
                            
                            # Clean up long standard names for the x-axis visual
                            df_melted_ela['Standard / Assessment'] = df_melted_ela['Standard / Assessment'].apply(
                                lambda x: x[:15] + "..." if len(x) > 15 else x
                            )
                            
                            fig = px.box(
                                df_melted_ela, x="Standard / Assessment", y="Score (0-4)",
                                title="Standards-Based Assessment Distributions",
                                color_discrete_sequence=['#6366F1'] # Indigo Theme
                            )
                            fig.update_layout(
                                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                                margin=dict(l=10, r=10, t=40, b=10), height=300,
                                yaxis=dict(title="Score (0-4)", range=[-0.2, 4.2], gridcolor="rgba(148, 163, 184, 0.15)"),
                                xaxis=dict(title="")
                            )
                            st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)

                        except Exception as e:
                            st.error(f"Error processing ELA data: {e}")
                else:
                    st.warning(f"Data file not found at: `{target_csv}`")
            else:
                st.caption("ℹ️ No statistical data repository attached to this record.")
        
        st.markdown("<br>", unsafe_allow_html=True)

# Resume Access Block
st.markdown("### Credentials & Accreditations")
res_col1, res_col2 = st.columns(2)
with res_col1:
    t_cv = "documents/kyle_teaching_cv.pdf"
    if os.path.exists(t_cv):
         with open(t_cv, "rb") as f:
            st.download_button("📂 Download Teaching Portfolio Resume (PDF)", f.read(), "Killebrew_Teaching.pdf")
    else:
        st.button("📂 Teaching Resume File Staged Locally", disabled=True)

with res_col2:
    st.markdown("###### Standardized Learner Profiles")
    st.caption("Click to explore tracking indices for programming logic, mathematical intuition, and research replication frameworks.")

st.divider()

# =============================================================================
# SECTION 3: MENTORSHIP & TUTORING GATEWAYS
# =============================================================================
st.header("3. Direct Mentorship & Private Booking")
st.write("Looking for a structured academic track or a transition path out of legacy software tools? Secure a direct consulting window below.")

# Platform execution links dynamically loaded from the dictionary mapping
m_buttons = st.columns(len(mentorship['tutoring_platforms']))
for idx, (platform, url) in enumerate(mentorship['tutoring_platforms'].items()):
    with m_buttons[idx]:
        st.link_button(f"🌐 Schedule via {platform}", url, use_container_width=True)