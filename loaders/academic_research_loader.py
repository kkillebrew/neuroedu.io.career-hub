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
from scipy.optimize import curve_fit
import re # Import Python's Regular Expression library
import requests
from io import BytesIO, StringIO
import streamlit as st
import json
import time

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


@st.cache_data
def get_sfm_data(grouping_mode, metric_mode, apply_qc=True):
    """
    Pure Cloud Architecture: Fetches BOTH the Parquet and CSV dynamically 
    from Private GitHub using secure tokens, merges, and applies de-identification.
    """
    
    # Secure Cache Buster: Forces GitHub to give you the freshest file immediately
    cache_buster = int(time.time())
    PARQUET_RAW_URL = f"https://raw.githubusercontent.com/kkillebrew/SFM/refs/heads/main/sfm_dashboard_data.parquet?t={cache_buster}"
    DEMOG_RAW_URL = "https://raw.githubusercontent.com/kkillebrew/SFM/refs/heads/main/SYON-3TDemographics-DATA-2023-05-11-1249.csv"
    
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
        p_res = requests.get(PARQUET_RAW_URL, headers=headers, timeout=15)
        if p_res.status_code == 200:
            df = pd.read_parquet(BytesIO(p_res.content))
        else:
            print(f"⚠️ Parquet Fetch Failed. Status Code: {p_res.status_code}")
            return pd.DataFrame() 
    except Exception as e:
        print(f"⚠️ Parquet Fetch Error: {e}")
        return pd.DataFrame()

    # ==========================================
    # NEW: QUALITY CONTROL FILTERING
    # ==========================================
    if apply_qc:
        if 'QC_Pass' in df.columns:
            start_len = len(df)
            # Drop anyone who scored a 0 on the master QC mask
            df = df[df['QC_Pass'] == 1].copy()
            end_len = len(df)
            if start_len != end_len:
                # This will put a green success banner at the top of your app so you KNOW it worked!
                st.success(f"🧪 QC Applied: Removed {start_len - end_len} excluded runs.")
        else:
            st.error("⚠️ 'QC_Pass' column not found in Parquet file. Ensure Colab script ran successfully.")

    if 'Bistable' in df.columns:
        df = df.rename(columns={'Bistable': 'Bistable_Hz', 'Control': 'Real_Switch_Hz'})
        
    df = df[df['Bistable_Hz'] > 0].copy()
    df['Bistable_Dur'] = 1 / df['Bistable_Hz']
    df['Real_Switch_Dur'] = 1 / df['Real_Switch_Hz']
    df['Merge_ID'] = df['Subject'].astype(str).str.replace(r'\D', '', regex=True)

    # --- 2. FETCH DEMOGRAPHICS (.csv) ---
    dx_col = None
    try:
        c_res = requests.get(DEMOG_RAW_URL, headers=headers, timeout=15)
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
#########################################################
#---   Analyze and Process the SFM Behavioral Data   ---#
#########################################################
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
        y_range = [np.log10(0.005), np.log10(0.5)] 
        y_ticks = [0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5]
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

def get_test_retest_data(df):
    """
    Filters for subjects with multiple visits and pivots the data 
    for Test-Retest correlation and Median Range analysis.
    """
    # Defensive check: if Visit_Number doesn't exist, return empty safe dataframe
    if 'Visit_Number' not in df.columns:
        return pd.DataFrame(columns=['Subject', 'Visit_1_Hz', 'Visit_2_Hz', 'Hz_Difference'])
        
    df_visits = df[df['Visit_Number'].isin([1, 2])].copy()
    
    # CRITICAL FIX: Use pivot_table with aggfunc='first' to safely bypass duplicate rows caused by demographic merges
    df_tr = df_visits.pivot_table(
        index='Subject', 
        columns='Visit_Number', 
        values='Bistable_Hz',
        aggfunc='first' 
    ).dropna()
    
    # Check if both Visit 1 and Visit 2 actually exist in the data
    if 1 not in df_tr.columns or 2 not in df_tr.columns:
        return pd.DataFrame(columns=['Subject', 'Visit_1_Hz', 'Visit_2_Hz', 'Hz_Difference'])
    
    # Isolate strictly the two columns and rename them safely
    df_tr = df_tr[[1, 2]]
    df_tr.columns = ['Visit_1_Hz', 'Visit_2_Hz']
    df_tr['Hz_Difference'] = df_tr['Visit_2_Hz'] - df_tr['Visit_1_Hz']
    
    return df_tr.reset_index()

