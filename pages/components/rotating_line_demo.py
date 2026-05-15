"""
=============================================================================
MODULE: pages/components/rotating_line_demo.py
AUTHOR: Kyle W. Killebrew, PhD
DESCRIPTION: 
    Custom Streamlit component to render the Rotating Line Illusion.
    Because Streamlit cannot natively handle 60Hz visual rendering loops, 
    this module injects an HTML5 <canvas> and JavaScript requestAnimationFrame 
    loop directly into the web page.

    --- MATLAB BRIDGE ---
    This completely replaces the Psychtoolbox setup in your original code:
    - Screen('OpenWindow') -> <canvas> element
    - Screen('DrawLine') / Screen('DrawDots') -> CanvasRenderingContext2D (ctx)
    - Screen('Flip') -> window.requestAnimationFrame()
=============================================================================
"""

import streamlit.components.v1 as components

def render_rotating_line_demo(base_speed, modulation, shape, show_dots=True):
    """
    Generates and embeds the interactive illusion.
    
    Args:
        base_speed (int): The baseline rotational speed (RPM).
        modulation (float): The 'constant' variable from modulateSpeed.m
        shape (str): The aperture shape ('Ellipse', 'Rectangle', 'Diamond').
        show_dots (bool): Toggles the red tracking dots at the line ends.
    """
    
    # Map the shape string to an integer ID for the JS engine
    # MATLAB Bridge: This is similar to passing a switch/case integer ID 
    # instead of doing slow string comparisons inside the drawing loop.
    shape_map = {"Ellipse": 0, "Rectangle": 1, "Diamond": 2}
    shape_id = shape_map.get(shape, 0)
    
    # Convert Python boolean (True/False) to JavaScript boolean (true/false)
    js_show_dots = "true" if show_dots else "false"

    # --- THE HTML/JS STRING ---
    # Note: We use f""" to start a multi-line string. 
    # Every CSS and JS curly brace must be doubled (e.g., {{ }}) so Python 
    # doesn't mistake them for Python variables.
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
        /* MATLAB Bridge: This is your backColor = [128 128 128] */
        body {{ margin: 0; display: flex; justify-content: center; align-items: center; background-color: #808080; overflow: hidden; }}
        canvas {{ background-color: #808080; }} /* Stripped all borders and shadows */
    </style>
    </head>
    <body>
        <canvas id="stimulusCanvas" width="600" height="500"></canvas>
        <script>
            // --- INITIALIZATION ---
            // MATLAB Bridge: Equivalent to [w, rect] = Screen('OpenWindow', 0, backColor)
            const canvas = document.getElementById('stimulusCanvas');
            const ctx = canvas.getContext('2d');
            
            // Injected Python Variables (From Streamlit UI sliders)
            const baseSpeed = {base_speed}; 
            const modulation = {modulation}; 
            const shapeId = {shape_id};
            const drawDotsToggle = {js_show_dots};
            
            // Monitor coordinates for center of screen (x0, y0)
            const cx = canvas.width / 2;
            const cy = canvas.height / 2;
            
            // Aperture dimensions
            const apWidth = 250;  // Horizontal radius (Long axis)
            const apHeight = 125; // Vertical radius (Short axis)
            
            let angle = 0; // Current orientation (theta)
            let lastTime = performance.now();

            // --- MAIN DRAWING LOOP ---
            function drawLoop(currentTime) {{
                // 1. Calculate time delta for smooth movement regardless of monitor Hz
                const dt = (currentTime - lastTime) / 1000; 
                lastTime = currentTime;

                // 2. Clear screen (Psychtoolbox does this implicitly on Flip)
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                
                // 3. Calculate current line length based on Aperture (radialLength)
                let radAngle = angle * (Math.PI / 180);
                let currentLength = 0;
                
                if (shapeId === 0) {{ 
                    // Ellipse Math (Direct translation from your drawDemo.m)
                    // radialLength = sqrt( 1 / ( (sind(orientation)/apHeight)^2 + (cosd(orientation)/apLength)^2 ) )
                    currentLength = (apWidth * apHeight) / Math.sqrt(
                        Math.pow(apHeight * Math.cos(radAngle), 2) + 
                        Math.pow(apWidth * Math.sin(radAngle), 2)
                    );
                }} else if (shapeId === 1) {{ 
                    // Rectangle constraints
                    let absCos = Math.abs(Math.cos(radAngle));
                    let absSin = Math.abs(Math.sin(radAngle));
                    currentLength = Math.min(apWidth / absCos, apHeight / absSin);
                }} else {{ 
                    // Diamond constraints
                    let absCos = Math.abs(Math.cos(radAngle));
                    let absSin = Math.abs(Math.sin(radAngle));
                    currentLength = (apWidth * apHeight) / (apHeight * absCos + apWidth * absSin);
                }}

                // 4. Update the angle (modulateSpeed.m bridge)
                // Normalize the length factor: 0 when horizontal, 1 when vertical
                let lengthFactor = (apWidth - currentLength) / (apWidth - apHeight);
                
                // actualSpeed calculation
                let currentSpeed = baseSpeed * (1 + (modulation * lengthFactor));
                
                angle += currentSpeed * dt;
                if (angle >= 360) angle -= 360;

                // 5. Draw the stimulus (Screen('DrawLine') & Screen('DrawDots'))
                ctx.save();
                ctx.translate(cx, cy);
                ctx.rotate(radAngle);
                
                // Draw the occluded line (White)
                ctx.beginPath();
                ctx.moveTo(-currentLength, 0);
                ctx.lineTo(currentLength, 0);
                ctx.lineWidth = 6;
                ctx.strokeStyle = '#FFFFFF'; 
                ctx.stroke();
                
                // Draw Tracking Dots (Red) if enabled
                if (drawDotsToggle) {{
                    ctx.beginPath();
                    ctx.arc(-currentLength, 0, 8, 0, Math.PI * 2);
                    ctx.arc(currentLength, 0, 8, 0, Math.PI * 2);
                    ctx.fillStyle = '#FF0000'; 
                    ctx.fill();
                }}

                ctx.restore();

                // 6. Loop (Screen('Flip'))
                requestAnimationFrame(drawLoop);
            }}

            // Start the hardware-accelerated loop
            requestAnimationFrame(drawLoop);
        </script>
    </body>
    </html>
    """ # <--- THIS IS THE CRITICAL CLOSING QUOTE! 
    
    # Embed the HTML string into Streamlit. 
    # Height must be slightly larger than the 500px canvas to prevent scrollbars.
    components.html(html_code, height=520)



### - Create a miniature version of the demo for display purposes - ###
def render_mini_demo(demo_type, modulation=0.0, speed=50, size=150):
    """
    Renders a miniature, static-configured HTML5 canvas for the Rotating Line.
    demo_type options: 'long', 'short', 'aperture'
    """
    # MATLAB Bridge: This sets our specific sizes for the Control condition lines
    # vs the Experimental aperture dimensions.
    if demo_type == 'long':
        shape_id = -1 # Special flag for raw line
        ap_width, ap_height = 65, 65 # Line radius
    elif demo_type == 'short':
        shape_id = -1
        ap_width, ap_height = 35, 35 # Line radius
    else: # 'aperture'
        shape_id = 0
        ap_width, ap_height = 65, 30 # Ellipse radii

    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ margin: 0; display: flex; justify-content: center; align-items: center; background-color: #808080; overflow: hidden; }}
            canvas {{ background-color: #808080; }}
            .label {{ position: absolute; bottom: 5px; font-family: sans-serif; color: white; font-size: 12px; background: rgba(0,0,0,0.5); padding: 2px 6px; border-radius: 4px;}}
        </style>
    </head>
    <body>
        <canvas id="stimCanvas" width="{size}" height="{size}"></canvas>
        <div class="label">{demo_type.upper()}</div>
        <script>
            const canvas = document.getElementById('stimCanvas');
            const ctx = canvas.getContext('2d');
            const cx = canvas.width / 2;
            const cy = canvas.height / 2;
            
            const shapeId = {shape_id};
            const apWidth = {ap_width};
            const apHeight = {ap_height};
            const modulation = {modulation};
            const baseSpeed = {speed};
            
            let angle = 0;
            let lastTime = performance.now();

            function drawLoop(currentTime) {{
                const dt = (currentTime - lastTime) / 1000; 
                lastTime = currentTime;
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                
                let radAngle = angle * (Math.PI / 180);
                let currentLength = 0;
                
                if (shapeId === -1) {{ // No aperture, pure line
                    currentLength = apWidth; 
                }} else {{ // Ellipse
                    currentLength = (apWidth * apHeight) / Math.sqrt(
                        Math.pow(apHeight * Math.cos(radAngle), 2) + 
                        Math.pow(apWidth * Math.sin(radAngle), 2)
                    );
                }}

                // Calculate Speed Modulation
                let lengthFactor = (apWidth - currentLength) / (apWidth - apHeight);
                if (shapeId === -1) lengthFactor = 0; // No length change, no mod
                
                let currentSpeed = baseSpeed * (1 + (modulation * lengthFactor));
                angle += currentSpeed * dt;
                if (angle >= 360) angle -= 360;

                ctx.save();
                ctx.translate(cx, cy);
                ctx.rotate(radAngle);
                
                ctx.beginPath();
                ctx.moveTo(-currentLength, 0);
                ctx.lineTo(currentLength, 0);
                ctx.lineWidth = 4;
                ctx.strokeStyle = '#FFFFFF'; 
                ctx.stroke();
                
                // Red tracking dots
                ctx.beginPath();
                ctx.arc(-currentLength, 0, 5, 0, Math.PI * 2);
                ctx.arc(currentLength, 0, 5, 0, Math.PI * 2);
                ctx.fillStyle = '#FF0000'; 
                ctx.fill();

                ctx.restore();
                requestAnimationFrame(drawLoop);
            }}
            requestAnimationFrame(drawLoop);
        </script>
    </body>
    </html>
    """
    import streamlit.components.v1 as components
    # Render with no scrolling allowed
    components.html(html_code, height=size, scrolling=False)