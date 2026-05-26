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
        color_discrete_map={
            "You (Active Session)": "#38BDF8",       # Sky Blue
            "Global Cohort Population": "#475569"    # Muted Slate
        },
        labels={
            "index_difficulty": "Task Difficulty Index (ID in bits)",
            "movement_time": "Average Movement Execution Time (MT in ms)"
        },
        title="Fitts's Law Motor Execution Regression Model",
        hover_data=['index_difficulty', 'movement_time']
    )

    # Add the unified ordinary least squares (OLS) trendline
    id_range = np.linspace(df_grouped['index_difficulty'].min(), df_grouped['index_difficulty'].max(), 50)
    fit_line = slope * id_range + intercept

    # Track mathematical trendline coordinates in separate dataframe
    df_fit = pd.DataFrame({
        'index_difficulty': id_range,
        'movement_time': fit_line,
        'Subject Group': 'Regression Fit Line'
    })

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
    stats_summary = {
        'intercept_a': round(intercept, 1),
        'slope_b': round(slope, 1),
        'r_squared': round(r_value ** 2, 3),
        'p_val': round(p_value, 4)
    }

    return fig, stats_summary