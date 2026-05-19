"""
=============================================================================
MODULE: pages/1_academic_research_app.py
AUTHOR: Kyle W. Killebrew, PhD
DESCRIPTION: 
    The presentation layer for the Academic Research portfolio.
    Builds the UI dynamically and integrates live Plotly visualizations.
=============================================================================
"""

import streamlit as st
import sys
import os
import numpy as np
import plotly.express as px
import pandas as pd  # <--- ADD THIS LINE
import json          # <--- ADD THIS LINE (if not already there)
import streamlit.components.v1 as components

# --- PATH CONFIGURATION ---
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from loaders.academic_research_loader import (
    get_publications_data, 
    get_research_expertise, 
    get_academic_assets,
    get_project_narratives,
    get_sfm_data,
    get_percept_duration_data,  # <-- NEW
    get_response_counts_data,   # <-- NEW
    get_rt_histogram_data,      # <-- NEW
    get_accuracy_data,          # <-- NEW
    get_test_retest_data,       # <-- NEW
    get_rotating_line_data,     # Start of rotating line stuff
    get_vwm_behavioral_data,    # <-- NEW
    get_vwm_eeg_data,           # <-- NEW
    PLOTLY_CONFIG
)

from pages.components.rotating_line_demo import render_rotating_line_demo, render_mini_demo, render_vector_demo
from pages.components.vwm_encoding_demo import render_vwm_demo
from career_hub_loader import get_references_metadata
from career_hub_sidebar import apply_global_settings, render_sidebar

# --- INITIALIZATION ---
apply_global_settings("Kyle W. Killebrew, PhD | Academic Research")
render_sidebar()

pubs_df = get_publications_data()
expertise = get_research_expertise()
narratives = get_project_narratives()

# ==========================================
# TOP SECTION: CV & PUBLICATIONS
# ==========================================
st.title("Academic Career & Research")
c1, c2 = st.columns([2, 1])

with c1:
    st.header("Publications")
    for _, row in pubs_df.iterrows():
        st.markdown(f"**{row['Year']}** | [{row['Title']}]({row['Link']})")

with c2:
    st.header("Academic Assets")
    ac_cv = "documents/kyle_academic_cv.pdf"
    if os.path.exists(ac_cv):
        with open(ac_cv, "rb") as f:
            st.download_button("📂 Download Academic CV", f.read(), "Killebrew_Academic_CV.pdf")
    
    st.markdown("### Research Expertise")
    st.info("\n".join([f"• {item}" for item in expertise]))

st.divider()

# ==========================================
# BOTTOM SECTION: INTERACTIVE TABS
# ==========================================
st.header("Interactive Research Methodologies")
st.write("A visual summary of methodologies utilized to uncover neural biomarkers and understand visual biases.")

# UPDATE your tabs definition
tabs = st.tabs([
    "🧩 1. Biomarkers of Psychosis (SFM)", 
    "🔄 2. The Rotating Line Illusion",  # <-- Renamed this tab
    "🧠 3. Encoding Visual Objects Into Memory", 
    "📊 4. Ensemble Encoding", 
    "🎯 5. Intraparietal Regions Involvment In Working Memory Encoding"
])

