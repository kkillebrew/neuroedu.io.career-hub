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
# 1. Base64 Image Encoding 
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

# 2. Logo Isolation (Centered at the very top)
st.markdown(f"""
<style>
.logo-container {{ text-align: center; margin-bottom: 30px; }}
.logo-container img {{ max-width: 320px; width: 100%; height: auto; }}
</style>
<div class="logo-container">
    <img src="data:image/png;base64,{b64_logo}" alt="Neuro-Edu Logo">
</div>
""", unsafe_allow_html=True)

# 3. Side-by-Side Biographic Layout
col_img, col_text = st.columns([1, 2.5], gap="large")

with col_img:
    st.markdown(f"""
<style>
.profile-img-container {{
    width: 100%;
    aspect-ratio: 1 / 1; /* Forces a perfect square bounding box */
    border-radius: 50%;
    overflow: hidden; 
    border: 3px solid #334155;
    background-color: #0F172A;
    box-shadow: 0 4px 10px rgba(0,0,0,0.5);
}}
.profile-img-container img {{
    width: 100%;
    height: 100%;
    object-fit: cover; /* Prevents image warping */
    object-position: 25% 50%; /* X-Axis % and Y-Axis %. Moves the crop window! */
}}
</style>
<div class="profile-img-container">
    <img src="data:image/jpeg;base64,{b64_profile}" alt="{bio['name']}">
</div>
""", unsafe_allow_html=True)

with col_text:
    # Pulling 'title' and 'bio' directly from your data loader dict
    st.markdown(f"""
<style>
.masthead-title {{ font-size: 3rem; font-weight: bold; color: #F8FAFC; margin-bottom: 5px; line-height: 1.1; }}
.masthead-subtitle {{ font-size: 1.3rem; color: #38BDF8; margin-bottom: 20px; font-weight: 500; }}
.vision-header {{ font-size: 1.1rem; color: #F8FAFC; font-weight: bold; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 1px; border-bottom: 1px solid #334155; padding-bottom: 5px; display: inline-block;}}
.vision-blurb {{ font-size: 1rem; color: #CBD5E1; line-height: 1.6; background-color: transparent; }}
</style>
<div class="masthead-title">{bio['name']}</div>
<div class="masthead-subtitle">{bio['title']}</div>
<div class="vision-header">Strategic Vision</div>
<div class="vision-blurb">{bio['bio']}</div>
""", unsafe_allow_html=True)

st.divider()

# --- EXPLORE MY WORK: THE PORTFOLIO MATRIX ---
st.markdown("""
<style>
/* Dark Slate Themed Portfolio Boxes - Scaled Up & Height Locked */
.portfolio-box { background-color: #0F172A; border: 1px solid #334155; border-radius: 8px; padding: 25px; height: 100%; display: flex; flex-direction: column; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
.portfolio-header { color: #F8FAFC; text-align: center; margin-bottom: 25px; font-size: 1.4rem; font-weight: bold; border-bottom: 1px solid #334155; padding-bottom: 15px; }

/* Flexbox Alternating Layout Matrix */
.proj-row { display: flex; align-items: stretch; margin-bottom: 20px; gap: 20px; flex: 1; }
.proj-row.reverse { flex-direction: row-reverse; }
.proj-text { flex: 1.5; display: flex; flex-direction: column; justify-content: center; }
.proj-title { font-weight: 600; color: #E2E8F0; font-size: 1.1rem; margin-bottom: 6px; }
.proj-desc { color: #94A3B8; font-size: 0.95rem; line-height: 1.5; }

/* Larger Canvas Blocks */
.proj-canvas { flex: 1; background-color: #1E293B; border-radius: 6px; border: 1px solid #475569; min-height: 120px; display: flex; align-items: center; justify-content: center; color: #64748B; font-size: 0.9rem; font-style: italic;}
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

# --- PROFESSIONAL REFERENCES (Matching Spoke Format) ---
st.markdown("<h3 style='color: #F8FAFC; margin-bottom: 20px;'>Academic & Professional References</h3>", unsafe_allow_html=True)

st.markdown("""
<style>
.ref-card { background-color: #0F172A; padding: 15px; border-radius: 6px; border: 1px solid #1E293B; height: 100%; box-shadow: 0 2px 4px rgba(0,0,0,0.2); }
</style>
""", unsafe_allow_html=True)

ref_cols = st.columns(3)
for i, ref in enumerate(references):
    with ref_cols[i % 3]:
        st.markdown(f"""
<div class="ref-card">
    <p class="ref-name" style="font-weight: bold; font-size: 1.1rem; margin-bottom: 0; color: #F8FAFC;">{ref['name']}</p>
    <p class="ref-title" style="font-size: 0.9rem; color: #94A3B8; margin-bottom: 0.5rem;">{ref['title']}</p>
    <p style="font-size: 0.95rem; margin-bottom: 0;"><a href="mailto:{ref['contact']}" style="text-decoration: none; color: #38BDF8;">✉️ {ref['contact']}</a></p>
</div>
        """, unsafe_allow_html=True)