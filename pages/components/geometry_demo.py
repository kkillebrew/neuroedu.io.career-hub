"""
=============================================================================
MODULE: pages/components/geometry_demo.py
AUTHOR: Kyle W. Killebrew, PhD
DESCRIPTION: 
    Custom Streamlit component to render the Area Generation animation.
    Uses HTML5 <canvas> to render a 60Hz continuous animation loop independent
    of the Python backend.

    --- MATLAB BRIDGE ---
    This replicates a standard Psychtoolbox procedural animation:
    1. Define static textures/bounds.
    2. Modulate positions via a time vector (performance.now() % 6000).
    3. Push to screen via requestAnimationFrame (equivalent to Screen('Flip')).
=============================================================================
"""

# Only import the external dependencies needed to build the component
import streamlit.components.v1 as components

def render_geometry_area_demo(base_units, height_units):
    """
    Renders the continuous 6-second mathematical transformation loop.
    Escaped braces for Python f-string compatibility.
    """
    
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ margin: 0; display: flex; justify-content: center; align-items: center; background-color: #F1F5F9; overflow: hidden; font-family: 'Inter', sans-serif; }}
            canvas {{ background-color: #E2E8F0; border-radius: 8px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); }}
        </style>
    </head>
    <body>
        <canvas id="geomCanvas" width="700" height="400"></canvas>
        <script>
            const canvas = document.getElementById('geomCanvas');
            const ctx = canvas.getContext('2d');
            
            const U = 40;
            const W = {base_units} * U;
            const H = {height_units} * U;
            const cx = 450; 
            const cy = 200;
            const fx = 50;
            const fy = 210;

            const colorBase = '#38BDF8';
            const colorHeight = '#4ADE80';
            const colorShape = 'rgba(148, 163, 184, 0.3)';
            const colorLine = '#475569';

            function easeInOutCubic(x) {{
                return x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2;
            }}

            function drawLoop(currentTime) {{
                const t = currentTime % 6000;
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                
                let diagAlpha = 0;
                let splitOffset = 0;
                let showTriangleFormula = false;
                
                if (t > 1000 && t < 2000) {{
                    diagAlpha = (t - 1000) / 1000;
                }} else if (t >= 2000 && t < 5000) {{
                    diagAlpha = 1;
                }} else if (t >= 5000) {{
                    diagAlpha = 1 - ((t - 5000) / 1000);
                }}

                if (t >= 2000 && t < 3000) {{
                    splitOffset = easeInOutCubic((t - 2000) / 1000);
                }} else if (t >= 3000 && t < 4000) {{
                    splitOffset = 1;
                }} else if (t >= 4000 && t < 5000) {{
                    splitOffset = 1 - easeInOutCubic((t - 4000) / 1000);
                }}
                
                if (t >= 1500 && t <= 5200) showTriangleFormula = true;

                ctx.font = "bold 32px sans-serif";
                if (!showTriangleFormula) {{
                    ctx.fillStyle = colorLine; ctx.fillText("Area = ", fx, fy);
                    ctx.fillStyle = colorBase; ctx.fillText("b", fx + 110, fy);
                    ctx.fillStyle = colorLine; ctx.fillText(" × ", fx + 130, fy);
                    ctx.fillStyle = colorHeight; ctx.fillText("h", fx + 180, fy);
                }} else {{
                    ctx.fillStyle = colorLine; ctx.fillText("Area = ½ × ", fx, fy);
                    ctx.fillStyle = colorBase; ctx.fillText("b", fx + 175, fy);
                    ctx.fillStyle = colorLine; ctx.fillText(" × ", fx + 195, fy);
                    ctx.fillStyle = colorHeight; ctx.fillText("h", fx + 245, fy);
                }}

                const ox1 = -splitOffset * 30; 
                const oy1 = splitOffset * 30;
                const ox2 = splitOffset * 30; 
                const oy2 = -splitOffset * 30;

                const left = cx - W/2;
                const top = cy - H/2;
                const right = cx + W/2;
                const bottom = cy + H/2;

                ctx.lineWidth = 4;
                ctx.lineJoin = 'round';

                ctx.beginPath();
                ctx.moveTo(left + ox1, top + oy1);
                ctx.lineTo(left + ox1, bottom + oy1);
                ctx.lineTo(right + ox1, bottom + oy1);
                ctx.closePath();
                ctx.fillStyle = colorShape; ctx.fill();
                ctx.strokeStyle = colorLine; ctx.stroke();
                
                ctx.font = "bold 24px sans-serif";
                ctx.fillStyle = colorHeight; ctx.fillText("h", left + ox1 - 25, cy + oy1 + 8);
                ctx.fillStyle = colorBase; ctx.fillText("b", cx + ox1 - 8, bottom + oy1 + 30);

                ctx.beginPath();
                ctx.moveTo(left + ox2, top + oy2);
                ctx.lineTo(right + ox2, top + oy2);
                ctx.lineTo(right + ox2, bottom + oy2);
                ctx.closePath();
                ctx.fillStyle = colorShape; ctx.fill();
                ctx.strokeStyle = colorLine; ctx.stroke();

                if (splitOffset > 0.1) {{
                    ctx.globalAlpha = splitOffset;
                    ctx.fillStyle = colorBase; ctx.fillText("b", cx + ox2 - 8, top + oy2 - 15);
                    ctx.fillStyle = colorHeight; ctx.fillText("h", right + ox2 + 15, cy + oy2 + 8);
                    ctx.globalAlpha = 1.0;
                }}

                if (diagAlpha > 0 && splitOffset === 0) {{
                    ctx.beginPath();
                    ctx.moveTo(left, top);
                    ctx.lineTo(right, bottom);
                    // FIXED: Using ${{diagAlpha}} here prevents the NameError
                    ctx.strokeStyle = `rgba(239, 68, 68, ${{diagAlpha}})`; 
                    ctx.setLineDash([10, 10]);
                    ctx.stroke();
                    ctx.setLineDash([]);
                }}

                requestAnimationFrame(drawLoop);
            }}

            requestAnimationFrame(drawLoop);
        </script>
    </body>
    </html>
    """
    
    # Render with a height slightly larger than the canvas to prevent scrollbars
    components.html(html_code, height=420)