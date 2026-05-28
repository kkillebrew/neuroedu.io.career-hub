"""
=============================================================================
MODULE: loaders/visual_search_loader.py
AUTHOR: Kyle W. Killebrew, PhD
DESCRIPTION:
    The "Model" controller for the Visual Search Experiment.
    Processes raw trial arrays, applies the 5ms ghost-dropout filter,
    and generates Plotly Graph Objects for Treisman & Wolfe search slopes.
=============================================================================
"""
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy.stats import linregress

def process_visual_search_analytics(raw_trials, current_user_uid):
    """
    Cleanses reaction time data, computes Search Cost (RT differences),
    and generates You vs. Global benchmarking models.
    """
    if not raw_trials:
        return None, None, "No empirical data logged yet. Be the first to start the experiment!"

    df = pd.DataFrame(raw_trials)
    
    # --- BLUEPRINT GUARDRAIL: FILTER GHOST DROPOUTS ---
    df = df.dropna(subset=['condition', 'set_size', 'reaction_time'])
    df = df[df['reaction_time'] > 5.0]
    
    if len(df) < 5:
        return None, None, "Insufficient data points to model serial vs parallel processing."

    color_map = {
        'Color': '#38BDF8', 
        'Shape': '#A78BFA', 
        'Spatial': '#F59E0B', 
        'Conjunction': '#EF4444'
    }

    # =========================================================================
    # TAB 1: LINEAR REGRESSION (You vs. Global Cohort)
    # =========================================================================
    # MATLAB Equivalent: groupsummary for user and population
    user_means = df[df['user_id'] == current_user_uid].groupby(['condition', 'set_size'])['reaction_time'].mean().reset_index()
    global_means = df.groupby(['condition', 'set_size'])['reaction_time'].mean().reset_index()

    fig_reg = go.Figure()
    user_stats = {}
    
    for condition in color_map.keys():
        # 1. Plot Global Cohort (Solid Benchmark Lines)
        g_cond = global_means[global_means['condition'] == condition]
        if len(g_cond) >= 2:
            slope_g, int_g, _, _, _ = linregress(g_cond['set_size'], g_cond['reaction_time'])
            fig_reg.add_trace(go.Scatter(
                x=[25, 100], y=[slope_g * 25 + int_g, slope_g * 100 + int_g],
                mode='lines', name=f'{condition} (Global Average)',
                line=dict(color=color_map[condition], width=3, dash='solid'),
                hoverinfo='skip', showlegend=False
            ))

        # 2. Plot Active User (Dashed Lines & Data Markers)
        u_cond = user_means[user_means['condition'] == condition]
        if len(u_cond) >= 2:
            slope_u, int_u, r_u, p_u, _ = linregress(u_cond['set_size'], u_cond['reaction_time'])
            user_stats[condition] = {'slope': slope_u, 'intercept': int_u, 'p': p_u}
            
            fig_reg.add_trace(go.Scatter(
                x=u_cond['set_size'], y=u_cond['reaction_time'],
                mode='lines+markers', name=f'{condition} (You)',
                line=dict(color=color_map[condition], width=2, dash='dash'),
                marker=dict(color=color_map[condition], size=10, line=dict(color='#FFF', width=1))
            ))

    fig_reg.update_layout(
        title="Reaction Time by Set Size: You (Dashed) vs. Global Cohort (Solid)",
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="#F8FAFC",
        margin=dict(l=10, r=10, t=40, b=10), height=350,
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01, bgcolor="rgba(0,0,0,0)", font=dict(size=10)),
        xaxis=dict(title="Set Size (Number of Items)", gridcolor="rgba(148, 163, 184, 0.12)", tickvals=[25, 100]),
        yaxis=dict(title="Reaction Time (ms)", gridcolor="rgba(148, 163, 184, 0.12)")
    )

    # =========================================================================
    # TAB 2: DIFFERENCE SCORES (Search Cost Swarms)
    # =========================================================================
    # MATLAB Equivalent: Pivot table to subtract baseline RT from complex RT
    user_cond_means = df.groupby(['user_id', 'condition', 'set_size'])['reaction_time'].mean().reset_index()
    pivot_df = user_cond_means.pivot(index=['user_id', 'condition'], columns='set_size', values='reaction_time').reset_index()
    
    # Drop users who haven't completed both N=25 and N=100 yet
    pivot_df = pivot_df.dropna(subset=[25, 100])
    
    # Compute the true Search Cost Penalty (Difference Score)
    pivot_df['search_cost'] = pivot_df[100] - pivot_df[25]

    fig_box = go.Figure()
    
    for condition in color_map.keys():
        cond_data = pivot_df[pivot_df['condition'] == condition]
        if not cond_data.empty:
            # Group Beeswarm + Box Distribution
            fig_box.add_trace(go.Box(
                x=[condition] * len(cond_data), y=cond_data['search_cost'],
                name=condition, boxpoints='all', jitter=0.3, pointpos=-1.5,
                marker=dict(color=color_map[condition]), showlegend=False
            ))

            # Active User Location Pinpoint (High-contrast Star)
            u_data = cond_data[cond_data['user_id'] == current_user_uid]
            if not u_data.empty:
                fig_box.add_trace(go.Scatter(
                    x=[condition], y=u_data['search_cost'],
                    mode='markers', name=f"{condition} (You)",
                    marker=dict(color='#F8FAFC', size=14, symbol='star', line=dict(color=color_map[condition], width=2))
                ))

    fig_box.update_layout(
        boxmode='group', 
        title="Search Cost Penalty (RT Difference: 100 Items - 25 Items)",
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="#F8FAFC",
        margin=dict(l=10, r=10, t=40, b=10), height=350,
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01, bgcolor="rgba(0,0,0,0)", font=dict(size=10)),
        yaxis=dict(title="Penalty Added (ms)", gridcolor="rgba(148, 163, 184, 0.12)")
    )

    return fig_reg, fig_box, user_stats