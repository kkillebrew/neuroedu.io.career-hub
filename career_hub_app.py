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
# This tells the script to look one folder up to find the 'loaders' directory
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
# 1. Base64 Image Encoding (Bypassing Streamlit's rigid image constraints for CSS control)
# MATLAB Analogy: Similar to using `imread` combined with `imfinfo` to handle raw image matrices safely.
current_dir = os.path.dirname(os.path.abspath(__file__))
logo_path = os.path.join(current_dir, "documents", "Neuro-Edu_Logo_Transparent.png")
img_path = os.path.join(current_dir, "documents", "kyle.jpg")

def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    else:
        # Graceful Failure: If the image breaks, this error tells you exactly where it looked.
        st.error(f"⚠️ Debug: Image not found at absolute path: {image_path}")
        return ""

b64_logo = get_base64_image(logo_path)
b64_profile = get_base64_image(img_path)

# 2. High-Contrast Slate CSS & Structural Injection
# Note: HTML inside st.markdown MUST be left-aligned to prevent Markdown from rendering it as a code block.
st.markdown(f"""
<style>
/* Profile Image Architecture */
.profile-img-container {{
    width: 180px; 
    height: 180px;
    margin: 0 auto 20px auto;
    overflow: hidden; 
    border-radius: 50%;
    border: 2px solid #334155;
    background-color: #0F172A;
}}
.profile-img-container img {{
    width: 150%; 
    margin: -25% 0 0 -25%; 
}}
.logo-container {{ text-align: center; margin-bottom: 15px; }}
.logo-container img {{ max-width: 280px; width: 100%; height: auto; }}

/* Typography & Header Hierarchy */
.masthead-title {{ font-size: 2.5rem; font-weight: bold; color: #F8FAFC; text-align: center; margin-bottom: 5px; line-height: 1.2; }}
.masthead-subtitle {{ font-size: 1.15rem; color: #94A3B8; text-align: center; margin-bottom: 25px; font-weight: 500; }}
.vision-header {{ font-size: 1.05rem; color: #F8FAFC; text-align: center; font-weight: bold; margin-bottom: 5px; text-transform: uppercase; letter-spacing: 1px; }}
.vision-blurb {{ font-size: 0.9rem; color: #CBD5E1; text-align: center; max-width: 750px; margin: 0 auto 40px auto; line-height: 1.6; padding: 15px; background-color: #0F172A; border-radius: 8px; border: 1px solid #1E293B; }}
</style>

<div class="logo-container">
    <img src="data:image/png;base64,{b64_logo}" alt="Neuro-Edu Logo">
</div>
<div class="profile-img-container">
    <img src="data:image/jpeg;base64,{b64_profile}" alt="Kyle W. Killebrew">
</div>
<div class="masthead-title">{bio['name']}</div>
<div class="masthead-subtitle">Behavioral, Cognitive, Neuro, and Data Scientist and Educational Mentor</div>

<!-- Added missing Strategic Vision structure -->
<div class="vision-header">Strategic Vision</div>
<div class="vision-blurb">
    {bio['bio']}
</div>
""", unsafe_allow_html=True)

st.divider()

# --- EXPLORE MY WORK: THE PORTFOLIO MATRIX ---
st.markdown("""
<style>
/* Dark Slate Themed Portfolio Boxes */
.portfolio-box { background-color: #0F172A; border: 1px solid #334155; border-radius: 8px; padding: 20px; height: 100%; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
.portfolio-header { color: #F8FAFC; text-align: center; margin-bottom: 20px; font-size: 1.25rem; font-weight: bold; border-bottom: 1px solid #334155; padding-bottom: 10px; }

/* Flexbox Alternating Layout Matrix */
.proj-row { display: flex; align-items: stretch; margin-bottom: 15px; gap: 15px; }
.proj-row.reverse { flex-direction: row-reverse; }
.proj-text { flex: 1.5; display: flex; flex-direction: column; justify-content: center; }
.proj-title { font-weight: 600; color: #E2E8F0; font-size: 0.95rem; margin-bottom: 4px; }
.proj-desc { color: #94A3B8; font-size: 0.8rem; line-height: 1.4; }
.proj-canvas { flex: 1; background-color: #1E293B; border-radius: 4px; border: 1px solid #334155; min-height: 80px; display: flex; align-items: center; justify-content: center; color: #475569; font-size: 0.75rem; font-style: italic;}
</style>
""", unsafe_allow_html=True)