def get_accuracy_data(df):
    """
    Returns accuracy counts. 
    If Raw column is missing, it falls back to the filtered column to prevent crashes.
    """
    # Defensive check: if the Raw column isn't there yet, just use the Filtered one twice
    if 'Control_Correct_Responses_Raw' not in df.columns:
        raw_col = 'Control_Correct_Responses'
    else:
        raw_col = 'Control_Correct_Responses_Raw'
        
    raw_data = df[['Subject', raw_col]].rename(columns={raw_col: 'Control_Correct_Responses_Raw'}).dropna()
    filtered_data = df[['Subject', 'Control_Correct_Responses']].dropna()
    
    return raw_data, filtered_data

def get_percept_duration_data(df):
    """Unpacks button presses, calculates durations within the same block, and tags the block."""
    df_main = df[df['Visit_Number'] == 1] if 'Visit_Number' in df.columns else df
    all_durations = []
    
    for _, row in df_main.iterrows():
        for task_type in ['Control', 'Bistable']:
            raw_json = row.get(f"{task_type}_Raw_Events_JSON")
            if pd.isna(raw_json) or not raw_json or raw_json == '[]': continue
            
            try:
                events = json.loads(raw_json)
                
                # 1. Sort events chronologically to guarantee no accidental negative math
                events.sort(key=lambda x: float(x[1]) if isinstance(x, list) else float(x.get('Time', 0)))
                
                for i in range(len(events) - 1):
                    e1, e2 = events[i], events[i+1]
                    
                    # 2. Extract block labels safely
                    block1 = e1[0] if isinstance(e1, list) else e1.get('Block')
                    block2 = e2[0] if isinstance(e2, list) else e2.get('Block')
                    
                    # 3. CRITICAL: Only calculate duration if the presses belong to the SAME block
                    if block1 == block2:
                        t1 = float(e1[1] if isinstance(e1, list) else e1.get('Time'))
                        t2 = float(e2[1] if isinstance(e2, list) else e2.get('Time'))
                        
                        dur = t2 - t1
                        
                        # 4. Only keep logical durations (> 0s) and explicitly store the Block label
                        if dur > 0:
                            all_durations.append({
                                'Subject': row['Subject'],
                                'Task_Type': task_type,
                                'Block': int(block1), # <--- Storing the correct Block label here!
                                'Direction': str(e1[2] if isinstance(e1, list) else e1.get('Key')).lower(),
                                'Duration_Sec': dur
                            })
            except: continue
            
    return pd.DataFrame(all_durations)

def get_rt_histogram_data(df):
    """Unpacks the raw reaction times for the Control Task."""
    # This MUST match the pivoted name in the Parquet
    rt_col = "Control_Raw_RT_JSON" 
    
    all_rts = []
    # Use the column directly from the merged dataframe
    for _, row in df.iterrows():
        raw_json = row.get(rt_col)
        if pd.isna(raw_json) or not raw_json or raw_json == '[]': 
            continue
        
        try:
            rts = json.loads(raw_json)
            for rt in rts:
                # Handle nested list [0.45] or float 0.45
                val = rt[0] if isinstance(rt, list) else rt
                all_rts.append({'Subject': row['Subject'], 'Reaction_Time_Sec': float(val)})
        except: 
            continue
            
    return pd.DataFrame(all_rts)

