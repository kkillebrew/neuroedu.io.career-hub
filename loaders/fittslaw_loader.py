"""
=============================================================================
MODULE: loaders/fittslaw_loader.py
AUTHOR: Kyle W. Killebrew, PhD & Data Science Mentorship Engine
STATUS: Active Production Blueprint (Lesson 4)
DESCRIPTION:
    The "Model" controller for the Fitts's Law Experiment dashboard.
    Downloads, aggregates, and processes multi-user Firestore collections.
    Computes linear regression matrices using scipy.stats.
=============================================================================
"""

import pandas as pd
import numpy as np
import plotly.express as px
from scipy.stats import linregress

def process_cohort_fitts_regression(raw_trials, current_user_uid):
    """
    Processes raw Firestore records into a dual-series cohort regression plot.
    
    MATLAB Analogy: This is equivalent to taking a dynamic matrix, splitting
    indices by UserID, running [b,bint,r,rint,stats] = regress(Y,X), and
    plotting both fit lines on a single hold-on axis.
    """
    if not raw_trials:
        # High contrast fallback state if database returns an empty collection
        return None, "No empirical data logged yet. Be the first to start the experiment!"

    # Transform list of dicts to DataFrame with strict column boundaries
    df = pd.DataFrame(raw_trials)
    
    # Clean and convert types safely
    df['index_difficulty'] = pd.to_numeric(df['index_difficulty'], errors='coerce')
    df['movement_time'] = pd.to_numeric(df['movement_time'], errors='coerce')
    df = df.dropna(subset=['index_difficulty', 'movement_time'])

    if len(df) < 5:
        return None, "Too few data points collected to run statistical regression."

    # Segment current user session from the global cohort population
    df['Subject Group'] = np.where(df['user_id'] == current_user_uid, "You (Active Session)", "Global Cohort Population")

    # Group records by Index of Difficulty and Subject Group to obtain clean means
    # This prevents scatter points from piling up vertically on identical ID bounds
    df_grouped = df.groupby(['index_difficulty', 'Subject Group'])['movement_time'].mean().reset_index()

    # Calculate overall linear parameters using scipy.stats
    slope, intercept, r_value, p_value, std_err = linregress(
        df_grouped['index_difficulty'], 
        df_grouped['movement_time']
    )

    # Build the high contrast educational regression plot
    fig = px.scatter(
        df_grouped,
        x='index_difficulty',
        y='movement_time',
        color='Subject Group',
        color_discrete_map={{
            "You (Active Session)": "#38BDF8",       # Sky Blue
            "Global Cohort Population": "#475569"    # Muted Slate
        }},
        labels={{
            "index_difficulty": "Task Difficulty Index (ID in bits)",
            "movement_time": "Average Movement Execution Time (MT in ms)"
        }},
        title="Fitts's Law Motor Execution Regression Model",
        hover_data=['index_difficulty', 'movement_time']
    )

    # Add the unified ordinary least squares (OLS) trendline
    id_range = np.linspace(df_grouped['index_difficulty'].min(), df_grouped['index_difficulty'].max(), 50)
    fit_line = slope * id_range + intercept

    # Track mathematical trendline coordinates in separate dataframe
    df_fit = pd.DataFrame({{
        'index_difficulty': id_range,
        'movement_time': fit_line,
        'Subject Group': 'Regression Fit Line'
    }})

    # Merge fit trace over coordinates
    fig.add_traces(
        px.line(df_fit, x='index_difficulty', y='movement_time', color_discrete_sequence=["#10B981"])
        .update_traces(line=dict(dash="dash", width=2.5))
        .data
    )

    # Standardize layout boundaries
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="#F8FAFC",
        margin=dict(l=10, r=10, t=50, b=10),
        height=320,
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01, bgcolor="rgba(15,23,42,0.6)"),
        xaxis=dict(gridcolor="rgba(148, 163, 184, 0.12)"),
        yaxis=dict(gridcolor="rgba(148, 163, 184, 0.12)")
    )

    # Pack statistical parameters for display inside the dashboard markdown card
    stats_summary = {{
        'intercept_a': round(intercept, 1),
        'slope_b': round(slope, 1),
        'r_squared': round(r_value ** 2, 3),
        'p_val': round(p_value, 4)
    }}

    return fig, stats_summary


---

## 6. Part C: The Spoke Layout Route Patch

Open `pages/2_mentorship_app.py`. Locate your **Active Lesson Routing Matrix** (the vertical list of tabs or radio selectors) and integrate the new spoke.