# Three uniform, horizontally aligned display blocks
b1, b2, b3 = st.columns(3, gap="large")

with b1:
    st.markdown("""
<div class="portfolio-box">
    <div class="portfolio-header">Data Science Portfolio</div>
    <div class="proj-row">
        <div class="proj-canvas">Canvas Render</div>
        <div class="proj-text">
            <div class="proj-title">Longitudinal MAPS Percentile Engine</div>
            <div class="proj-desc">A memory-optimized data pipeline utilizing Pandas explicit column filtering to track national percentile growth metrics across sequential testing terms.</div>
        </div>
    </div>
    <div class="proj-row reverse">
        <div class="proj-canvas">Canvas Render</div>
        <div class="proj-text" style="text-align: right;">
            <div class="proj-title">Keyboard Typing Behavior Analysis</div>
            <div class="proj-desc">An interactive machine learning pipeline executing feature extraction and cluster analysis on behavioral keystroke dynamics to isolate user profiles.</div>
        </div>
    </div>
    <div class="proj-row">
        <div class="proj-canvas">Canvas Render</div>
        <div class="proj-text">
            <div class="proj-title">Time-Series Signal Processing Dashboard</div>
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
            <div class="proj-title">Cortical Dynamics in Psychosis Populations</div>
            <div class="proj-desc">High-density EEG research mapping phase-locking values and neural oscillations during cognitive tasks to isolate biomarkers.</div>
        </div>
    </div>
    <div class="proj-row">
        <div class="proj-canvas">Canvas Render</div>
        <div class="proj-text">
            <div class="proj-title">Working Memory Grouping Metrics</div>
            <div class="proj-desc">Behavioral modeling analysis exploring the limits of human visual short-term storage capacity when processing chunked arrays.</div>
        </div>
    </div>
    <div class="proj-row reverse">
        <div class="proj-canvas">Canvas Render</div>
        <div class="proj-text" style="text-align: right;">
            <div class="proj-title">Psychophysics Replication Frameworks</div>
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
            <div class="proj-title">Fitts's Law Neuro-Motor Control Rig</div>
            <div class="proj-desc">An interactive HTML5 Canvas reaction-time engine that maps human visual-motor channel capacity and bandwidth.</div>
        </div>
    </div>
    <div class="proj-row reverse">
        <div class="proj-canvas">Canvas Render</div>
        <div class="proj-text" style="text-align: right;">
            <div class="proj-title">Visual Search & Attention Task</div>
            <div class="proj-desc">A pre-attentive feature binding experiment replicating Treisman and Wolfe paradigms to demonstrate parallel pop-out mechanics.</div>
        </div>
    </div>
    <div class="proj-row">
        <div class="proj-canvas">Canvas Render</div>
        <div class="proj-text">
            <div class="proj-title">Geometric Space & Dissection Displayer</div>
            <div class="proj-desc">A real-time coordinate transformation simulator utilizing HTML5 loops to visually demonstrate area derivation to students.</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.divider()

# --- PROFESSIONAL DOCUMENTATION ---
st.markdown("<h3 style='text-align: center; color: #F8FAFC; margin-bottom: 20px;'>Professional Documentation</h3>", unsafe_allow_html=True)

# 4 Symmetrical flat-styled buttons without emoticons
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
st.markdown("<h3 style='color: #F8FAFC; margin-bottom: 20px;'>Professional and Academic References</h3>", unsafe_allow_html=True)

ref_cols = st.columns(3)
for i, ref in enumerate(references):
    # Explicit modulo loop division to distribute seamlessly across the 3-column grid
    with ref_cols[i % 3]:
        st.markdown(f"""
            <div style="background-color: #0F172A; padding: 15px; border-radius: 6px; border: 1px solid #1E293B; height: 100%;">
                <p style="font-weight: bold; font-size: 1.05rem; color: #F8FAFC; margin-bottom: 2px;">{ref['name']}</p>
                <p style="font-size: 0.85rem; color: #94A3B8; margin-bottom: 10px;">{ref['title']}</p>
                <p style="font-size: 0.9rem; margin-bottom: 0;"><a href="mailto:{ref['contact']}" style="text-decoration: none; color: #38BDF8;">{ref['contact']}</a></p>
            </div>
        """, unsafe_allow_html=True)