def get_response_counts_data(df):
    """Counts left/right button presses for both tasks."""
    df_main = df[df['Visit_Number'] == 1] if 'Visit_Number' in df.columns else df
    all_counts = []
    
    for _, row in df_main.iterrows():
        for task_type in ['Control', 'Bistable']:
            raw_json = row.get(f"{task_type}_Raw_Events_JSON")
            if pd.isna(raw_json) or not raw_json or raw_json == '[]': continue
            
            try:
                events = json.loads(raw_json)
                l = sum(1 for e in events if 'left' in str(e[2] if isinstance(e, list) else e.get('Key')).lower())
                r = sum(1 for e in events if 'right' in str(e[2] if isinstance(e, list) else e.get('Key')).lower())
                
                all_counts.append({
                    'Subject': row['Subject'], 
                    'Task_Type': task_type,
                    'Left_Presses': l, 
                    'Right_Presses': r
                })
            except: continue
    return pd.DataFrame(all_counts)

#########################################################
#---    Load In the Rotating Line Behavioral Data    ---#
#########################################################
@st.cache_data
def get_rotating_line_data():
    """
    Fetches combined Parquet file from GitHub.
    Applies Bounded curve fits to prevent mathematical outliers on noisy subjects.
    """

    try:
        github_token = os.environ.get("GITHUB_TOKEN")
        if not github_token:
            try:
                github_token = st.secrets["GITHUB_TOKEN"]
            except Exception:
                pass
                
        if not github_token:
            return None, None
            
        cache_buster = int(time.time())
        username = "kkillebrew"
        repo = "RotatingLine"
        file_path = "RotatingLine_Exp/rotating_line_combined.parquet" 
        raw_url = f"https://raw.githubusercontent.com/{username}/{repo}/main/{file_path}?t={cache_buster}"
        
        headers = {'Authorization': f'token {github_token}'}
        response = requests.get(raw_url, headers=headers, timeout=15)
        if response.status_code != 200:
            return None, None
            
        df = pd.read_parquet(BytesIO(response.content))
        
        # --- THE MATH ENGINES ---
        def sigmoid_curve(x, k, x0):
            return 1 / (1 + np.exp(-k * (x - x0).clip(-100, 100)))
            
        def parabola_curve(x, a, h, k):
            return a * (x - h)**2 + k

        def process_block(task_df, task_name):
            if task_df.empty:
                return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), {}
                
            x_smooth = np.linspace(task_df['X_Value'].min(), task_df['X_Value'].max(), 100)
            individual_fits = []
            avg_fits = []
            group_pse_dict = {}
            
            for size_cond in task_df['Size'].unique():
                size_df = task_df[task_df['Size'] == size_cond]
                
                # 1. Individual Fits
                for subj in size_df['Subject_ID'].unique():
                    subj_data = size_df[size_df['Subject_ID'] == subj]
                    x_data = subj_data['X_Value'].values
                    
                    try:
                        if task_name == 'Control':
                            y_data = subj_data['Percent_Faster'].values 
                            popt, _ = curve_fit(sigmoid_curve, x_data, y_data, p0=[1.0, np.median(x_data)], maxfev=2000)
                            y_smooth = sigmoid_curve(x_smooth, popt[0], popt[1]) * 100 
                            subj_pse = popt[1]
                        else:
                            y_data = subj_data['Percent_Faster'].values * 100
                            # FIXED: Added strict physical bounds for [a, h, k]
                            # 'h' is the PSE, bounded strictly between -2.0 and 8.0 Mod Units
                            bounds = ([-np.inf, -2.0, 0.0], [np.inf, 8.0, 100.0])
                            popt, _ = curve_fit(parabola_curve, x_data, y_data, p0=[10.0, 1.0, 50.0], bounds=bounds, maxfev=2000)
                            y_smooth = parabola_curve(x_smooth, popt[0], popt[1], popt[2])
                            subj_pse = popt[1] 
                            
                        subj_fit_df = pd.DataFrame({'X_Value': x_smooth, 'Fit_Percent': y_smooth})
                        subj_fit_df['Subject_ID'] = subj
                        subj_fit_df['Size'] = size_cond
                        subj_fit_df['PSE'] = subj_pse
                        individual_fits.append(subj_fit_df)
                    except:
                        # Silently skip noisy subjects who break the physical bounds
                        pass 

                # 2. Group Average Fits
                avg_raw = size_df.groupby('X_Value')['Percent_Faster'].mean().reset_index()
                try:
                    if task_name == 'Control':
                        popt_avg, _ = curve_fit(sigmoid_curve, avg_raw['X_Value'], avg_raw['Percent_Faster'], p0=[1.0, np.median(avg_raw['X_Value'])])
                        avg_y_smooth = sigmoid_curve(x_smooth, popt_avg[0], popt_avg[1]) * 100
                        group_pse_dict[size_cond] = popt_avg[1]
                    else:
                        # FIXED: Bounded Average calculation as well
                        bounds = ([-np.inf, -2.0, 0.0], [np.inf, 8.0, 100.0])
                        popt_avg, _ = curve_fit(parabola_curve, avg_raw['X_Value'], avg_raw['Percent_Faster'] * 100, p0=[10.0, 1.0, 50.0], bounds=bounds)
                        avg_y_smooth = parabola_curve(x_smooth, popt_avg[0], popt_avg[1], popt_avg[2])
                        group_pse_dict[size_cond] = popt_avg[1]
                        
                    df_avg_fit = pd.DataFrame({'X_Value': x_smooth, 'Fit_Percent': avg_y_smooth})
                    df_avg_fit['Size'] = size_cond
                    avg_fits.append(df_avg_fit)
                except:
                    pass

            df_ind_fits = pd.concat(individual_fits, ignore_index=True) if individual_fits else pd.DataFrame()
            df_avg_fits = pd.concat(avg_fits, ignore_index=True) if avg_fits else pd.DataFrame()
                
            return task_df, df_ind_fits, df_avg_fits, group_pse_dict

        control_data = process_block(df[df['Task'] == 'Control'], 'Control')
        experimental_data = process_block(df[df['Task'] == 'Experimental'], 'Experimental')
        
        return control_data, experimental_data
        
    except Exception as e:
        st.error(f"Error executing get_rotating_line_data: {e}")
        return None, None

