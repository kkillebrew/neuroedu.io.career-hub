############################################################################
# rotating_line_demo: generates the rotating line illusion demo 
############################################################################

import streamlit.components.v1 as components

def render_rotating_line_demo(base_speed, modulation, shape):
    """
    Generates an HTML5 Canvas that perfectly mimics the MATLAB Psychtoolbox Screen('Flip') loop.
    MATLAB Bridge: 
      - Canvas Context (ctx) = Screen('DrawLine', w)
      - requestAnimationFrame = Screen('Flip')
    """
    
    # Map the shape string to an integer for the JS switch statement
    shape_map = {"Ellipse": 0, "Rectangle": 1, "Diamond": 2}
    shape_id = shape_map.get(shape, 0)
    
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ margin: 0; display: flex; justify-content: center; align-items: center; background-color: #808080; }}
            canvas {{ background-color: #808080; border: 2px solid #333; box-shadow: 0px 4px 10px rgba(0,0,0,0.5); }}
        </style>
    </head>
    <body>
        <canvas id="stimulusCanvas" width="500" height="500"></canvas>
        <script>
            const canvas = document.getElementById('stimulusCanvas');
            const ctx = canvas.getContext('2d');
            
            // Experiment Variables (Passed from Streamlit Python Widgets!)
            const baseSpeed = {base_speed}; // Base RPM
            const modulation = {modulation}; // The 'constant' variable from modulateSpeed.m
            const shapeId = {shape_id};
            
            // Monitor / Canvas variables
            const cx = canvas.width / 2;
            const cy = canvas.height / 2;
            
            // Aperture dimensions
            const apWidth = 200;  // Horizontal radius
            const apHeight = 100; // Vertical radius
            
            let angle = 0; // Current orientation (theta)
            let lastTime = performance.now();

            function drawLoop(currentTime) {{
                // 1. Calculate time delta for smooth movement regardless of framerate
                const dt = (currentTime - lastTime) / 1000; 
                lastTime = currentTime;

                // 2. Clear screen (Psychtoolbox implicit clear on Flip)
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                
                // 3. Calculate current line length based on Aperture
                // MATLAB: radialLength = sqrt( 1 / ( (sind(orientation)/apHeight)^2 + (cosd(orientation)/apLength)^2 ) )
                let radAngle = angle * (Math.PI / 180);
                let currentLength = 0;
                
                if (shapeId === 0) {{ // Ellipse
                    currentLength = (apWidth * apHeight) / Math.sqrt(
                        Math.pow(apHeight * Math.cos(radAngle), 2) + 
                        Math.pow(apWidth * Math.sin(radAngle), 2)
                    );
                }} else if (shapeId === 1) {{ // Rectangle (simplified logic for demo)
                    // Logic to constrain line to a bounding box
                    let absCos = Math.abs(Math.cos(radAngle));
                    let absSin = Math.abs(Math.sin(radAngle));
                    currentLength = Math.min(apWidth / absCos, apHeight / absSin);
                }} else {{ // Diamond
                    let absCos = Math.abs(Math.cos(radAngle));
                    let absSin = Math.abs(Math.sin(radAngle));
                    currentLength = (apWidth * apHeight) / (apHeight * absCos + apWidth * absSin);
                }}

                // 4. Update the angle (Modulate Speed)
                // MATLAB: actualSpeed = baseSpeed + constant * radialLength (approximated here)
                // If modulation > 0, it artificially speeds up as it gets shorter (vertical)
                let currentSpeed = baseSpeed * (1 + (modulation * (apWidth / currentLength - 1)));
                angle += currentSpeed * dt;
                if (angle >= 360) angle = 0;

                // 5. Draw the stimulus (Screen('DrawLine'))
                ctx.save();
                ctx.translate(cx, cy);
                ctx.rotate(radAngle);
                
                // Draw Line
                ctx.beginPath();
                ctx.moveTo(-currentLength, 0);
                ctx.lineTo(currentLength, 0);
                ctx.lineWidth = 6;
                ctx.strokeStyle = '#FFFFFF'; // White line
                ctx.stroke();
                
                // Draw Dots at the ends (drawDotsToggle from MATLAB)
                ctx.beginPath();
                ctx.arc(-currentLength, 0, 6, 0, Math.PI * 2);
                ctx.arc(currentLength, 0, 6, 0, Math.PI * 2);
                ctx.fillStyle = '#FF0000'; // Red dots to track
                ctx.fill();

                ctx.restore();

                // 6. Loop (Screen('Flip'))
                requestAnimationFrame(drawLoop);
            }}

            // Start the loop
            requestAnimationFrame(drawLoop);
        </script>
    </body>
    </html>
    """
    
    # Embed the HTML into the Streamlit app
    components.html(html_code, height=520)
