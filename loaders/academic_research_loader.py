"""
=============================================================================
MODULE: loaders/academic_research_loader.py
AUTHOR: Kyle W. Killebrew, PhD
DESCRIPTION: 
    The "Model" layer for the Academic Research spoke. 
    Handles publications, academic training, and research assets.
    
    --- MATLAB BRIDGE ---
    Equivalent to a dedicated function like `getAcademicData.m` that returns 
    multiple workspace variables (Tables and Structs) for the UI to display.
=============================================================================
"""

import os
import pandas as pd
import numpy as np
import plotly.express as px
from scipy import stats # <--- NEW STATS ENGINE
import re # Import Python's Regular Expression library

    import requests
    from io import BytesIO, StringIO
    import streamlit as st

# --- PLOTLY CONFIGURATION ---
PLOTLY_CONFIG = {'scrollZoom': False, 'displayModeBar': False, 'staticPlot': False}

def get_publications_data():
    """
    Returns a structured DataFrame of all peer-reviewed academic publications.
    MATLAB Equivalent: T = table(Year, Title, Journal, Link)
    """
    return pd.DataFrame({
        'Year': [2024, 2018, 2017, 2015, 2020], 
        'Title': [
            'Faster bi-stable visual switching in psychosis',
            'Electrophysiological correlates of encoding processes in a full-report visual working memory paradigm',
            'Induced and evoked human electrophysiological correlates of visual working memory set-size effects at encoding',
            'Intraparietal regions play a material general role in working memory', 
            'The Neural Representation of Ensemble Mean'
        ],
        'Journal': [
            'Nature (Translational Psychiatry)', 
            'Springer', 
            'PLOS ONE', 
            'PMC / NIH', 
            'UNR (Dissertation/Thesis)'
        ],
        'Link': [
            'https://www.nature.com/articles/s41398-024-02913-z.pdf',
            'https://link.springer.com/content/pdf/10.3758/s13415-018-0574-8.pdf',
            'https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0167022&type=printable',
            'https://pmc.ncbi.nlm.nih.gov/articles/PMC4468015/pdf/nihms689438.pdf',
            'https://scholarwolf.unr.edu/server/api/core/bitstreams/817b85e5-4335-4751-8f2d-605d3bcf7b31/content'
        ]
    }).sort_values('Year', ascending=False)

def get_research_expertise():
    """
    Returns core academic methodologies and domains.
    MATLAB Equivalent: A cell array of character vectors.
    """
    return [
        "High-Density Electroencephalography (EEG)",
        "Visual Working Memory & Perception",
        "Psychosis & Schizophrenia Modeling",
        "Digital Signal Processing (FFT, Time-Frequency Analysis)",
        "Experimental Paradigm Design (Psychtoolbox, PsychoPy)"
    ]

def get_academic_assets():
    """
    Returns metadata for academic downloads.
    MATLAB Equivalent: A scalar struct with string fields.
    """
    return {
        'academic_cv_path': 'documents/kyle_academic_cv.pdf',
        'research_statement': 'documents/kyle_research_statement.pdf'
    }

