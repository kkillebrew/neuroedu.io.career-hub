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
    shape_map = {"Ellipse": 0, "Rectangle": 1, "Diamond": 2}
    shape_id = shape_map.get(shape, 0)
    
    # Python booleans to JS booleans
    js_show_dots = "true" if show_dots else "false"

    # We use an f-string to inject the Python variables into the JavaScript block.
    # Note: Because it's an f-string, standard JS curly braces {} must be doubled {{}}!
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            /* MATLAB Bridge: This is your backColor = [128 128 128] */
            body {{ margin: 0; display: flex; justify-content: center; align-items: center; background-color: #808080; overflow: hidden; }}
            canvas {{ background-color: #808080; border: 2px solid #333; box-shadow: 0px 4px 10px rgba(0,0,0,0.5); border-radius: 8px; }}
        </style>
    </head>
    <body>
        <canvas id="stimulusCanvas" width="600" height="500"></canvas>
        <script>
            // --- INITIALIZATION ---
            // MATLAB Bridge: Equivalent to [w, rect] = Screen('OpenWindow', 0, backColor)
            const canvas = document.getElementById('stimulusCanvas');
            const ctx = canvas.getContext('2d');
            
            // Injected Python Variables (From Streamlit UI)
            const baseSpeed = {base_speed}; // Base degrees per second (approx)
            const modulation = {modulation}; // The 'constant' variable from modulateSpeed.m
            const shapeId = {shape_id};
            const drawDotsToggle = {js_show_dots};
            
            // Monitor variables
            const cx = canvas.width / 2;
            const cy = canvas.height / 2;
            
            // Aperture dimensions (apWidth and apHeight)
            const apWidth = 250;  // Horizontal radius (Long axis)
            const apHeight = 125; // Vertical radius (Short axis)
            
            let angle = 0; // Current orientation (theta)
            let lastTime = performance.now();

            // --- MAIN DRAWING LOOP ---
            function drawLoop(currentTime) {{
                // 1. Calculate time delta for smooth movement regardless of monitor Hz
                const dt = (currentTime - lastTime) / 1000; 
                lastTime = currentTime;

                // 2. Clear screen (Psychtoolbox implicit clear on Flip)
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                
                // 3. Calculate current line length based on Aperture (radialLength)
                let radAngle = angle * (Math.PI / 180);
                let currentLength = 0;
                
                if (shapeId === 0) {{ 
                    // Ellipse Math (Direct translation from drawDemo.m)
                    // MATLAB: radialLength = sqrt( 1 / ( (sind(orientation)/apHeight)^2 + (cosd(orientation)/apLength)^2 ) )
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

                // 4. Update the angle (Modulate Speed)
                // MATLAB Bridge: modulateSpeed.m & drawDemo.m actualSpeed calculation.
                // It artificially speeds up as the line gets shorter (approaches vertical axis)
                // Normalizing length factor: 0 when horizontal, 1 when vertical
                let lengthFactor = (apWidth - currentLength) / (apWidth - apHeight);
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
                ctx.lineWidth =
