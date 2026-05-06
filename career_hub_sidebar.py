"""
=============================================================================
MODULE: career_hub_sidebar.py (UI Controller)
AUTHOR: Kyle W. Killebrew, PhD
DESCRIPTION: 
    Centralized sidebar component for the Career Hub ecosystem.
    Imports into app.py and all pages/ scripts to ensure a uniform
    UI without duplicating code.
=============================================================================
"""

import streamlit as st

def render_sidebar():
    """
    Renders the custom sidebar with the masthead, directory, presence links,
    and unified CSS styling.
    
    MATLAB ANALOGY: This is like a custom UI function that accepts a figure 
    handle and builds out the standardized uipanels and uicontrols.
    """
    
    # --- 1. GLOBAL SIDEBAR CSS (Styling & Bug Fixes) ---
    st.markdown("""
        <style>
        /* Hide the default Streamlit sidebar navigation menu to remove emojis/clutter */
        [data-testid="stSidebarNav"] {display: none;}
        
        /* Fix the Chevron Bug: Prevent custom fonts from overriding Streamlit's internal icons */
        [data-testid="collapsedControl"] {
            font-family: sans-serif !important; 
        }

        /* Standardize Sidebar Background & Text using Palette A (Neuromorphic Blue) */
        [data-testid="stSidebar"] {
            background-color: #0F172A; /* Deep Slate */
            color: #F8FAFC; /* Crisp White */
            font-family: 'Inter', 'Segoe UI', sans-serif;
        }

        /* Custom link styling to replace the default navigation */
        .sidebar-link {
            display: block;
            padding: 0.5rem 1rem;
            color: #F8FAFC !important;
            text-decoration: none;
            font-size: 1.05rem;
            border-radius: 5px;
            margin-bottom: 5px;
            transition: background-color 0.3s, color 0.3s;
        }
        .sidebar-link:hover {
            background-color: #1E293B; /* Slightly lighter slate */
            color: #38BDF8 !important; /* Bright Sky Blue Accent */
        }
        
        /* Masthead styling */
        .masthead-container {
            display: flex;
            align-items: center;
            gap: 15px;
            margin-top: -40px; /* Pulls content up to remove dead whitespace */
            margin-bottom: 30px;
        }
        .masthead-text {
            line-height: 1.2;
        }
        .masthead-name {
            font-size: 1.1rem;
            font-weight: bold;
            color: #F8FAFC;
        }
        .masthead-title {
            font-size: 0.85rem;
            color: #94A3B8; /* Muted Slate */
        }
        
        /* Presence / Social Bar Styling */
        .presence-bar {
            display: flex;
            gap: 15px;
            justify-content: center;
            margin-top: 30px;
            margin-bottom: 20px;
            flex-wrap: wrap; /* Allows icons to wrap if screen is very narrow */
        }
        .presence-icon {
            color: #94A3B8;
            transition: color 0.3s;
        }
        .presence-icon:hover {
            color: #38BDF8; /* Sky Blue Accent on hover */
        }
        
        /* Copyright footer */
        .sidebar-footer {
            text-align: center;
            font-size: 0.75rem;
            color: #64748B;
            margin-top: 40px;
        }
        </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        # --- 2. MASTHEAD (Brain Logo + Welcome) ---
        # The SVG uses "currentColor" so it perfectly matches our CSS text colors.
        brain_svg = """
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="55" height="55" fill="none" stroke="#38BDF8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M50 85 C30 85, 15 70, 15 50 C15 35, 25 20, 40 15 C45 13, 55 13, 60 15 C75 20, 85 35, 85 50 C85 70, 70 85, 50 85 Z" />
          <path d="M30 35 L45 25 L60 30 L70 45 L65 65 L50 75 L35 60 Z" />
          <circle cx="30" cy="35" r="3" fill="#38BDF8"/>
          <circle cx="45" cy="25" r="3" fill="#38BDF8"/>
          <circle cx="60" cy="30" r="3" fill="#38BDF8"/>
          <circle cx="70" cy="45" r="3" fill="#38BDF8"/>
          <circle cx="65" cy="65" r="3" fill="#38BDF8"/>
          <circle cx="50" cy="75" r="3" fill="#38BDF8"/>
          <circle cx="35" cy="60" r="3" fill="#38BDF8"/>
          <circle cx="50" cy="50" r="4" fill="#38BDF8"/>
          <path d="M50 50 L30 35 M50 50 L45 25 M50 50 L60 30 M50 50 L70 45 M50 50 L65 65 M50 50 L50 75 M50 50 L35 60" opacity="0.5"/>
        </svg>
        """
        
        st.markdown(f"""
            <div class="masthead-container">
                <div>{brain_svg}</div>
                <div class="masthead-text">
                    <div class="masthead-name">Kyle W. Killebrew, PhD</div>
                    <div class="masthead-title">Data Scientist & AI Educator</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        st.divider()

        # --- 3. DIRECTORY LINKS ---
        # We use st.page_link for internal pages to maintain Single-Page App speeds.
        # Setting icon=None removes the default Streamlit emojis.
        # Career Hub spokes #
        # Using native st.page_link for Streamlit's internal router
        st.page_link("career_hub_app.py", label="Career Hub (Home)", icon=None)
        st.page_link("pages/1_academic_profile.py", label="Academic Research Profile", icon=None)
        st.page_link("pages/2_tutoring_mentorship.py", label="Tutoring and Career Mentorship", icon=None)

        # We keep the raw HTML ONLY for the external jump to the Data Hub!
        data_hub_url = "https://data-projects.neuro-edu.io"
        st.markdown(f'<a href="{data_hub_url}" target="_self" class="sidebar-link">Data Science Projects</a>', unsafe_allow_html=True)

        st.divider()

        # --- 4. PRESENCE / SOCIAL BAR ---
        # Using scalable SVGs arranged horizontally via Flexbox
        # Wyzant SVG placeholder (using a generic education icon since Wyzant lacks a standard open-source SVG)
        wyzant_svg = """<svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor"><path d="M12 3L1 9l4 2.18v6L12 21l7-3.82v-6l2.12-1.15V17h2V9L12 3zm6.82 6L12 12.72 5.18 9 12 5.28 18.82 9zM17 15.99l-5 2.73-5-2.73v-3.72L12 15l5-2.73v3.72z"/></svg>"""

        presence_html = f"""
        <div class="presence-bar">
            <a href="https://linkedin.com/in/yourprofile" target="_blank" class="presence-icon" title="LinkedIn">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor"><path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z"/></svg>
            </a>
            <a href="https://github.com/yourprofile" target="_blank" class="presence-icon" title="GitHub">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor"><path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.332-5.467-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/></svg>
            </a>
            <a href="https://scholar.google.com/citations?user=yourid" target="_blank" class="presence-icon" title="Google Scholar">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor"><path d="M12 24a7 7 0 1 1 0-14 7 7 0 0 1 0 14zm0-24L0 9.5l4.838 3.911L12 17.428l7.162-4.017v6.611h2v-8.156L24 9.5z"/></svg>
            </a>
            <a href="https://orcid.org/your-orcid" target="_blank" class="presence-icon" title="ORCID">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor"><path d="M12 0C5.372 0 0 5.372 0 12s5.372 12 12 12 12-5.372 12-12S18.628 0 12 0zM7.369 4.378c.525 0 .947.431.947.947s-.422.949-.947.949a.95.95 0 0 1-.949-.949c0-.516.424-.947.949-.947zm-.722 3.038h1.444v10.041H6.647V7.416zm3.562 0h3.9c3.712 0 5.344 2.653 5.344 5.025 0 2.578-2.016 5.025-5.325 5.025h-3.919V7.416zm1.444 1.303v7.444h2.297c3.272 0 4.022-2.484 4.022-3.722 0-2.016-1.284-3.722-4.097-3.722h-2.222z"/></svg>
            </a>
            <a href="https://twitter.com/yourhandle" target="_blank" class="presence-icon" title="X (Twitter)">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>
            </a>
            <a href="https://www.wyzant.com/Tutors/yourprofile" target="_blank" class="presence-icon" title="Wyzant Tutoring">
                {wyzant_svg}
            </a>
        </div>
        """
        st.markdown(presence_html, unsafe_allow_html=True)

        # --- 5. COPYRIGHT FOOTER ---
        st.markdown("""
            <div class="sidebar-footer">
                © 2026 Kyle W. Killebrew.<br>
                Data, models, and resume entirely self-authored.
            </div>
        """, unsafe_allow_html=True)