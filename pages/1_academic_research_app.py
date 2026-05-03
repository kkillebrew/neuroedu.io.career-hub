# Inside pages/1_academic_research.py
st.title("Academic Career & Research")

# --- SIDEBAR ---
with st.sidebar:

    # --- 1. HIDE DEFAULT NAVIGATION ---
    # This CSS turns off Streamlit's ugly auto-generated file list
    st.markdown("""
        <style>
            [data-testid="stSidebarNav"] {display: none !important;}
        </style>
    """, unsafe_allow_html=True)

    # --- 2. CUSTOM DIRECTORY MENU ---
    st.divider()
    st.subheader("🧭 Directory")
    
    # Internal Pages (Make sure these filenames perfectly match your GitHub!)
    st.page_link("career_hub_app.py", label="Hub", icon="🏠")
    st.page_link("pages/1_academic_research_app.py", label="Academic Research Profile", icon="🔬")
    st.page_link("pages/2_mentorship_app.py", label="Academic Mentorship", icon="🎓")
    
    # External Data Hub Link (Styled to match your deep navy sidebar text)
    st.markdown("""
        <div style="padding: 0.35rem 0;">
            <a href="https://data-projects.neuro-edu.io" target="_blank" style="text-decoration: none; color: #f8fafc; font-size: 1rem; display: flex; align-items: center; gap: 0.5rem;">
                📊 <span>Data Science Projects ↗</span>
            </a>
        </div>
    """, unsafe_allow_html=True)
    
    st.divider()

    # --- 3. MY SOCIALS ---
    st.subheader("🌐 Presence")
    st.markdown(f"🔬 [ORCID Profile](https://orcid.org/{academic.get('orcid', '')})")
    st.markdown(f"📈 [Google Scholar]({academic.get('google_scholar', '#')})")
    st.markdown(f"💼 [LinkedIn Profile]({academic.get('linkedin', '#')})")
    
    st.divider()
    st.caption("PhD Portfolio System | 2026")

c1, c2 = st.columns([2, 1])

with c1:
    st.header("Publications")
    # Loop through your pubs_df here as we did before
    for _, row in pubs_df.iterrows():
        st.markdown(f"**{row['Year']}** | [{row['Title']}]({row['Link']})")

with c2:
    st.header("Academic Assets")
    # Academic-specific CV download
    ac_cv = "documents/kyle_academic_cv.pdf"
    if os.path.exists(ac_cv):
        with open(ac_cv, "rb") as f:
            st.download_button("📂 Download Academic CV", f.read(), "Killebrew_Academic_CV.pdf")
    
    st.markdown("### Research Expertise")
    st.info("• Electrophysiology (EEG)\n• Psychosis Modeling\n• Experimental Design")