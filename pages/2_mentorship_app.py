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

# --- IMPORT DATA & COMPONENTS ---
from loaders.mentorship_loader import get_mentorship_data
from career_hub_loader import get_biographic_metadata, get_portfolio_metadata
from career_hub_sidebar import apply_global_settings, render_sidebar

# This import now works because the circular reference is broken in the component file
from pages.components.geometry_demo import render_geometry_area_demo
from pages.components.probability_demo import render_probability_demo  # <-- NEW: Import Galton Board
from pages.components.pythagorean_demo import render_pythagorean_demo

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

# --- CRITICAL FIX: LAZY LOADING ROUTER ---
# Replaces st.tabs() with a conditional radio to prevent background canvas execution
active_lesson = st.radio(
    "Select Interactive Lesson Demo to Load:",
    [
        "📐 Lesson 1: Geometry & Area Generation", 
        "🎲 Lesson 2: Probability & Chance Space",
        "📐 Lesson 3: Pythagorean Theorem Matrix" # <-- NEW Spoke Entry
    ],
    horizontal=True,
    label_visibility="collapsed"
)

# --- LESSON 1: GEOMETRY ---
if "Geometry" in active_lesson:
    st.subheader("How an Area Function is Born")
    st.write("We teach kids that a triangle's area is derived directly by dissecting a bounded coordinate plane.")
    
    # Construct the 3-column layout requested (Animation & Formula | Gap | Inputs)
    anim_col, gap_col, input_col = st.columns([3, 0.2, 1])
    
    with input_col:
        st.markdown("<br><br>", unsafe_allow_html=True) # Vertical spacer
        st.info("💡 **Adjust Dimensions**\n\nWatch how the space transforms in real-time.")
        
        # Sliders represent dimensions bounded safely between 2 and 10
        b_units = st.slider("Base (b) Units", min_value=2, max_value=6, value=3, step=1)
        h_units = st.slider("Height (h) Units", min_value=2, max_value=6, value=4, step=1)
        
        st.caption(f"**Total Area (Rect):** {b_units * h_units} units²\n\n**Total Area (Tri):** {(b_units * h_units)/2} units²")
        
    with anim_col:
        # Inject the hardware-accelerated HTML5/JS animation loop
        render_geometry_area_demo(base_units=b_units, height_units=h_units)

# --- LESSON 2: PROBABILITY ---
elif "Probability" in active_lesson:
    st.subheader("Visualizing Probability Space")
    st.write("Instead of tracking abstract formulas, children learn better by seeing outcomes populate a frequency plane.")
    
    # 1. Parameter Input
    num_samples = st.selectbox("Select Number of Empirical Trials to Run:", [50, 100, 250, 500, 750, 1000])
    
    # 2. Render the Matter.js Physics Component
    # We no longer process Pandas/NumPy arrays here. We pass the parameter directly 
    # to the browser to handle the Plinko state machine.
    st.info("💡 **Watch the Distribution Form**\n\nNotice how the random binary choices at each peg naturally assemble into a Gaussian distribution.")
    render_probability_demo(sample_count=num_samples)