# =====================================================================
# VISUAL WORKING MEMORY (VWM) DATA LOADERS
# =====================================================================
from scipy.stats import ttest_rel, ttest_1samp

def _fetch_github_parquet(base_name):
    """Fetches a single pre-aggregated Parquet file from GitHub."""
    
    # 1. Safely check the cloud environment FIRST
    github_token = os.environ.get("GITHUB_TOKEN")
    
    # 2. Only attempt Streamlit secrets if running locally, and catch the error if it fails
    if not github_token:
        try:
            github_token = st.secrets["GITHUB_TOKEN"]
        except Exception:
            pass

    headers = {'Authorization': f"token {github_token}"} if github_token else {}
    url = f"https://raw.githubusercontent.com/kkillebrew/workingMemoryGrouping/main/Color/VWM_Parquet_Master/{base_name}.parquet"
    
    try:
        res = requests.get(url, headers=headers, timeout=15)
        res.raise_for_status() 
        return pd.read_parquet(BytesIO(res.content))
    except Exception as e:
        print(f"Failed to load {base_name}: {e}")
        return pd.DataFrame()

@st.cache_data
def get_vwm_behavioral_data():
    return _fetch_github_parquet('vwm_behavioral')

# --- MEMORY OPTIMIZED PROCESSORS (DOWNLOAD & VAPORIZE) ---
@st.cache_data
def get_processed_vwm_vep():
    df = _fetch_github_parquet('vwm_eeg_time_summary')
    if df.empty: return df
    
    cond_lower = df['Condition'].str.lower()
    df['Grouping_Condition'] = np.where(
        cond_lower.str.contains('nogrp'), 'Not Grouped',
        np.where(cond_lower.str.contains('grpnoprb'), 'Grouped Non-Probed', 'Grouped Probed')
    )
    return df.groupby(['Grouping_Condition', 'Time_s'])['Amplitude_uV'].mean().reset_index()

