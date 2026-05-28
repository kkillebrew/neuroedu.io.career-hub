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

    # --- SCIENTIFIC GUARDRAIL: FILTER UNREALISTIC dropout/0ms DATA ---
    # Drops empty fields or extreme outliers under 5ms caused by async packet drops
    df = df.dropna(subset=['index_difficulty', 'movement_time'])
    df = df[df['movement_time'] > 5.0]
    
    if len(df) < 5:
        return None, None, "Too few valid data points collected to compute analytics."

    # Round ID bounds to strict intervals to align the vertical groupings neatly
    df['index_difficulty'] = df['index_difficulty'].round(2)

    # ---------------------------------------------------------
    # STEP 1: MATRICES SEPARATION & COLLAPSE
    # ---------------------------------------------------------
    df_you_raw = df[df['user_id'] == current_user_uid]
    df_user_means = df.groupby(['user_id', 'index_difficulty'])['movement_time'].mean().reset_index()

    df_you_mean = df_user_means[df_user_means['user_id'] == current_user_uid]
    df_other_means = df_user_means[df_user_means['user_id'] != current_user_uid]
    df_global_mean = df_user_means.groupby('index_difficulty')['movement_time'].mean().reset_index()

    # ---------------------------------------------------------
    # STEP 2: STATISTICAL REGRESSION (OLS)
    # ---------------------------------------------------------
    user_has_model = False
    try:
        if df_you_mean['index_difficulty'].nunique() >= 2:
            slope_u, int_u, r_u, p_u, _ = linregress(df_you_mean['index_difficulty'], df_you_mean['movement_time'])
            user_has_model = True
        else:
            raise ValueError()
    except Exception:
        slope_u, int_u, r_u, p_u = 0, 0, 0, 1

    try:
        slope_g, int_g, r_g, p_g, _ = linregress(df_global_mean['index_difficulty'], df_global_mean['movement_time'])
    except Exception:
        slope_g, int_g, r_g, p_g = 0, 0, 0, 1

    id_range = np.linspace(df['index_difficulty'].min(), df['index_difficulty'].max(), 50)

    # ---------------------------------------------------------
    # PLOT 1: LINEAR REGRESSION
    # ---------------------------------------------------------
    fig_reg = go.Figure()

    fig_reg.add_trace(go.Scatter(
        x=df_you_raw['index_difficulty'], y=df_you_raw['movement_time'],
        mode='markers', name='Your Raw Trials',
        marker=dict(color='rgba(239, 68, 68, 0.15)', size=5)
    ))

    fig_reg.add_trace(go.Scatter(
        x=df_other_means['index_difficulty'], y=df_other_means['movement_time'],
        mode='markers', name='Other Users (Averages)',
        marker=dict(color='rgba(34, 197, 94, 0.3)', size=6)
    ))

    fig_reg.add_trace(go.Scatter(
        x=df_global_mean['index_difficulty'], y=df_global_mean['movement_time'],
        mode='markers', name='Global Cohort Average',
        marker=dict(color='rgba(34, 197, 94, 1)', size=10, symbol='diamond', line=dict(color='#FFF', width=1))
    ))

    fig_reg.add_trace(go.Scatter(
        x=df_you_mean['index_difficulty'], y=df_you_mean['movement_time'],
        mode='markers', name='Your Processing Average',
        marker=dict(color='rgba(239, 68, 68, 1)', size=10, line=dict(color='#FFF', width=1))
    ))

    fig_reg.add_trace(go.Scatter(
        x=id_range, y=(slope_g * id_range + int_g),
        mode='lines', name='Global OLS',
        line=dict(color='rgba(34, 197, 94, 0.7)', dash='dash', width=2)
    ))
    
    if user_has_model:
        fig_reg.add_trace(go.Scatter(
            x=id_range, y=(slope_u * id_range + int_u),
            mode='lines', name='Your Motor OLS',
            line=dict(color='rgba(239, 68, 68, 1)', dash='dash', width=2.5)
        ))

    fig_reg.update_layout(
        title="Fitts's Law: Individual Bandwidth vs. Global Cohort",
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="#F8FAFC",
        margin=dict(l=10, r=150, t=40, b=10), # Increase right margin (r) to 150 to make room
        legend=dict(yanchor="middle", y=0.5, xanchor="left", x=1.02, bgcolor="rgba(0,0,0,0)", font=dict(color="#F8FAFC")),
        xaxis=dict(title="Index of Difficulty (bits)", gridcolor="rgba(148, 163, 184, 0.12)"),
        yaxis=dict(title="Movement Time (ms)", gridcolor="rgba(148, 163, 184, 0.12)")
    )

    # ---------------------------------------------------------
    # PLOT 2: DISTRIBUTIONS (Side-by-Side Box & Swarm)
    # ---------------------------------------------------------
    fig_swarm = go.Figure()

    fig_swarm.add_trace(go.Box(
        x=df_you_raw['index_difficulty'], y=df_you_raw['movement_time'],
        name="Your Trial Variance", boxpoints='all', jitter=0.3, pointpos=-1.5,
        marker=dict(color='rgba(239, 68, 68, 0.4)', size=4), 
        line=dict(color='rgba(239, 68, 68, 0.8)', width=1.5)
    ))

    fig_swarm.add_trace(go.Box(
        x=df_user_means['index_difficulty'], y=df_user_means['movement_time'],
        name="Cohort Averages Distribution", boxpoints='all', jitter=0.3, pointpos=1.5,
        marker=dict(color='rgba(34, 197, 94, 0.4)', size=5), 
        line=dict(color='rgba(34, 197, 94, 0.8)', width=1.5)
    ))

    fig_swarm.add_trace(go.Scatter(
        x=df_you_mean['index_difficulty'], y=df_you_mean['movement_time'],
        mode='markers', name="Your Average Position",
        marker=dict(color='#F8FAFC', size=12, symbol='star', line=dict(color='#EF4444', width=2))
    ))

    fig_swarm.update_layout(
        boxmode='group', 
        title="Execution Variance & Cohort Placement",
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="#F8FAFC",
        margin=dict(l=10, r=150, t=40, b=10), # Increase right margin (r) to 150 to make room
        legend=dict(yanchor="middle", y=0.5, xanchor="left", x=1.02, bgcolor="rgba(0,0,0,0)", font=dict(color="#F8FAFC")),
        xaxis=dict(title="Index of Difficulty (bits)", gridcolor="rgba(148, 163, 184, 0.12)"),
        yaxis=dict(title="Movement Time (ms)", gridcolor="rgba(148, 163, 184, 0.12)")
    )

    stats_summary = {
        'user': {
            'intercept_a': round(int_u, 1) if user_has_model else "N/A",
            'slope_b': round(slope_u, 1) if user_has_model else "N/A",
            'r_squared': round(r_u ** 2, 3) if user_has_model else "N/A",
            'p_val': (round(p_u, 4) if p_u >= 0.0001 else "<0.0001") if user_has_model else "N/A"
        },
        'global': {
            'intercept_a': round(int_g, 1),
            'slope_b': round(slope_g, 1),
            'r_squared': round(r_g ** 2, 3),
            'p_val': round(p_g, 4) if p_g >= 0.0001 else "<0.0001"
        }
    }

    return fig_reg, fig_swarm, stats_summary