def get_project_narratives():
    """
    Returns the text blurbs and image metadata for the research project showcases.
    MATLAB Equivalent: A 1xN Struct Array containing text and image filename fields.
    """
    return [
        {
            "header": "Uncovering biomarkers of psychosis",
            "blurb": "Psychotic disorders are debilitating and affect roughly 3% of the US population. According to recent estimates, the economic burden in the US of schizophrenia was 343.2 billion USD. Early identification of these disorders can have dramatic affects on future outcomes which will have direct reliefs on future costs. As the age of onset of these disorders occurs relatively late in life, it is crucial to identify markers of disease onset as soon as possible. One way to identify useful biomarkers is through the careful study of visual dysfunction in these populations. A particularly fruitful avenue of visual dysfunction that can be used to test psychosis is bi-stable perception. It has been shown that people with psychosis alternate between these two percepts at rates different to those of healthy controls.",
            "image_file": "bistableExamples.png"
        },
        {
            "header": "Eye-Tracking In People With Psychosis",
            "blurb": "Eyetracking during visual tasks is one method of differentiating individuals with psychosis from healthy controls. Individuals with psychosis show greater irregularities in both amount of eye movements and blinks and can be reliably predicted based on these numbers. Another predictor of psychosis is pupil dilation which is often attributed to attentional capture which is known to be reduced in psychosis. In this project I used an inverse correlation analysis to directly examine probabilities of increased pupil dilation in response to reported changes in perception and attentional capture in people with psychosis and healthy controls.",
            "image_file": "project1.png"
        },
        {
            "header": "Modeling Neural Data To Predict Viewing Conditions",
            "blurb": "Psychotic individuals show a variety of visual abnormalities and processing deficits which are, in part, responsible for positive psychotic symptoms, such as delusions and hallucinations. In this project, in order to test how impairments in a wide variety of possible neural functions may affect visual processing I modeled the neural processes involved in bi-stable perception using a divisive normalization model. This model utilizes two layers, in which nodes at each layer normalize activity of each other by the average activity within that layer. I found that of the factors tested, attention seems to play the largest role in predicting similar perceptual outcomes to that of psychotic individuals.",
            "image_file": "project2.png"
        },
        {
            "header": "Understanding visual biases when viewing data",
            "blurb": "Understanding how people perceive and understand visualized data (aka graphs and plots) is key to creating easily understandable and interpretable data visualizations. A commonly overlooked aspect of perception that highly affects data visualization is ensemble encoding, the process by which people quickly and efficiently extract high level summary information from perceptual input. For example, in a scatter plot perception of the position of individual data points can be affected by the perception of the average location of all the data points. Thus skewing the perceived location of the data points towards the average location.",
            "image_file": "ensembleExamples.png"
        },
        {
            "header": "Perception Of Group Characteristics Affects Individual Items",
            "blurb": "When objects are presented together as part of a group, people extract summary perceptual information from the group, such as the average location, size, or orientation. In this project I examined how adding visual uncertainty (e.g. noise) might affect their ability to gather visual information about individual objects in the group. I showed that given decreased information for an individual object will lead to an increase in people’s reliance on the average. This has large implications on how to more efficiently present cluttered data visualizations, such as scatter plots or bar charts.",
            "image_file": "project3.png"
        }
    ]

#############################################
#---   Load in the SFM Behavioral Data   ---#
#############################################
# --- PLOTLY CONFIGURATION ---
def get_category_colors():
    """Expanded palette for new psychosis subgroups."""
    return {
        'Controls': '#10b981',             
        'Relatives': '#3b82f6',            
        'PwPP (All)': '#ef4444',           
        'SZ (Schizophrenia)': '#dc2626',   
        'SCA (Schizoaffective)': '#f97316',
        'BIP (Bipolar)': '#8b5cf6',        
        'BIP_COM (Bipolar + Other)': '#d946ef', 
        'Total Sample': '#64748b',         
        'Unknown': '#cbd5e1'
    }

