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
    Uses Matter.js to simulate marbles filling the area, tipping, and splitting.
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
            // --- 1. PHYSICS ENGINE INITIALIZATION ---
            const Engine = Matter.Engine,
                  Render = Matter.Render,
                  Runner = Matter.Runner,
                  Bodies = Matter.Bodies,
                  Body = Matter.Body,
                  Composite = Matter.Composite,
                  Events = Matter.Events;

            const engine = Engine.create();
            
            // Bulletproof gravity call (handles both old and new Matter.js versions)
            const gravity = engine.gravity || engine.world.gravity;
            gravity.y = 1;
            gravity.x = 0;

            const canvas = document.getElementById('geomCanvas');
            const render = Render.create({{
                canvas: canvas,
                engine: engine,
                options: {{
                    width: 700,
                    height: 400,
                    wireframes: false, 
                    background: 'transparent'
                }}
            }});

            // --- 2. DYNAMIC GEOMETRY SCALING ---
            const U = 40; 
            const W = {base_units} * U;
            const H = {height_units} * U;
            const cx = 450; 
            const cy = 200;
            
            // Calculate marble radius to perfectly fill 65% of the bounding area
            const packingFraction = 0.65;
            const targetArea = W * H * packingFraction;
            const r = Math.sqrt(targetArea / (100 * Math.PI));

            // --- 3. CONSTRUCTING THE RIGID BODIES ---
            const thickness = 60; // Thick walls prevent high-speed tunneling
            const wallColor = '#475569';
            const wallOpt = {{ isStatic: true, friction: 0.0, render: {{ fillStyle: wallColor }} }};
            
            let ground = Bodies.rectangle(cx, cy + H/2 + thickness/2, W + thickness*2, thickness, wallOpt);
            let ceiling = Bodies.rectangle(cx, cy - H/2 - thickness/2, W + thickness*2, thickness, wallOpt);
            let leftWall = Bodies.rectangle(cx - W/2 - thickness/2, cy, thickness, H, wallOpt);
            let rightWall = Bodies.rectangle(cx + W/2 + thickness/2, cy, thickness, H, wallOpt);

            // The Diagonal Bulldozer (Bottom-Left to Top-Right)
            const diagLength = Math.sqrt(W*W + H*H);
            const diagAngle = -Math.atan2(H, W); 
            let splitter = Bodies.rectangle(cx, cy, diagLength, 8, {{
                isStatic: true,
                angle: diagAngle,
                friction: 0.0,
                render: {{ fillStyle: '#EF4444' }} 
            }});
            
            Body.setPosition(splitter, {{ x: -1000, y: -1000 }}); // Hide initially
            Composite.add(engine.world, [ground, ceiling, leftWall, rightWall, splitter]);

            let marbles = [];
            let marbleCount = 0;

            // --- 4. THE CHOREOGRAPHY STATE MACHINE ---
            let startTime = performance.now();
            let phase = 0;
            
            function easeInOutSine(x) {{
                return -(Math.cos(Math.PI * x) - 1) / 2;
            }}

            Events.on(engine, 'beforeUpdate', function() {{
                let t = performance.now() - startTime;
                let cycle = t % 11000; // 11-second master loop

                // PHASE 1: Reset (0 - 100ms)
                if (cycle < 100 && phase !== 1) {{
                    phase = 1;
                    marbles.forEach(m => Composite.remove(engine.world, m));
                    marbles = [];
                    marbleCount = 0;
                    
                    gravity.x = 0;
                    gravity.y = 1;
                    
                    Body.setPosition(ground, {{ x: cx, y: cy + H/2 + thickness/2 }});
                    Body.setPosition(ceiling, {{ x: cx, y: cy - H/2 - thickness/2 }});
                    Body.setPosition(leftWall, {{ x: cx - W/2 - thickness/2, y: cy }});
                    Body.setPosition(rightWall, {{ x: cx + W/2 + thickness/2, y: cy }});
                    Body.setPosition(splitter, {{ x: -1000, y: -1000 }}); 
                }}
                
                // PHASE 1b: Pour Marbles (100ms - 2000ms)
                else if (cycle >= 100 && cycle < 2000 && marbleCount < 100) {{
                    // Drop 2 marbles per physics frame to simulate pouring
                    for(let k=0; k<2; k++) {{
                        if(marbleCount >= 100) break;
                        let m = Bodies.circle(cx + (Math.random()*(W - r*4)) - (W/2 - r*2), cy - H/2 + r*2 + Math.random()*10, r, {{
                            restitution: 0.3,
                            friction: 0.05,
                            render: {{ fillStyle: '#38BDF8', strokeStyle: '#0284C7', lineWidth: 1 }}
                        }});
                        marbles.push(m);
                        Composite.add(engine.world, m);
                        marbleCount++;
                    }}
                }}
                
                // PHASE 2: Tip the Gravity Vector (3000ms - 4500ms)
                else if (cycle >= 3000 && cycle < 4500) {{
                    phase = 2;
                    let p = (cycle - 3000) / 1500;
                    let angle = easeInOutSine(p) * (Math.PI / 4); // Tip 45 degrees
                    gravity.x = Math.sin(angle);
                    gravity.y = Math.cos(angle);
                    
                    // Add slight jitter to unstick jammed marbles
                    if (Math.random() < 0.1) {{
                        marbles.forEach(m => {{
                            Body.setVelocity(m, {{ x: m.velocity.x + (Math.random()-0.5), y: m.velocity.y + (Math.random()-0.5) }});
                        }});
                    }}
                }}
                
                // PHASE 3: Slide the Bulldozer Splitter (5500ms - 7000ms)
                else if (cycle >= 5500 && cycle < 7000) {{
                    phase = 3;
                    let p = (cycle - 5500) / 1500;
                    let pop = easeInOutSine(p);
                    
                    // Slide the diagonal from the Bottom-Right corner into the Center
                    let startX = cx + W/2;
                    let startY = cy + H/2;
                    Body.setPosition(splitter, {{
                        x: startX + (cx - startX) * pop,
                        y: startY + (cy - startY) * pop
                    }});
                }}
                
                // PHASE 4: Pop Apart into Triangles (7500ms - 9000ms)
                else if (cycle >= 7500 && cycle < 9000) {{
                    phase = 4;
                    let p = (cycle - 7500) / 1500;
                    let pop = easeInOutSine(p) * 20; // Maximum separation distance
                    
                    // Top-Left half moves Up/Left, Bottom-Right half moves Down/Right
                    Body.setPosition(leftWall, {{ x: cx - W/2 - thickness/2 - pop, y: cy - pop }});
                    Body.setPosition(ceiling, {{ x: cx - pop, y: cy - H/2 - thickness/2 - pop }});
                    
                    Body.setPosition(rightWall, {{ x: cx + W/2 + thickness/2 + pop, y: cy + pop }});
                    Body.setPosition(ground, {{ x: cx + pop, y: cy + H/2 + thickness/2 + pop }});
                }}
            }});

            // --- 5. OVERLAY THE FORMULA (Runs after physics calculation) ---
            Events.on(render, 'afterRender', function() {{
                const context = render.context;
                let t = (performance.now() - startTime) % 11000;
                
                context.font = "bold 32px sans-serif";
                context.textAlign = "left";
                const fx = 50; const fy = 210;

                if (t < 5500) {{
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