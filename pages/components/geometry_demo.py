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
    Renders a 10-second physics-based mathematical transformation loop.
    Uses Matter.js to simulate 100 marbles filling the area, tipping, and splitting.
    
    MATLAB Bridge: This replaces a rigid-body ode45 loop. We offload the collision
    matrix processing entirely to the browser's V8 Javascript engine.
    """
    
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <!-- Inject Matter.js Physics Engine via CDN -->
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
            const Engine = Matter.Engine,
                  Render = Matter.Render,
                  Runner = Matter.Runner,
                  Bodies = Matter.Bodies,
                  Body = Matter.Body,
                  Composite = Matter.Composite,
                  Events = Matter.Events;

            const engine = Engine.create();
            // Start with standard downward gravity
            engine.world.gravity.y = 1;
            engine.world.gravity.x = 0;

            const canvas = document.getElementById('geomCanvas');
            const render = Render.create({{
                canvas: canvas,
                engine: engine,
                options: {{
                    width: 700,
                    height: 400,
                    wireframes: false, // Set to true to debug collision meshes
                    background: 'transparent'
                }}
            }});

            // --- 2. DYNAMIC GEOMETRY SCALING ---
            const U = 40; // 1 unit = 40px
            const W = {base_units} * U;
            const H = {height_units} * U;
            const cx = 450; 
            const cy = 200;
            
            // Calculate exact marble radius so 100 marbles fill ~65% of the total volume (standard circle packing)
            const packingFraction = 0.65;
            const targetArea = W * H * packingFraction;
            const r = Math.sqrt(targetArea / (100 * Math.PI));

            // --- 3. CONSTRUCTING THE RIGID BODIES ---
            const thickness = 20;
            const wallColor = '#475569';
            const wallOpt = {{ isStatic: true, friction: 0.0, render: {{ fillStyle: wallColor }} }};
            
            // We build the box out of 4 distinct walls so we can translate them later
            let ground = Bodies.rectangle(cx, cy + H/2 + thickness/2, W + thickness*2, thickness, wallOpt);
            let ceiling = Bodies.rectangle(cx, cy - H/2 - thickness/2, W + thickness*2, thickness, wallOpt);
            let leftWall = Bodies.rectangle(cx - W/2 - thickness/2, cy, thickness, H, wallOpt);
            let rightWall = Bodies.rectangle(cx + W/2 + thickness/2, cy, thickness, H, wallOpt);

            // The Diagonal Splitter (Hypotenuse)
            const diagLength = Math.sqrt(W*W + H*H);
            const diagAngle = Math.atan2(H, W);
            let splitter = Bodies.rectangle(cx, cy, diagLength, 8, {{
                isStatic: true,
                angle: diagAngle,
                friction: 0.0,
                render: {{ fillStyle: '#EF4444' }} // Red cutting line
            }});
            
            // Move splitter off-screen initially
            Body.setPosition(splitter, {{ x: -1000, y: -1000 }});
            Composite.add(engine.world, [ground, ceiling, leftWall, rightWall, splitter]);

            let marbles = [];
            function pourMarbles() {{
                for(let i=0; i<100; i++) {{
                    // Add spatial jitter so they don't spawn exactly inside each other
                    let m = Bodies.circle(cx + (Math.random()*W/2 - W/4), cy - H/2 - 50 - (i*10), r, {{
                        restitution: 0.5, // Bounciness
                        friction: 0.01,
                        render: {{ fillStyle: '#38BDF8', strokeStyle: '#0284C7', lineWidth: 1 }}
                    }});
                    marbles.push(m);
                    Composite.add(engine.world, m);
                }}
            }}

            // --- 4. THE CHOREOGRAPHY STATE MACHINE ---
            let startTime = performance.now();
            let phase = 0;
            
            // Easing function for smooth mechanical movements
            function easeInOutSine(x) {{
                return -(Math.cos(Math.PI * x) - 1) / 2;
            }}

            Events.on(engine, 'beforeUpdate', function() {{
                let t = performance.now() - startTime;
                let cycle = t % 11000; // 11-second total loop

                // PHASE 1: Reset & Pour (0 - 3s)
                if (cycle < 100 && phase !== 1) {{
                    phase = 1;
                    marbles.forEach(m => Composite.remove(engine.world, m));
                    marbles = [];
                    engine.world.gravity.x = 0;
                    engine.world.gravity.y = 1;
                    
                    Body.setPosition(ground, {{ x: cx, y: cy + H/2 + thickness/2 }});
                    Body.setPosition(ceiling, {{ x: cx, y: cy - H/2 - thickness/2 }});
                    Body.setPosition(leftWall, {{ x: cx - W/2 - thickness/2, y: cy }});
                    Body.setPosition(rightWall, {{ x: cx + W/2 + thickness/2, y: cy }});
                    Body.setPosition(splitter, {{ x: -1000, y: -1000 }}); // Hide
                    
                    pourMarbles();
                }}
                
                // PHASE 2: Tip the Gravity Vector (3s - 4.5s)
                else if (cycle >= 3000 && cycle < 4500) {{
                    phase = 2;
                    let p = (cycle - 3000) / 1500;
                    let angle = easeInOutSine(p) * (Math.PI / 4); // Tip 45 degrees
                    // Rotate the gravity vector to simulate tilting the box
                    engine.world.gravity.x = Math.sin(angle);
                    engine.world.gravity.y = Math.cos(angle);
                    
                    // Add slight random velocity jolts ("rumble") to unstick jammed marbles
                    if (Math.random() < 0.1) {{
                        marbles.forEach(m => {{
                            Body.setVelocity(m, {{ x: m.velocity.x + (Math.random()-0.5), y: m.velocity.y + (Math.random()-0.5) }});
                        }});
                    }}
                }}
                
                // PHASE 3: Slide the Splitter (5.5s - 7s)
                else if (cycle >= 5500 && cycle < 7000) {{
                    phase = 3;
                    let p = (cycle - 5500) / 1500;
                    let pop = easeInOutSine(p);
                    
                    // Slide the diagonal from top-left to center
                    let startX = cx - W/2;
                    let startY = cy - H/2;
                    Body.setPosition(splitter, {{
                        x: startX + (cx - startX) * pop,
                        y: startY + (cy - startY) * pop
                    }});
                }}
                
                // PHASE 4: Pop Apart (7.5s - 9s)
                else if (cycle >= 7500 && cycle < 9000) {{
                    phase = 4;
                    let p = (cycle - 7500) / 1500;
                    let pop = easeInOutSine(p) * 20; // 20px displacement
                    
                    // The separation vector is perpendicular to the diagonal
                    let dx = Math.sin(diagAngle) * pop;
                    let dy = -Math.cos(diagAngle) * pop;
                    
                    // Shift the two distinct triangle halves apart
                    Body.setPosition(leftWall, {{ x: cx - W/2 - thickness/2 - dx, y: cy - dy }});
                    Body.setPosition(ground, {{ x: cx - dx, y: cy + H/2 + thickness/2 - dy }});
                    
                    Body.setPosition(rightWall, {{ x: cx + W/2 + thickness/2 + dx, y: cy + dy }});
                    Body.setPosition(ceiling, {{ x: cx + dx, y: cy - H/2 - thickness/2 + dy }});
                }}
            }});

            // --- 5. POST-RENDER UI OVERLAYS ---
            // Draw the math formulas on top of the physics canvas
            Events.on(render, 'afterRender', function() {{
                const context = render.context;
                let t = (performance.now() - startTime) % 11000;
                
                context.font = "bold 32px sans-serif";
                context.textAlign = "left";
                const fx = 50; const fy = 210;

                // Render specific formula state based on the current loop phase
                if (t < 5500) {{
                    context.fillStyle = colorLine; context.fillText("Area = ", fx, fy);
                    context.fillStyle = '#38BDF8'; context.fillText("b", fx + 110, fy);
                    context.fillStyle = colorLine; context.fillText(" × ", fx + 130, fy);
                    context.fillStyle = '#4ADE80'; context.fillText("h", fx + 180, fy);
                }} else {{
                    context.fillStyle = colorLine; context.fillText("Area = ½ × ", fx, fy);
                    context.fillStyle = '#38BDF8'; context.fillText("b", fx + 175, fy);
                    context.fillStyle = colorLine; context.fillText(" × ", fx + 195, fy);
                    context.fillStyle = '#4ADE80'; context.fillText("h", fx + 245, fy);
                }}
            }});

            // Ignite the Engine
            Render.run(render);
            Runner.run(Runner.create(), engine);
        </script>
    </body>
    </html>
    """
    
    components.html(html_code, height=420)