@st.cache_data
def get_processed_vwm_snr():
    df = _fetch_github_parquet('vwm_eeg_trial_power_summary')
    if df.empty: return df
    
    snr_cols = [c for c in df.columns if 'SNR' in c]

    # Average channels FIRST to shrink row count and save memory
    df_mean = df.groupby(['Subject_ID', 'Condition'])[snr_cols].mean().reset_index()

    melted = df_mean.melt(id_vars=['Subject_ID', 'Condition'], 
                          value_vars=snr_cols, 
                          var_name='Frequency_Type', value_name='SNR')

    # The Original Labeling Logic
    melted['Signal_Type'] = np.where(
        melted['Frequency_Type'].str.contains('IM', case=False), 
        'Intermodulation (Sum/Diff)', 
        'Fundamental (Base Hz)'
    )

    cond_lower = melted['Condition'].str.lower()
    melted['Grouping_Status'] = np.where(
        cond_lower.str.contains('grp') & ~cond_lower.str.contains('nogrp'), 
        'Grouped', 'Non-Grouped'
    )

    # --- CRITICAL DATA RESTORATION (REGEX FILTER) ---
    import re
    # Extract the exact integer from the column name (e.g., 'SNR_3Hz' -> '3')
    melted['Freq_Hz_Str'] = melted['Frequency_Type'].str.extract(r'(\d+)')
    
    def is_valid_frequency(row):
        # Keep all Intermodulation frequencies
        if row['Signal_Type'] == 'Intermodulation (Sum/Diff)':
            return True
        
        # For Fundamentals, extract the explicit numbers from the condition string 
        # (e.g., 'grpPrb3_12' becomes the list ['3', '12'])
        cond_nums = re.findall(r'\d+', str(row['Condition']))
        
        # Only keep the row if its frequency matches a number actually in the condition
        return str(row['Freq_Hz_Str']) in cond_nums
        
    melted['Valid'] = melted.apply(is_valid_frequency, axis=1)
    melted_clean = melted[melted['Valid']]

    return melted_clean.groupby(['Subject_ID', 'Grouping_Status', 'Signal_Type'])['SNR'].mean().reset_index()

@st.cache_data
def get_processed_fft_grid():
    df = _fetch_github_parquet('vwm_eeg_full_spectrum')
    if df.empty: return df
    
    target_pairs = ['3_5', '3_12', '5_3', '5_12', '12_3', '12_5', '20_3', '20_5']
    conds = [f'grpPrb{p}' for p in target_pairs] + [f'noGrp{p}' for p in target_pairs]
    
    df_filt = df[df['Condition'].isin(conds)].copy()
    df_avg = df_filt.groupby(['Condition', 'Frequency_Hz'])['Power'].mean().reset_index()
    df_avg['Grouping'] = np.where(df_avg['Condition'].str.startswith('grp'), 'Grouped', 'Not Grouped')
    df_avg['Pair'] = df_avg['Condition'].str.replace('grpPrb', '').str.replace('noGrp', '')
    return df_avg