# 3. Handle the dynamic input control matrix and render the Canvas view
# =============================================================================
# SPOKE LAYER ROUTING CONTROL MATRIX: LESSON 3 - PYTHAGOREAN THEOREM MATRIX
# =============================================================================
elif "Pythagorean" in active_lesson:
    st.subheader("Geometric Visualization of $A^2 + B^2 = C^2$")
    
    # Establish a clean layout split for variables vs execution canvas
    anim_col, gap_col, input_col = st.columns([3, 0.2, 1])
    
    with input_col:
        st.info("💡 **Triangle Vectors**\n\nEnter the boundaries below to see the square structures transform.")
        input_mode = st.selectbox("Define Dimensions By:", ["Side Lengths", "Internal Angles"])
        
        if input_mode == "Side Lengths":
            # Bounded between 3 and 8 to prevent physics viewport out-of-bounds clipping
            side_a = st.slider("Base Dimension (Side A)", min_value=3, max_value=8, value=4, step=1)
            side_b = st.slider("Height Dimension (Side B)", min_value=3, max_value=8, value=3, step=1)
        else:
            # Mathematical fallback conversion logic for dynamic angle mapping
            angle_theta = st.slider("Internal Angle (Θ°)", min_value=15, max_value=75, value=36, step=1)
            
            # Extrapolate relative sides using trigonometry scale transformations
            # Locking the hypotenuse to a stable scale value keeps the simulation frames bounded
            hypotenuse_reference = 6.5
            side_a = hypotenuse_reference * np.cos(np.radians(angle_theta))
            side_b = hypotenuse_reference * np.sin(np.radians(angle_theta))
            
        # Display instant mathematical feedback inside the control container sidebar
        area_a = side_a ** 2
        area_b = side_b ** 2
        area_c = area_a + area_b
        st.markdown(f"""
        <div style="background-color: rgba(30, 41, 59, 0.5); padding: 12px; border-radius: 6px; border-left: 3px solid #10B981;">
            <p style="margin:0; font-size:0.85rem; color:#94A3B8;"><b>Area Verification Layer:</b></p>
            <p style="margin:4px 0 0 0; font-family:monospace; font-size:0.9rem;">
                A² ({area_a:.1f}) + B² ({area_b:.1f})<br>
                <b>= C² ({area_c:.1f})</b>
            </p>
        </div>
        """, unsafe_allow_html=True)
            
    with anim_col:
        # Launch browser GPU-accelerated Matter.js simulation frame
        # Routing the slider arguments directly into the synchronized view component parameters
        render_pythagorean_demo(a_units=side_a, b_units=side_b)

st.divider()

# =============================================================================
# SECTION 2: EDUCATION (Teaching Career History & Performance Analytics)
# =============================================================================
st.header("2. Education & Professional History")
st.write("Tracking quantitative student development, milestone testing metrics, and higher-education instruction.")

# Define Plotly standard configuration to lock the UI per the Style Guide
PLOTLY_CONFIG = {'scrollZoom': False, 'displayModeBar': False, 'staticPlot': False}

# --- THE ABSOLUTE REPOSITORY PATH ANCHOR ---
# __file__ evaluates to the absolute path of this file (.../pages/2_mentorship_app.py).
# Stepping up two folder layers targets the repository base path (.../neuroedu.io.career-hub.git/).
# MATLAB Analogy: Equivalent to fileparts(fileparts(mfilename('fullpath')))
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

