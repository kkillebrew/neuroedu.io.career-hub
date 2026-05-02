"""
=============================================================================
MODULE: Portfolio Data Hub (portfolio_loader.py)
AUTHOR: Kyle W. Killebrew, PhD
DESCRIPTION: 
    This module serves strictly as the Data Dictionary (the "Model" layer). 
    It should ONLY contain function definitions (def). No execution logic!
    
    --- MATLAB BRIDGE ---
    If you are coming from MATLAB, think of this module as a dedicated data 
    function (e.g., `load_portfolio_data.m`) that outputs cleanly formatted 
    workspace variables (tables and structs) for your App Designer UI to consume.
=============================================================================
"""

import pandas as pd

def get_biographic_metadata():
    """
    Defines core biographic info and the master 'About Me' narrative.
    MATLAB Equivalent: A scalar structure (e.g., bio.name = 'Kyle'; bio.title = '...')
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
    MATLAB Equivalent: A mix of Tables, Structs, and Cell Arrays.
    """
    # 1. Publication Data (MATLAB Table equivalent)
    pubs = pd.DataFrame({
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
    })
    
    # 2. Skill Proficiency (For Radar Chart / Progress Bars)
    skills = {
        'Python (DS)': 95, 
        'MATLAB (App)': 95, 
        'Statistics': 90, 
        'Exp. Design': 95, 
        'ML/AI': 85,
        'Mentorship': 98
    }
    
    # 3. Philosophy
    beliefs = {
        'sop': 'To empower individuals and organizations through hands-on data science and inquiry-driven education.',
        'core_principles': [
            'Precision & Methodology: High-quality inputs yield high-quality insights.',
            'Passion-Driven Action: True learning stems from genuine curiosity.',
            'Lifelong Learning: Skill acquisition is a continuous journey.',
            'Undeniable Documentation: The backbone of reproducibility.'
        ]
    }

    # 4. Academic IDs (Matches the .get() calls in app.py)
    academic_ids = {
        'orcid': '0000-0002-6112-9214',
        'google_scholar': 'https://scholar.google.com/citations?user=vPIdl8kAAAAJ&hl=en',
        'linkedin': 'https://www.linkedin.com/in/kylewkillebrew/'
    }
    
    return pubs, skills, beliefs, academic_ids

def get_teaching_metadata():
    return {
        'qualifications': [
            '15+ Years Educational Experience (MS to PhD Level)',
            'Specialized 1-on-1 Mentorship & Personalized Curricula',
            'Programming (Python, MATLAB, R) & Data Science',
            'Neuroscience, Biology, and Advanced Mathematics'
        ],
        'rates': {
            'Standard Hourly': '$40 - $75/hr', 
            'Consulting': 'Project-Based Quote'
        }
    }

def get_references_metadata():
    """
    Defines professional references for social proof.
    MATLAB Equivalent: A 1xN struct array with multiple fields.
    NOTE: Quotes removed for a cleaner, high-contrast professional look.
    """
    return [
        {
            "name": "Dr. Gideon P. Caplovitz", 
            "title": "Professor, UNR (PhD Mentor)", 
            "contact": "gcaplovitz@unr.edu"
        },
        {
            "name": "Dr. Michael-Paul Schallmo", 
            "title": "Professor, UMN (Post-doc Advisor)", 
            "contact": "schal110@umn.edu"
        },
        {
            "name": "Kelly Thorson", 
            "title": "Principal, Lied STEM", 
            "contact": "thorskt@nv.ccsd.net"
        },
        {
            "name": "Dr. Marian Berryhill", 
            "title": "Professor, UNR (PhD Co-Mentor)", 
            "contact": "mberryhill@unr.edu"
        },
        {
            "name": "Dr. Ryan Mruczek", 
            "title": "Professor, College of the Holy Cross", 
            "contact": "rmruczek@holycross.edu"
        }
    ]