# --- TAB 1: STRUCTURE FROM MOTION (SFM) ---
with tabs[0]:
    sfm_text = narratives[0]
    col_text, col_img = st.columns([1.5, 1], gap="large")
    
    with col_text:
        st.subheader(sfm_text["header"])
        st.write(sfm_text["blurb"])
        st.info("**Methodology:** Participants viewed an ambiguous rotating cylinder. By pressing buttons to indicate perceptual phase shifts, we extracted the switch rate ($Hz$).")
        
    with col_img:
        gif_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "documents", "rotatingCylinder.gif")
        if os.path.exists(gif_path):
            st.image(gif_path, use_container_width=True, caption="Bi-Stable Structure From Motion")
            
    st.divider()

    # Create the 5 main tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Control Data Analysis", 
        "Main Behavioral Analysis", 
        "Modeling", 
        "Eyetracking", 
        "MRS"
    ])

    with tab1:
        st.header("Control Data Analysis")
        
        # Safely fetch the REAL baseline data using the required positional arguments
        df_tab1 = get_sfm_data(
            grouping_mode="Standard (Controls vs. Relatives vs. PwPP)", 
            metric_mode="Switch Rate (Hz)", 
            apply_qc=True
        )
        
        if df_tab1.empty:
            st.warning("Data not loaded. Please check your data sources.")
        else:
            # --- SECTION 1: Histograms ---
            st.subheader("1. Distribution Profiles")
            hist_choice = st.selectbox(
                "Select Distribution to View:", 
                ["Percept Durations", "Participant Responses", "Reaction Times"],
                index=0 
            )
            
            if hist_choice == "Percept Durations":
                df_pd = get_percept_duration_data(df_tab1)
                if df_pd.empty:
                    st.warning("⚠️ No percept duration data available in the current dataset.")
                else:
                    fig_hist = px.histogram(df_pd, x="Duration_Sec", color="Task_Type", barmode="overlay", nbins=50, title="Percept Durations")
                    st.plotly_chart(fig_hist, use_container_width=True)
                
            elif hist_choice == "Participant Responses":
                # FETCH THE DUAL DATAFRAMES
                raw_acc, filtered_acc = get_accuracy_data(df_tab1) 
                
                if raw_acc.empty:
                    st.warning("⚠️ No participant response data available.")
                else:
                    st.write("### QC Impact: Response Accuracy")
                    
                    # --- Chart A: Upper Histogram (Unfiltered) ---
                    fig_upper = px.histogram(
                        raw_acc, 
                        x="Control_Correct_Responses_Raw",
                        nbins=12, 
                        title="UNFILTERED: Total Correct Responses (No RT limit)",
                        labels={'Control_Correct_Responses_Raw': 'Number of Correct Responses'},
                        color_discrete_sequence=['#94a3b8']
                    )
                    fig_upper.add_vline(x=5.5, line_dash="dash", line_color="#ef4444", annotation_text="Pass Threshold (6)")
                    fig_upper.update_layout(height=350, margin=dict(t=50, b=0, l=0, r=0))
                    fig_upper.update_xaxes(range=[-0.5, 11.5], dtick=1)
                    st.plotly_chart(fig_upper, use_container_width=True, config=PLOTLY_CONFIG)
                    
                    st.markdown("<br>", unsafe_allow_html=True) 
                    
                    # --- Chart B: Lower Histogram (Filtered) ---
                    fig_lower = px.histogram(
                        filtered_acc, 
                        x="Control_Correct_Responses",
                        nbins=12, 
                        title="FILTERED: Responses within 6s Window (QC Applied)",
                        labels={'Control_Correct_Responses': 'Number of Correct Responses'},
                        color_discrete_sequence=['#10b981']
                    )
                    fig_lower.add_vline(x=5.5, line_dash="dash", line_color="#ef4444", annotation_text="Pass Threshold (6)")
                    fig_lower.update_layout(height=350, margin=dict(t=50, b=0, l=0, r=0))
                    fig_lower.update_xaxes(range=[-0.5, 11.5], dtick=1)
                    st.plotly_chart(fig_lower, use_container_width=True, config=PLOTLY_CONFIG)

            elif hist_choice == "Reaction Times":
                df_rt_hist = get_rt_histogram_data(df_tab1)
                if df_rt_hist.empty:
                    st.warning("⚠️ No RT data found. Check column: Control_Raw_RT_JSON")
                else:
                    fig_rt_dist = px.histogram(
                        df_rt_hist, 
                        x="Reaction_Time_Sec", 
                        nbins=50, 
                        title="Distribution of All Reaction Times (Control Task)",
                        color_discrete_sequence=['#6366f1']
                    )
                    st.plotly_chart(fig_rt_dist, use_container_width=True)
                    
            st.divider()
            
            # --- SECTION 2: Control Task Performance ---
            st.subheader("2. Control Task Performance")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                away_towards_data = []
                
                for _, row in df_tab1.iterrows():
                    # Unpack 'Towards' (Correct) Durations
                    towards_json = row.get("Control_Durations_Towards_JSON")
                    if pd.notna(towards_json) and towards_json != '[]':
                        try:
                            for dur in json.loads(towards_json):
                                away_towards_data.append({'Subject': row['Subject'], 'Type': 'Towards (Correct)', 'Duration_Sec': float(dur)})
                        except Exception: pass
                    
                    # Unpack 'Away' (Incorrect) Durations
                    away_json = row.get("Control_Durations_Away_JSON")
                    if pd.notna(away_json) and away_json != '[]':
                        try:
                            for dur in json.loads(away_json):
                                away_towards_data.append({'Subject': row['Subject'], 'Type': 'Away (Incorrect)', 'Duration_Sec': float(dur)})
                        except Exception: pass
                            
                df_dir = pd.DataFrame(away_towards_data)
                
                if not df_dir.empty:
                    # Average per subject so the box plot isn't distorted by one person with 50 micro-blinks
                    df_dir_ave = df_dir.groupby(['Subject', 'Type'])['Duration_Sec'].mean().reset_index()
                    
                    fig_dir = px.box(
                        df_dir_ave, 
                        x="Type", 
                        y="Duration_Sec", 
                        points="all", 
                        title="Average Duration (Control Task)",
                        color="Type",
                        color_discrete_map={"Towards (Correct)": "#10b981", "Away (Incorrect)": "#ef4444"}
                    )
                    fig_dir.update_traces(jitter=0.6, pointpos=0, width=0.3)
                    fig_dir.update_layout(showlegend=False, xaxis_title="")
                    st.plotly_chart(fig_dir, use_container_width=True)
                else:
                    st.warning("⚠️ No Towards/Away data found in the current dataset.")
                    
            with col2:
                # We use the underscore to ignore the first part of the tuple (raw)
                # and assign the second part to 'filtered_acc_df' so line 250 works.
                _, filtered_acc_df = get_accuracy_data(df_tab1) 
                
                fig_acc = px.box(
                    filtered_acc_df, # <--- This name now matches line 247
                    y="Control_Correct_Responses", 
                    points="all", 
                    title="Task Accuracy (Max 11)"
                )
                fig_acc.update_traces(jitter=0.6, pointpos=0, width=0.3)
                st.plotly_chart(fig_acc, use_container_width=True)
                
            with col3:
                # This code will now run because col2 no longer crashes!
                df_rt_all = get_rt_histogram_data(df_tab1)
                if not df_rt_all.empty:
                    df_rt_ave = df_rt_all.groupby('Subject')['Reaction_Time_Sec'].mean().reset_index()
                    fig_rt_ave = px.box(df_rt_ave, y="Reaction_Time_Sec", points="all", title="Average RT")
                    fig_rt_ave.update_traces(jitter=0.6, pointpos=0, width=0.3)
                    st.plotly_chart(fig_rt_ave, use_container_width=True)
                else:
                    st.warning("⚠️ No RT data found.")
                
            with st.expander("View Legacy pHCP References (EPS)"):
                ref_col1, ref_col2, ref_col3 = st.columns(3)
                with ref_col1: st.image("documents/pHCP_EPS_Files/AveDurAwayTowards.png", caption="pHCP Ave Dur Away/Towards")
                with ref_col2: st.image("documents/pHCP_EPS_Files/PaperFig_AccFULL.png", caption="pHCP Accuracy")
                with ref_col3: st.image("documents/pHCP_EPS_Files/AveRT.png", caption="pHCP Average RT")
    
    with tab2:
        st.subheader("Data Exploration: Switch Rates & Percept Durations")
        
        # --- UI CONTROLLERS ---
        ui_c1, ui_c2 = st.columns(2)
        
        with ui_c1:
            selected_grouping = st.selectbox(
                "Select grouping for analysis:",
                [
                    "Standard (Controls vs. Relatives vs. PwPP)",
                    "Detailed Psychosis (SZ vs. SCA vs. BIP vs. Controls)",
                    "SZ vs Bip_Com (Schizophrenia vs. Bipolar+Other vs. Controls)",
                    "Standard + Total Combined (Includes Sample Average)"
                ]
            )
            # NEW: The Quality Control Toggle
            apply_qc_filter = st.checkbox(
                "Apply Quality Control Exclusions (Drop participants failing control task)", 
                value=True, # Default to True (exclusions applied)
                help="Filters out participants who failed to detect at least 6 real switches within 6 seconds."
            )
            
        with ui_c2:
            selected_metric = st.selectbox(
                "Select metric to visualize:",
                ["Switch Rate (Hz)", "Average Percept Duration (sec)"]
            )
        
        # --- DATA HYDRATION ---
        # NEW: Pass the checkbox state into the loader!
        # Pass BOTH UI states directly into the loader engine
        df_sfm = get_sfm_data(grouping_mode=selected_grouping, metric_mode=selected_metric, apply_qc=apply_qc_filter)
        
        if df_sfm.empty:
            st.warning("⚠️ Data files not found. Please ensure `sfm_dashboard_data.parquet` and `SYON-3TDemographics...csv` are in the documents folder.")
        else:
            # --- PLOTTING & STATS ---
            c1, c2 = st.columns([2, 1])
            
            with c1:
                st.markdown("### Behavioral Performance")
                
                # Setup column mapping based on dropdown
                if "Rate" in selected_metric:
                    ctrl_col, bi_col = 'Real_Switch_Hz', 'Bistable_Hz'
                else:
                    ctrl_col, bi_col = 'Real_Switch_Dur', 'Bistable_Dur'  # <--- Fixed!
                
                # Split the main chart area into two side-by-side graphs
                chart_col1, chart_col2 = st.columns(2)
                
                with chart_col1:
                    fig_ctrl = px.box(df_sfm, x="Group", y=ctrl_col, points="all", title="Control Task")
                    fig_ctrl.update_traces(jitter=0.7, pointpos=0, width=0.3)
                    fig_ctrl.update_layout(yaxis_title=f"Control {selected_metric}")
                    st.plotly_chart(fig_ctrl, use_container_width=True)
                    
                with chart_col2:
                    fig_bi = px.box(df_sfm, x="Group", y=bi_col, points="all", title="Bistable Task")
                    fig_bi.update_traces(jitter=0.7, pointpos=0, width=0.3)
                    fig_bi.update_layout(yaxis_title=f"Bistable {selected_metric}")
                    st.plotly_chart(fig_bi, use_container_width=True)

            # KEEP THIS EXACTLY AS YOU HAD IT (Just indented to match c1)
            with c2:
                st.markdown("### Live Statistical Insights")
                st.caption("Non-parametric K-W and Mann-Whitney U models dynamically computed based on current parameters.")
                
                # Determine which column to run the stats on based on the dropdown
                stat_target = 'Bistable_Hz' if "Rate" in selected_metric else 'Bistable_Dur'
                
                # Fetch and display the live stats!
                from loaders.academic_research_loader import generate_live_statistics
                stats_output = generate_live_statistics(df_sfm, stat_target)
                st.info(f"**Bistable Task Stats:**\n\n{stats_output}") # Added a bold header to clarify it's the Bistable stats
                
                with st.expander("View Full Raw Subject Data"):
                    # Updated display_cols to show both Control and Bistable raw numbers
                    display_cols = ['Subject', 'Group', ctrl_col, bi_col] 
                    available_cols = [c for c in display_cols if c in df_sfm.columns]
                    st.dataframe(df_sfm[available_cols], use_container_width=True, hide_index=True)

        # Legacy EPS Expander - Centered Image
        with st.expander("View Legacy pHCP Reference (EPS)"):
            _, center_col, _ = st.columns([1, 2, 1]) # The middle column takes up 50% of the space
            with center_col:
                if "Switch Rate" in selected_metric:
                    st.image("documents/pHCP_EPS_Files/AveSwitchRate.png", caption="pHCP Switch Rate")
                elif "Percept Duration" in selected_metric:
                    st.image("documents/pHCP_EPS_Files/AvePercDur.png", caption="pHCP Percept Duration")

    with tab3:
        st.header("Modeling")
        st.info("Modeling pipeline coming soon.")

    with tab4:
        st.header("Eyetracking")
        st.info("Eyetracking integration coming soon.")

    with tab5:
        st.header("MRS")
        st.info("MRS correlation data coming soon.")