for job in mentorship['career_history']:
    with st.container():
        # Decouple text logs from the data visualizations using a clean 1:2 column layout
        c_left, c_right = st.columns([1, 2], gap="medium")
        with c_left:
            st.markdown(f"#### **{job['school']}**")
            st.markdown(f"*{job['role']}*")
            st.caption(f"🗓️ {job['years']}")
            st.write(job['metrics'])
            
        with c_right:
            if job.get('file_path'):
                # --- THE ABSOLUTE PATH ASSEMBLY ---
                # We combine the immutable repo_root anchor with the sub-path from the loader.
                target_csv = os.path.join(repo_root, job['file_path'])
                
                if os.path.exists(target_csv):
                    # ---------------------------------------------------------
                    # DATA PIPELINE TYPE 1: LONGITUDINAL MAPS PERCENTILES
                    # ---------------------------------------------------------
                    if job['dataset_type'] == 'maps':
                        cols_to_load = ["Last Name", "First Name", "Fall '25%", "Winter '25%", "Spring '25%"]
                        try:
                            df_maps = pd.read_csv(target_csv, usecols=cols_to_load)
                            
                            df_melted = df_maps.melt(
                                id_vars=["Last Name", "First Name"], 
                                value_vars=["Fall '25%", "Winter '25%", "Spring '25%"],
                                var_name="Testing Term", 
                                value_name="Percentile"
                            )
                            df_melted['Testing Term'] = df_melted['Testing Term'].str.replace("%", "")
                            
                            fig = px.box(
                                df_melted, x="Testing Term", y="Percentile", points="all",
                                title="Longitudinal MAP Percentile Distributions",
                                color="Testing Term",
                                color_discrete_sequence=['#94A3B8', '#38BDF8', '#4ADE80']
                            )
                            fig.update_layout(
                                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                                margin=dict(l=10, r=10, t=40, b=10), height=280, showlegend=False,
                                yaxis=dict(title="National Percentile Scale", gridcolor="rgba(148, 163, 184, 0.12)")
                            )
                            st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
                        except Exception as e:
                            st.error(f"Error executing MAPs data parse: {e}")

                    # ---------------------------------------------------------
                    # DATA PIPELINE TYPE 2: STANDARDS-BASED ELA METRICS
                    # ---------------------------------------------------------
                    elif job['dataset_type'] == 'ela':
                        myth_components = ['Sequence', 'Techniques', 'Transitions', 'Details', 'Conclusion']
                        core_standards = [
                            'Article Analysis - Citing Evidence (RI.7.1.)', 
                            'Article Analysis - Central Idea (RI.7.1)', 
                            'RI.7.5: Quiz (Text Structure)', 'SLG #3', 
                            'RI.7.6 Transportation', 'Unit Test: Percy Jackson'
                        ]
                        cols_to_load = ["Last Name", "First Name"] + core_standards + myth_components
                        
                        try:
                            df_ela = pd.read_csv(target_csv, usecols=cols_to_load)
                            df_ela = df_ela.replace({'M': np.nan})
                            assess_cols = core_standards + myth_components
                            df_ela[assess_cols] = df_ela[assess_cols].apply(pd.to_numeric, errors='coerce')
                            
                            df_ela['Create Your Own Myth'] = df_ela[myth_components].mean(axis=1, skipna=True)
                            
                            plot_cols = core_standards + ['Create Your Own Myth']
                            df_plot = df_ela[["Last Name", "First Name"] + plot_cols].copy()
                            
                            df_melted_ela = df_plot.melt(
                                id_vars=["Last Name", "First Name"], value_vars=plot_cols,
                                var_name="Standard / Assessment", value_name="Score (0-4)"
                            )
                            df_melted_ela['Standard / Assessment'] = df_melted_ela['Standard / Assessment'].apply(
                                lambda x: x[:15] + "..." if len(x) > 15 else x
                            )
                            
                            fig = px.box(
                                df_melted_ela, x="Standard / Assessment", y="Score (0-4)",
                                title="Standards Mastery Distributions (0-4 Scale)", color_discrete_sequence=['#6366F1']
                            )
                            fig.update_layout(
                                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                                margin=dict(l=10, r=10, t=40, b=10), height=280,
                                yaxis=dict(title="Proficiency Score", range=[-0.2, 4.2], gridcolor="rgba(148, 163, 184, 0.12)"),
                                xaxis=dict(title="")
                            )
                            st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
                        except Exception as e:
                            st.error(f"Error executing ELA standards parse: {e}")
                else:
                    st.warning(f"File target missing during absolute container lookup. Looked for: `{target_csv}`")

            # ---------------------------------------------------------
            # DATA PIPELINE TYPE 3: UNIVERSITY COURSE MATRIX DISPLAY
            # ---------------------------------------------------------
            elif job.get('dataset_type') == 'university':
                st.markdown("###### 🎓 Lectured Undergraduate Curricula:")
                for course in job.get('courses_taught', []):
                    st.markdown(f"`{course}`")
            
            else:
                st.caption("ℹ️ No statistical data repository attached to this record.")
        
        st.markdown("<br>", unsafe_allow_html=True)

# Resume Access Block
st.markdown("### Credentials & Accreditations")
res_col1, res_col2 = st.columns(2)
with res_col1:
    # Anchor the PDF retrieval securely to the root level documents folder
    t_cv = os.path.join(repo_root, "documents/kyle_teaching_cv.pdf")
    if os.path.exists(t_cv):
         with open(t_cv, "rb") as f:
            st.download_button("📂 Download Teaching Portfolio Resume (PDF)", f.read(), "kyle_teaching_cv.pdf")
    else:
        # High contrast fallback displays the exact path being queried on the container
        st.button("📂 Teaching Resume Staged on Server", disabled=True)
        st.caption(f"Debug Target: `{t_cv}`")

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