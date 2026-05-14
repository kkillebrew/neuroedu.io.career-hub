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
    PLOTLY_CONFIG
)

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

# Create the Tabs Layout
tabs = st.tabs([
    "🧩 1. Biomarkers of Psychosis (SFM)", 
    "👁️ 2. Eye-Tracking", 
    "🧠 3. Neural Modeling", 
    "📊 4. Visual Biases", 
    "🎯 5. Ensemble Encoding"
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
        # Fetch a baseline copy of the data just for Tab 1
        df_tab1 = get_sfm_data(apply_qc=True) 
        
        # --- SECTION 1: Histograms ---
        st.subheader("1. Distribution Profiles")
        hist_choice = st.selectbox(
            "Select Distribution to View:", 
            ["Percept Durations", "Participant Responses", "Reaction Times"],
            index=0 
        )
        
        if hist_choice == "Percept Durations":
            df_pd = get_percept_duration_data(df_tab1)
            fig_hist = px.histogram(df_pd, x="Duration_Sec", color="Task_Type", barmode="overlay", nbins=50, title="Percept Durations")
            st.plotly_chart(fig_hist, use_container_width=True)
            
        elif hist_choice == "Participant Responses":
            df_counts = get_response_counts_data(df_tab1)
            df_melt = df_counts.melt(id_vars=['Subject', 'Task_Type'], value_vars=['Left_Presses', 'Right_Presses'], var_name='Key', value_name='Count')
            fig_hist = px.box(df_melt, x="Key", y="Count", color="Task_Type", points="all", title="Participant Responses (Left vs Right)")
            fig_hist.update_traces(jitter=0.6, pointpos=0, width=0.3) # Narrow box, wide dots
            st.plotly_chart(fig_hist, use_container_width=True)
            
        elif hist_choice == "Reaction Times":
            df_rt = get_rt_histogram_data(df_tab1)
            fig_hist = px.histogram(df_rt, x="Reaction_Time_Sec", nbins=50, title="Reaction Times (Control Task)")
            st.plotly_chart(fig_hist, use_container_width=True)
        
        with st.expander("View Legacy pHCP Reference (EPS)"):
            if hist_choice == "Percept Durations":
                st.image("documents/pHCP_EPS_Files/HistOfPercDurations.png")
            elif hist_choice == "Participant Responses":
                st.image("documents/pHCP_EPS_Files/HistOfPartResponses.png")
            elif hist_choice == "Reaction Times":
                st.image("documents/pHCP_EPS_Files/HistOfReactionTimes.png")
                
        st.divider()
        
        # --- SECTION 2: Control Task Performance ---
        st.subheader("2. Control Task Performance")
        col1, col2, col3 = st.columns(3) # <-- Changed to 3 columns
        
        with col1:
            df_pd_ctrl = get_percept_duration_data(df_tab1)
            df_dir = df_pd_ctrl[df_pd_ctrl['Task_Type'] == 'Control'].groupby(['Subject', 'Direction'])['Duration_Sec'].sum().reset_index()
            fig_dir = px.box(df_dir, x="Direction", y="Duration_Sec", points="all", title="Duration Away/Towards")
            fig_dir.update_traces(jitter=0.6, pointpos=0, width=0.3)
            st.plotly_chart(fig_dir, use_container_width=True)

        with col2:
            df_acc = get_accuracy_data(df_tab1)
            fig_acc = px.box(df_acc, y="Control_Correct_Responses", points="all", title="Task Accuracy (Max 11)")
            fig_acc.update_traces(jitter=0.6, pointpos=0, width=0.3)
            st.plotly_chart(fig_acc, use_container_width=True)
            
        with col3:
            df_rt_all = get_rt_histogram_data(df_tab1)
            df_rt_ave = df_rt_all.groupby('Subject')['Reaction_Time_Sec'].mean().reset_index()
            fig_rt_ave = px.box(df_rt_ave, y="Reaction_Time_Sec", points="all", title="Average RT")
            fig_rt_ave.update_traces(jitter=0.6, pointpos=0, width=0.3)
            st.plotly_chart(fig_rt_ave, use_container_width=True)
            
        with st.expander("View Legacy pHCP References (EPS)"):
            ref_col1, ref_col2, ref_col3 = st.columns(3)
            with ref_col1: st.image("documents/pHCP_EPS_Files/AveDurAwayTowards.png", caption="pHCP Ave Dur Away/Towards")
            with ref_col2: st.image("documents/pHCP_EPS_Files/PaperFig_AccFULL.png", caption="pHCP Accuracy")
            with ref_col3: st.image("documents/pHCP_EPS_Files/AveRT.png", caption="pHCP Average RT")

        st.divider()
        
        # --- SECTION 3: Test-Retest Reliability ---
        st.subheader("3. Test-Retest Reliability")
        col4, col5 = st.columns(2)
        df_tr = get_test_retest_data(df_tab1)
        
        with col4:
            fig_corr = px.scatter(df_tr, x="Visit_1_Hz", y="Visit_2_Hz", hover_data=['Subject'], title="Test-Retest Correlation")
            fig_corr.add_shape(type="line", x0=0, y0=0, x1=df_tr['Visit_1_Hz'].max(), y1=df_tr['Visit_1_Hz'].max(), line=dict(dash="dash", color="gray"))
            st.plotly_chart(fig_corr, use_container_width=True)

        with col5:
            fig_diff = px.box(df_tr, y="Hz_Difference", points="all", title="Median Range (V2 - V1)")
            fig_diff.update_traces(jitter=0.6, pointpos=0, width=0.3)
            fig_diff.add_hline(y=0, line_dash="dash", line_color="red")
            st.plotly_chart(fig_diff, use_container_width=True)
            
        with st.expander("View Legacy pHCP References (EPS)"):
            ref_col4, ref_col5 = st.columns(2)
            with ref_col4: st.image("documents/pHCP_EPS_Files/TestRetestSwitchRates.png", caption="pHCP Test-Retest")
            with ref_col5: st.image("documents/pHCP_EPS_Files/TestReTest_MedianRange.png", caption="pHCP Median Range")


    with tab2:
        # --- LIVE DATA DASHBOARD ---
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
                help="Filters out participants who failed to detect at least 7 real switches within 4 seconds."
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
                    ctrl_col, bi_col = 'Control_Dur', 'Bistable_Dur' 
                
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


# --- PLACEHOLDERS FOR REMAINING TABS ---
for i in range(1, 5):
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
