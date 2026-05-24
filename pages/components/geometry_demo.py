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
        <!-- INJECT THE PHYSICS ENGINE -->
        <script src="https://cdnjs.cloudflare.com/ajax/libs/matter-js/0.19.0/matter.min.js"></script>
        <style>
            body {{ margin: 0; display: flex; justify-content: center; align-items: center; background-color: #F1F5F9; overflow: hidden; font-family: 'Inter', sans-serif; }}
            canvas {{ background-color: #E2E8F0; border-radius: 8px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); }}
        </style>
    </head>
    <body>
        <canvas id="geomCanvas" width="700" height="400"></canvas>
        <script>
            // --- 1. PHYSICS ENGINE INITIALIZATION ---
            // MATLAB Bridge: Equivalent to initializing a Simscape Multibody environment
            const Engine = Matter.Engine,
                  Render = Matter.Render,
                  Runner = Matter.Runner,
                  Bodies = Matter.Bodies,
                  Composite = Matter.Composite,
                  Body = Matter.Body;

            const engine = Engine.create();
            // Lower gravity slightly for a more "floaty" pedagogical aesthetic
            engine.world.gravity.y = 0.8; 

            // --- 2. CANVAS & RENDERER ---
            const canvas = document.getElementById('geomCanvas');
            const render = Render.create({{
                canvas: canvas,
                engine: engine,
                options: {{
                    width: 700,
                    height: 400,
                    wireframes: false, // Set to true for debugging bounding boxes
                    background: 'transparent'
                }}
            }});

            // Grid sizing
            const U = 40;
            const W = {base_units} * U;
            const H = {height_units} * U;
            const cx = 450; 
            const cy = 200;

            // --- 3. RECTANGLE BOUNDARIES (The "Container") ---
            // We build the rectangle out of 4 static walls so the marbles stay inside
            const wallOptions = {{ isStatic: true, render: {{ fillStyle: '#475569' }} }};
            const leftWall = Bodies.rectangle(cx - W/2, cy, 10, H, wallOptions);
            const rightWall = Bodies.rectangle(cx + W/2, cy, 10, H, wallOptions);
            const bottomWall = Bodies.rectangle(cx, cy + H/2, W, 10, wallOptions);
            const topWall = Bodies.rectangle(cx, cy - H/2, W, 10, wallOptions);
            
            // The diagonal splitting line (Initially hidden off-screen or scaled to 0)
            const diagonalSplit = Bodies.rectangle(cx, cy, Math.sqrt(W*W + H*H), 10, {{ 
                isStatic: true, 
                angle: Math.atan2(H, W),
                isSensor: true // Marbles ignore it until phase 3
            }});

            Composite.add(engine.world, [leftWall, rightWall, bottomWall, topWall, diagonalSplit]);

            // --- 4. THE MARBLE GENERATOR ---
            const marbles = [];
            function pourMarbles(count) {{
                for (let i = 0; i < count; i++) {{
                    // Add slight random jitter to drop positions so they bounce naturally
                    let startX = cx + (Math.random() * 40 - 20);
                    let startY = cy - H/2 + 20;
                    
                    let marble = Bodies.circle(startX, startY, 8, {{
                        restitution: 0.6, // Bounciness
                        friction: 0.05,
                        render: {{ fillStyle: '#38BDF8' }}
                    }});
                    marbles.push(marble);
                    Composite.add(engine.world, marble);
                }}
            }}

            // --- 5. THE STATE MACHINE LOOP ---
            // This replaces the procedural Math.sin loop with a timed logic controller
            let startTime = performance.now();
            
            function stateMachine() {{
                let t = (performance.now() - startTime) % 8000; // 8 second total loop
                
                if (t < 100) {{
                    // Phase 1: Reset & Pour
                    if (marbles.length === 0) pourMarbles(40);
                }} else if (t > 3000 && t < 4000) {{
                    // Phase 2: Tip the container 45 degrees
                    // Body.setAngle(container, newAngle);
                }} else if (t > 4000 && t < 5500) {{
                    // Phase 3: Activate diagonal split and grow it
                }} else if (t > 5500 && t < 7000) {{
                    // Phase 4: Pop the two triangles apart
                }} else if (t > 7800) {{
                    // Phase 5: Clear world for restart
                }}

                requestAnimationFrame(stateMachine);
            }}

            // Start the physics and rendering engines
            Render.run(render);
            Runner.run(Runner.create(), engine);
            requestAnimationFrame(stateMachine);
        </script>
    </body>
    </html>
    """
    
    # Render with a height slightly larger than the canvas to prevent scrollbars
    components.html(html_code, height=420)