@st.cache_data
def get_processed_index_spectra():
    """Calculates the 1-100Hz Index Spectrum for all 12 Condition Pairs."""
    df = _fetch_github_parquet('vwm_eeg_full_spectrum')
    if df.empty: return pd.DataFrame(), pd.DataFrame()

    # Generate all 12 combinations dynamically
    base_freqs = ['3', '5', '12', '20']
    target_pairs = [f"{t}_{g}" for t in base_freqs for g in base_freqs if t != g]

    conds = [f'grpPrb{p}' for p in target_pairs] + [f'noGrp{p}' for p in target_pairs]

    df_filt = df[df['Condition'].isin(conds)].copy()
    df_filt['Pair'] = df_filt['Condition'].str.replace('grpPrb', '').str.replace('noGrp', '')
    df_filt['Grouping'] = np.where(df_filt['Condition'].str.startswith('grp'), 'Grouped', 'Not Grouped')

    # Pivot to align Grouped/NotGrouped side-by-side per Subject/Freq
    pivoted = df_filt.pivot_table(index=['Subject_ID', 'Pair', 'Frequency_Hz'], columns='Grouping', values='Power').reset_index()
    pivoted.dropna(subset=['Grouped', 'Not Grouped'], inplace=True)

    # Calculate Index: (Grp - noGrp) / (Grp + noGrp)
    idx_math = (pivoted['Grouped'] - pivoted['Not Grouped']) / (pivoted['Grouped'] + pivoted['Not Grouped'])
    pivoted['Index_Value'] = idx_math.replace([np.inf, -np.inf], np.nan).fillna(0.0)

    # Average across subjects for the 12 line plots
    df_spectra = pivoted.groupby(['Pair', 'Frequency_Hz'])['Index_Value'].mean().reset_index()

    # We return the raw pivoted data too, so the Role summary plot can use it without recalculating!
    return pivoted, df_spectra

@st.cache_data
def get_vwm_role_index():
    """Extracts the specific Index value based on whether the frequency was the Target or the Grouped item."""
    pivoted, _ = get_processed_index_spectra()
    if pivoted.empty: return pd.DataFrame()

    records = []
    unique_freqs = pivoted['Frequency_Hz'].unique()

    for pair in pivoted['Pair'].unique():
        t_str, g_str = pair.split('_')
        t_hz, g_hz = float(t_str), float(g_str)

        pair_df = pivoted[pivoted['Pair'] == pair]

        # Find closest frequency bins
        closest_t = unique_freqs[np.abs(unique_freqs - t_hz).argmin()]
        closest_g = unique_freqs[np.abs(unique_freqs - g_hz).argmin()]

        # Extract the index when this Hz was the TARGET
        df_t = pair_df[pair_df['Frequency_Hz'] == closest_t].copy()
        df_t['Base_Hz'] = t_str + 'Hz'
        df_t['Role'] = 'Target Object'

        # Extract the index when this Hz was the GROUPED object
        df_g = pair_df[pair_df['Frequency_Hz'] == closest_g].copy()
        df_g['Base_Hz'] = g_str + 'Hz'
        df_g['Role'] = 'Grouped Object'

        records.extend([df_t, df_g])

    return pd.concat(records, ignore_index=True)

def calculate_vwm_stats(df_stats, metric_col):
    """Calculates paired t-tests for the VWM Grouping conditions."""
    def get_sig_stars(p):
        if pd.isna(p): return ""
        if p <= 0.001: return "***"
        elif p <= 0.01: return "**"
        elif p <= 0.05: return "*"
        else: return "ns"

    pivot_df = df_stats.pivot(index='Subject_ID', columns='Grouping_Condition', values=metric_col).dropna()
    if not all(col in pivot_df.columns for col in ['Grouped Probed', 'Grouped Non-Probed', 'Not Grouped']):
        return "Insufficient data."
        
    t1, p1 = ttest_rel(pivot_df['Grouped Probed'], pivot_df['Grouped Non-Probed'])
    t2, p2 = ttest_rel(pivot_df['Grouped Probed'], pivot_df['Not Grouped'])
    t3, p3 = ttest_rel(pivot_df['Grouped Non-Probed'], pivot_df['Not Grouped'])
    
    return f"**Grouped Probed vs. Non-Probed:** $t = {t1:.2f}$, $p = {p1:.4f}$ **{get_sig_stars(p1)}** \n\n**Grouped Probed vs. Not Grouped:** $t = {t2:.2f}$, $p = {p2:.4f}$ **{get_sig_stars(p2)}** \n\n**Grouped Non-Probed vs. Not Grouped:** $t = {t3:.2f}$, $p = {p3:.4f}$ **{get_sig_stars(p3)}** \n\n*(Significance: *p<.05, **p<.01, ***p<.001)*"