### 2-Rotating Line ###
with tabs[1]:
        st.header("The Rotating Line Illusion")
        
        # --- MASTHEAD: 2-Column Layout ---
        # MATLAB Bridge: Think of this like setting up a subplot(1,2,x) figure.
        demo_col_left, demo_col_right = st.columns([1, 1.5])
        
        with demo_col_left:
            st.subheader("Interactive Demonstration")
            st.markdown("""
            **The Phenomenon:** When a line rotating at a constant speed is occluded by an elliptical aperture, 
            the human visual system misinterprets the shrinking and growing of the line as changes in rotational speed. 
            It appears to slow down as it reaches the vertical axis and speed up toward the horizontal.
            
            **Instructions:** 1. Observe the line rotating. Does it look like it's changing speed?
            2. Use the **Speed Modulation** slider to artificially speed up and slow down the line. 
            3. Find the exact point where the line appears to rotate at a perfectly constant speed (Your Point of Subjective Equality).
            """)
            # Notice we removed the controls from this left column entirely!
            
        with demo_col_right:
            # STREAMLIT TRICK: We want the controls below the canvas, but we need their 
            # values BEFORE we can draw the canvas. 
            # We create an empty container first to hold the canvas's physical space at the top.
            canvas_placeholder = st.container()

            # Now we draw the controls visually below that empty space
            st.markdown("### Demo Controls")
            demo_speed = st.slider("Base Rotational Speed (RPM)", min_value=10, max_value=150, value=50, step=5, key="demo_speed_slider")
            demo_mod = st.slider("Speed Modulation (Nullify Effect)", min_value=0.0, max_value=5.0, value=0.0, step=0.1, key="demo_mod_slider")
            
            # Layout the dropdown and checkbox side-by-side cleanly
            ctrl_col1, ctrl_col2 = st.columns(2)
            with ctrl_col1:
                demo_shape = st.selectbox("Aperture Shape", ["Ellipse", "Rectangle", "Diamond"], key="demo_shape_select")
            with ctrl_col2:
                st.write("") # Spacer to vertically align with selectbox
                st.write("")
                demo_dots = st.checkbox("Show Tracking Dots", value=True, key="demo_dots_check")

            # Finally, we inject our HTML function INTO the placeholder at the top, 
            # passing in the variables we just collected from the controls below it!
            with canvas_placeholder:
                render_rotating_line_demo(demo_speed, demo_mod, demo_shape, demo_dots)

        st.divider()

        # --- SUB-TABS: The Analytical Breakdown ---
        # MATLAB Bridge: This separates our raw "task" from our data analysis scripts.
        rl_tabs = st.tabs(["🧪 1. Mini Experiment", "📊 2. Control Data & Analysis", "🧠 3. Main Findings"])
        
        with rl_tabs[0]:
            st.subheader("Find Your PSE (Point of Subjective Equality)")
            st.info("Experiment logic will go here.")
            
        with rl_tabs[1]:
            st.subheader("Baseline Psychometric Functions")
            st.markdown("Comparing the Point of Subjective Equality (PSE) between the Control and Experimental conditions.")
            
            import plotly.graph_objects as go

            def build_psychometric_plot(df_raw, df_ind_fits, df_avg_fit, pse_dict, title, x_label):
                fig = go.Figure()
                
                # --- NEW COLOR MAPPING ---
                # MATLAB Bridge: color_map = {'Long': [1 0 0], 'Short': [0 0 1], 'N/A': [0 1 0]}
                color_map = {'Long': 'red', 'Short': 'blue', 'N/A': 'green'}
                
                # Plot each Size Condition 
                for size_cond in df_raw['Size'].unique():
                    base_color = color_map.get(size_cond, 'gray') # Default to gray if something goes wrong
                    
                    # 1. Individual Subjects (Transparent Colors)
                    size_raw = df_raw[df_raw['Size'] == size_cond]
                    for subj in size_raw['Subject_ID'].unique():
                        subj_data = size_raw[size_raw['Subject_ID'] == subj]
                        
                        # Faint Individual Dots
                        fig.add_trace(go.Scatter(
                            x=subj_data['X_Value'], y=subj_data['Percent_Faster'] * 100, 
                            mode='markers', showlegend=False,
                            marker=dict(color=base_color, size=6), opacity=0.3
                        ))
                        
                        # Faint Individual Curve
                        if not df_ind_fits.empty:
                            subj_fit = df_ind_fits[(df_ind_fits['Subject_ID'] == subj) & (df_ind_fits['Size'] == size_cond)]
                            if not subj_fit.empty:
                                fig.add_trace(go.Scatter(
                                    x=subj_fit['X_Value'], y=subj_fit['Fit_Percent'], 
                                    mode='lines', showlegend=False,
                                    line=dict(color=base_color, width=1), opacity=0.2
                                ))

                    # 2. Grand Average (Bold Colors)
                    if not df_avg_fit.empty:
                        size_avg_fit = df_avg_fit[df_avg_fit['Size'] == size_cond]
                        avg_raw = size_raw.groupby('X_Value')['Percent_Faster'].mean().reset_index()
                        
                        label_name = f'Group Avg ({size_cond})' if size_cond != 'N/A' else 'Group Average Fit'
                        
                        # Bold Average Dots
                        fig.add_trace(go.Scatter(
                            x=avg_raw['X_Value'], y=avg_raw['Percent_Faster'] * 100,
                            mode='markers', showlegend=False,
                            marker=dict(color=base_color, size=10, line=dict(color='black', width=1)),
                            opacity=1.0
                        ))
                        
                        # Bold Average Curve
                        fig.add_trace(go.Scatter(
                            x=size_avg_fit['X_Value'], y=size_avg_fit['Fit_Percent'],
                            mode='lines', name=label_name,
                            line=dict(color=base_color, width=4),
                            opacity=1.0
                        ))

                    # 3. Plot the PSE Threshold Line
                    if size_cond in pse_dict and not pd.isna(pse_dict[size_cond]):
                        pse_val = pse_dict[size_cond]
                        fig.add_vline(x=pse_val, line_dash="dash", line_color=base_color)

                # The 50% anchor line
                fig.add_hline(y=50, line_dash="dot", line_color="gray", annotation_text="50%")

                fig.update_layout(
                    title=title, xaxis_title=x_label,
                    yaxis_title="% 'Faster' Responses" if "Control" in title else "",
                    yaxis_range=[-5, 105], height=450, margin=dict(l=20, r=20, t=40, b=20),
                    legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5)
                )
                return fig

            # --- FETCH DATA & RENDER SIDE-BY-SIDE ---
            control_pack, exp_pack = get_rotating_line_data()
            
            if control_pack is not None and exp_pack is not None:
                plot_col_left, plot_col_right = st.columns(2)
                
                c_df, c_ind, c_avg, c_pse_dict = control_pack
                e_df, e_ind, e_avg, e_pse_dict = exp_pack
                
                with plot_col_left:
                    fig_control = build_psychometric_plot(c_df, c_ind, c_avg, c_pse_dict, "Control (No Aperture)", "Rotational Speed (RPM)")
                    st.plotly_chart(fig_control, use_container_width=True, config=PLOTLY_CONFIG)
                    
                    if 'Long' in c_pse_dict: st.info(f"**Long Line PSE:** {c_pse_dict['Long']:.2f} RPM")
                    if 'Short' in c_pse_dict: st.info(f"**Short Line PSE:** {c_pse_dict['Short']:.2f} RPM")
                        
                with plot_col_right:
                    fig_exp = build_psychometric_plot(e_df, e_ind, e_avg, e_pse_dict, "Experimental (With Aperture)", "Speed Modulation Amount")
                    st.plotly_chart(fig_exp, use_container_width=True, config=PLOTLY_CONFIG)
                    
                    if 'N/A' in e_pse_dict: st.success(f"**Experimental Group PSE:** {e_pse_dict['N/A']:.2f} Mod Units")
            else:
                st.warning("Fetching secure data from GitHub pipeline... Please wait or verify your connection.")
            
        with rl_tabs[2]:
            st.subheader("Main Findings: Visual Size & The Nulling Effect")
            
            import plotly.graph_objects as go
            
            # Fetch the data
            control_pack, exp_pack = get_rotating_line_data()
            
            c_df, c_ind, c_avg, c_pse_dict = control_pack
            e_df, e_ind, e_avg, e_pse_dict = exp_pack

            # Group Averages (for the annotation lines)
            c_pse_long = c_pse_dict.get('Long', 60)
            c_pse_short = c_pse_dict.get('Short', 50)
            e_pse = e_pse_dict.get('N/A', 1.5)

            # Extract Individual PSE lists for the Beeswarm plots
            ind_pse_long = c_ind[c_ind['Size'] == 'Long'][['Subject_ID', 'PSE']].drop_duplicates()['PSE'].tolist()
            ind_pse_short = c_ind[c_ind['Size'] == 'Short'][['Subject_ID', 'PSE']].drop_duplicates()['PSE'].tolist()
            ind_pse_exp = e_ind[['Subject_ID', 'PSE']].drop_duplicates()['PSE'].tolist()

            st.divider()

            # =========================================================
            # FIGURE 1: Control (Size-Speed Illusion)
            # =========================================================
            st.markdown("### 1. The Size-Speed Illusion (No Aperture)")
            st.write("Even without an aperture, human vision naturally perceives longer objects as moving slower than shorter objects rotating at the exact same physical speed.")
            
            fig1 = go.Figure()
            
            # Box 1: Long Line
            fig1.add_trace(go.Box(
                y=ind_pse_long, x=[0] * len(ind_pse_long),
                name='Long Line', marker_color='red',
                boxpoints='all', jitter=0.3, pointpos=0, # pointpos=0 centers the beeswarm over the box
                fillcolor='rgba(255,0,0,0.2)', line=dict(width=2)
            ))
            
            # Box 2: Short Line
            fig1.add_trace(go.Box(
                y=ind_pse_short, x=[1] * len(ind_pse_short),
                name='Short Line', marker_color='blue',
                boxpoints='all', jitter=0.3, pointpos=0,
                fillcolor='rgba(0,0,255,0.2)', line=dict(width=2)
            ))

            # --- ANNOTATION: The Vertical Gap Line ---
            delta = abs(c_pse_long - c_pse_short)
            higher_val = max(c_pse_long, c_pse_short)
            lower_val = min(c_pse_long, c_pse_short)
            
            # Draw vertical dashed line exactly between the boxes (x=0.5)
            fig1.add_shape(type="line", x0=0.5, y0=lower_val, x1=0.5, y1=higher_val, line=dict(color="black", width=2, dash="dash"))
            fig1.add_shape(type="line", x0=0.45, y0=lower_val, x1=0.55, y1=lower_val, line=dict(color="black", width=2))
            fig1.add_shape(type="line", x0=0.45, y0=higher_val, x1=0.55, y1=higher_val, line=dict(color="black", width=2))

            fig1.add_annotation(
                x=0.52, y=(higher_val + lower_val)/2,
                text=f"Gap: {delta:.1f} RPM",
                showarrow=False, font=dict(size=13, color="black"), align="left", xanchor="left"
            )

            fig1.update_layout(
                showlegend=False,
                yaxis_title="Physical RPM Required for Equality",
                xaxis=dict(showticklabels=False, range=[-0.5, 1.5]), # Force perfect centering
                height=350, margin=dict(l=0, r=0, t=20, b=0) # Removed side margins to align with Streamlit columns!
            )
            st.plotly_chart(fig1, use_container_width=True, config=PLOTLY_CONFIG)

            # --- HTML DEMOS CENTERED UNDER BOXES ---
            # We add a 15% spacer on the left to perfectly absorb the width of the Plotly Y-Axis!
            spacer_left, col1, col2, spacer_right = st.columns([0.15, 1, 1, 0.05])
            
            with col1: 
                render_mini_demo('long', speed=c_pse_long, size=50)
            with col2: 
                render_mini_demo('short', speed=c_pse_short, size=50)

            st.divider()

            # =========================================================
            # FIGURE 2: Experimental (The Aperture Nulling Effect)
            # =========================================================
            st.markdown("### 2. Nulling the Rotating Line Illusion")
            st.write("By mapping the speed modulation factor directly to the perceived deformation caused by the aperture, we can completely nullify the illusion.")

            plot_col, demo_col = st.columns([4, 1])

            # Define static plot dimensions to feed into our pixel-tracking math
            plot_height = 400 
            top_margin = 20
            bottom_margin = 20

            with plot_col:
                fig2 = go.Figure()
                fig2.add_trace(go.Box(
                    y=ind_pse_exp, name='Group PSE',
                    marker_color='green', boxpoints='all', jitter=0.3, pointpos=0,
                    fillcolor='rgba(0,128,0,0.2)', line=dict(width=2)
                ))
                
                fig2.add_hline(y=4.0, line_dash="dot", line_color="red", annotation_text="Over-Modulated")
                fig2.add_hline(y=e_pse, line_dash="dash", line_color="green", annotation_text="Subjective Equality (PSE)")
                fig2.add_hline(y=0.0, line_dash="solid", line_color="blue", annotation_text="Unmodulated (Max Illusion)")

                fig2.update_layout(
                    showlegend=False,
                    yaxis_title="Speed Modulation Factor",
                    yaxis_range=[-3, 5], # NEW: Expanded scale
                    xaxis=dict(showticklabels=False), 
                    height=plot_height, 
                    margin=dict(l=0, r=0, t=top_margin, b=bottom_margin)
                )
                st.plotly_chart(fig2, use_container_width=True, config=PLOTLY_CONFIG)

            with demo_col:
                # --- DYNAMIC Y-AXIS TRACKING MATH ---
                # We calculate the exact pixel spacing needed to perfectly align the centers 
                # of the 50px HTML canvases with the exact heights of the Plotly Y-Axis lines.
                plot_area_height = plot_height - top_margin - bottom_margin
                y_max, y_min = 5.0, -3.0
                y_range = y_max - y_min
                px_per_unit = plot_area_height / y_range
                
                # Calculate pixel distance from the very top of the Plotly figure to the center of each line
                center_4 = top_margin + (y_max - 4.0) * px_per_unit
                center_pse = top_margin + (y_max - e_pse) * px_per_unit
                center_0 = top_margin + (y_max - 0.0) * px_per_unit
                
                # Subtract 25px (half the canvas size) to find the top edge of each canvas,
                # then calculate the pure empty space needed between them.
                gap_1 = max(0, center_4 - 25) 
                gap_2 = max(0, (center_pse - 25) - (center_4 + 25)) 
                gap_3 = max(0, (center_0 - 25) - (center_pse + 25)) 

                # Render the dynamically spaced column using invisible HTML blocks
                st.markdown(f"<div style='height: {gap_1}px'></div>", unsafe_allow_html=True)
                render_mini_demo('aperture', modulation=4.0, size=50) 
                
                st.markdown(f"<div style='height: {gap_2}px'></div>", unsafe_allow_html=True)
                render_mini_demo('aperture', modulation=e_pse, size=50) 
                
                st.markdown(f"<div style='height: {gap_3}px'></div>", unsafe_allow_html=True)
                render_mini_demo('aperture', modulation=0.0, size=50)

            st.divider()

            # =========================================================
            # THEORETICAL MODELING
            # =========================================================
            st.markdown("### 3. Theoretical Modeling: Local Motion Signals")
            st.markdown("""
            As detailed in **Porter et al. (2011)** regarding rotating ellipses, the human visual system relies heavily on **local orthogonal motion signals** (component vectors) to interpret global object motion. 
            
            In the models below, the **green lines** represent the true physical velocity vectors ($v = \omega \cdot r$). Notice how the tip vectors in the *Unmodulated Aperture* shrink drastically as the line approaches the vertical axis. By applying the mathematical PSE Modulation, we dynamically alter $\omega$ to perfectly counteract the shrinking $r$, keeping the tip vectors constant and neutralizing the visual distortion!
            """)

            mod_col1, mod_col2, mod_col3, mod_col4 = st.columns(4)
            
            with mod_col1:
                render_vector_demo('short', speed=50)
                st.markdown("<p style='text-align: center; margin-top: 5px;'><b>1. Short Line</b></p>", unsafe_allow_html=True)
                
            with mod_col2:
                render_vector_demo('long', speed=50)
                st.markdown("<p style='text-align: center; margin-top: 5px;'><b>2. Long Line</b></p>", unsafe_allow_html=True)
                
            with mod_col3:
                render_vector_demo('aperture', modulation=0.0, speed=50)
                st.markdown("<p style='text-align: center; margin-top: 5px;'><b>3. Aperture (0.0 Mod)</b></p>", unsafe_allow_html=True)
                
            with mod_col4:
                render_vector_demo('aperture', modulation=e_pse, speed=50)
                st.markdown(f"<p style='text-align: center; margin-top: 5px;'><b>4. Aperture (Nullified)</b></p>", unsafe_allow_html=True)

