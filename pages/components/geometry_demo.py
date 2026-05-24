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
        <canvas id="geomCanvas" width="1000" height="600"></canvas>
        <script>
            const Engine = Matter.Engine, Render = Matter.Render, Runner = Matter.Runner;
            const Bodies = Matter.Bodies, Body = Matter.Body, Composite = Matter.Composite, Events = Matter.Events;

            const CAT_WALL = 0x0001;
            const CAT_MARBLE = 0x0002;
            const CAT_SWORD = 0x0004;

            const engine = Engine.create();
            const gravity = engine.gravity || engine.world.gravity;
            gravity.y = 1; gravity.x = 0;

            const render = Render.create({{
                canvas: document.getElementById('geomCanvas'), engine: engine,
                options: {{ width: 1000, height: 600, wireframes: false, background: 'transparent' }}
            }});

            const U = 35; 
            const W = {base_units} * U;
            const H = {height_units} * U;
            const cx = 650; const cy = 300;
            
            const marbleRadius = (U - 2) / 2;
            const cols = {base_units};
            const rows = {height_units};
            
            const thickness = 40; 
            const wallOpt = {{ 
                isStatic: true, friction: 0.0, 
                render: {{ fillStyle: '#475569' }},
                collisionFilter: {{ category: CAT_WALL }} 
            }};
            
            let ground = Bodies.rectangle(cx, cy + H/2 + thickness/2, W + thickness*2, thickness, wallOpt);
            let ceiling = Bodies.rectangle(cx, cy - H/2 - thickness/2, W + thickness*2, thickness, wallOpt);
            let leftWall = Bodies.rectangle(cx - W/2 - thickness/2, cy, thickness, H + thickness*2, wallOpt);
            let rightWall = Bodies.rectangle(cx + W/2 + thickness/2, cy, thickness, H + thickness*2, wallOpt);

            const diagLength = Math.sqrt(W*W + H*H) + 40; 
            const splitOpt = {{ 
                isStatic: true, friction: 0.0, angle: Math.PI/2, 
                render: {{ fillStyle: '#EF4444' }},
                collisionFilter: {{ category: CAT_SWORD, mask: CAT_MARBLE }}
            }};
            
            let splitLeft = Bodies.rectangle(cx, cy - 1000, diagLength, 4, splitOpt);
            let splitRight = Bodies.rectangle(cx, cy - 1000, diagLength, 4, splitOpt);

            let box = Composite.create();
            Composite.add(box, [ground, ceiling, leftWall, rightWall]);
            Composite.add(engine.world, [box, splitLeft, splitRight]);

            let marbles = [];
            const diagAngle = Math.atan2(H, -W); 
            const targetTilt = Math.PI/2 - diagAngle; 

            let startTime = performance.now();
            let phase = -1;
            let currentRotation = 0;
            let lastPop = 0;

            function easeInOut(x) {{ return -(Math.cos(Math.PI * x) - 1) / 2; }}

            Events.on(engine, 'beforeUpdate', function() {{
                let t = performance.now() - startTime;
                let cycle = t % 12000; 

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
                    Body.setPosition(splitLeft, {{ x: cx, y: cy - 1000 }});
                    Body.setPosition(splitRight, {{ x: cx, y: cy - 1000 }});

                    const startX = cx - W/2 + U/2;
                    const startY = cy - H/2 + U/2;
                    for (let i = 0; i < cols; i++) {{
                        for (let j = 0; j < rows; j++) {{
                            let m = Bodies.circle(startX + i*U, startY + j*U, marbleRadius, {{
                                restitution: 0.1, friction: 0.05, density: 0.05,
                                render: {{ fillStyle: '#38BDF8', strokeStyle: '#0284C7', lineWidth: 1 }},
                                collisionFilter: {{ category: CAT_MARBLE, mask: CAT_WALL | CAT_MARBLE | CAT_SWORD }}
                            }});
                            marbles.push(m);
                            Composite.add(engine.world, m);
                        }}
                    }}
                }}
                
                else if (cycle >= 2500 && cycle < 4000) {{
                    phase = 2;
                    let p = (cycle - 2500) / 1500;
                    let desiredRotation = easeInOut(p) * targetTilt;
                    let delta = desiredRotation - currentRotation;
                    Composite.rotate(box, delta, {{x: cx, y: cy}});
                    currentRotation = desiredRotation;
                    
                    if (Math.random() < 0.2) marbles.forEach(m => Body.applyForce(m, m.position, {{x: (Math.random()-0.5)*0.0005, y: 0}}));
                }}
                
                else if (cycle >= 4500 && cycle < 6500) {{
                    phase = 3;
                    let p = (cycle - 4500) / 2000;
                    let dropY = (cy - 1000) + (1000 * easeInOut(p));
                    
                    Body.setPosition(splitLeft, {{ x: cx, y: dropY }});
                    Body.setPosition(splitRight, {{ x: cx, y: dropY }});
                }}
                
                else if (cycle >= 7000 && cycle < 8500) {{
                    phase = 4;
                    let p = (cycle - 7000) / 1500;
                    let pop = easeInOut(p) * 60; // Increased to 60px separation
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

            Events.on(render, 'afterRender', function() {{
                const context = render.context;
                let t = (performance.now() - startTime) % 12000;
                context.font = "bold 34px sans-serif"; context.textAlign = "left";
                const fx = 50; const fy = 310;

                if (t < 7000) {{
                    context.fillStyle = '#475569'; context.fillText("Area = ", fx, fy);
                    context.fillStyle = '#38BDF8'; context.fillText("b", fx + 120, fy);
                    context.fillStyle = '#475569'; context.fillText(" × ", fx + 145, fy);
                    context.fillStyle = '#4ADE80'; context.fillText("h", fx + 195, fy);
                }} else {{
                    context.fillStyle = '#475569'; context.fillText("Area = ½ × ", fx, fy);
                    context.fillStyle = '#38BDF8'; context.fillText("b", fx + 195, fy);
                    context.fillStyle = '#475569'; context.fillText(" × ", fx + 220, fy);
                    context.fillStyle = '#4ADE80'; context.fillText("h", fx + 270, fy);
                }}
            }});

            Render.run(render);
            Runner.run(Runner.create(), engine);
        </script>
    </body>
    </html>
    """
    components.html(html_code, height=620)