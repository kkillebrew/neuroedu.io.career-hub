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
    Renders a physics-based geometry transformation.
    Perfectly packs a grid of marbles, rotates, bisects, and pops apart.
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
        <canvas id="geomCanvas" width="1200" height="700"></canvas>
        <script>
            // --- 1. ENGINE & COLLISION SETUP ---
            const Engine = Matter.Engine, Render = Matter.Render, Runner = Matter.Runner;
            const Bodies = Matter.Bodies, Body = Matter.Body, Composite = Matter.Composite, Events = Matter.Events;

            // Collision Bitmasks (Allows the swords to pass through walls but block marbles)
            const CAT_WALL = 0x0001;
            const CAT_MARBLE = 0x0002;
            const CAT_SWORD = 0x0004;

            const engine = Engine.create();
            engine.positionIterations = 8; // Increased for stability with thin walls
            engine.velocityIterations = 8;
            const gravity = engine.gravity || engine.world.gravity;
            gravity.y = 1; gravity.x = 0;

            const render = Render.create({{
                canvas: document.getElementById('geomCanvas'), engine: engine,
                options: {{ width: 1200, height: 700, wireframes: false, background: 'transparent' }}
            }});

            // --- 2. GRID MATH & SIZING ---
            const U = 35; // Size of 1 grid cell
            const W = {base_units} * U;
            const H = {height_units} * U;
            // Center box to the left so formula has the entire upper-right space
            const cx = 500; const cy = 350; 
            
            // Marble Diameter = Grid Cell - 2px for dense packing
            const marbleRadius = (U - 2) / 2;
            const cols = {base_units};
            const rows = {height_units};
            
            // --- 3. CONSTRUCT RIGID BODIES ---
            const thickness = 12; // Shrunk walls, expanded swords so they match
            const wallOpt = {{ 
                isStatic: true, friction: 0.0, 
                render: {{ fillStyle: '#475569' }},
                collisionFilter: {{ category: CAT_WALL }} 
            }};
            
            let ground = Bodies.rectangle(cx, cy + H/2 + thickness/2, W + thickness*2, thickness, wallOpt);
            let ceiling = Bodies.rectangle(cx, cy - H/2 - thickness/2, W + thickness*2, thickness, wallOpt);
            let leftWall = Bodies.rectangle(cx - W/2 - thickness/2, cy, thickness, H + thickness*2, wallOpt);
            let rightWall = Bodies.rectangle(cx + W/2 + thickness/2, cy, thickness, H + thickness*2, wallOpt);

            // Two overlapping swords that will cap the separated triangles perfectly
            const diagLength = Math.sqrt(W*W + H*H) + 30;
            const splitOpt = {{ 
                isStatic: true, friction: 0.0, angle: Math.PI/2, 
                render: {{ fillStyle: '#EF4444' }},
                collisionFilter: {{ category: CAT_SWORD, mask: CAT_MARBLE }} 
            }};
            
            let splitLeft = Bodies.rectangle(cx, cy - 1200, diagLength, thickness, splitOpt);
            let splitRight = Bodies.rectangle(cx, cy - 1200, diagLength, thickness, splitOpt);

            let box = Composite.create();
            Composite.add(box, [ground, ceiling, leftWall, rightWall]);
            Composite.add(engine.world, [box, splitLeft, splitRight]);

            let marbles = [];
            
            // Rotation math to make Top-Right -> Bottom-Left diagonal perfectly vertical
            const diagAngle = Math.atan2(H, -W); 
            const targetTilt = Math.PI/2 - diagAngle; 

            // --- 4. CHOREOGRAPHY STATE MACHINE ---
            let startTime = performance.now();
            let phase = -1;
            let currentRotation = 0;
            let lastPop = 0;

            function easeInOut(x) {{ return -(Math.cos(Math.PI * x) - 1) / 2; }}

            Events.on(engine, 'beforeUpdate', function() {{
                let t = performance.now() - startTime;
                let cycle = t % 12000; 

                // PHASE 1: Reset & Grid Fill
                if (cycle < 100 && phase !== 1) {{
                    phase = 1; lastPop = 0;
                    
                    marbles.forEach(m => Composite.remove(engine.world, m));
                    marbles = [];
                    Composite.rotate(box, -currentRotation, {{x: cx, y: cy}}); 
                    currentRotation = 0;
                    
                    Body.setPosition(ground, {{ x: cx, y: cy + H/2 + thickness/2 }});
                    Body.setPosition(ceiling, {{ x: cx, y: cy - H/2 - thickness/2 }});
                    Body.setPosition(leftWall, {{ x: cx - W/2 - thickness/2, y: cy }});
                    Body.setPosition(rightWall, {{ x: cx + W/2 + thickness/2, y: cy }});
                    Body.setPosition(splitLeft, {{ x: cx, y: cy - 1200 }});
                    Body.setPosition(splitRight, {{ x: cx, y: cy - 1200 }});

                    // Instantly spawn perfect grid of 50/50 marbles
                    const startX = cx - W/2 + U/2;
                    const startY = cy - H/2 + U/2;
                    for (let i = 0; i < cols; i++) {{
                        for (let j = 0; j < rows; j++) {{
                            let m = Bodies.circle(startX + i*U, startY + j*U, marbleRadius, {{
                                restitution: 0.1, friction: 0.01, density: 0.05,
                                render: {{ fillStyle: '#38BDF8', strokeStyle: '#0284C7', lineWidth: 1 }},
                                collisionFilter: {{ category: CAT_MARBLE, mask: CAT_WALL | CAT_MARBLE | CAT_SWORD }}
                            }});
                            marbles.push(m);
                            Composite.add(engine.world, m);
                        }}
                    }}
                }}
                
                // PHASE 2: Tip to Diamond
                else if (cycle >= 2500 && cycle < 4000) {{
                    phase = 2;
                    let p = (cycle - 2500) / 1500;
                    let desiredRotation = easeInOut(p) * targetTilt;
                    let delta = desiredRotation - currentRotation;
                    Composite.rotate(box, delta, {{x: cx, y: cy}});
                    currentRotation = desiredRotation;
                    
                    if (Math.random() < 0.2) marbles.forEach(m => Body.applyForce(m, m.position, {{x: (Math.random()-0.5)*0.0005, y: 0}}));
                }}
                
                // PHASE 3: Drop the Ghost Swords
                else if (cycle >= 4500 && cycle < 6500) {{
                    phase = 3;
                    let p = (cycle - 4500) / 2000;
                    let dropY = (cy - 1200) + (1200 * easeInOut(p));
                    
                    Body.setPosition(splitLeft, {{ x: cx, y: dropY }});
                    Body.setPosition(splitRight, {{ x: cx, y: dropY }});
                }}
                
                // PHASE 4: Pop Triangles Apart (Synchronized normal tracking)
                else if (cycle >= 7000 && cycle < 8500) {{
                    phase = 4;
                    let p = (cycle - 7000) / 1500;
                    
                    // Total separation target matches your requested 1 full grid unit (~U pixels)
                    let pop = easeInOut(p) * U; 
                    let delta = pop - lastPop;
                    lastPop = pop;
                    
                    // Compute the exact normal vector perpendicular to your diagonal slice trajectory
                    // This ensures the custom corners match edge-to-edge as they decouple
                    let perpAngle = diagAngle + Math.PI / 2;
                    let moveX = Math.cos(perpAngle) * delta;
                    let moveY = Math.sin(perpAngle) * delta;
                    
                    // Triangle group 1 (Left Side Assembly + Left Sword Cap) slides away
                    Body.translate(ceiling, {x: -moveX, y: -moveY});
                    Body.translate(leftWall, {x: -moveX, y: -moveY});
                    Body.translate(splitLeft, {x: -moveX, y: -moveY});
                    
                    // Triangle group 2 (Right Side Assembly + Right Sword Cap) slides away opposite
                    Body.translate(ground, {x: moveX, y: moveY});
                    Body.translate(rightWall, {x: moveX, y: moveY});
                    Body.translate(splitRight, {x: moveX, y: moveY});
                }}
            }});

            // --- 5. OVERLAY FORMULA & TRACKING LABELS ---
            // Helper function to orbit labels while keeping them upright
            function drawUprightLabel(context, body, text, color, localNx, localNy, offset) {{
                let a = body.angle;
                // Rotate local normal by body angle to get world space offset
                let worldNx = localNx * Math.cos(a) - localNy * Math.sin(a);
                let worldNy = localNx * Math.sin(a) + localNy * Math.cos(a);
                let px = body.position.x + worldNx * offset;
                let py = body.position.y + worldNy * offset;
                
                context.fillStyle = color;
                context.textAlign = "center";
                context.textBaseline = "middle";
                context.font = "bold 34px sans-serif";
                context.fillText(text, px, py);
            }}

            Events.on(render, 'afterRender', function() {{
                const context = render.context;
                let t = (performance.now() - startTime) % 12000;
                
                // 1. Draw perfectly spaced formula in the Upper Left (shifted slightly right)
                context.font = "bold 40px sans-serif"; 
                context.textBaseline = "alphabetic";
                context.textAlign = "left";
                
                // Adjusted coordinates: Upper-Left, shifted right from the edge
                const fx = 120; 
                const fy = 120;
                let currentX = fx;
                
                function drawText(text, color) {
                    context.fillStyle = color;
                    context.fillText(text, currentX, fy);
                    currentX += context.measureText(text).width;
                }

                if (t < 7000) {
                    drawText("Area", '#475569'); drawText(" = ", '#475569');
                    drawText("b", '#38BDF8'); drawText(" × ", '#475569'); drawText("h", '#4ADE80');
                } else {
                    drawText("Area", '#475569'); drawText(" = ", '#475569'); drawText("½", '#475569');
                    drawText(" × ", '#475569'); drawText("b", '#38BDF8'); drawText(" × ", '#475569'); drawText("h", '#4ADE80');
                }

                // 2. Draw Orbiting Upright Side Labels
                let off = (thickness / 2) + 30;
                drawUprightLabel(context, ceiling, "b", '#38BDF8', 0, -1, off);
                drawUprightLabel(context, ground, "b", '#38BDF8', 0, 1, off);
                drawUprightLabel(context, leftWall, "h", '#4ADE80', -1, 0, off);
                drawUprightLabel(context, rightWall, "h", '#4ADE80', 1, 0, off);
            }});

            Render.run(render);
            Runner.run(Runner.create(), engine);
        </script>
    </body>
    </html>
    """
    components.html(html_code, height=720)