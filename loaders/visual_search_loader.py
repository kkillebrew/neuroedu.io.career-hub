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
    if not raw_trials:
        return None, None, "No empirical data logged yet. Be the first to start the experiment!"

    df = pd.DataFrame(raw_trials)
    df = df.dropna(subset=['condition', 'set_size', 'reaction_time'])
    df = df[df['reaction_time'] > 5.0]
    
    if len(df) < 5:
        return None, None, "Insufficient data points to model serial vs parallel processing."

    # NEW: Dictionary mapping the raw database conditions to the requested Labels & Colors
    style_map = {
        'Conjunction': {'label': 'Conjunction (Color)', 'color': '#EF4444'},  # Red
        'Spatial':     {'label': 'Conjunction (Letter)', 'color': '#A78BFA'}, # Purple
        'Color':       {'label': 'Popout (Color)', 'color': '#FACC15'},       # Yellow
        'Shape':       {'label': 'Popout (Letter)', 'color': '#3B82F6'}       # Blue
    }

    user_means = df[df['user_id'] == current_user_uid].groupby(['condition', 'set_size'])['reaction_time'].mean().reset_index()
    global_means = df.groupby(['condition', 'set_size'])['reaction_time'].mean().reset_index()

    fig_reg = go.Figure()
    user_stats = {}
    
    for condition, style in style_map.items():
        # Global Cohort (Solid)
        g_cond = global_means[global_means['condition'] == condition]
        if len(g_cond) >= 2:
            slope_g, int_g, _, _, _ = linregress(g_cond['set_size'], g_cond['reaction_time'])
            fig_reg.add_trace(go.Scatter(
                x=[25, 100], y=[slope_g * 25 + int_g, slope_g * 100 + int_g],
                mode='lines', name=f"{style['label']} - Group",
                line=dict(color=style['color'], width=3, dash='solid')
            ))

        # Active User (Dashed)
        u_cond = user_means[user_means['condition'] == condition]
        if len(u_cond) >= 2:
            slope_u, int_u, r_u, p_u, _ = linregress(u_cond['set_size'], u_cond['reaction_time'])
            user_stats[condition] = {'slope': slope_u, 'intercept': int_u, 'p': p_u}
            fig_reg.add_trace(go.Scatter(
                x=u_cond['set_size'], y=u_cond['reaction_time'],
                mode='lines+markers', name=f"{style['label']} - You",
                line=dict(color=style['color'], width=2, dash='dash'),
                marker=dict(color=style['color'], size=10, line=dict(color='#FFF', width=1))
            ))

    # Center-Right Legend Placement
    fig_reg.update_layout(
        title="Reaction Time by Set Size: You vs. Global Cohort",
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="#F8FAFC",
        margin=dict(l=10, r=150, t=40, b=10), height=350, # Added right margin space for legend
        legend=dict(yanchor="middle", y=0.5, xanchor="left", x=1.02, bgcolor="rgba(0,0,0,0)", font=dict(size=10)),
        xaxis=dict(title="Set Size (Number of Items)", gridcolor="rgba(148, 163, 184, 0.12)", tickvals=[25, 100]),
        yaxis=dict(title="Reaction Time (ms)", gridcolor="rgba(148, 163, 184, 0.12)")
    )

    user_cond_means = df.groupby(['user_id', 'condition', 'set_size'])['reaction_time'].mean().reset_index()
    pivot_df = user_cond_means.pivot(index=['user_id', 'condition'], columns='set_size', values='reaction_time').reset_index()
    pivot_df = pivot_df.dropna(subset=[25, 100])
    pivot_df['search_cost'] = pivot_df[100] - pivot_df[25]

    fig_box = go.Figure()
    
    for condition, style in style_map.items():
        cond_data = pivot_df[pivot_df['condition'] == condition]
        if not cond_data.empty:
            fig_box.add_trace(go.Box(
                x=[style['label']] * len(cond_data), y=cond_data['search_cost'],
                name=f"{style['label']} - Group", boxpoints='all', jitter=0.3, pointpos=-1.5,
                marker=dict(color=style['color']), showlegend=False
            ))
            u_data = cond_data[cond_data['user_id'] == current_user_uid]
            if not u_data.empty:
                fig_box.add_trace(go.Scatter(
                    x=[style['label']], y=u_data['search_cost'],
                    mode='markers', name=f"{style['label']} - You",
                    marker=dict(color='#F8FAFC', size=14, symbol='star', line=dict(color=style['color'], width=2))
                ))

    fig_box.update_layout(
        boxmode='group', 
        title="Search Cost Penalty (RT Difference: 100 Items - 25 Items)",
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="#F8FAFC",
        margin=dict(l=10, r=150, t=40, b=10), height=350,
        legend=dict(yanchor="middle", y=0.5, xanchor="left", x=1.02, bgcolor="rgba(0,0,0,0)", font=dict(size=10)),
        yaxis=dict(title="Penalty Added (ms)", gridcolor="rgba(148, 163, 184, 0.12)")
    )

    return fig_reg, fig_box, user_stats