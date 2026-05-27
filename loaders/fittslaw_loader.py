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
import plotly.graph_objects as go
from scipy.stats import linregress

def process_cohort_fitts_regression(raw_trials, current_user_uid):
    if not raw_trials:
        return None, None, "No empirical data logged yet. Be the first to start the experiment!"

    df = pd.DataFrame(raw_trials)
    
    # Validation guardrail
    if 'index_difficulty' not in df.columns or 'movement_time' not in df.columns:
        return None, None, "Database structure mismatch."

    df = df.dropna(subset=['index_difficulty', 'movement_time'])
    if len(df) < 5:
        return None, None, "Too few data points collected to run statistical regression."

    # Round ID bounds slightly to create clean vertical stacks on the X-axis
    df['index_difficulty'] = df['index_difficulty'].round(2)
    df['Subject Group'] = np.where(df['user_id'] == current_user_uid, "You (Active Session)", "Global Cohort Population")

    # --- MATLAB BRIDGE: The 10xN "Cell Array" Collapse ---
    # We group by User ID and Index of Difficulty. 
    # If a user runs the experiment 3 times (N=3), they will have 30 rows. 
    # This function automatically collapses all their repetitive trials at a specific ID into a single user average.
    df_user_means = df.groupby(['user_id', 'Subject Group', 'index_difficulty'])['movement_time'].mean().reset_index()

    # Calculate overall regression using the user-averaged matrix
    slope, intercept, r_value, p_value, std_err = linregress(
        df_user_means['index_difficulty'], 
        df_user_means['movement_time']
    )

    # ==========================================
    # PLOT 1: Linear Regression (User Averages)
    # ==========================================
    fig_reg = px.scatter(
        df_user_means, x='index_difficulty', y='movement_time', color='Subject Group',
        color_discrete_map={"You (Active Session)": "#38BDF8", "Global Cohort Population": "#475569"},
        labels={"index_difficulty": "Task Difficulty Index (ID in bits)", "movement_time": "Average Movement Time (ms)"},
        title="Fitts's Law Motor Execution (User Averages)", opacity=0.8
    )

    id_range = np.linspace(df_user_means['index_difficulty'].min(), df_user_means['index_difficulty'].max(), 50)
    fit_line = slope * id_range + intercept
    
    fig_reg.add_traces(px.line(x=id_range, y=fit_line, color_discrete_sequence=["#10B981"]).update_traces(line=dict(dash="dash", width=2.5)).data[0])
    fig_reg.data[-1].name = "OLS Trendline"
    fig_reg.data[-1].showlegend = True

    fig_reg.update_layout(
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="#F8FAFC",
        margin=dict(l=10, r=10, t=50, b=10), height=320,
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01, bgcolor="rgba(15,23,42,0.6)"),
        xaxis=dict(gridcolor="rgba(148, 163, 184, 0.12)"), yaxis=dict(gridcolor="rgba(148, 163, 184, 0.12)")
    )

    # ==========================================
    # PLOT 2: Opaque Trial Variance vs Bright Averages
    # ==========================================
    fig_swarm = go.Figure()

    # 1. Global Cohort Raw Trials (Transparent Gray/Slate)
    df_cohort = df[df['Subject Group'] == "Global Cohort Population"]
    if not df_cohort.empty:
        fig_swarm.add_trace(go.Box(
            x=df_cohort['index_difficulty'], y=df_cohort['movement_time'],
            name="Cohort Trials", boxpoints='all', jitter=0.4, pointpos=0,
            marker=dict(color='rgba(148, 163, 184, 0.2)', size=4),
            line=dict(color='rgba(148, 163, 184, 0.3)', width=1),
            fillcolor='rgba(0,0,0,0)'
        ))

    # 2. Your Raw Trials (Transparent Blue)
    df_you = df[df['Subject Group'] == "You (Active Session)"]
    if not df_you.empty:
        fig_swarm.add_trace(go.Box(
            x=df_you['index_difficulty'], y=df_you['movement_time'],
            name="Your Trials", boxpoints='all', jitter=0.3, pointpos=0,
            marker=dict(color='rgba(56, 189, 248, 0.4)', size=5),
            line=dict(color='rgba(56, 189, 248, 0.6)', width=1),
            fillcolor='rgba(0,0,0,0)'
        ))

    # 3. Your Averages (Bright Solid Orange Diamonds)
    df_you_means = df_user_means[df_user_means['Subject Group'] == "You (Active Session)"]
    if not df_you_means.empty:
        fig_swarm.add_trace(go.Scatter(
            x=df_you_means['index_difficulty'], y=df_you_means['movement_time'],
            name="Your Averages", mode='markers',
            marker=dict(color='#F59E0B', size=10, symbol='diamond', line=dict(color='#FFFFFF', width=1))
        ))

    fig_swarm.update_layout(
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="#F8FAFC",
        margin=dict(l=10, r=10, t=50, b=10), height=320,
        title="Trial Variance vs. Personal Averages",
        xaxis=dict(title="Task Difficulty Index (ID)", gridcolor="rgba(148, 163, 184, 0.12)"),
        yaxis=dict(title="Movement Time (ms)", gridcolor="rgba(148, 163, 184, 0.12)"),
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01, bgcolor="rgba(15,23,42,0.6)")
    )

    stats_summary = {
        'intercept_a': round(intercept, 1),
        'slope_b': round(slope, 1),
        'r_squared': round(r_value ** 2, 3),
        'p_val': round(p_value, 4)
    }

    # Return BOTH figures along with the stats
    return fig_reg, fig_swarm, stats_summary