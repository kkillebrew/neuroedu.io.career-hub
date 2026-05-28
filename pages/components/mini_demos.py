"""
=============================================================================
MODULE: pages/components/mini_demos.py
AUTHOR: PyViz Web & Data Mentor
DESCRIPTION: 
    Lightweight, isolated HTML5 Canvas and Plotly.js payloads for the 
    main career hub landing page. Designed to run at 60fps with zero 
    Streamlit/Python backend overhead.
=============================================================================
"""

import streamlit.components.v1 as components

def render_fittslaw_mini(height=140):
    """Renders a static, pre-computed Plotly JS scatter + regression fit."""
    html_code = """
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://cdn.plot.ly/plotly-2.24.1.min.js"></script>
        <style>
            body { margin: 0; background-color: #1E293B; border-radius: 6px; overflow: hidden; display: flex; align-items: center; justify-content: center;}
            #plot { width: 100%; height: 100%; }
        </style>
    </head>
    <body>
        <div id="plot"></div>
        <script>
            // Pre-computed summary data to keep the payload < 50kb
            var trace_data = {
                x: [1, 1.5, 2.2, 3.1, 4.0, 4.8, 5.5],
                y: [210, 260, 340, 420, 500, 610, 690],
                mode: 'markers',
                marker: {color: '#38BDF8', size: 6, opacity: 0.8},
                name: 'Trials'
            };
            
            var trace_fit = {
                x: [0.5, 6],
                y: [160, 740], // MT = a + b * ID
                mode: 'lines',
                line: {color: '#EF4444', width: 2, dash: 'dot'},
                name: 'Fit'
            };

            var layout = {
                margin: {l: 10, r: 10, t: 10, b: 10},
                paper_bgcolor: 'rgba(0,0,0,0)',
                plot_bgcolor: 'rgba(0,0,0,0)',
                xaxis: {visible: false},
                yaxis: {visible: false},
                showlegend: false,
                annotations: [{
                    x: 4.5, y: 250, xref: 'x', yref: 'y',
                    text: 'R² = 0.95', showarrow: false,
                    font: {color: '#4ADE80', size: 12, family: 'Inter, sans-serif'}
                }]
            };

            Plotly.newPlot('plot', [trace_data, trace_fit], layout, {displayModeBar: false, staticPlot: true});
        </script>
    </body>
    </html>
    """
    components.html(html_code, height=height)


def render_pythagorean_mini(height=140):
    """Renders a pure HTML5 requestAnimationFrame loop demonstrating a^2 + b^2 = c^2."""
    html_code = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body { margin: 0; background-color: #1E293B; border-radius: 6px; overflow: hidden; display: flex; justify-content: center; align-items: center;}
            canvas { display: block; }
        </style>
    </head>
    <body>
        <canvas id="pyCanvas" width="180" height="140"></canvas>
        <script>
            const ctx = document.getElementById('pyCanvas').getContext('2d');
            
            function draw() {
                // Time-based state machine loop (4 seconds total)
                let t = (performance.now() % 4000) / 4000; 
                
                ctx.clearRect(0, 0, 180, 140);
                
                ctx.save();
                ctx.translate(90, 80); // Center point
                
                // Rotation phase (State 3: 3-4s)
                if (t > 0.75) {
                    let rot = (t - 0.75) * 4; // Normalize 0 to 1
                    ctx.rotate(rot * Math.PI * 2);
                }

                // 1. Draw core right triangle
                ctx.beginPath();
                ctx.moveTo(-15, 15);
                ctx.lineTo(15, 15);
                ctx.lineTo(-15, -15);
                ctx.closePath();
                ctx.strokeStyle = '#38BDF8';
                ctx.lineWidth = 2;
                ctx.stroke();

                // 2. Draw squares (State 2: Opacity pulse)
                let alpha = (t > 0.25 && t < 0.75) ? Math.sin((t - 0.25) * 2 * Math.PI) * 0.4 + 0.1 : 0.1;
                
                // Bottom square (a^2)
                ctx.fillStyle = `rgba(56, 189, 248, ${alpha})`;
                ctx.fillRect(-15, 15, 30, 30);
                
                // Left square (b^2)
                ctx.fillStyle = `rgba(74, 222, 128, ${alpha})`;
                ctx.fillRect(-45, -15, 30, 30);
                
                // Hypotenuse square (c^2) - requires rotation
                ctx.save();
                ctx.rotate(-Math.PI/4); // Rotate 45 degrees
                ctx.fillStyle = `rgba(239, 68, 68, ${alpha})`;
                ctx.fillRect(0, 0, 42.4, 42.4); // 30 * sqrt(2)
                ctx.restore();

                ctx.restore();
                requestAnimationFrame(draw);
            }
            draw();
        </script>
    </body>
    </html>
    """
    components.html(html_code, height=height)


def render_geometry_mini(height=140):
    """Renders area dissection (splitting squares into triangles)."""
    html_code = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body { margin: 0; background-color: #1E293B; border-radius: 6px; overflow: hidden; display: flex; justify-content: center; align-items: center;}
        </style>
    </head>
    <body>
        <canvas id="geoCanvas" width="180" height="140"></canvas>
        <script>
            const ctx = document.getElementById('geoCanvas').getContext('2d');
            
            function draw() {
                let t = (performance.now() % 4000);
                ctx.clearRect(0, 0, 180, 140);
                
                ctx.save();
                ctx.translate(90, 70);

                // Calculate split offset
                let offset = 0;
                if (t > 2000 && t < 3000) offset = ((t - 2000) / 1000) * 15;
                if (t >= 3000) offset = 15;

                // Left triangle
                ctx.save();
                ctx.translate(-offset, offset);
                ctx.beginPath();
                ctx.moveTo(-25, -25);
                ctx.lineTo(-25, 25);
                ctx.lineTo(25, 25);
                ctx.closePath();
                ctx.fillStyle = 'rgba(56, 189, 248, 0.2)';
                ctx.fill();
                ctx.strokeStyle = '#38BDF8';
                ctx.lineWidth = 2;
                ctx.stroke();
                ctx.restore();

                // Right triangle
                ctx.save();
                ctx.translate(offset, -offset);
                ctx.beginPath();
                ctx.moveTo(-25, -25);
                ctx.lineTo(25, -25);
                ctx.lineTo(25, 25);
                ctx.closePath();
                ctx.fillStyle = 'rgba(74, 222, 128, 0.2)';
                ctx.fill();
                ctx.strokeStyle = '#4ADE80';
                ctx.stroke();
                ctx.restore();

                // Sword line animation
                if (t > 1000 && t < 2000) {
                    let drop = -40 + (((t - 1000) / 1000) * 80);
                    ctx.beginPath();
                    ctx.moveTo(drop - 15, drop + 15);
                    ctx.lineTo(drop + 15, drop - 15);
                    ctx.strokeStyle = '#EF4444';
                    ctx.lineWidth = 3;
                    ctx.stroke();
                }

                ctx.restore();
                requestAnimationFrame(draw);
            }
            draw();
        </script>
    </body>
    </html>
    """
    components.html(html_code, height=height)