# =====================================================================
# TAB 3: VISUAL WORKING MEMORY (Index 2)
# =====================================================================
with tabs[2]:    
    st.markdown("### Interactive VWM Frequency Tagging Paradigm")
    st.write("Click below to experience the encoding phase. Maintain fixation on the center cross while the visual stimuli flicker at precise frequencies (3Hz and 5Hz).")
    
    if st.button("Run Mini-Experiment", key="run_vwm"):
        render_vwm_demo()
        st.caption("Rendering via HTML5 Canvas. Left stimulus: 3Hz, Right stimulus: 5Hz.")
        
    st.divider()
    
    # --- SUB-TABS FOR DATA ANALYSIS ---
    vwm_tabs = st.tabs([
        "1. Behavioral Findings", 
        "2. EEG & FFT Results", 
        "3. Control Data & Analysis", 
        "4. Additional Projects"
    ])
    
    # --- SUB-TABS FOR DATA ANALYSIS ---
    vwm_tabs = st.tabs([
        "1. Behavioral Findings", 
        "2. EEG Data Initial Preprocessing and Visualization", 
        "3. EEG Frequency Tagging Analysis", 
        "4. Additional Projects"
    ])
    
    with vwm_tabs[0]:
        st.markdown("#### Behavioral Accuracy: Simultaneous vs. Sequential Full-Report")
        df_beh = get_vwm_behavioral_data()
        
        if not df_beh.empty:
            # Create a percentage column for easier plotting
            df_beh['Correct_Pct'] = df_beh['Correct'] * 100
            
            # ---------------------------------------------------------
            # FIGURE 2A: Overall Accuracy by Task
            # ---------------------------------------------------------
            st.markdown("##### Overall Accuracy by Recall Type")
            st.write("Participants performed significantly better in the simultaneous recall condition compared to the sequential condition.")
            
            acc_overall = df_beh.groupby('Task')['Correct_Pct'].mean().reset_index()
            # Calculate standard error for error bars if desired (omitted for clean Plotly defaults, but mean is exact)
            
            fig_2a = px.bar(acc_overall, x='Task', y='Correct_Pct', color='Task',
                            title="Figure 2A: Overall Accuracy",
                            labels={'Correct_Pct': 'Accuracy (% Correct)', 'Task': 'Recall Type'},
                            range_y=[0, 100])
            
            # Add the 10% estimated chance line
            fig_2a.add_hline(y=10, line_dash="dash", line_color="black", annotation_text="Chance")
            st.plotly_chart(fig_2a, use_container_width=True, config=PLOTLY_CONFIG)
            
            st.divider()
            
            # ---------------------------------------------------------
            # FIGURE 2B: Accuracy by Response Order
            # ---------------------------------------------------------
            st.markdown("##### Accuracy by Response Order")
            st.write("Performance was better for early responses, and the slope of performance was steeper in the simultaneous task.")
            
            # Group by Task and Trial_Order
            acc_order = df_beh.groupby(['Task', 'Trial_Order'])['Correct_Pct'].mean().reset_index()
            
            # Ensure Trial_Order is treated as a categorical string for the X-axis
            acc_order['Response Order'] = acc_order['Trial_Order'].apply(lambda x: f"{int(x)} Item")
            
            fig_2b = px.bar(acc_order, x='Response Order', y='Correct_Pct', color='Task', barmode='group',
                            title="Figure 2B: Accuracy by Response Order",
                            labels={'Correct_Pct': 'Accuracy (% Correct)'},
                            range_y=[0, 100])
            st.plotly_chart(fig_2b, use_container_width=True, config=PLOTLY_CONFIG)
            
            st.divider()
            
            # ---------------------------------------------------------
            # FIGURE 2C: Percentage of Trials by Number of Items Remembered
            # ---------------------------------------------------------
            st.markdown("##### Distribution of Items Remembered")
            st.write("Consistent with a 'subset-of-items' model, the majority of trials resulted in two items being correctly recalled.")
            
            # To calculate items recalled PER TRIAL, we need to group the 4 rows that make up a single trial.
            # We create a synthetic 'Trial_ID' by assuming every 4 rows per subject/task is one trial.
            df_beh['Trial_ID'] = df_beh.groupby(['Subject_ID', 'Task']).cumcount() // 4
            
            # Sum the 'Correct' column (0 or 1) across the 4 items in each trial
            trials_summary = df_beh.groupby(['Subject_ID', 'Task', 'Trial_ID'])['Correct'].sum().reset_index()
            trials_summary.rename(columns={'Correct': 'Items_Remembered'}, inplace=True)
            
            # Calculate the percentage of trials for each bin (0, 1, 2, 3, 4 items) per task
            task_counts = trials_summary.groupby('Task').size()
            dist_df = trials_summary.groupby(['Task', 'Items_Remembered']).size().reset_index(name='Count')
            
            # Normalize to percentages
            dist_df['Percentage of Trials'] = dist_df.apply(
                lambda row: (row['Count'] / task_counts[row['Task']]) * 100, axis=1
            )
            
            fig_2c = px.bar(dist_df, x='Items_Remembered', y='Percentage of Trials', color='Task', barmode='group',
                            title="Figure 2C: Percentage of Trials by Number of Items Remembered",
                            labels={'Items_Remembered': 'Number of Items Remembered'},
                            range_y=[0, 100])
            
            # Ensure the X-axis shows all numbers 0-4 discretely
            fig_2c.update_xaxes(tickmode='linear', tick0=0, dtick=1)
            st.plotly_chart(fig_2c, use_container_width=True, config=PLOTLY_CONFIG)
            
        else:
            st.info("Loading Behavioral Data from GitHub...")

    with vwm_tabs[1]:
        st.markdown("#### EEG Analysis: VEPs and SSVEP Signal-to-Noise Ratio (SNR)")
        
        df_time, df_power = get_vwm_eeg_data()
        
        if df_time is not None and not df_time.empty:
            # 1. VISUAL EVOKED POTENTIAL (VEP)
            st.markdown("##### Occipital ROI Grand Average (Time-Series)")
            st.write("This waveform represents the neural activity averaged across the posterior occipital-parietal cluster.")
            
            # Let the user pick a task to view
            selected_task = st.radio("Select Task to View VEP:", df_time['Task'].unique(), horizontal=True)
            
            df_plot_time = df_time[df_time['Task'] == selected_task]
            grand_waveform = df_plot_time.groupby(['Condition', 'Time_s'])['Amplitude_uV'].mean().reset_index()
            
            fig_time = px.line(grand_waveform, x='Time_s', y='Amplitude_uV', color='Condition',
                               title=f"Grand Average VEP ({selected_task} Task)",
                               labels={'Time_s': 'Time (s)', 'Amplitude_uV': 'Amplitude (µV)'})
            st.plotly_chart(fig_time, use_container_width=True, config=PLOTLY_CONFIG)
            
        if df_power is not None and not df_power.empty:
            st.divider()
            # 2. SSVEP SIGNAL-TO-NOISE RATIO
            st.markdown("##### SSVEP Frequency Tagging (SNR)")
            st.write("Replicating Figure 3: Analyzing the Signal-to-Noise ratio of the visual flicker frequencies.")
            
            # For a basic overview, let's average the SNR across all channels for now
            # (We will build the 256-channel Topographic Maps in the next step!)
            snr_cols = [col for col in df_power.columns if 'SNR' in col]
            
            # Melt the dataframe so we can plot all frequencies side-by-side
            df_power_melted = df_power.melt(id_vars=['Subject_ID', 'Task', 'Condition', 'Channel'], 
                                            value_vars=snr_cols, 
                                            var_name='Frequency', value_name='SNR')
            
            # Average across channels and subjects to get the Grand Mean SNR per frequency
            grand_snr = df_power_melted.groupby(['Task', 'Frequency'])['SNR'].mean().reset_index()
            
            fig_snr = px.bar(grand_snr, x='Frequency', y='SNR', color='Task', barmode='group',
                             title="Grand Average SNR by Frequency Tag",
                             labels={'SNR': 'Signal-to-Noise Ratio'})
            st.plotly_chart(fig_snr, use_container_width=True, config=PLOTLY_CONFIG)

# --- PLACEHOLDERS FOR REMAINING TABS ---
for i in range(3, 5):
    with tabs[i]:
        st.subheader(narratives[i]["header"])
        st.write(narratives[i]["blurb"])
        
        # Load static images as placeholders for now
        img_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "documents", narratives[i]["image_file"])
        if os.path.exists(img_path):
            st.image(img_path, width=400)
        
        st.warning("Interactive Python pipeline currently under construction.")

st.divider()

# ==========================================
# REFERENCES SECTION
# ==========================================
references = get_references_metadata()
st.header("Academic & Professional References")
ref_cols = st.columns(3)

for i, ref in enumerate(references):
    with ref_cols[i % 3]:
        st.markdown(f"""
            <div class="ref-card">
                <p class="ref-name" style="font-weight: bold; font-size: 1.1rem; margin-bottom: 0;">{ref['name']}</p>
                <p class="ref-title" style="font-size: 0.9rem; color: #475569; margin-bottom: 0.5rem;">{ref['title']}</p>
                <p style="font-size: 0.95rem;"><a href="mailto:{ref['contact']}" style="text-decoration: none; color: #0284c7;">✉️ {ref['contact']}</a></p>
            </div>
        """, unsafe_allow_html=True)
