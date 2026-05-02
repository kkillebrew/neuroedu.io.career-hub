"""
=============================================================================
MODULE: loaders/publications_loader.py
AUTHOR: Kyle W. Killebrew, PhD
DESCRIPTION: 
    The "Model" layer for the Publications spoke. 
    Handles the structured library of peer-reviewed research.
    
    --- MATLAB BRIDGE ---
    Equivalent to a standalone function like `getPubData.m` that returns 
    a Table for the UI to iterate through.
=============================================================================
"""

import pandas as pd

def get_publications_data():
    """
    Returns a structured DataFrame of all academic publications.
    MATLAB Equivalent: T = table(Year, Title, Journal, Link)
    """
    return pd.DataFrame({
        'Year': [2024, 2018, 2017, 2015, 2020], 
        'Title': [
            'Faster bi-stable visual switching in psychosis',
            'Electrophysiological correlates of encoding processes in a full-report visual working memory paradigm',
            'Induced and evoked human electrophysiological correlates of visual working memory set-size effects at encoding',
            'Intraparietal regions play a material general role in working memory: Evidence supporting an internal attentional role', 
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

def get_publication_metrics():
    """
    Returns high-level stats for the header.
    """
    return {
        'total_citations': 'Pending API',
        'h_index': 'Pending API',
        'fields': ['Neuroscience', 'Psychosis', 'Working Memory']
    }