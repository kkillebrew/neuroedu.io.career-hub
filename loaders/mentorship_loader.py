"""
=============================================================================
MODULE: loaders/mentorship_loader.py
AUTHOR: Kyle W. Killebrew, PhD
DESCRIPTION: 
    The "Model" layer for the Mentorship spoke. 
    Handles educational qualifications and consulting rates.
    
    --- MATLAB BRIDGE ---
    Equivalent to a data struct or a dedicated script like `getMentorshipInfo.m`.
=============================================================================
"""
def get_mentorship_data():
    """
    Returns structured data for the mentorship and tutoring UI.
    MATLAB Equivalent: m = struct('qualifications', {}, 'rates', struct())
    """
    return {
        'qualifications': [
            '15+ Years Educational Experience (MS to PhD Level)',
            'Specialized 1-on-1 Mentorship & Personalized Curricula',
            'Programming (Python, MATLAB, R) & Data Science',
            'Neuroscience, Biology, and Advanced Mathematics',
            'Certified STEM Curriculum Designer'
        ],
        'rates': {
            'Standard Hourly': '$40 - $75/hr', 
            'Consulting': 'Project-Based Quote',
            'Group Sessions': 'Contact for Tiered Pricing'
        },
        'methodology': [
            'Inquiry-Based Learning: Focus on the "why" behind the code.',
            'Direct Bridge: Specialized training for MATLAB users moving to Python.',
            'Project-Centric: Learning through building actual data pipelines.'
        ]
    }
