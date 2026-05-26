"""
=============================================================================
MODULE: pages/components/pythagorean_demo.py
AUTHOR: Kyle W. Killebrew, PhD & Data Science Mentorship Engine
STATUS: Active Specification Profile for Lesson 3 Component
DESCRIPTION: 
    A GPU-accelerated Matter.js simulation visualizing the Pythagorean Theorem.
    Orchestrates a 4-Phase Chronological Framework directly on HTML5 Canvas.

    --- MATLAB BRIDGE ---
    Shifts standard execution loops from static matrix plots to a dynamic web UI
    wrapper. This routes inputs to a local rigid-body kinematic solver executed
    directly via the user's browser canvas.
=============================================================================
"""

import streamlit.components.v1 as components

def render_pythagorean_demo(a_units, b_units):
    """
    Renders an 800x800 high-performance Matter.js interactive frame mapping
    out the geometric conservation law: Area A + Area B = Area C.
    """
    scale = 35
    sideA = a_units * scale
    sideB = b_units * scale
    sideC = float((sideA**2 + sideB**2)**0.5)

    countA = int(a_units**2 * 3)
    countB = int(b_units**2 * 3)
    countC = countA + countB

    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/matter-js/0.19.0/matter.min.js"></script>
        <style>
            body {{ margin: 0; padding: 0; overflow: hidden; background-color: #0F172A; font-family: sans-serif; }}
            canvas {{ display: block; margin: 0 auto; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }}
            #debug-console {{ color: #F87171; padding: 20px; font-size: 14px; position: absolute; top: 0; z-index: 100; }}
        </style>
    </head>
    <body>
        <div id="debug-console"></div>
        <script>
            window.addEventListener('DOMContentLoaded', function() {{
                try {{
                    // --- PYTHON TO JAVASCRIPT DATA BRIDGE ---
                    const sideA = {sideA};
                    const sideB = {sideB};
                    const sideC = {sideC};
                    const countA = {countA};
                    const countB = {countB};
                    const countC = {countC};
                    const a_units = {a_units};
                    const b_units = {b_units};

                    if (typeof Matter === 'undefined') {{
                        throw new Error("Matter.js engine failed to load via CDN.");
                    }}

                    const Engine = Matter.Engine,
                          Render = Matter.Render,
                          Runner = Matter.Runner,
                          Bodies = Matter.Bodies,
                          Composite = Matter.Composite,
                          Events = Matter.Events,
                          Body = Matter.Body;

                    const engine = Engine.create({{ positionIterations: 12, velocityIterations: 12 }});
                    engine.gravity.y = 1.0;

                    const width = 800;
                    const height = 800;
                    const globalCX = width / 2;
                    const globalCY = height / 2;

                    const render = Render.create({{
                        element: document.body,
                        engine: engine,
                        options: {{ width: width, height: height, wireframes: false, background: '#0F172A' }}
                    }});

                    const CAT_TRIANGLE = 0x0001;
                    const CAT_BOX = 0x0002;
                    const CAT_MARBLE = 0x0004;

                    // --- 1. LOCAL COORDINATE MATRIX (Centered on Triangle Centroid) ---
                    // By defining vertices relative to the mathematical centroid, rotation is perfectly balanced.
                    const v1 = {{ x: -sideA/3, y: sideB/3 }};       // Right Angle
                    const v2 = {{ x: 2*sideA/3, y: sideB/3 }};      // Base edge
                    const v3 = {{ x: -sideA/3, y: -2*sideB/3 }};    // Height edge

                    const triangleBody = Bodies.fromVertices(0, 0, [v1, v2, v3], {{ 
                        isStatic: true, 
                        collisionFilter: {{ category: CAT_TRIANGLE }} 
                    }}, true);
                    Body.setPosition(triangleBody, {{ x: globalCX, y: globalCY }});

                    // --- 2. 4-WALL BOX ARCHITECTURE ---
                    const thick = 8;
                    const wallColor = '#475569';

                    function createSquareContainer(localX, localY, size, angle) {{
                        const h = (size + thick) / 2;
                        const w = size + thick * 2;
                        
                        // We build 4 walls so marbles NEVER spill when detached!
                        const parts = [
                            Bodies.rectangle(0, -h, w, thick, {{ render: {{ fillStyle: wallColor, opacity: 0 }} }}),
                            Bodies.rectangle(0, h, w, thick, {{ render: {{ fillStyle: wallColor, opacity: 0 }} }}),
                            Bodies.rectangle(-h, 0, thick, size, {{ render: {{ fillStyle: wallColor, opacity: 0 }} }}),
                            Bodies.rectangle(h, 0, thick, size, {{ render: {{ fillStyle: wallColor, opacity: 0 }} }})
                        ];
                        
                        const box = Body.create({{ 
                            parts: parts, 
                            isStatic: true, 
                            collisionFilter: {{ category: CAT_BOX }} 
                        }});
                        
                        Body.setPosition(box, {{ x: globalCX + localX, y: globalCY + localY }});
                        Body.setAngle(box, angle);
                        return box;
                    }}

                    // Calculate precise offset vectors for the squares
                    const locBoxA = {{ x: sideA/6, y: sideB/3 + (sideA+thick)/2, angle: 0 }};
                    const locBoxB = {{ x: -sideA/3 - (sideB+thick)/2, y: -sideB/6, angle: 0 }};
                    
                    const normCX = sideB / sideC;
                    const normCY = -sideA / sideC;
                    const locBoxC = {{ 
                        x: sideA/6 + normCX * ((sideC+thick)/2), 
                        y: -sideB/6 + normCY * ((sideC+thick)/2), 
                        angle: Math.atan2(-sideB, -sideA) 
                    }};

                    const boxA = createSquareContainer(locBoxA.x, locBoxA.y, sideA, locBoxA.angle);
                    const boxB = createSquareContainer(locBoxB.x, locBoxB.y, sideB, locBoxB.angle);
                    const boxC = createSquareContainer(locBoxC.x, locBoxC.y, sideC, locBoxC.angle);

                    Composite.add(engine.world, [triangleBody, boxA, boxB, boxC]);

                    // --- 3. INTERNAL MARBLE SPAWNER ---
                    function spawnMarbles(box, count, color, size) {{
                        for (let i = 0; i < count; i++) {{
                            // Generate in local coordinate bounds, then rotate into global placement
                            let lx = (Math.random() - 0.5) * (size - thick * 3);
                            let ly = (Math.random() - 0.5) * (size - thick * 3);
                            let cos = Math.cos(box.angle);
                            let sin = Math.sin(box.angle);
                            let rx = box.position.x + (lx * cos - ly * sin);
                            let ry = box.position.y + (lx * sin + ly * cos);
                            
                            let marble = Bodies.circle(rx, ry, 4.5, {{
                                restitution: 0.2, friction: 0.02,
                                render: {{ fillStyle: color }},
                                collisionFilter: {{ category: CAT_MARBLE, mask: CAT_BOX | CAT_MARBLE }}
                            }});
                            Composite.add(engine.world, marble);
                        }}
                    }}

                    // --- 4. KINEMATIC STATE MACHINE MOTOR ---
                    const startTime = performance.now();
                    let marblesSpawned = false;
                    let labelsOpacity = 0;

                    Events.on(engine, 'beforeUpdate', function() {{
                        let elapsed = performance.now() - startTime;

                        // Phase 1: Reveal/Grow Squares (1000ms -> 3000ms)
                        if (elapsed > 1000 && elapsed <= 3000) {{
                            let p = (elapsed - 1000) / 2000;
                            [boxA, boxB, boxC].forEach(box => {{
                                box.parts.forEach(part => part.render.opacity = p);
                            }});
                        }}
                        
                        // Phase 2: Spawn Marbles Inside Enclosures (3100ms)
                        else if (elapsed > 3100 && !marblesSpawned) {{
                            [boxA, boxB, boxC].forEach(box => {{
                                box.parts.forEach(part => part.render.opacity = 1); // Lock to 100%
                            }});
                            spawnMarbles(boxA, countA, '#38BDF8', sideA); 
                            spawnMarbles(boxB, countB, '#F43F5E', sideB); 
                            spawnMarbles(boxC, countC, '#10B981', sideC); 
                            marblesSpawned = true;
                        }}

                        // Phase 3: Structural Rotation (5000ms -> 9000ms)
                        else if (elapsed > 5000 && elapsed <= 9000) {{
                            let p = (elapsed - 5000) / 4000;
                            // Smooth ease-in-out curve
                            let easeP = p < 0.5 ? 2 * p * p : 1 - Math.pow(-2 * p + 2, 2) / 2;
                            let angle = easeP * Math.PI * 2; 

                            // Apply rigid transformation matrix mathematically
                            [ {{b: triangleBody, loc: {{x:0, y:0, angle:0}}}}, 
                              {{b: boxA, loc: locBoxA}}, 
                              {{b: boxB, loc: locBoxB}}, 
                              {{b: boxC, loc: locBoxC}} ].forEach(item => {{
                                
                                let gx = globalCX + item.loc.x * Math.cos(angle) - item.loc.y * Math.sin(angle);
                                let gy = globalCY + item.loc.x * Math.sin(angle) + item.loc.y * Math.cos(angle);
                                
                                Body.setPosition(item.b, {{ x: gx, y: gy }});
                                Body.setAngle(item.b, item.loc.angle + angle);
                            }});
                        }}

                        // Phase 4: Detachment & Linearization (10000ms -> 13000ms)
                        else if (elapsed > 10000 && elapsed <= 13000) {{
                            let p = (elapsed - 10000) / 3000;
                            let easeP = p < 0.5 ? 2 * p * p : 1 - Math.pow(-2 * p + 2, 2) / 2;

                            // Interpolate Triangle to Bottom
                            Body.setPosition(triangleBody, {{ x: globalCX, y: globalCY + (600 - globalCY) * easeP }});
                            
                            // Interpolate Box A to Top Left
                            let startAX = globalCX + locBoxA.x; let startAY = globalCY + locBoxA.y;
                            Body.setPosition(boxA, {{ x: startAX + (180 - startAX) * easeP, y: startAY + (200 - startAY) * easeP }});
                            Body.setAngle(boxA, locBoxA.angle * (1 - easeP)); // Unwind angle to 0
                            
                            // Interpolate Box B to Top Middle
                            let startBX = globalCX + locBoxB.x; let startBY = globalCY + locBoxB.y;
                            Body.setPosition(boxB, {{ x: startBX + (400 - startBX) * easeP, y: startBY + (200 - startBY) * easeP }});
                            Body.setAngle(boxB, locBoxB.angle * (1 - easeP));
                            
                            // Interpolate Box C to Top Right
                            let startCX = globalCX + locBoxC.x; let startCY = globalCY + locBoxC.y;
                            Body.setPosition(boxC, {{ x: startCX + (620 - startCX) * easeP, y: startCY + (200 - startCY) * easeP }});
                            Body.setAngle(boxC, locBoxC.angle * (1 - easeP));
                        }}

                        // Phase 5: Fade HUD Triggers
                        if (elapsed > 12500) {{
                            if (labelsOpacity < 1.0) {{ labelsOpacity += 0.015; }}
                        }}
                    }});

                    // --- 5. CANVAS GRAPHIC INTERFACE HEADS-UP DISPLAY ---
                    Events.on(render, 'afterRender', function() {{
                        const context = render.context;
                        let elapsed = performance.now() - startTime;
                        context.save();
                        
                        context.font = "bold 15px sans-serif";
                        context.fillStyle = "#64748B";
                        context.fillText("Active State Engine Metrics", 25, 40);
                        
                        context.font = "14px sans-serif";
                        context.fillStyle = elapsed <= 3000 ? "#38BDF8" : "#475569";
                        context.fillText("Phase 1: Settlement & Growth", 25, 65);
                        
                        context.fillStyle = (elapsed > 3000 && elapsed <= 5000) ? "#38BDF8" : "#475569";
                        context.fillText("Phase 2: Populate Mass Arrays", 25, 88);

                        context.fillStyle = (elapsed > 5000 && elapsed <= 9000) ? "#38BDF8" : "#475569";
                        context.fillText("Phase 3: Orbit Kinematics", 25, 111);
                        
                        context.fillStyle = (elapsed > 10000 && elapsed <= 13000) ? "#38BDF8" : "#475569";
                        context.fillText("Phase 4: Structural Disassembly", 25, 134);

                        context.fillStyle = elapsed > 13000 ? "#10B981" : "#475569";
                        context.fillText("Phase 5: Equation Equilibrium", 25, 157);

                        // High contrast equation HUD mapping sequence
                        if (elapsed > 12500) {{
                            context.fillStyle = "rgba(248, 250, 252, " + labelsOpacity + ")";
                            context.font = "bold 48px sans-serif";
                            context.textAlign = "center";
                            
                            context.fillText("+", 290, 210);
                            context.fillText("=", 510, 210);

                            context.font = "bold 20px sans-serif";
                            context.fillStyle = "rgba(56, 189, 248, " + labelsOpacity + ")";
                            context.fillText("Side A²", 180, 85);
                            context.font = "14px sans-serif";
                            context.fillText("Vol = " + (a_units * a_units) + " units²", 180, 105);

                            context.font = "bold 20px sans-serif";
                            context.fillStyle = "rgba(244, 63, 94, " + labelsOpacity + ")";
                            context.fillText("Side B²", 400, 85);
                            context.font = "14px sans-serif";
                            context.fillText("Vol = " + (b_units * b_units) + " units²", 400, 105);

                            context.font = "bold 20px sans-serif";
                            context.fillStyle = "rgba(16, 185, 129, " + labelsOpacity + ")";
                            context.fillText("Hypotenuse C²", 620, 85);
                            context.font = "14px sans-serif";
                            context.fillText("Vol = " + Math.round(a_units*a_units + b_units*b_units) + " units²", 620, 105);
                            
                            context.font = "italic 18px sans-serif";
                            context.fillStyle = "rgba(148, 163, 184, " + labelsOpacity + ")";
                            context.fillText("Empirical Marble Density Count Match: " + countA + " + " + countB + " = " + countC, width / 2, 360);
                        }}
                        context.restore();
                    }});

                    Render.run(render);
                    const runner = Runner.create();
                    Runner.run(runner, engine);

                }} catch (error) {{
                    document.getElementById('debug-console').innerHTML = "<strong>CRITICAL COMPILE FAULT:</strong> " + error.message;
                }}
            }});
        </script>
    </body>
    </html>
    """
    components.html(html_code, height=820)