"""
=============================================================================
MODULE: Portfolio Data Hub (portfolio_loader.py)
AUTHOR: Kyle W. Killebrew, PhD
DESCRIPTION: 
    This module serves strictly as the Data Dictionary. 
    It should ONLY contain function definitions (def). No execution logic!
    
    --- MATLAB BRIDGE ---
    If you are coming from MATLAB, think of this module as a dedicated data 
    function (e.g., `load_portfolio_data.m`) that outputs cleanly formatted 
    workspace variables (tables and structs) for your App Designer UI to consume.
    
    By centralizing data here, updates to your CV or Bio only need to be 
    made in this file to reflect globally across the app.
=============================================================================
"""

import pandas as pd

def get_biographic_metadata():
    """
    Defines core biographic info and the master 'About Me' narrative.
    
    MATLAB Equivalent: A scalar structure (e.g., bio.name = 'Kyle'; bio.title = '...')
    
    Returns:
        dict: Containing 'name', 'title', 'bio', and 'interests'.
    """
    return {
        'name': 'Kyle W. Killebrew, PhD',
        'title': 'Data Scientist, Neuroscientist & Educational Mentor',
        'bio': ("With 15 years of experience spanning neuroscience, mathematical modeling, and education, "
                "I bridge the gap between theoretical research and interactive data science. Holding a PhD "
                "in Neuroscience, my background involves studying brain dynamics across diverse populations—from "
                "undergraduates to patients with psychosis. Today, I channel my passion for lifelong learning "
                "into data science and mentorship, helping students and organizations uncover meaningful insights "
                "through hypothesis-driven research, meticulous modeling, and inquiry-based education.")
    }

def get_portfolio_metadata():
    """
    Defines the structured data for technical skills, philosophy, and academic publications.
    
    Returns:
        tuple: (pubs_df, skills_dict, beliefs_dict, links_dict)
    """
    # 1. Publication Data 
    # MATLAB Equivalent: A MATLAB `table` (e.g., table(Year, Title, Journal, Link))
    # Stored as a Pandas DataFrame for easy UI iteration and native table rendering.
    pubs = pd.DataFrame({
        'Year': [2015, 2017, 2018, 2024, 2020], 
        'Title': [
            'Intraparietal regions play a material general role in working memory: Evidence supporting an internal attentional role', 
            'Induced and evoked human electrophysiological correlates of visual working memory set-size effects at encoding',
            'Electrophysiological correlates of encoding processes in a full-report visual working memory paradigm',
            'Faster bi-stable visual switching in psychosis',
            'The Neural Representation of Ensemble Mean'
        ],
        'Journal': [
            'PMC / NIH', 
            'PLOS ONE', 
            'Springer', 
            'Nature (Translational Psychiatry)', 
            'UNR (Dissertation/Thesis)'
        ],
        'Link': [
            'https://pmc.ncbi.nlm.nih.gov/articles/PMC4468015/pdf/nihms689438.pdf',
            'https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0167022&type=printable',
            'https://link.springer.com/content/pdf/10.3758/s13415-018-0574-8.pdf',
            'https://www.nature.com/articles/s41398-024-02913-z.pdf',
            'https://scholarwolf.unr.edu/server/api/core/bitstreams/817b85e5-4335-4751-8f2d-605d3bcf7b31/content'
        ]
    })
    
    # 2. Skill Proficiency (Mapped to UI progress bars)
    # MATLAB Equivalent: A standard struct or a `containers.Map` for fast key-value lookups.
    skills = {
        'Python (Data Science)': 95, 
        'MATLAB (App Designer)': 95, 
        'Advanced Statistics': 90, 
        'Experimental Design': 95, 
        'Machine Learning': 85
    }
    
    # 3. Philosophy & Principles
    # MATLAB Equivalent: A struct containing strings and cell arrays of character vectors.
    beliefs = {
        'sop': 'To empower individuals and organizations through hands-on data science and inquiry-driven education.',
        'core_principles': [
            'Precision & Methodology: High-quality inputs yield high-quality insights.',
            'Passion-Driven Action: True learning stems from genuine curiosity.',
            'Lifelong Learning: Skill acquisition is a continuous journey.',
            'Undeniable Documentation: Documentation is the backbone of reproducibility.'
        ]
    }
    
    return pubs, skills, beliefs, {}

def get_teaching_metadata():
    """
    Defines tutoring qualifications and rates.
    
    MATLAB Equivalent: A nested struct containing character vectors and sub-structs.
    
    Returns:
        dict: Service descriptions and financial metadata.
    """
    return {
        'qualifications': [
            '15+ Years Educational Experience (Middle School to College Level)',
            'Specialized 1-on-1 Mentorship & Personalized Curricula',
            'Programming (Python, MATLAB, R) & Data Science',
            'Neuroscience, Biology, and Advanced Mathematics'
        ],
        'rates': {
            'Hourly Rate': '$40 - $74/hr', 
            'Consulting': 'Contact for Quote'
        }
    }

def get_references_metadata():
    """
    Defines professional references for social proof.
    
    MATLAB Equivalent: A 1xN struct array (e.g., refs(1).name = '...', refs(2).name = '...').
    
    Returns:
        list: List of dictionaries containing contact and title info.
    """
    return [
        {"name": "Dr. Gideon P. Caplovitz", "title": "Professor, UNR (PhD Mentor)", "contact": "gcaplovitz@unr.edu"},
        {"name": "Dr. Michael-Paul Schallmo", "title": "Professor, UMN (Post-doc Advisor)", "contact": "schal110@umn.edu"},
        {"name": "Kelly Thorson", "title": "Principal, Lied STEM", "contact": "thorskt@nv.ccsd.net"},
        {"name": "Dr. Marian Berryhill", "title": "Professor, UNR (PhD Co-Mentor)", "contact": "mberryhill@unr.edu"},
        {"name": "Dr. Ryan Mruczek", "title": "Professor, College of the Holy Cross (Research Peer)", "contact": "rmruczek@holycross.edu"}
    ]
