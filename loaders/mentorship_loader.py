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
    # Think of this expansion as adding fields to a nested struct array: 
    # m.career_history = struct('school', {}, 'role', {}, 'metrics', {})
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
            'Inquiry-Based Learning: Focus on the "why" behind the mathematical mechanics.',
            'Direct Bridge: Specialized training for MATLAB users moving to Python.',
            'Project-Centric: Learning through building actual data pipelines.'
        ],
        'career_history': [
            {
                'school': 'Lied STEM Academy',
                'role': '6th Grade Math/Science Educator',
                'years': '2024 - 2025',
                'metrics': 'Analyzed longitudinal MAP test percentile growth across Fall, Winter, and Spring.',
                'dataset_type': 'maps',
                'file_path': 'documents/6th Grade Maps Growth - Period 1.csv'
            },
            {
                'school': 'Lied STEM Academy',
                'role': '7th Grade ELA / Humanities Educator',
                'years': '2025 - Present',
                'metrics': 'Standards-based assessment tracking (0-4 scale) across core literacy competencies.',
                'dataset_type': 'ela',
                'file_path': 'documents/7th Grade ELA Assessment Scores - Period 1.csv'
            },
            {
                'school': 'University of Minnesota',
                'role': 'Postdoctoral Researcher & Lecturer',
                'years': '2020 - 2024',
                'metrics': 'Mentored undergraduate research tracks in computational neuroscience and programming.',
                'dataset_type': None,
                'file_path': None
            }
        ],
        # NEW: Links for external platforms
        'tutoring_platforms': {
            'Wyzant': 'https://www.wyzant.com/tutors/your_link_here',
            'LinkedIn ProFinder': 'https://www.linkedin.com/in/kylewkillebrew/'
        }
    }
