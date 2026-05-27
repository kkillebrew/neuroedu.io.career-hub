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
    Cleanses reaction time data and generates parallel vs. serial OLS models.
    """
    if not raw_trials:
        return None, None, "No empirical data logged yet. Be the first to start the experiment!"

    df = pd.DataFrame(raw_trials)
    
    # --- BLUEPRINT GUARDRAIL: FILTER GHOST DROPOUTS ---
    # MATLAB Equivalent: df(df.reaction_time > 5.0, :)
    df = df.dropna(subset=['condition', 'set_size', 'reaction_time'])
    df = df[df['reaction_time'] > 5.0]
    
    if len(df) < 5:
        return None, None, "Insufficient data points to model serial vs parallel processing."

    # Separate User vs Global
    df_user = df[df['user_id'] == current_user_uid]
    
    # Calculate Means
    # MATLAB Equivalent: groupsummary(df, {'condition', 'set_size'}, 'mean', 'reaction_time')
    user_means = df_user.groupby(['condition', 'set_size'])['reaction_time'].mean().reset_index()
    global_means = df.groupby(['condition', 'set_size'])['reaction_time'].mean().reset_index()

    # Define color palette based on expected cognitive load
    color_map = {
        'Color': '#38BDF8',       # Parallel (Pop-out)
        'Shape': '#A78BFA',       # Parallel (Pop-out)
        'Spatial': '#F59E0B',     # Serial (Moderate)
        'Conjunction': '#EF4444'  # Serial (Strict Binding)
    }

    # --- TAB 1: LINEAR REGRESSION (OLS Slopes) ---
    fig_reg = go.Figure()
    
    user_stats = {}
    for condition in color_map.keys():
        u_cond = user_means[user_means['condition'] == condition]
        if len(u_cond) >= 2:
            # SciPy OLS Calculation
            slope, intercept, r_val, p_val, _ = linregress(u_cond['set_size'], u_cond['reaction_time'])
            user_stats[condition] = {'slope': slope, 'intercept': intercept, 'p': p_val}
            
            x_range = np.array([25, 100])
            y_pred = slope * x_range + intercept
            
            # Plot raw user means
            fig_reg.add_trace(go.Scatter(
                x=u_cond['set_size'], y=u_cond['reaction_time'],
                mode='markers', name=f'{condition} (You)',
                marker=dict(color=color_map[condition], size=10, line=dict(color='#FFF', width=1))
            ))
            # Plot User OLS Trendline
            fig_reg.add_trace(go.Scatter(
                x=x_range, y=y_pred,
                mode='lines', name=f'{condition} OLS',
                line=dict(color=color_map[condition], width=2, dash='dash')
            ))

    fig_reg.update_layout(
        title="Reaction Time by Set Size (Parallel vs Serial)",
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="#F8FAFC",
        margin=dict(l=10, r=10, t=40, b=10), height=350,
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01, bgcolor="rgba(0,0,0,0)"),
        xaxis=dict(title="Set Size (Number of Items)", gridcolor="rgba(148, 163, 184, 0.12)", tickvals=[25, 100]),
        yaxis=dict(title="Reaction Time (ms)", gridcolor="rgba(148, 163, 184, 0.12)")
    )

    # --- TAB 2: DISTRIBUTIONS (Boxplots) ---
    fig_box = go.Figure()
    for condition in color_map.keys():
        df_cond_user = df_user[df_user['condition'] == condition]
        if not df_cond_user.empty:
            fig_box.add_trace(go.Box(
                x=df_cond_user['set_size'], y=df_cond_user['reaction_time'],
                name=condition, boxpoints='all', jitter=0.3, pointpos=-1.5,
                marker=dict(color=color_map[condition])
            ))

    fig_box.update_layout(
        boxmode='group', 
        title="Individual Trial Variance",
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="#F8FAFC",
        margin=dict(l=10, r=10, t=40, b=10), height=350,
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01, bgcolor="rgba(0,0,0,0)"),
        xaxis=dict(title="Set Size", gridcolor="rgba(148, 163, 184, 0.12)"),
        yaxis=dict(title="Reaction Time (ms)", gridcolor="rgba(148, 163, 184, 0.12)")
    )

    return fig_reg, fig_box, user_stats