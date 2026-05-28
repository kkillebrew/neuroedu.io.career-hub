"""
=============================================================================
MODULE: pages/components/mini_demos_research.py
AUTHOR: PyViz Web & Data Mentor
DESCRIPTION: 
    Isolated payloads for the Academic Research Portfolio. Handles pure HTML5
    canvas loops and Base64 image injections to bypass Python/Streamlit overhead.
=============================================================================
"""

import streamlit.components.v1 as components
import base64
import os

def get_base64_fallback(file_path):
    """
    Reads a local image/gif and converts it to a Base64 string.
    If the file is missing (e.g., user hasn't generated it yet), it returns
    a tiny transparent 1x1 pixel to prevent the UI from breaking.
    """
    if os.path.exists(file_path):
        with open(file_path, "rb") as img_file:
            encoded_string = base64.b64encode(img_file.read()).decode()
            # Determine MIME type based on extension
            mime = "image/gif" if file_path.lower().endswith(".gif") else "image/png"
            return f"data:{mime};base64,{encoded_string}"
    else:
        # Fallback: 1x1 transparent PNG to prevent broken image icons
        return "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="


def render_sfm_mini(height=140):
    """
    Renders a split pane: Left is a Base64 GIF of the Structure-From-Motion cylinder.
    Right is a lightweight Plotly.js chart displaying behavioral thresholds.
    """
    # Attempt to load the GIF, fallback to transparent if missing
    gif_data_uri = get_base64_fallback("documents/sfm_cylinder.gif")
    
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://cdn.plot.ly/plotly-2.24.1.min.js"></script>
        <style>
            body {{ margin: 0; background-color: #1E293B; border-radius: 6px; overflow: hidden; display: flex; height: {height}px; }}
            .visual-pane {{ width: 40%; background-color: #0F172A; display: flex; align-items: center; justify-content: center; }}
            .visual-pane img {{ width: 100%; height: 100%; object-fit: cover; opacity: 0.8; }}
            .chart-pane {{ width: 60%; height: 100%; }}
        </style>
    </head>
    <body>
        <div class="visual-pane">
            <img src="{gif_data_uri}" alt="SFM Cylinder">
        </div>
        <div class="chart-pane" id="plot"></div>
        <script>
            /* * Visualization Best Practice: 
             * We use a muted slate (#64748B) for the control group and an attention-grabbing 
             * red (#EF4444) for the Schizophrenia group to cue the user to the abnormality.
             */
            var data = [{{
                x: ['Control', 'Sz'],
                y: [0.85, 0.42], // Pre-computed threshold means
                type: 'bar',
                marker: {{
                    color: ['#64748B', '#EF4444']
                }}
            }}];

            var layout = {{
                margin: {{l: 25, r: 10, t: 25, b: 25}},
                paper_bgcolor: 'rgba(0,0,0,0)',
                plot_bgcolor: 'rgba(0,0,0,0)',
                title: {{ text: 'Coherence Threshold', font: {{color: '#94A3B8', size: 10}} }},
                xaxis: {{ tickfont: {{color: '#94A3B8', size: 10}} }},
                yaxis: {{ visible: false }},
                showlegend: false
            }};

            Plotly.newPlot('plot', data, layout, {{displayModeBar: false, staticPlot: true}});
        </script>
    </body>
    </html>
    """
    components.html(html_code, height=height)


def render_eeg_mini(height=140):
    """
    Injects the static, high-res pre-computed EEG topographic map figure.
    Completely bypasses the heavy mne-python library initialization.
    """
    topo_data_uri = get_base64_fallback("documents/eeg_topos.png")
    
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ margin: 0; background-color: #1E293B; border-radius: 6px; overflow: hidden; display: flex; align-items: center; justify-content: center; height: {height}px; }}
            img {{ width: 100%; height: 100%; object-fit: contain; padding: 5px; }}
        </style>
    </head>
    <body>
        <img src="{topo_data_uri}" alt="EEG Topographies">
    </body>
    </html>
    """
    components.html(html_code, height=height)


def render_rotating_line_mini(height=140):
    """
    Pure HTML5 Canvas simulation of a visual illusion. 
    Left line rotates constantly. Right line modulates speed dynamically.
    """
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ margin: 0; background-color: #1E293B; border-radius: 6px; overflow: hidden; display: flex; justify-content: center; align-items: center; height: {height}px; }}
            canvas {{ display: block; }}
        </style>
    </head>
    <body>
        <canvas id="illusionCanvas" width="300" height="{height}"></canvas>
        <script>
            const ctx = document.getElementById('illusionCanvas').getContext('2d');
            let lastTime = performance.now();
            let angleA = 0;
            let angleB = 0;
            const baseSpeed = 0.0015; // Base angular velocity

            function draw(time) {{
                let dt = time - lastTime;
                lastTime = time;
                
                // Prevent massive jumps if the browser tab goes inactive
                if (dt > 50) dt = 16; 

                ctx.clearRect(0, 0, 300, {height});
                
                // --- Line A: Constant Rotation (Uncorrected) ---
                angleA += dt * baseSpeed;
                ctx.save();
                ctx.translate(75, {height/2});
                ctx.rotate(angleA);
                ctx.beginPath(); ctx.moveTo(-35, 0); ctx.lineTo(35, 0);
                ctx.strokeStyle = '#38BDF8'; // Muted blue
                ctx.lineWidth = 3; 
                ctx.stroke();
                ctx.restore();

                // --- Line B: Modulated Rotation (Corrected) ---
                // Speed is modulated using a sine wave based on its current angle
                // Multiply angle by 2 so it speeds up/slows down symmetrically twice per rotation
                let speedMod = 1 + 0.8 * Math.sin(angleB * 2); 
                angleB += dt * baseSpeed * speedMod;
                
                ctx.save();
                ctx.translate(225, {height/2});
                ctx.rotate(angleB);
                ctx.beginPath(); ctx.moveTo(-35, 0); ctx.lineTo(35, 0);
                ctx.strokeStyle = '#4ADE80'; // Success green
                ctx.lineWidth = 3; 
                ctx.stroke();
                ctx.restore();

                // Draw a subtle divider
                ctx.beginPath(); ctx.moveTo(150, 20); ctx.lineTo(150, {height-20});
                ctx.strokeStyle = '#334155'; ctx.lineWidth = 1; ctx.stroke();

                requestAnimationFrame(draw);
            }}
            requestAnimationFrame(draw);
        </script>
    </body>
    </html>
    """
    components.html(html_code, height=height)