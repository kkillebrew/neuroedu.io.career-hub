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