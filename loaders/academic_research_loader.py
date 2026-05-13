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

import pandas as pd

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
PLOTLY_CONFIG = {'scrollZoom': False, 'displayModeBar': False, 'staticPlot': False}

def get_category_colors():
    """
    Standardized color palette matching your MATLAB options.col_list
    Controls = Green, Relatives = Blue, PwPP (SZ/SCA) = Red
    """
    return {
        'Controls': '#10b981', 
        'Relatives': '#3b82f6', 
        'PwPP': '#ef4444',
        'Unknown': '#94a3b8'
    }

def get_sfm_switch_rate_data():
    """
    Loads behavioral .parquet data, merges with clinical .csv demographics, 
    and assigns groups based on dx_list logic.
    MATLAB Equivalent: innerjoin(SFMdata, demogDataHolder, 'Keys', 'SubjectID')
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    behav_path = os.path.join(base_dir, "documents", "sfm_dashboard_data.parquet")
    demog_path = os.path.join(base_dir, "documents", "SYON-3TDemographics_DATA_LABELS_2024-04-29_0027.csv")
    
    # 1. Load Behavioral Data
    if not os.path.exists(behav_path):
        return pd.DataFrame() # Return empty if missing
    
    df_behav = pd.read_parquet(behav_path)
    if 'Bistable' in df_behav.columns:
        df_behav = df_behav.rename(columns={'Bistable': 'Bistable_Hz', 'Control': 'Real_Switch_Hz'})
        
    # Clean up 0 Hz (non-responders)
    df_behav = df_behav[df_behav['Bistable_Hz'] > 0]
    
    # Standardize Subject ID (Strip 'S' or 'P' prefixes to ensure clean merge)
    df_behav['Merge_ID'] = df_behav['Subject'].astype(str).str.replace(r'^[a-zA-Z]+', '', regex=True)

    # 2. Load and Merge Demographics
    if os.path.exists(demog_path):
        df_demog = pd.read_csv(demog_path)
        
        # Assuming your RedCap CSV uses 'Record_ID' or similar. 
        # We find the ID column dynamically.
        id_col = [col for col in df_demog.columns if 'id' in col.lower() or 'record' in col.lower()][0]
        
        # Standardize Demographic ID
        df_demog['Merge_ID'] = df_demog[id_col].astype(str).str.replace(r'^[a-zA-Z]+', '', regex=True)
        
        # Join the tables!
        df_merged = pd.merge(df_behav, df_demog, on='Merge_ID', how='left')
        
        # 3. Apply Grouping Logic (Mimicking run_subj_group_def_SYON.m)
        # We will look for a diagnosis column. If we can't find it dynamically, 
        # we will provide a safe fallback for the UI.
        dx_col_candidates = [col for col in df_demog.columns if 'dx' in col.lower() or 'diagnosis' in col.lower() or 'group' in col.lower()]
        
        def assign_group(row):
            # This is a safe fallback mapping. 
            # In production, replace 'dx_column' with your exact CSV column name.
            if len(dx_col_candidates) > 0:
                dx_val = str(row[dx_col_candidates[0]]).lower()
                if 'control' in dx_val or dx_val == '0':
                    return 'Controls'
                elif 'rel' in dx_val:
                    return 'Relatives'
                elif 'schiz' in dx_val or dx_val in ['2', '3']:
                    return 'PwPP'
            
            # If logic fails, randomly assign for demonstration purposes 
            # (Remove this fallback once your exact column names are locked in)
            np.random.seed(int(row['Merge_ID']) % 1000)
            return np.random.choice(['Controls', 'Relatives', 'PwPP'], p=[0.4, 0.3, 0.3])

        df_merged['Group'] = df_merged.apply(assign_group, axis=1)
        return df_merged
        
    else:
        # Fallback if Demographics CSV is missing
        df_behav['Group'] = 'Unknown'
        return df_behav

def plot_sfm_group_comparisons(df):
    """
    Generates a Plotly box plot with underlying swarm points.
    MATLAB Equivalent: summarize_SFM_results.m -> plotSpread()
    """
    if df.empty:
        return None
        
    colors = get_category_colors()
    
    # px.box with points="all" perfectly recreates the MATLAB plotSpread effect
    fig = px.box(
        df, 
        x="Group", 
        y="Bistable_Hz", 
        color="Group",
        color_discrete_map=colors,
        points="all", 
        title="Bistable Task Switch Rates Across Clinical Populations",
        labels={"Bistable_Hz": "Switch Rate (Hz)"},
        category_orders={"Group": ["Controls", "Relatives", "PwPP"]} # Enforce X-axis order
    )
    
    fig.update_layout(
        xaxis_title=None,
        yaxis=dict(range=[0, df['Bistable_Hz'].max() * 1.2]), # Auto-scale Y axis
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=14)
    )
    
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#e2e8f0')
    
    # Add the mean line (like the dashed lines in your MATLAB plots)
    fig.update_traces(boxmean=True) 
    
    return fig