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
import pandas as pd          # Restored for Section 2 Data Pipelines
import plotly.express as px  # Restored for Section 2 Data Pipelines
import uuid
import requests
import json

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
from pages.components.fittslaw_demo import render_fittslaw_demo
from loaders.fittslaw_loader import process_cohort_fitts_regression
from pages.components.visual_search_demo import render_visual_search_demo
from loaders.visual_search_loader import process_visual_search_analytics

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

# Define Plotly standard configuration to lock the UI globally
PLOTLY_CONFIG = {'scrollZoom': False, 'displayModeBar': False, 'staticPlot': False}

# =============================================================================
# SECTION 1: EDUCATIONAL DESIGN & PHILOSOPHY (Interactive Visual Lessons)
# =============================================================================
st.header("1. Educational Design & Philosophy")
st.write("""
My methodology relies on **cognitive grounding**—showing students how mathematical rules are generated 
conceptually, rather than demanding blind memorization. This maximizes attention capture and structural encoding.
""")

# --- CENTRALIZED FIREBASE CREDENTIAL MATRIX ---
firebase_config_dict = {
    "apiKey": "AIzaSyAkchjI1WCkFd7gVZCQB1Jyn23TslP58b0",
    "authDomain": "neuroedu-career-hub.firebaseapp.com",
    "projectId": "neuroedu-career-hub",
    "storageBucket": "neuroedu-career-hub.appspot.com",
    "messagingSenderId": "1068398164186",
    "appId": "1:1068398164186:web:093262de26300585618de3"
}

firebase_config_str = json.dumps(firebase_config_dict)
project_id = firebase_config_dict["projectId"]

# This globally defines the database collection target for all spokes
app_id = "neuroedu-career-hub"

# --- NEW: GLOBAL SESSION IDENTITY ---
# This ensures they remain the exact same user across all experiments today
if 'hub_user_id' not in st.session_state:
    st.session_state.hub_user_id = f"anon_{uuid.uuid4().hex[:8]}"

# Extracts the global ID into a variable accessible by all lesson blocks
user_uid = st.session_state.hub_user_id

