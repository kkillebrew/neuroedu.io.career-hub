"""
=============================================================================
MODULE: career_hub_app.py (Main Hub Entry Point)
AUTHOR: Kyle W. Killebrew, PhD
VERSION: 4.0 (Micro-Frontend Hub)
DESCRIPTION: 
    The landing page for career-hub.neuro-edu.io. Handles professional
    summary, CV downloads, and links to the Data Projects spoke hub.
=============================================================================
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import os
import sys
import requests
import base64

# --- PATH CONFIGURATION ---
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from career_hub_loader import (
    get_biographic_metadata, 
    get_portfolio_metadata, 
    get_references_metadata,
)

from career_hub_sidebar import apply_global_settings, render_sidebar

########################################
#        APPLY GLOBAL SETTINGS         #
########################################
apply_global_settings("Kyle W. Killebrew, PhD | Career Hub")

########################################
#  RENDER THE SIDEBAR FOR CAREER-HUB   #
########################################
render_sidebar()

# --- DATA HYDRATION ---
bio = get_biographic_metadata()
pubs, skills, academic = get_portfolio_metadata()
references = get_references_metadata()

# --- MASTHEAD & BIOGRAPHIC LAYOUT ---
current_dir = os.path.dirname(os.path.abspath(__file__))
logo_path = os.path.join(current_dir, "documents", "Neuro-Edu_Logo_Transparent.png")
img_path = os.path.join(current_dir, "documents", "kyle.jpg")

def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    else:
        st.error(f"⚠️ Debug: Image not found at absolute path: {image_path}")
        return ""

b64_logo = get_base64_image(logo_path)
b64_profile = get_base64_image(img_path)

st.markdown(f"""
<style>
.logo-container {{ text-align: center; margin-bottom: 30px; }}
.logo-container img {{ max-width: 320px; width: 100%; height: auto; }}
</style>
<div class="logo-container">
    <img src="data:image/png;base64,{b64_logo}" alt="Neuro-Edu Logo">
</div>
""", unsafe_allow_html=True)

col_img, col_text = st.columns([1, 2.5], gap="large")

with col_img:
    st.markdown(f"""
<style>
.profile-img-container {{
    width: 120px; 
    height: 120px;
    margin: 0 auto 20px auto;
    overflow: hidden; 
    border-radius: 50%;
    border: 2px solid #334155;
    background-color: #0F172A;
    display: flex;
    justify-content: center;
    align-items: center;
}}
.profile-img-container img {{
    width: 100%;
    height: 100%;
    object-fit: cover; 
}}
</style>
<div class="profile-img-container">
    <img src="data:image/jpeg;base64,{b64_profile}" alt="{bio['name']}">
</div>
""", unsafe_allow_html=True)

with col_text:
    st.markdown(f"""
