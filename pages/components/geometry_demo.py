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

            const CAT_WALL = 0x0001;
            const CAT_MARBLE = 0x0002;
            const CAT_SWORD = 0x0004;

            const engine = Engine.create();
            engine.positionIterations = 16; 
            engine.velocityIterations = 16;
            const gravity = engine.gravity || engine.world.gravity;
            gravity.y = 1; gravity.x = 0;

            const render = Render.create({{
                canvas: document.getElementById('geomCanvas'), engine: engine,
                options: {{ width: 1200, height: 700, wireframes: false, background: 'transparent' }}
            }});

            // --- 2. GRID MATH & SIZING ---
            const U = 48; 
            const W = {base_units} * U;
            const H = {height_units} * U;
            const cx = 600; const cy = 350; // Perfectly centered
            
            const marbleRadius = (U - 2) / 2;
            const cols = {base_units};
            const rows = {height_units};
            const valAreaRect = cols * rows;
            const valAreaTri = valAreaRect / 2;
            
            // --- 3. CONSTRUCT RIGID BODIES ---
            const thickness = 6; 
            const wallOpt = {{ 
                isStatic: true, friction: 0.0, 
                render: {{ fillStyle: '#475569' }},
                collisionFilter: {{ category: CAT_WALL }} 
            }};
            
            let ground = Bodies.rectangle(cx, cy + H/2 + thickness/2, W + thickness*2, thickness, wallOpt);
            let ceiling = Bodies.rectangle(cx, cy - H/2 - thickness/2, W + thickness*2, thickness, wallOpt);
            let leftWall = Bodies.rectangle(cx - W/2 - thickness/2, cy, thickness, H + thickness*2, wallOpt);
            let rightWall = Bodies.rectangle(cx + W/2 + thickness/2, cy, thickness, H + thickness*2, wallOpt);

            const diagLength = Math.sqrt(W*W + H*H) + thickness;
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
                let cycle = t % 15000; // Expanded to 15s total loop

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
                
                else if (cycle >= 4000 && cycle < 5500) {{
                    phase = 2;
                    let p = (cycle - 4000) / 1500;
                    let desiredRotation = easeInOut(p) * targetTilt;
                    let delta = desiredRotation - currentRotation;
                    Composite.rotate(box, delta, {{x: cx, y: cy}});
                    currentRotation = desiredRotation;
                    if (Math.random() < 0.2) marbles.forEach(m => Body.applyForce(m, m.position, {{x: (Math.random()-0.5)*0.001, y: 0}}));
                }}
                
                else if (cycle >= 6000 && cycle < 8000) {{
                    phase = 3;
                    let p = (cycle - 6000) / 2000;
                    let dropY = (cy - 1200) + (1200 * easeInOut(p));
                    Body.setPosition(splitLeft, {{ x: cx, y: dropY }});
                    Body.setPosition(splitRight, {{ x: cx, y: dropY }});
                }}
                
                else if (cycle >= 8500 && cycle < 10000) {{
                    phase = 4;
                    let p = (cycle - 8500) / 1500;
                    let pop = easeInOut(p) * U; 
                    let delta = pop - lastPop;
                    lastPop = pop;
                    
                    Body.translate(ceiling, {{x: -delta, y: 0}});
                    Body.translate(leftWall, {{x: -delta, y: 0}});
                    Body.translate(splitLeft, {{x: -delta, y: 0}});
                    
                    Body.translate(ground, {{x: delta, y: 0}});
                    Body.translate(rightWall, {{x: delta, y: 0}});
                    Body.translate(splitRight, {{x: delta, y: 0}});
                }}
            }});

            // --- 5. OVERLAY FORMULA & TRACKING LABELS ---
            
            // Text crossfade engine prevents layout jumping by centering text within the max width of both strings
            function drawFadingText(context, text1, text2, color1, color2, alpha2, x, y) {{
                let w1 = context.measureText(text1).width;
                let w2 = context.measureText(text2).width;
                let wMax = Math.max(w1, w2);

                context.globalAlpha = Math.max(0, 1 - alpha2);
                context.fillStyle = color1;
                context.fillText(text1, x + (wMax - w1)/2, y);

                context.globalAlpha = Math.max(0, alpha2);
                context.fillStyle = color2;
                context.fillText(text2, x + (wMax - w2)/2, y);

                context.globalAlpha = 1.0;
                return x + wMax;
            }}

            // --- FIXED-WIDTH FADE ENGINE ---
            function drawFadingText(context, text1, text2, color1, color2, alpha2, x, y, fixedWidth) {{}
                context.textAlign = "center"; // Center text within the reserved fixedWidth slot
                let centerX = x + fixedWidth / 2;

                context.globalAlpha = Math.max(0, 1 - alpha2);
                context.fillStyle = color1;
                context.fillText(text1, centerX, y);

                context.globalAlpha = Math.max(0, alpha2);
                context.fillStyle = color2;
                context.fillText(text2, centerX, y);

                context.globalAlpha = 1.0;
                return x + fixedWidth;
            }}

            Events.on(render, 'afterRender', function() {{}
                const context = render.context;
                let t = (performance.now() - startTime) % 15000;
                
                context.font = "bold 40px sans-serif"; 
                context.textBaseline = "alphabetic";
                
                // --- FORMULA LAYOUT (Anchored to Equals Sign) ---
                const eqX = 250; // The fixed anchor for the '=' sign
                const eqWidth = context.measureText(" = ").width;
                const slotWidth = 120; // Fixed width for terms (Area, b, h)
                
                context.textAlign = "center";
                context.fillStyle = '#475569';
                context.fillText(" = ", eqX, 120);

                let alphaNum = t > 2000 ? Math.min(1, (t - 2000) / 1500) : 0;
                let alphaAreaTri = t > 10500 ? Math.min(1, (t - 10500) / 1500) : 0;

                if (t < 7000) {{}
                    drawFadingText(context, "Area", valAreaRect.toString(), '#475569', '#475569', alphaNum, eqX - slotWidth, 120, slotWidth);
                    drawFadingText(context, "b", cols.toString(), '#38BDF8', '#38BDF8', alphaNum, eqX + eqWidth, 120, slotWidth);
                    context.fillText(" × ", eqX + eqWidth + slotWidth + 20, 120);
                    drawFadingText(context, "h", rows.toString(), '#4ADE80', '#4ADE80', alphaNum, eqX + eqWidth + slotWidth + 60, 120, slotWidth);
                }} else {{
                    drawFadingText(context, "Area", valAreaTri.toString(), '#475569', '#475569', alphaAreaTri, eqX - slotWidth, 120, slotWidth);
                    context.fillStyle = '#EF4444'; context.fillText("½ ×", eqX + 50, 120);
                    drawFadingText(context, "b", cols.toString(), '#38BDF8', '#38BDF8', 1, eqX + eqWidth + slotWidth - 40, 120, slotWidth);
                    context.fillStyle = '#475569'; context.fillText(" × ", eqX + eqWidth + slotWidth*2 - 20, 120);
                    drawFadingText(context, "h", rows.toString(), '#4ADE80', '#4ADE80', 1, eqX + eqWidth + slotWidth*2 + 20, 120, slotWidth);
                }}
                
                // Orbiting labels remain as before
                let off = (thickness / 2) + 30;
                drawUprightFadingLabel(context, ceiling, "b", cols.toString(), '#38BDF8', alphaNum, 0, -1, off);
                drawUprightFadingLabel(context, ground, "b", cols.toString(), '#38BDF8', alphaNum, 0, 1, off);
                drawUprightFadingLabel(context, leftWall, "h", rows.toString(), '#4ADE80', alphaNum, -1, 0, off);
                drawUprightFadingLabel(context, rightWall, "h", rows.toString(), '#4ADE80', alphaNum, 1, 0, off);
            }});

            Render.run(render);
            Runner.run(Runner.create(), engine);
        </script>
    </body>
    </html>
    """
    components.html(html_code, height=720)