```python
# --- LESSON ROUTING SELECTION --
active_lesson = st.radio(
    "Select Interactive Lesson Demo to Load:",
    [
        "📐 Lesson 1: Geometry & Area Generation", 
        "🎲 Lesson 2: Probability & Chance Space",
        "📐 Lesson 3: Pythagorean Theorem Matrix",
        "🧠 Lesson 4: Neuro-Motor Reaction Experiment" # <-- INTEGRATION SPOKE
    ],
    horizontal=True,
    label_visibility="collapsed"
)

# ... [Lessons 1, 2, and 3 logic remains exactly unchanged] ...

elif "Neuro-Motor" in active_lesson:
    st.subheader("Fitts's Law: Quantitative Neuro-Motor Profiling")
    st.write("""
    Explore sensory-motor bandwidth limits by clicking home triggers and target targets as quickly as possible.
    Your results are aggregated against our global cohort database in real time.
    """)

    # Setup dual layout columns
    experiment_col, analytics_col = st.columns([1.1, 1.0], gap="medium")

    # Extract global variables populated during session start
    app_id = typeof __app_id !== 'undefined' ? __app_id : 'default-app-id'
    firebase_config = typeof __firebase_config !== 'undefined' ? __firebase_config : {}
    user_uid = auth.currentUser.uid if auth.currentUser else "anonymous_guest"

    with experiment_col:
        st.info("🎯 **Target Challenge Grid**\nClick the baseline 'TAP HERE' node to unlock targets.")
        
        # Launch Fitts's Law Experiment Engine
        render_fittslaw_demo(app_id=app_id, firebase_config=firebase_config, user_uid=user_uid)

    with analytics_col:
        st.info("📈 **Cohort Performance Analysis**")
        
        # Retrieve raw database records (Rule 2: Read entire collection, filter in Python)
        try:
            # Placeholder fetch routine - database handler parses this under the Hood
            raw_fitts_data = fetch_public_collection('fitts_trials') 
            
            fig_regression, stats = process_cohort_fitts_regression(raw_fitts_data, current_user_uid=user_uid)
            
            if fig_regression:
                st.plotly_chart(fig_regression, use_container_width=True)
                
                # Render scientific telemetry readouts using LaTeX-style formatting
                st.markdown(f"""
                <div style="background-color: rgba(30, 41, 59, 0.5); padding: 15px; border-radius: 8px; border-left: 4px solid #10B981;">
                    <p style="margin: 0; font-size: 0.9rem; color: #94A3B8;"><b>OLS Statistical Formula Model:</b></p>
                    <p style="margin: 5px 0; font-size: 1.1rem; font-family: monospace; color:#10B981;">
                        MT = {stats['intercept_a']} + {stats['slope_b']} &middot; ID
                    </p>
                    <p style="margin: 0; font-size: 0.8rem; color: #64748B;">
                        Variance R²: <b>{stats['r_squared']}</b> | Model Significance p: <b>{stats['p_val']}</b>
                    </p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.warning(stats) # Displays clean fallback alert
        except Exception as err:
            st.error(f"Failed to compile regression chart: {err}")


'''
## 7. The Lessons Learned Encyclopedia (Troubleshooting Compendium)

During the construction of your third educational spoke (The Pythagorean Theorem Physics Matrix), we solved several complex cross-compilation errors. Any developer updating this repository **must read these four guidelines** to prevent immediate dashboard failures.

### Guideline 1: The F-String Variable Injection Escape
* **The Problem:** Streamlit compiles Javascript inside multiline f-strings: `f""" <script> ... </script> """`. Because Python interprets single curly braces (`{}`) as variable inputs, standard Javascript code dictionaries throw compiler crashes instantly.
* **The Guardrail:** Every structural Javascript curly brace must be cleanly doubled up (`{{` and `}}`) to prevent Python interpolation attempts. Single curly braces must only be used when passing active Python variables (e.g., `{app_id}`) down to the data bridge.

### Guideline 2: Avoid Instant Multi-turn Physics Rotation Snaps
* **The Problem:** Matter.js handles coordinates in local and global rotational frames. If you rotate a box $360^{\circ}$ ($2\pi$ radians) during Phase 3, but set its target linear angle to $0$ in Phase 4, the engine will attempt to spin the box $360^{\circ}$ *backward within a single frame*. This instant centripetal velocity acts like an explosion, ejecting every marble inside.
* **The Guardrail:** Always normalize rotation bounds prior to translation: `Body.setAngle(box, box.angle - 2 * Math.PI)`.

### Guideline 3: Mitigate High-Speed Wall Tunneling (CCD)
* **The Problem:** Smaller bodies moving inside high-velocity containers can slip directly through solid boundaries between animation steps.
* **The Guardrail:**
    1.  Boost engine collision passes: `const engine = Engine.create({ positionIterations: 24, velocityIterations: 20 });`.
    2.  Always bridge relative velocity vectors manually when transforming kinematic positions: `Body.setVelocity(item, { x: newX - oldX, y: newY - oldY });`.

### Guideline 4: Separate Multi-Body Translational Collisions
* **The Problem:** Moving multiple closed coordinate containers across intersecting layout paths causes overlapping boxes to compress and pop the marbles out.
* **The Guardrail:** Always assign independent parallel binary masks (`collisionFilter.category` and `collisionFilter.mask`) to each sub-container so they pass through each other like ghosts during linear translation.


***

### Summary of Completed Upgrades:
We successfully completed all structural, kinematic, and visual layout parameters for the Pythagorean Spoke in `pages/components/pythagorean_demo.py` and connected the inputs inside `pages/2_mentorship_app.py`:
1.  **Algebraic Text Clearances:** Pushed the formula headers and `Vol` indicators to an algebraic $45\text{px}$ buffer above the vertical box stacks, removing any overlap with the mathematical `+` and `=` operators.
2.  **Telemetry Deletion:** Cleanly stripped the development phase diagnostic markers from the canvas, providing a polished production layout.
3.  **Kinematic Phase Choreography:** Programmed the triangle to remain locked inside the geometric screen center while the boxes explode outward, only transitioning down to the bottom-right quadrant *after* the boxes slide into their stacked vertical configurations.
4.  **Database Strategy Guide Generated:** Packaged all architectural guidelines, Firestore path rules, and physics troubleshooting lessons into a comprehensive Markdown blueprint file (`fittslaw_blueprint.md`) to establish an elite science experiment layout for your future updates!
'''