<style>
.masthead-title {{ font-size: 3rem; font-weight: bold; color: #F8FAFC; margin-bottom: 5px; line-height: 1.1; }}
.masthead-subtitle {{ font-size: 1.3rem; color: #38BDF8; margin-bottom: 20px; font-weight: 500; }}
.vision-header {{ font-size: 1.1rem; color: #F8FAFC; font-weight: bold; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 1px; border-bottom: 1px solid #334155; padding-bottom: 5px; display: inline-block;}}
.vision-blurb {{ font-size: 1rem; color: #CBD5E1; line-height: 1.6; background-color: transparent; }}
</style>
<div class="masthead-title">{bio['name']}</div>
<div class="masthead-subtitle">Behavioral, Cognitive, Neuro, and Data Scientist and Educational Mentor</div>
<div class="vision-header">Strategic Vision</div>
<div class="vision-blurb">{bio['bio']}</div>
""", unsafe_allow_html=True)

st.divider()

# --- EXPLORE MY WORK: THE PORTFOLIO MATRIX ---
st.markdown("""
<style>
.proj-title a { color: #E2E8F0; text-decoration: none; transition: color 0.3s ease; }
.proj-title a:hover { color: #38BDF8; }

.portfolio-box { background-color: #0F172A; border: 1px solid #334155; border-radius: 8px; padding: 25px; height: 100%; display: flex; flex-direction: column; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
.portfolio-header { color: #F8FAFC; text-align: center; margin-bottom: 25px; font-size: 1.4rem; font-weight: bold; border-bottom: 1px solid #334155; padding-bottom: 15px; }

.proj-row { display: flex; align-items: stretch; margin-bottom: 20px; gap: 20px; flex: 1; }
.proj-row.reverse { flex-direction: row-reverse; }
.proj-text { flex: 1.5; display: flex; flex-direction: column; justify-content: center; }
.proj-title { font-weight: 600; color: #E2E8F0; font-size: 1.1rem; margin-bottom: 6px; }
.proj-desc { color: #94A3B8; font-size: 0.95rem; line-height: 1.5; }
.proj-canvas { flex: 1; background-color: #1E293B; border-radius: 6px; border: 1px solid #475569; min-height: 120px; display: flex; align-items: center; justify-content: center; color: #64748B; font-size: 0.9rem; font-style: italic;}
</style>
""", unsafe_allow_html=True)

b1, b2, b3 = st.columns(3, gap="large")

with b1:
    st.markdown("""
<div class="portfolio-box">
    <div class="portfolio-header">Data Science Portfolio</div>
    <div class="proj-row">
        <div class="proj-canvas">Canvas Render</div>
        <div class="proj-text">
            <div class="proj-title"><a href="#">Longitudinal MAPS Percentile Engine</a></div>
            <div class="proj-desc">A memory-optimized data pipeline utilizing Pandas explicit column filtering to track national percentile growth metrics across sequential testing terms.</div>
        </div>
    </div>
    <div class="proj-row reverse">
        <div class="proj-canvas">Canvas Render</div>
        <div class="proj-text" style="text-align: right;">
            <div class="proj-title"><a href="#">Keyboard Typing Behavior Analysis</a></div>
            <div class="proj-desc">An interactive machine learning pipeline executing feature extraction and cluster analysis on behavioral keystroke dynamics to isolate user profiles.</div>
        </div>
    </div>
    <div class="proj-row">
        <div class="proj-canvas">Canvas Render</div>
        <div class="proj-text">
            <div class="proj-title"><a href="#">Time-Series Signal Processing Dashboard</a></div>
            <div class="proj-desc">A high-performance visualization dashboard designed for large-scale EEG data tracking, applying automated artifact rejection.</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

with b2:
    st.markdown("""
<div class="portfolio-box">
    <div class="portfolio-header">Academic Research Portfolio</div>
    <div class="proj-row reverse">
        <div class="proj-canvas">Canvas Render</div>
        <div class="proj-text" style="text-align: right;">
            <div class="proj-title"><a href="#">Cortical Dynamics in Psychosis Populations</a></div>
            <div class="proj-desc">High-density EEG research mapping phase-locking values and neural oscillations during cognitive tasks to isolate biomarkers.</div>
        </div>
    </div>
    <div class="proj-row">
        <div class="proj-canvas">Canvas Render</div>
        <div class="proj-text">
            <div class="proj-title"><a href="#">Working Memory Grouping Metrics</a></div>
            <div class="proj-desc">Behavioral modeling analysis exploring the limits of human visual short-term storage capacity when processing chunked arrays.</div>
        </div>
    </div>
    <div class="proj-row reverse">
        <div class="proj-canvas">Canvas Render</div>
        <div class="proj-text" style="text-align: right;">
            <div class="proj-title"><a href="#">Psychophysics Replication Frameworks</a></div>
            <div class="proj-desc">An automated statistical analysis suite built to process multi-participant trial data, verifying experimental design paradigms.</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

with b3:
    st.markdown("""
<div class="portfolio-box">
    <div class="portfolio-header">Education & Mentorship Portfolio</div>
    <div class="proj-row">
        <div class="proj-canvas">Canvas Render</div>
        <div class="proj-text">
            <div class="proj-title"><a href="#">Fitts's Law Neuro-Motor Control Rig</a></div>
            <div class="proj-desc">An interactive HTML5 Canvas reaction-time engine that maps human visual-motor channel capacity and bandwidth.</div>
        </div>
    </div>
    <div class="proj-row reverse">
        <div class="proj-canvas">Canvas Render</div>
        <div class="proj-text" style="text-align: right;">
            <div class="proj-title"><a href="#">Visual Search & Attention Task</a></div>
            <div class="proj-desc">A pre-attentive feature binding experiment replicating Treisman and Wolfe paradigms to demonstrate parallel pop-out mechanics.</div>
        </div>
    </div>
    <div class="proj-row">
        <div class="proj-canvas">Canvas Render</div>
        <div class="proj-text">
            <div class="proj-title"><a href="#">Geometric Space & Dissection Displayer</a></div>
            <div class="proj-desc">A real-time coordinate transformation simulator utilizing HTML5 loops to visually demonstrate area derivation to students.</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.divider()

# --- RESTORED: PROFESSIONAL DOCUMENTATION ---
st.markdown("<h3 style='text-align: center; color: #F8FAFC; margin-bottom: 20px;'>Professional Documentation</h3>", unsafe_allow_html=True)

doc_1, doc_2, doc_3, doc_4 = st.columns(4)

with doc_1:
    st.button("Data Science Resume", use_container_width=True)
with doc_2:
    st.button("Academic CV", use_container_width=True)
with doc_3:
    st.button("Teaching and Mentorship Resume", use_container_width=True)
with doc_4:
    st.button("AI Research Portfolio", use_container_width=True)

st.divider()

# --- PROFESSIONAL REFERENCES (Modulo Grid) ---
st.markdown("""
<style>
.ref-card { background-color: #0F172A; padding: 15px; border-radius: 6px; border: 1px solid #1E293B; height: 100%; box-shadow: 0 2px 4px rgba(0,0,0,0.2); }
.ref-name { font-weight: bold; font-size: 1.05rem; color: #F8FAFC; margin-bottom: 2px; }
.ref-title { font-size: 0.85rem; color: #94A3B8; margin-bottom: 10px; }
.ref-contact { font-size: 0.9rem; margin-bottom: 0; }
.ref-contact a { text-decoration: none; color: #38BDF8; transition: color 0.3s ease; }
.ref-contact a:hover { color: #F8FAFC; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h3 style='color: #F8FAFC; margin-bottom: 20px;'>Academic & Professional References</h3>", unsafe_allow_html=True)

ref_cols = st.columns(3)
for i, ref in enumerate(references):
    with ref_cols[i % 3]:
        st.markdown(f"""
<div class="ref-card">
    <p class="ref-name">{ref['name']}</p>
    <p class="ref-title">{ref['title']}</p>
    <p class="ref-contact"><a href="mailto:{ref['contact']}">✉️ {ref['contact']}</a></p>
</div>
        """, unsafe_allow_html=True)