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
        # This update expands our struct array fields. It is equivalent to:
        # history(2).school = 'University of Nevada, Reno';
        # history(2).courses = {'PSY 301', 'NEUR 401'};
        'career_history': [
            {
                'school': 'Lied STEM Academy',
                'role': '6th Grade Math/Science Educator',
                'years': '2024 - 2025',
                'metrics': 'Analyzed longitudinal MAP test percentile growth across Fall, Winter, and Spring terms.',
                'dataset_type': 'maps',
                # --- FIXED TYPO: maps_score -> maps_scores ---
                'file_path': 'documents/maps_scores/6th Grade Maps Growth - Period 1.csv' 
            },
            {
                'school': 'Lied STEM Academy',
                'role': '7th Grade ELA / Humanities Educator',
                'years': '2025 - Present',
                'metrics': 'Standards-based assessment tracking (0-4 scale) across core literacy competencies.',
                'dataset_type': 'ela',
                # --- FIXED TYPO: maps_score -> maps_scores ---
                'file_path': 'documents/maps_scores/7th Grade ELA Assessment Scores - Period 1.csv'
            },
            {
                'school': 'University of Nevada, Reno',
                'role': 'Graduate Teaching Assistant & Lecturer',
                'years': '2015 - 2020',
                'metrics': 'Instructed advanced university-level course tracks across behavioral data analysis, neuroscience, and experimental methods.',
                'dataset_type': 'university',
                'file_path': None,
                # DO NOT CHANGE THESE UNR COURSE LINKS - REQUIRED FOR ACTIVE ROUTING
                'courses_taught': [
                    "[PSY 101](https://catalog.unr.edu/preview_course_nopop.php?catoid=58&coid=1096902): Introduction to Psychology",
                    "[PSY 210](https://catalog.unr.edu/preview_course.php?catoid=58&coid=1096904): Statistical Methods",
                    "[PSY 240](https://catalog.unr.edu/preview_course_nopop.php?catoid=58&coid=1096906&print): Introduction to Research Methods",
                    "[PSY 310](https://catalog.unr.edu/preview_course_nopop.php?catoid=58&coid=1096910): Educational/Experimental Psychology",
                    "[PSY 403](https://catalog.unr.edu/preview_course_nopop.php?catoid=58&coid=1096912&print): Physiological Psychology",
                    "[PSY 405](https://catalog.unr.edu/preview_course_nopop.php?catoid=58&coid=1096914): Perception",
                    "[PSY 427](https://catalog.unr.edu/preview_course_nopop.php?catoid=58&coid=1098024): Computer Applications in Social and Behavioral Science",
                    "[PSY 432](https://catalog.unr.edu/preview_course_nopop.php?catoid=58&coid=1096923): Human Memory"
                ]
            }
        ],
        # NEW: Links for external platforms
        'tutoring_platforms': {
            'Wyzant': 'https://www.wyzant.com/tutors/your_link_here',
            'LinkedIn ProFinder': 'https://www.linkedin.com/in/kylewkillebrew/'
        }
    }
