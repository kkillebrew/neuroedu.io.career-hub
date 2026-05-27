"""
=============================================================================
MODULE: loaders/fittslaw_loader.py
AUTHOR: Kyle W. Killebrew, PhD & Data Science Mentorship Engine
STATUS: Active Production Blueprint (Lesson 4)
DESCRIPTION:
    The "Model" controller for the Fitts's Law Experiment dashboard.
    Processes the raw 10xN arrays into distinct user means and global cohort
    comparisons using strict Plotly Graph Objects for layered coloring.
=============================================================================
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy.stats import linregress

def process_cohort_fitts_regression(raw_trials, current_user_uid):
    if not raw_trials:
        return None, None, "No empirical data logged yet. Be the first to start the experiment!"

    df = pd.DataFrame(raw_trials)
    
    if 'index_difficulty' not in df.columns or 'movement_time' not in df.columns:
        return None, None, "Database structure mismatch."

    df = df.dropna(subset=['index_difficulty', 'movement_time'])
    if len(df) < 5:
        return None, None, "Too few data points collected to run statistical regression."

    # Round ID bounds to strict intervals to align the vertical groupings
    df['index_difficulty'] = df['index_difficulty'].round(2)

    # ---------------------------------------------------------
    # STEP 1: MATRICES SEPARATION & "CELL ARRAY" COLLAPSE
    # ---------------------------------------------------------
    # 1. Your Raw Trials (10xN arrays)
    df_you_raw = df[df['user_id'] == current_user_uid]

    # 2. Collapse all raw trials into strict User Averages for each Difficulty Index
    df_user_means = df.groupby(['user_id', 'index_difficulty'])['movement_time'].mean().reset_index()

    # 3. Separate the Averages
    df_you_mean = df_user_means[df_user_means['user_id'] == current_user_uid]
    df_other_means = df_user_means[df_user_means['user_id'] != current_user_uid]

    # 4. Calculate the True Global Cohort Mean (The average of all individual user averages)
    df_global_mean = df_user_means.groupby('index_difficulty')['movement_time'].mean().reset_index()

    # ---------------------------------------------------------
    # STEP 2: STATISTICAL REGRESSION (OLS)
    # ---------------------------------------------------------
    # Regress for Current User
    try:
        # Check if we have enough distinct ID points to run a regression (Min 2 points)
        if df_you_mean['index_difficulty'].nunique() >= 2:
            slope_u, int_u, r_u, p_u, _ = linregress(df_you_mean['index_difficulty'], df_you_mean['movement_time'])
        else:
            # Raise error to trigger the 'except' block if variation is insufficient
            raise ValueError("Insufficient variance")
    except Exception:
        # Fallback values when the user hasn't played enough or varied difficulty enough
        slope_u, int_u, r_u, p_u = 0, 0, 0, 1

    # Regress for Global Cohort
    try:
        slope_g, int_g, r_g, p_g, _ = linregress(df_global_mean['index_difficulty'], df_global_mean['movement_time'])
    except Exception:
        slope_g, int_g, r_g, p_g = 0, 0, 0, 1

    # Define the X-axis sweep for the trendlines
    id_range = np.linspace(df['index_difficulty'].min(), df['index_difficulty'].max(), 50)

    # ---------------------------------------------------------
    # PLOT 1: LINEAR REGRESSION (Bandwidth Modeling)
    # ---------------------------------------------------------
    fig_reg = go.Figure()

    # Layer 1: Faded Red (Your Raw Motor Variance)
    fig_reg.add_trace(go.Scatter(
        x=df_you_raw['index_difficulty'], y=df_you_raw['movement_time'],
        mode='markers', name='Your Raw Trials',
        marker=dict(color='rgba(239, 68, 68, 0.15)', size=5)
    ))

    # Layer 2: Faded Green (Other Individual User Averages)
    fig_reg.add_trace(go.Scatter(
        x=df_other_means['index_difficulty'], y=df_other_means['movement_time'],
        mode='markers', name='Other Users (Averages)',
        marker=dict(color='rgba(34, 197, 94, 0.3)', size=6)
    ))

    # Layer 3: Bright Green (True Global Average)
    fig_reg.add_trace(go.Scatter(
        x=df_global_mean['index_difficulty'], y=df_global_mean['movement_time'],
        mode='markers', name='Global Cohort Average',
        marker=dict(color='rgba(34, 197, 94, 1)', size=10, symbol='diamond', line=dict(color='#FFF', width=1))
    ))

    # Layer 4: Bright Red (Your Calculated Average)
    fig_reg.add_trace(go.Scatter(
        x=df_you_mean['index_difficulty'], y=df_you_mean['movement_time'],
        mode='markers', name='Your Processing Average',
        marker=dict(color='rgba(239, 68, 68, 1)', size=10, line=dict(color='#FFF', width=1))
    ))

    # Layer 5: OLS Trendlines
    fig_reg.add_trace(go.Scatter(
        x=id_range, y=(slope_g * id_range + int_g),
        mode='lines', name='Global OLS',
        line=dict(color='rgba(34, 197, 94, 0.7)', dash='dash', width=2)
    ))
    fig_reg.add_trace(go.Scatter(
        x=id_range, y=(slope_u * id_range + int_u),
        mode='lines', name='Your Motor OLS',
        line=dict(color='rgba(239, 68, 68, 1)', dash='dash', width=2.5)
    ))

    fig_reg.update_layout(
        title="Fitts's Law: Individual Bandwidth vs. Global Cohort",
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="#F8FAFC",
        margin=dict(l=10, r=10, t=40, b=10), height=350,
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01, bgcolor="rgba(15,23,42,0.7)"),
        xaxis=dict(title="Index of Difficulty (bits)", gridcolor="rgba(148, 163, 184, 0.12)"),
        yaxis=dict(title="Movement Time (ms)", gridcolor="rgba(148, 163, 184, 0.12)")
    )

    # ---------------------------------------------------------
    # PLOT 2: DISTRIBUTIONS (Side-by-Side Box & Swarm)
    # ---------------------------------------------------------
    fig_swarm = go.Figure()

    # Group 1 (Red Box): Your Raw Trials
    fig_swarm.add_trace(go.Box(
        x=df_you_raw['index_difficulty'], y=df_you_raw['movement_time'],
        name="Your Trial Variance", boxpoints='all', jitter=0.3, pointpos=-1.5,
        marker=dict(color='rgba(239, 68, 68, 0.4)', size=4), 
        line=dict(color='rgba(239, 68, 68, 0.8)', width=1.5)
    ))

    # Group 2 (Green Box): Global Cohort Averages Distribution
    fig_swarm.add_trace(go.Box(
        x=df_user_means['index_difficulty'], y=df_user_means['movement_time'],
        name="Cohort Averages Distribution", boxpoints='all', jitter=0.3, pointpos=1.5,
        marker=dict(color='rgba(34, 197, 94, 0.4)', size=5), 
        line=dict(color='rgba(34, 197, 94, 0.8)', width=1.5)
    ))

    # Highlighting Overlay: Pinpoint exactly where the user's average sits among the cohort
    fig_swarm.add_trace(go.Scatter(
        x=df_you_mean['index_difficulty'], y=df_you_mean['movement_time'],
        mode='markers', name="Your Average Position",
        marker=dict(color='#F8FAFC', size=12, symbol='star', line=dict(color='#EF4444', width=2))
    ))

    fig_swarm.update_layout(
        boxmode='group', # Forces the red and green boxes to sit side-by-side at each ID tick
        title="Execution Variance & Cohort Placement",
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="#F8FAFC",
        margin=dict(l=10, r=10, t=40, b=10), height=350,
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01, bgcolor="rgba(15,23,42,0.7)"),
        xaxis=dict(title="Index of Difficulty (bits)", gridcolor="rgba(148, 163, 184, 0.12)"),
        yaxis=dict(title="Movement Time (ms)", gridcolor="rgba(148, 163, 184, 0.12)")
    )

    # Pack BOTH statistical parameters for display inside the dashboard
    stats_summary = {
        'user': {
            'intercept_a': round(int_u, 1),
            'slope_b': round(slope_u, 1),
            'r_squared': round(r_u ** 2, 3),
            'p_val': round(p_u, 4) if p_u >= 0.0001 else "<0.0001"
        },
        'global': {
            'intercept_a': round(int_g, 1),
            'slope_b': round(slope_g, 1),
            'r_squared': round(r_g ** 2, 3),
            'p_val': round(p_g, 4) if p_g >= 0.0001 else "<0.0001"
        }
    }

    # Return BOTH figures along with the dual stats dictionary
    return fig_reg, fig_swarm, stats_summary