# --- CRITICAL FIX: LAZY LOADING ROUTER ---
# Replaces st.tabs() with a conditional radio to prevent background canvas execution
active_lesson = st.radio(
    "Select Interactive Lesson Demo to Load:",
    [
        "📐 Lesson 1: Geometry & Area Generation",
        "🎲 Lesson 2: Probability & Chance Space",
        "📐 Lesson 3: Pythagorean Theorem Matrix",
        "🧠 Lesson 4: Neuro-Motor Reaction Experiment",
        "👁️ Lesson 5: Visual Search & Attention" # <-- ADD THIS LINE
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
        b_units = st.slider("Base (b) Units", min_value=2, max_value=10, value=6, step=1)
        h_units = st.slider("Height (h) Units", min_value=2, max_value=10, value=5, step=1)
        
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
    st.info("💡 **Watch the Distribution Form**\n\nNotice how the random binary choices at each peg naturally assemble into a Gaussian distribution.")
    render_probability_demo(sample_count=num_samples)

# --- LESSON 3: PYTHAGORUS ---
elif "Pythagorean" in active_lesson:
    st.subheader("Geometric Visualization of $A^2 + B^2 = C^2$")
    
    # Establish a clean layout split for variables vs execution canvas
    anim_col, gap_col, input_col = st.columns([3, 0.2, 1])
    
    with input_col:
        st.info("💡 **Triangle Vectors**\n\nEnter the boundaries below to see the square structures transform.")
        input_mode = st.selectbox("Define Dimensions By:", ["Side Lengths", "Internal Angles"])
        
        if input_mode == "Side Lengths":
            # Bounded between 3 and 8 to prevent physics viewport out-of-bounds clipping
            side_a = st.slider("Base Dimension (Side A)", min_value=2, max_value=6, value=4, step=1)
            side_b = st.slider("Height Dimension (Side B)", min_value=2, max_value=6, value=3, step=1)
        else:
            # Mathematical fallback conversion logic for dynamic angle mapping
            angle_theta = st.slider("Internal Angle (Θ°)", min_value=15, max_value=75, value=36, step=1)
            
            # Extrapolate relative sides using trigonometry scale transformations
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
        render_pythagorean_demo(a_units=side_a, b_units=side_b)

# --- LESSON 4: FITT'S LAW ---
elif "Neuro-Motor" in active_lesson:
    st.subheader("Fitts's Law: Quantitative Neuro-Motor Profiling")
    
    st.markdown("""
    **The Science of Sensory-Motor Bandwidth:** Replicating Paul Fitts's classic 1954 psychophysics paradigm. 
    This experiment measures your motor control channel capacity. By rapidly tapping targets of varying sizes and distances, 
    you are mapping the logarithmic trade-off between movement speed and target accuracy.
    """)

    # =========================================================================
    # STAGE 1: FULL-WIDTH CONTAINER FOR EXPERIMENT (Top Row)
    # =========================================================================
    st.info("🎯 **Target Challenge Grid**\nClick the 'START NOW' button to unlock targets.")
    render_fittslaw_demo(app_id=app_id, firebase_config=firebase_config_str, user_uid=user_uid)

    st.divider()

    # =========================================================================
    # STAGE 2: ANALYTICS COLUMN SPLIT (Bottom Row)
    # =========================================================================
    st.subheader("📊 Analytics & Telemetry Engine")
    graph_col, stats_col = st.columns([1.4, 1.0], gap="large")

    try:
        api_key = firebase_config_dict["apiKey"]
        rest_url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/artifacts/{app_id}/public/data/fitts_trials?key={api_key}"
        
        response = requests.get(rest_url)

        raw_fitts_data = []
        if response.status_code == 200:
            docs = response.json().get('documents', [])
            for doc in docs:
                fields = doc.get('fields', {})
                try:
                    raw_fitts_data.append({
                        'user_id': fields.get('user_id', {}).get('stringValue', 'unknown'),
                        'index_difficulty': float(fields.get('index_difficulty', {}).get('doubleValue', 0)),
                        'movement_time': float(fields.get('movement_time', {}).get('doubleValue', 0))
                    })
                except Exception:
                    continue
        
        fig_reg, fig_swarm, stats = process_cohort_fitts_regression(raw_fitts_data, current_user_uid=user_uid)
        
        with graph_col:
            if fig_reg:
                tab1, tab2 = st.tabs(["Linear Regression (Bandwidth)", "Trial Distributions (Variance)"])
                with tab1:
                    st.caption("**How to read this plot:** The slope of the line ($b$) models your sensory-motor bit-rate transmission. A flatter slope means you are highly efficient.")
                    st.plotly_chart(fig_reg, use_container_width=True, config=PLOTLY_CONFIG)
                with tab2:
                    st.caption("**How to read this plot:** The red box tracks your click consistency. The star pinpoints your average speed ranking among the global population.")
                    st.plotly_chart(fig_swarm, use_container_width=True, config=PLOTLY_CONFIG)
            else:
                st.warning(stats)

        with stats_col:
            if fig_reg:
                html_block = f"""
<div style="background-color: #EFF6FF; padding: 16px; border-radius: 8px; border-left: 4px solid #3B82F6; margin-bottom: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
    <p style="margin: 0 0 6px 0; font-size: 0.95rem; color: #1E40AF; font-weight: bold;">Statistical Significance & OLS Modeling</p>
    <p style="margin: 0; font-size: 0.85rem; color: #1E3A8A; line-height: 1.4;">
        We execute an Ordinary Least Squares (OLS) regression to systematically reject the null hypothesis (H₀: b = 0). A model significance rating of <b>p &lt; 0.05</b> mathematically confirms that task difficulty is actively governing motor processing speed.
    </p>
</div>

<div style="background-color: #FEF2F2; padding: 14px; border-radius: 8px; border-left: 4px solid #EF4444; margin-bottom: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
    <p style="margin: 0 0 6px 0; font-size: 0.85rem; color: #991B1B; font-weight: bold;">🎯 YOUR SENSORY-MOTOR PROFILE</p>
    <p style="margin: 0 0 4px 0; font-family: monospace; font-size: 1.1rem; color: #7F1D1D; font-weight: bold;">
        MT = {stats['user']['intercept_a']} + {stats['user']['slope_b']} &middot; ID
    </p>
    <p style="margin: 0; font-size: 0.8rem; color: #991B1B; line-height: 1.3;">
        Variance Explained (R²): <b>{stats['user']['r_squared']}</b><br>
        Model Significance (p): <b>{stats['user']['p_val']}</b>
    </p>
</div>

<div style="background-color: #F0FDF4; padding: 14px; border-radius: 8px; border-left: 4px solid #22C55E; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
    <p style="margin: 0 0 6px 0; font-size: 0.85rem; color: #166534; font-weight: bold;">👥 GLOBAL COHORT PROFILE</p>
    <p style="margin: 0 0 4px 0; font-family: monospace; font-size: 1.1rem; color: #14532D; font-weight: bold;">
        MT = {stats['global']['intercept_a']} + {stats['global']['slope_b']} &middot; ID
    </p>
    <p style="margin: 0; font-size: 0.8rem; color: #166534; line-height: 1.3;">
        Variance Explained (R²): <b>{stats['global']['r_squared']}</b><br>
        Model Significance (p): <b>{stats['global']['p_val']}</b>
    </p>
</div>
"""
                st.markdown(html_block, unsafe_allow_html=True)
                
    except Exception as err:
        st.error(f"Failed to compile regression chart: {err}")

    # =========================================================================
    # STAGE 3: RESTORED DISCUSSION & CITATIONS
    # =========================================================================
    st.markdown("""
    ---
    #### **Discussion & Conclusions**
    As observed in the significant p-values above, human movement is not simply determined by how far away an object is; it is strictly governed by the ratio of distance to target size. The implications of this formula heavily dictate modern UI/UX software design (e.g., placing critical buttons like the 'Start Menu' at the corners of screens, which grants them an essentially infinite 'Width' and dramatically lowers their Index of Difficulty). 
    
    *References:*
    * Fitts, P. M. (1954). The information capacity of the human motor system in controlling the amplitude of movement. *Journal of Experimental Psychology*, 47(6), 381–391.
    * MacKenzie, I. S. (1992). Fitts' Law as a research and design tool in human-computer interaction. *Human-Computer Interaction*, 7(1), 91-139.
    """)

# --- LESSON 5: VISUAL SEARCH ---
elif "Visual Search" in active_lesson:
    st.subheader("Visual Search: Parallel vs. Serial Processing")
    
    st.markdown("""
    **The Science of Feature Integration:** Replicating Treisman & Gelade's (1980) classic visual search paradigm. 
    This experiment tests whether your brain can process entire visual fields simultaneously (Parallel Pop-Out) 
    or if it must scan items one-by-one (Serial Conjunction Binding).
    """)

    # 1. Render Interactive Canvas
    st.info("🎯 **Find the Target**\nClick 'Start Visual Search Experiment' below to begin.")
    render_visual_search_demo(app_id=app_id, firebase_config=firebase_config_str, user_uid=user_uid)

    st.divider()

    # 2. Analytics Pipeline
    st.subheader("📊 Cognitive Telemetry Engine")
    graph_col, stats_col = st.columns([1.4, 1.0], gap="large")

    try:
        # Asymmetric REST Call for Visual Search Collection
        api_key = firebase_config_dict["apiKey"]
        rest_url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/artifacts/{app_id}/public/data/visual_search_trials?key={api_key}"
        
        response = requests.get(rest_url)
        raw_search_data = []
        
        if response.status_code == 200:
            docs = response.json().get('documents', [])
            for doc in docs:
                fields = doc.get('fields', {})
                try:
                    raw_search_data.append({
                        'user_id': fields.get('user_id', {}).get('stringValue', 'unknown'),
                        'condition': fields.get('condition', {}).get('stringValue', 'unknown'),
                        'set_size': int(fields.get('set_size', {}).get('integerValue', 0)),
                        'reaction_time': float(fields.get('reaction_time', {}).get('doubleValue', 0))
                    })
                except Exception:
                    continue
        
        fig_reg, fig_box, stats = process_visual_search_analytics(raw_search_data, current_user_uid=user_uid)
        
        with graph_col:
            if fig_reg:
                tab1, tab2 = st.tabs(["Linear Regression (Search Slopes)", "Trial Distributions (Variance)"])
                with tab1:
                    st.caption("**How to read this plot:** Flat lines mean your brain processed the entire screen instantly (Parallel). Steep upward slopes mean you had to scan items one-by-one (Serial).")
                    st.plotly_chart(fig_reg, use_container_width=True, config=PLOTLY_CONFIG)
                with tab2:
                    st.plotly_chart(fig_box, use_container_width=True, config=PLOTLY_CONFIG)
            else:
                st.warning(stats)

        with stats_col:
            if fig_reg and stats:
                conj_slope = stats.get('Conjunction', {}).get('slope', 0)
                color_slope = stats.get('Color', {}).get('slope', 0)
                
                html_block = f"""
<div style="background-color: #EFF6FF; padding: 16px; border-radius: 8px; border-left: 4px solid #3B82F6; margin-bottom: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
    <p style="margin: 0 0 6px 0; font-size: 0.95rem; color: #1E40AF; font-weight: bold;">Theory: The Pop-Out Effect</p>
    <p style="margin: 0; font-size: 0.85rem; color: #1E3A8A; line-height: 1.4;">
        Single features (like pure color) are processed automatically by the visual cortex before attention is even deployed. Conjunctions (Red AND Half-Circle) require active, serial attention to bind the features together.
    </p>
</div>

<div style="background-color: #FEF2F2; padding: 14px; border-radius: 8px; border-left: 4px solid #EF4444; margin-bottom: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
    <p style="margin: 0 0 6px 0; font-size: 0.85rem; color: #991B1B; font-weight: bold;">🧠 YOUR CONJUNCTION PENALTY</p>
    <p style="margin: 0 0 4px 0; font-family: monospace; font-size: 1.1rem; color: #7F1D1D; font-weight: bold;">
        + {conj_slope:.1f} ms / item
    </p>
    <p style="margin: 0; font-size: 0.8rem; color: #991B1B; line-height: 1.3;">
        This is your serial scanning speed. Every additional distractor adds this many milliseconds to your search time.
    </p>
</div>

<div style="background-color: #F0FDF4; padding: 14px; border-radius: 8px; border-left: 4px solid #22C55E; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
    <p style="margin: 0 0 6px 0; font-size: 0.85rem; color: #166534; font-weight: bold;">⚡ YOUR POP-OUT SPEED</p>
    <p style="margin: 0 0 4px 0; font-family: monospace; font-size: 1.1rem; color: #14532D; font-weight: bold;">
        + {color_slope:.1f} ms / item
    </p>
    <p style="margin: 0; font-size: 0.8rem; color: #166534; line-height: 1.3;">
        Because this slope is near zero, we mathematically prove that your brain processed 100 items just as fast as 25 items!
    </p>
</div>
"""
                st.markdown(html_block, unsafe_allow_html=True)
                
    except Exception as err:
        st.error(f"Failed to compile search telemetry: {err}")

st.divider()

# =============================================================================
# SECTION 2: EDUCATION (Teaching Career History & Performance Analytics)
# =============================================================================
st.header("2. Education & Professional History")
st.write("Tracking quantitative student development, milestone testing metrics, and higher-education instruction.")

# --- THE ABSOLUTE REPOSITORY PATH ANCHOR ---
# __file__ evaluates to the absolute path of this file (.../pages/2_mentorship_app.py).
# Stepping up two folder layers targets the repository base path (.../neuroedu.io.career-hub.git/).
# MATLAB Analogy: Equivalent to fileparts(fileparts(mfilename('fullpath')))
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

for job in mentorship['career_history']:
    with st.container():
        # Decouple text logs from the data visualizations using a clean 1:2 column layout
        c_left, c_right = st.columns([1, 2], gap="medium")
        
        # --- RESTORED: LEFT COLUMN TEXT ---
        with c_left:
            st.markdown(f"#### **{job['school']}**")
            st.markdown(f"*{job['role']}*")
            st.caption(f"🗓️ {job['years']}")
            st.write(job['metrics'])
            
        with c_right:
            if job.get('file_path'):
                # Assemble the strict absolute path
                target_csv = os.path.join(repo_root, job['file_path'])
                
                # ---------------------------------------------------------
                # DATA PIPELINE TYPE 1: LONGITUDINAL MAPS PERCENTILES
                # ---------------------------------------------------------
                if job['dataset_type'] == 'maps':
                    # --- FIXED: Exact column names from CSV schema ---
                    cols_to_load = ["Last", "First", "Fall '25 %", "Winter '25 %", "Spring '25 %"]
                    try:
                        # Memory-optimized load
                        df_maps = pd.read_csv(target_csv, usecols=cols_to_load)
                        
                        df_melted = df_maps.melt(
                            id_vars=["Last", "First"], 
                            value_vars=["Fall '25 %", "Winter '25 %", "Spring '25 %"],
                            var_name="Testing Term", 
                            value_name="Percentile"
                        )
                        
                        # Clean up the axis labels by removing the " %" string
                        df_melted['Testing Term'] = df_melted['Testing Term'].str.replace(" %", "")
                        
                        fig = px.box(
                            df_melted, x="Testing Term", y="Percentile", points="all",
                            title="Longitudinal MAP Percentile Distributions",
                            color="Testing Term",
                            color_discrete_sequence=['#94A3B8', '#38BDF8', '#4ADE80']
                        )
                        fig.update_layout(
                            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="#F8FAFC",
                            margin=dict(l=10, r=10, t=40, b=10), height=280, showlegend=False,
                            yaxis=dict(title="National Percentile Scale", gridcolor="rgba(148, 163, 184, 0.12)")
                        )
                        st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
                    
                    except FileNotFoundError:
                        st.error(f"System rejected path: `{target_csv}`. Check Linux case-sensitivity.")
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
                    # cols_to_load = ["Last Name", "First Name"] + core_standards + myth_components
                    
                    try:
                        # 1. Load the entire CSV into memory without the strict usecols filter
                        df_ela = pd.read_csv(target_csv)
                        
                        # 2. Print the exact headers to the Streamlit UI for diagnostic mapping
                        st.error("⚠️ ELA Column Name Mismatch. Please check the exact names below:")
                        st.code(df_ela.columns.tolist())
                        
                        # 3. Halt the rendering thread to prevent plotting errors
                        st.stop() 
                        
                    except FileNotFoundError:
                        st.error(f"System rejected path: `{target_csv}`. Check Linux case-sensitivity.")
                    except Exception as e:
                        st.error(f"Error executing ELA standards parse: {e}")

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