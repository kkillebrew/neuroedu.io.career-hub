import pandas as pd
import numpy as np

# =====================================================================
# MODULE: PORTFOLIO DATA HUB
# Purpose: Centralized data structures for the Career Web Application.
# =====================================================================

def get_biographic_metadata():
    """
    Returns general bio and resume information for the Home Page.
    Returns: dict
    """
    return {
        'name': 'Kyle W. Killebrew, PhD',
        'title': 'Data Scientist, Neuroscientist & Educational Mentor',
        'bio': "With 15 years of experience spanning neuroscience, mathematical modeling, and education, I bridge the gap between theoretical research and interactive data science. Holding a PhD in Neuroscience, my background involves studying brain dynamics across diverse populations—from undergraduates to patients with psychosis. Today, I channel my passion for lifelong learning into data science and mentorship, helping students and organizations uncover meaningful insights through hypothesis-driven research, meticulous modeling, and inquiry-based education.",
        'interests': ['Neuroscience & Brain Dynamics', 'Mathematical Modeling', 'Data Science & Analytics', 'Inquiry-Driven Education']
    }

def get_portfolio_metadata():
    """
    Returns the core data for the portfolio and researcher sections.
    """
    # 1. Researcher Profile (Publications)
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
    
    # 2. Skill Metrics
    skills = {
        'Python': 95,
        'MATLAB': 95,
        'Statistical Modeling': 90,
        'Data Visualization': 92,
        'Experimental Design': 95,
        'Teaching & Mentoring': 98
    }
    
    # 3. Beliefs & Statement of Purpose
    beliefs = {
        'sop': 'To empower individuals and organizations through hands-on data science and inquiry-driven education, fostering a lifelong passion for learning, rigorous methodology, and self-reliant discovery.',
        'core_principles': [
            'Precision & Methodology: High-quality inputs yield high-quality insights. Rigorous methodology matters more than the tool itself.',
            'Passion-Driven Action: True learning and impactful work stem from genuine curiosity and drive. Without passion, nothing is learned.',
            'Lifelong Learning: Skill acquisition isn\'t a one-off task; it is a continuous, enjoyable journey of adaptation and discovery.',
            'Undeniable Documentation: Meticulous documentation is the backbone of reproducibility, efficiency, and scalable success.'
        ]
    }
    
    # 4. Academic IDs
    academic_ids = {
        'orcid': '0000-0002-9662-9844',
        'google_scholar': 'https://scholar.google.com/citations?user=y-2G-voAAAAJ&hl=en'
    }
    
    return pubs, skills, beliefs, academic_ids

def get_teaching_metadata():
    """
    Returns data specifically for the tutoring and mentoring section.
    """
    return {
        'qualifications': [
            '15+ Years Educational Experience (Middle School to College Level)',
            'Specialized 1-on-1 Mentorship & Personalized Curricula',
            'Programming (Python, MATLAB, R) & Data Science',
            'Neuroscience, Biology, and Advanced Mathematics',
            'Hypothesis-Driven Research & Experimental Design'
        ],
        'rates': {
            'Hourly Rate': '$40 - $74/hr (varies based on subject, level, and prep required)',
            'Consulting & Project Design': 'Contact for Quote'
        },
        'learner_profile_fields': [
            'Current Grade/Level',
            'Primary Software/Subject',
            'Learning Style',
            'Short-term Goal'
        ]
    }

def get_references_metadata():
    """
    Returns professional and academic references.
    """
    return [
        {"name": "Dr. Gideon P. Caplovitz", "title": "Professor, UNR (PhD Mentor)", "contact": "gcaplovitz@unr.edu"},
        {"name": "Dr. Michael-Paul Schallmo", "title": "Professor, UMN (Post-doc Advisor)", "contact": "schal110@umn.edu"},
        {"name": "Kelly Thorson", "title": "Principal, Lied STEM", "contact": "thorskt@nv.ccsd.net"},
        {"name": "Dr. Marian Berryhill", "title": "Professor, UNR (PhD Co-Mentor)", "contact": "mberryhill@unr.edu"},
        {"name": "Dr. Ryan Mruczek", "title": "Professor, College of the Holy Cross (Research Peer)", "contact": "rmruczek@holycross.edu"}
    ]

if __name__ == "__main__":
    # Fetch all the data for console testing
    bio = get_biographic_metadata()
    pubs, skills, beliefs, academic = get_portfolio_metadata()
    teaching = get_teaching_metadata()
    references = get_references_metadata()

    print(f"=== PROFILE: {bio['name']} ===")
    print(f"Title: {bio['title']}")
    print(f"Bio: {bio['bio']}")
    print(f"\nLoaded {len(references)} Professional References.")