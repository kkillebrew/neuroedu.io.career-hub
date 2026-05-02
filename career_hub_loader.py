"""
=============================================================================
MODULE: career_hub_loader.py
AUTHOR: Kyle W. Killebrew, PhD
DESCRIPTION: 
    The "Model" layer for the main professional hub. Contains biographic, 
    portfolio, and reference metadata.
    
    --- MATLAB BRIDGE ---
    Think of this as a central data function (e.g., `load_portfolio_data.m`) 
    that returns structured tables and structs for the main app UI.
=============================================================================
"""

import pandas as pd

def get_biographic_metadata():
    """
    MATLAB Equivalent: bio = struct('name', '...', 'title', '...', 'bio', '...')
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
    Defines technical skills, academic IDs, and publication data.
    """
    # 1. Publication Data (MATLAB Table equivalent)
    pubs = pd.DataFrame({
        'Year': [2024, 2018, 2017, 2015, 2020], 
        'Title': [
            'Faster bi-stable visual switching in psychosis',
            'Electrophysiological correlates of encoding processes...',
            'Induced and evoked human electrophysiological correlates...',
            'Intraparietal regions play a material general role...', 
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
    })
    
    # 2. Skill Proficiency (Radar Chart Data)
    skills = {
        'Python (DS)': 95, 
        'MATLAB (App)': 95, 
        'Statistics': 90, 
        'Exp. Design': 95, 
        'ML/AI': 85,
        'Mentorship': 98
    }
    
    # 3. Academic IDs
    academic_ids = {
        'orcid': '0000-0002-6112-9214',
        'google_scholar': 'https://scholar.google.com/citations?user=vPIdl8kAAAAJ&hl=en',
        'linkedin': 'https://www.linkedin.com/in/kylewkillebrew/'
    }
    
    return pubs, skills, academic_ids

def get_references_metadata():
    """
    Professional references (now without quotes for high-contrast scanning).
    MATLAB Equivalent: 1x5 Struct Array.
    """
    return [
        {"name": "Dr. Gideon P. Caplovitz", "title": "Professor, UNR (PhD Mentor)", "contact": "gcaplovitz@unr.edu"},
        {"name": "Dr. Michael-Paul Schallmo", "title": "Professor, UMN (Post-doc Advisor)", "contact": "schal110@umn.edu"},
        {"name": "Kelly Thorson", "title": "Principal, Lied STEM", "contact": "thorskt@nv.ccsd.net"},
        {"name": "Dr. Marian Berryhill", "title": "Professor, UNR (PhD Co-Mentor)", "contact": "mberryhill@unr.edu"},
        {"name": "Dr. Ryan Mruczek", "title": "Professor, College of the Holy Cross", "contact": "rmruczek@holycross.edu"}
    ]