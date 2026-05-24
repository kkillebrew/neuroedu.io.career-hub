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
    Renders the physics-based Area transformation.
    """
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/matter-js/0.19.0/matter.min.js"></script>
        <style>
            body {{ margin: 0; display: flex; justify-content: center; align-items: center; background-color: #F1F5F9; overflow: hidden; font-family: 'Inter', sans-serif; }}
            canvas {{ background-color: #E2E8F0; border-radius: 8px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); }}
        </style>
    </head>
    <body>
        <canvas id="geomCanvas" width="700" height="400"></canvas>
        <script>
            const Engine = Matter.Engine, Render = Matter.Render, Runner = Matter.Runner;
            const Bodies = Matter.Bodies, Body = Matter.Body, Composite = Matter.Composite, Events = Matter.Events;

            const engine = Engine.create();
            const gravity = engine.gravity || engine.world.gravity;
            gravity.y = 1; gravity.x = 0;

            const render = Render.create({{
                canvas: document.getElementById('geomCanvas'), engine: engine,
                options: {{ width: 700, height: 400, wireframes: false, background: 'transparent' }}
            }});

            const U = 35; 
            const W = {base_units} * U;
            const H = {height_units} * U;
            const cx = 450; const cy = 200;
            
            // Calculate exactly 100 marbles to fill ~85% of the space
            const r = Math.sqrt((W * H * 0.85) / (100 * Math.PI));
            const thickness = 40; 
            const wallOpt = {{ isStatic: true, friction: 0.0, render: {{ fillStyle: '#475569' }} }};
            
            // Build the components
            let ground = Bodies.rectangle(cx, cy + H/2 + thickness/2, W + thickness*2, thickness, wallOpt);
            let ceiling = Bodies.rectangle(cx, cy - H/2 - thickness/2, W + thickness*2, thickness, wallOpt);
            let leftWall = Bodies.rectangle(cx - W/2 - thickness/2, cy, thickness, H + thickness*2, wallOpt);
            let rightWall = Bodies.rectangle(cx + W/2 + thickness/2, cy, thickness, H + thickness*2, wallOpt);

            // The Splitters (Two overlapping lines that will form the inner walls of the triangles)
            const diagLength = Math.sqrt(W*W + H*H) + 10;
            const diagAngle = Math.atan2(H, -W); // Angle from TR to BL
            
            const splitOpt = {{ isStatic: true, friction: 0.0, angle: diagAngle, render: {{ fillStyle: '#EF4444' }} }};
            let splitLeft = Bodies.rectangle(cx, cy - 800, diagLength, 6, splitOpt);
            let splitRight = Bodies.rectangle(cx, cy - 800, diagLength, 6, splitOpt);

            // Group them to rotate the box easily
            let box = Composite.create();
            Composite.add(box, [ground, ceiling, leftWall, rightWall, splitLeft, splitRight]);
            Composite.add(engine.world, box);

            let marbles = [];
            
            // Target angle to make the TR-BL diagonal perfectly vertical
            const targetTilt = -Math.PI/2 - diagAngle; 

            let startTime = performance.now();
            let phase = -1;
            let currentRotation = 0;

            function easeInOut(x) {{ return -(Math.cos(Math.PI * x) - 1) / 2; }}

            Events.on(engine, 'beforeUpdate', function() {{
                let t = performance.now() - startTime;
                let cycle = t % 12000; 

                // PHASE 1: Rapid Grid Pour (0 - 2000ms)
                if (cycle < 100 && phase !== 1) {{
                    phase = 1;
                    marbles.forEach(m => Composite.remove(engine.world, m));
                    marbles = [];
                    Composite.rotate(box, -currentRotation, {{x: cx, y: cy}}); // Reset rotation
                    currentRotation = 0;
                    
                    Body.setPosition(ground, {{ x: cx, y: cy + H/2 + thickness/2 }});
                    Body.setPosition(ceiling, {{ x: cx, y: cy - H/2 - thickness/2 }});
                    Body.setPosition(leftWall, {{ x: cx - W/2 - thickness/2, y: cy }});
                    Body.setPosition(rightWall, {{ x: cx + W/2 + thickness/2, y: cy }});
                    Body.setPosition(splitLeft, {{ x: cx, y: cy - 800 }});
                    Body.setPosition(splitRight, {{ x: cx, y: cy - 800 }});

                    // Pour 100 marbles
                    for(let i=0; i<100; i++) {{
                        let m = Bodies.circle(cx + (Math.random()*(W-r*2)) - W/2 + r, cy - H/2 + r*2 + (i*2), r, {{
                            restitution: 0.2, friction: 0.05,
                            render: {{ fillStyle: '#38BDF8', strokeStyle: '#0284C7', lineWidth: 1 }}
                        }});
                        marbles.push(m);
                        Composite.add(engine.world, m);
                    }}
                }}
                
                // PHASE 2: Tip to Diamond (2500 - 4000ms)
                else if (cycle >= 2500 && cycle < 4000) {{
                    phase = 2;
                    let p = (cycle - 2500) / 1500;
                    let desiredRotation = easeInOut(p) * targetTilt;
                    let delta = desiredRotation - currentRotation;
                    Composite.rotate(box, delta, {{x: cx, y: cy}});
                    currentRotation = desiredRotation;
                    
                    // Jitter marbles to settle them deeply into the corner
                    if (Math.random() < 0.2) marbles.forEach(m => Body.applyForce(m, m.position, {{x: (Math.random()-0.5)*0.001, y: 0}}));
                }}
                
                // PHASE 3: Slide Wedge Down (4500 - 6500ms)
                else if (cycle >= 4500 && cycle < 6500) {{
                    phase = 3;
                    let p = (cycle - 4500) / 2000;
                    let dropY = (cy - 800) + (800 * easeInOut(p));
                    
                    // The blades slide down the absolute Y axis (which aligns perfectly with the tilted diagonal)
                    Body.setPosition(splitLeft, {{ x: cx, y: dropY }});
                    Body.setPosition(splitRight, {{ x: cx, y: dropY }});
                }}
                
                // PHASE 4: Pop Apart (7000 - 8500ms)
                else if (cycle >= 7000 && cycle < 8500) {{
                    phase = 4;
                    let p = (cycle - 7000) / 1500;
                    let pop = easeInOut(p) * 2; // Move 2px per frame outwards
                    
                    // Move Left Triangle group (Top, Left, SplitLeft) to the left
                    Body.translate(ceiling, {{x: -pop, y: 0}});
                    Body.translate(leftWall, {{x: -pop, y: 0}});
                    Body.translate(splitLeft, {{x: -pop, y: 0}});
                    
                    // Move Right Triangle group (Bottom, Right, SplitRight) to the right
                    Body.translate(ground, {{x: pop, y: 0}});
                    Body.translate(rightWall, {{x: pop, y: 0}});
                    Body.translate(splitRight, {{x: pop, y: 0}});
                }}
            }});

            // --- 5. OVERLAY FORMULA ---
            Events.on(render, 'afterRender', function() {{
                const context = render.context;
                let t = (performance.now() - startTime) % 12000;
                context.font = "bold 32px sans-serif"; context.textAlign = "left";
                const fx = 30; const fy = 210;

                if (t < 7000) {{
                    context.fillStyle = '#475569'; context.fillText("Area = ", fx, fy);
                    context.fillStyle = '#38BDF8'; context.fillText("b", fx + 110, fy);
                    context.fillStyle = '#475569'; context.fillText(" × ", fx + 130, fy);
                    context.fillStyle = '#4ADE80'; context.fillText("h", fx + 180, fy);
                }} else {{
                    context.fillStyle = '#475569'; context.fillText("Area = ½ × ", fx, fy);
                    context.fillStyle = '#38BDF8'; context.fillText("b", fx + 175, fy);
                    context.fillStyle = '#475569'; context.fillText(" × ", fx + 195, fy);
                    context.fillStyle = '#4ADE80'; context.fillText("h", fx + 245, fy);
                }}
            }});

            Render.run(render);
            Runner.run(Runner.create(), engine);
        </script>
    </body>
    </html>
    """
    components.html(html_code, height=420)