def get_sfm_data(grouping_mode, metric_mode):
    """
    Pure Cloud Architecture: Fetches BOTH the Parquet and CSV dynamically 
    from Private GitHub using secure tokens, merges, and applies de-identification.
    """
    
    # PASTE YOUR RAW GITHUB URLS HERE:
    PARQUET_RAW_URL = "https://github.com/kkillebrew/SFM/blob/main/sfm_dashboard_data.parquet"
    DEMOG_RAW_URL = "https://github.com/kkillebrew/SFM/blob/main/SYON-3TDemographics-DATA-2023-05-11-1249.csv"
    
    # Securely pull the token from DigitalOcean's environment variables (or local secrets)
    try:
        local_secret = st.secrets["GITHUB_TOKEN"]
    except:
        local_secret = None
        
    token = os.environ.get("GITHUB_TOKEN", local_secret)
    headers = {"Authorization": f"token {token}"} if token else {}
    
    df = pd.DataFrame()
    
    # --- 1. FETCH BEHAVIORAL DATA (.parquet) ---
    try:
        p_res = requests.get(PARQUET_RAW_URL, headers=headers)
        if p_res.status_code == 200:
            df = pd.read_parquet(BytesIO(p_res.content))
        else:
            print(f"⚠️ Parquet Fetch Failed. Status Code: {p_res.status_code}")
            return pd.DataFrame() 
    except Exception as e:
        print(f"⚠️ Parquet Fetch Error: {e}")
        return pd.DataFrame()

    if 'Bistable' in df.columns:
        df = df.rename(columns={'Bistable': 'Bistable_Hz', 'Control': 'Real_Switch_Hz'})
        
    df = df[df['Bistable_Hz'] > 0].copy()
    df['Bistable_Dur'] = 1 / df['Bistable_Hz']
    df['Real_Switch_Dur'] = 1 / df['Real_Switch_Hz']
    df['Merge_ID'] = df['Subject'].astype(str).str.replace(r'\D', '', regex=True)

    # --- 2. FETCH DEMOGRAPHICS (.csv) ---
    dx_col = None
    try:
        c_res = requests.get(DEMOG_RAW_URL, headers=headers)
        if c_res.status_code == 200:
            df_demog = pd.read_csv(StringIO(c_res.text))
            id_col = next((c for c in df_demog.columns if 'id' in c.lower() or 'record' in c.lower()), None)
            df_demog['Merge_ID'] = df_demog[id_col].astype(str).str.replace(r'\D', '', regex=True)
            dx_col = next((c for c in df_demog.columns if 'dx' in c.lower() or 'diagnos' in c.lower() and 'id' not in c.lower()), None)
            
            df = pd.merge(df, df_demog, on='Merge_ID', how='left')
        else:
            print(f"⚠️ CSV Fetch Failed. Status Code: {c_res.status_code}")
    except Exception as e:
        print(f"⚠️ CSV Fetch Error: {e}")

    # --- 3. DYNAMIC GROUPING LOGIC ---
    def assign_group(row):
        try:
            subj_num = int(row['Merge_ID'])
            raw_dx = str(row[dx_col]).lower() if dx_col and pd.notna(row[dx_col]) else ""
            
            is_control = subj_num < 2000000
            is_relative = 2000000 <= subj_num < 6000000
            is_pwpp = subj_num >= 6000000
            
            is_sz = is_pwpp and ('schiz' in raw_dx or 'sz' in raw_dx or raw_dx == '2') and 'aff' not in raw_dx
            is_sca = is_pwpp and ('aff' in raw_dx or 'sca' in raw_dx or raw_dx == '3')
            is_bip = is_pwpp and ('bip' in raw_dx or raw_dx in ['4', '5'])
            
            if "Standard" in grouping_mode:
                if is_control: return 'Controls'
                if is_relative: return 'Relatives'
                if is_pwpp: return 'PwPP (All)'
                
            elif "Detailed Psychosis" in grouping_mode:
                if is_control: return 'Controls'
                if is_sz: return 'SZ (Schizophrenia)'
                if is_sca: return 'SCA (Schizoaffective)'
                if is_bip: return 'BIP (Bipolar)'
                return 'EXCLUDE'
                
            elif "SZ vs Bip_Com" in grouping_mode:
                if is_control: return 'Controls'
                if is_sz: return 'SZ (Schizophrenia)'
                if is_pwpp and not is_sz: return 'BIP_COM (Bipolar + Other)'
                return 'EXCLUDE'
                
            elif "Total Combined" in grouping_mode:
                if is_control: return 'Controls'
                if is_relative: return 'Relatives'
                if is_pwpp: return 'PwPP (All)'
                
            return 'Unknown'
        except ValueError: return 'Parse Error'

    df['Group'] = df.apply(assign_group, axis=1)
    df = df[df['Group'] != 'EXCLUDE'].copy()
    
    if "Total Combined" in grouping_mode:
        df_total = df.copy()
        df_total['Group'] = 'Total Sample'
        df = pd.concat([df, df_total], ignore_index=True)
        
    # --- 4. DE-IDENTIFICATION / MASKING ---
    unique_ids = sorted(df['Merge_ID'].unique())
    counters = {'1': 1, '2': 1, '3': 1, '8': 1}
    id_map = {}

    for uid in unique_ids:
        try:
            num = int(uid)
            if num < 2000000: prefix = '1'
            elif 2000000 <= num < 6000000: prefix = '2'
            elif num >= 6000000: prefix = '3'
            else: prefix = '8'
        except ValueError:
            prefix = '8'

        id_map[uid] = f"{prefix}{counters[prefix]:03d}"
        counters[prefix] += 1

    df['Subject'] = df['Merge_ID'].map(id_map)
    df = df.drop(columns=['Merge_ID']) 
    
    return df

