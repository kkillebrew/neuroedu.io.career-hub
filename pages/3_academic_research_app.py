# Inside pages/1_academic_research.py
st.title("Academic Career & Research")

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