def generate_live_statistics(df, metric_col):
    """
    MATLAB Equivalent: Running kruskalwallis() and ttest2().
    Computes live non-parametric stats for the dashboard.
    """
    from scipy import stats
    groups = df['Group'].unique()
    if len(groups) < 2: return "Not enough groups for statistical comparison."
    
    data_arrays = [df[df['Group'] == g][metric_col].dropna().values for g in groups]
    
    try:
        kw_stat, kw_p = stats.kruskal(*data_arrays)
        stats_text = f"**Global Kruskal-Wallis Test:** \n$H = {kw_stat:.2f}$, $p = {kw_p:.4f}$  \n"
    except ValueError:
        return "Variance issue. Cannot compute statistics."
        
    stats_text += "\n**Post-Hoc Comparisons (Mann-Whitney U):** \n"
    controls_data = df[df['Group'] == 'Controls'][metric_col].dropna().values
    
    if len(controls_data) > 0:
        for g in groups:
            if g not in ['Controls', 'Total Sample']:
                comp_data = df[df['Group'] == g][metric_col].dropna().values
                if len(comp_data) > 0:
                    u_stat, p_val = stats.mannwhitneyu(controls_data, comp_data, alternative='two-sided')
                    sig = "⭐" if p_val < 0.05 else ""
                    stats_text += f"- Controls vs {g}: $p = {p_val:.4f}$ {sig}  \n"
                    
    return stats_text

def plot_sfm_dashboard(df, metric_mode):
    """Renders the Plotly graph with dynamic Y-axes matching MATLAB summarize_SFM_results.m"""
    import plotly.express as px
    import numpy as np
    
    if df.empty: return None
        
    if "Switch Rate" in metric_mode:
        target_cols = ['Real_Switch_Hz', 'Bistable_Hz']
        y_title = "Switch Rate (Hz)"
        y_range = [np.log10(0.005), np.log10(1.5)] 
        y_ticks = [0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 1.5]
        baseline_val = 0.09
    else:
        target_cols = ['Real_Switch_Dur', 'Bistable_Dur']
        y_title = "Average Percept Duration (sec)"
        y_range = [np.log10(1), np.log10(60)]
        y_ticks = [1, 2.5, 5, 10, 25, 50]
        baseline_val = 11

    df_plot = df.melt(
        id_vars=['Subject', 'Group'], value_vars=target_cols,
        var_name='Task', value_name='Metric'
    )
    df_plot['Task'] = df_plot['Task'].replace({target_cols[0]: 'Control Task', target_cols[1]: 'Bistable Task'})
    
    order = sorted(list(df['Group'].unique()))
    if 'Controls' in order: order.insert(0, order.pop(order.index('Controls')))
    if 'Total Sample' in order: order.append(order.pop(order.index('Total Sample')))

    fig = px.box(
        df_plot, x="Group", y="Metric", color="Group",
        facet_col="Task", points="all", color_discrete_map=get_category_colors(),
        category_orders={"Group": order, "Task": ["Control Task", "Bistable Task"]}
    )
    
    fig.update_yaxes(
        type="log", range=y_range, tickvals=y_ticks,
        showgrid=True, gridwidth=1, gridcolor='#e2e8f0', title_text=y_title
    )
    
    fig.add_hline(
        y=baseline_val, line_dash="dash", line_color="black", line_width=2,
        row=1, col=1, annotation_text=f"Expected ({baseline_val})", annotation_position="bottom right"
    )
    
    fig.update_layout(showlegend=False, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(size=14))
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    fig.update_xaxes(title_text="")
    fig.update_traces(boxmean=True) 
    
    return fig
