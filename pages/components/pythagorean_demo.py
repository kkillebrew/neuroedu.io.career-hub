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
    wrapper. Features isolated collision tracking matrices to prevent cross-box
    interference during layout translations.
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

                    // INCREASED SOLVER ITERATIONS (Prevents high-speed tunneling)
                    const engine = Engine.create({{ positionIterations: 24, velocityIterations: 20 }});
                    engine.gravity.y = 1.0;

                    const width = 800;
                    const height = 800;
                    const globalCX = width / 2;
                    const globalCY = height / 2 - 30;

                    const render = Render.create({{
                        element: document.body,
                        engine: engine,
                        options: {{ width: width, height: height, wireframes: false, background: '#0F172A' }}
                    }});

                    // --- PARALLEL COLLISION MATRICES (The Overlap Fix) ---
                    // By giving each subsystem its own binary flag, they ghost through each other
                    // perfectly during the final layout transition without dragging foreign marbles.
                    const CAT_TRIANGLE = 0x0001;
                    const CAT_BOX_A = 0x0002;
                    const CAT_MARBLE_A = 0x0004;
                    const CAT_BOX_B = 0x0008;
                    const CAT_MARBLE_B = 0x0010;
                    const CAT_BOX_C = 0x0020;
                    const CAT_MARBLE_C = 0x0040;

                    const triangleBody = Bodies.fromVertices(globalCX, globalCY, [
                        {{ x: -sideA/3, y: sideB/3 }},
                        {{ x: 2*sideA/3, y: sideB/3 }},
                        {{ x: -sideA/3, y: -2*sideB/3 }}
                    ], {{ isStatic: true, collisionFilter: {{ category: CAT_TRIANGLE }} }}, true);

                    // --- 4-WALL BOX ARCHITECTURE (Thickened to Prevent Escapes) ---
                    const thick = 16; 
                    const wallColor = '#475569';

                    function createSquareContainer(localX, localY, size, angle, catBox, maskBox) {{
                        const h = (size + thick) / 2;
                        const w = size + thick * 2;
                        
                        const parts = [
                            Bodies.rectangle(0, -h, w, thick, {{ render: {{ fillStyle: wallColor, opacity: 0 }}, collisionFilter: {{ category: catBox, mask: maskBox }} }}),
                            Bodies.rectangle(0, h, w, thick, {{ render: {{ fillStyle: wallColor, opacity: 0 }}, collisionFilter: {{ category: catBox, mask: maskBox }} }}),
                            Bodies.rectangle(-h, 0, thick, size, {{ render: {{ fillStyle: wallColor, opacity: 0 }}, collisionFilter: {{ category: catBox, mask: maskBox }} }}),
                            Bodies.rectangle(h, 0, thick, size, {{ render: {{ fillStyle: wallColor, opacity: 0 }}, collisionFilter: {{ category: catBox, mask: maskBox }} }})
                        ];
                        
                        const box = Body.create({{ parts: parts, isStatic: true }});
                        Body.setPosition(box, {{ x: globalCX + localX, y: globalCY + localY }});
                        Body.setAngle(box, angle);
                        return box;
                    }}

                    // Local centroid alignments
                    const locBoxA = {{ x: sideA/6, y: sideB/3 + (sideA+thick)/2, angle: 0 }};
                    const locBoxB = {{ x: -sideA/3 - (sideB+thick)/2, y: -sideB/6, angle: 0 }};
                    const normCX = sideB / sideC;
                    const normCY = -sideA / sideC;
                    const locBoxC = {{ x: sideA/6 + normCX * ((sideC+thick)/2), y: -sideB/6 + normCY * ((sideC+thick)/2), angle: Math.atan2(-sideB, -sideA) }};

                    const boxA = createSquareContainer(locBoxA.x, locBoxA.y, sideA, locBoxA.angle, CAT_BOX_A, CAT_MARBLE_A);
                    const boxB = createSquareContainer(locBoxB.x, locBoxB.y, sideB, locBoxB.angle, CAT_BOX_B, CAT_MARBLE_B);
                    const boxC = createSquareContainer(locBoxC.x, locBoxC.y, sideC, locBoxC.angle, CAT_BOX_C, CAT_MARBLE_C);

                    Composite.add(engine.world, [triangleBody, boxA, boxB, boxC]);

                    function spawnMarbles(box, count, color, size, catMarble, maskMarble) {{
                        for (let i = 0; i < count; i++) {{
                            // Constrain spawn area to account for the new thicker walls
                            let lx = (Math.random() - 0.5) * (size - thick * 3);
                            let ly = (Math.random() - 0.5) * (size - thick * 3);
                            let cos = Math.cos(box.angle);
                            let sin = Math.sin(box.angle);
                            
                            let marble = Bodies.circle(
                                box.position.x + (lx * cos - ly * sin), 
                                box.position.y + (lx * sin + ly * cos), 
                                4.5, 
                                {{
                                    restitution: 0.1, friction: 0.05,
                                    render: {{ fillStyle: color }},
                                    collisionFilter: {{ category: catMarble, mask: maskMarble }}
                                }}
                            );
                            Composite.add(engine.world, marble);
                        }}
                    }}

                    // --- FINAL HUD TARGET COORDINATES (Stacked Logic) ---
                    const targetAX = 200;
                    const targetAY = sideA/2 + 90;
                    const targetBX = 200;
                    const targetBY = targetAY + sideA/2 + sideB/2 + 80;
                    const targetCX = 580;
                    const targetCY = (targetAY + targetBY) / 2;
                    const targetTriY = height - 100;

                    // --- CHOREOGRAPHY STATE MACHINE ---
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
                                box.parts.forEach(part => part.render.opacity = 1);
                            }});
                            // Map marbles strictly to their parent box collision realm
                            spawnMarbles(boxA, countA, '#38BDF8', sideA, CAT_MARBLE_A, CAT_BOX_A | CAT_MARBLE_A); 
                            spawnMarbles(boxB, countB, '#F43F5E', sideB, CAT_MARBLE_B, CAT_BOX_B | CAT_MARBLE_B); 
                            spawnMarbles(boxC, countC, '#10B981', sideC, CAT_MARBLE_C, CAT_BOX_C | CAT_MARBLE_C); 
                            marblesSpawned = true;
                        }}

                        // Phase 3: Structural Rotation (5000ms -> 9000ms)
                        else if (elapsed > 5000 && elapsed <= 9000) {{
                            let p = (elapsed - 5000) / 4000;
                            let easeP = p < 0.5 ? 2 * p * p : 1 - Math.pow(-2 * p + 2, 2) / 2;
                            let angle = easeP * Math.PI * 2; 

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

                        // Phase 4: Detachment & Stacked Vertical Linearization (10000ms -> 13000ms)
                        else if (elapsed > 10000 && elapsed <= 13000) {{
                            let p = (elapsed - 10000) / 3000;
                            let easeP = p < 0.5 ? 2 * p * p : 1 - Math.pow(-2 * p + 2, 2) / 2;

                            Body.setPosition(triangleBody, {{ x: globalCX, y: globalCY + (targetTriY - globalCY) * easeP }});
                            
                            let startAX = globalCX + locBoxA.x; let startAY = globalCY + locBoxA.y;
                            Body.setPosition(boxA, {{ x: startAX + (targetAX - startAX) * easeP, y: startAY + (targetAY - startAY) * easeP }});
                            Body.setAngle(boxA, locBoxA.angle * (1 - easeP)); 
                            
                            let startBX = globalCX + locBoxB.x; let startBY = globalCY + locBoxB.y;
                            Body.setPosition(boxB, {{ x: startBX + (targetBX - startBX) * easeP, y: startBY + (targetBY - startBY) * easeP }});
                            Body.setAngle(boxB, locBoxB.angle * (1 - easeP));
                            
                            let startCX = globalCX + locBoxC.x; let startCY = globalCY + locBoxC.y;
                            Body.setPosition(boxC, {{ x: startCX + (targetCX - startCX) * easeP, y: startCY + (targetCY - startCY) * easeP }});
                            Body.setAngle(boxC, locBoxC.angle * (1 - easeP));
                        }}

                        if (elapsed > 12500 && labelsOpacity < 1.0) {{
                            labelsOpacity += 0.015;
                        }}
                    }});

                    // --- CANVAS GRAPHIC INTERFACE HEADS-UP DISPLAY ---
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

                        if (elapsed > 12500) {{
                            context.fillStyle = "rgba(248, 250, 252, " + labelsOpacity + ")";
                            context.font = "bold 48px sans-serif";
                            context.textAlign = "center";
                            
                            // Align Plus Sign exactly in the 80px gap between Box A and B
                            let plusY = (targetAY + sideA/2 + targetBY - sideB/2) / 2;
                            context.fillText("+", 200, plusY + 16);
                            context.fillText("=", 390, targetCY + 16);

                            // Left Column: Box A 
                            context.font = "bold 20px sans-serif";
                            context.fillStyle = "rgba(56, 189, 248, " + labelsOpacity + ")";
                            context.fillText("Side A²", 200, targetAY - sideA/2 - 40);
                            context.font = "14px sans-serif";
                            context.fillText("Vol = " + (a_units * a_units) + " units²", 200, targetAY - sideA/2 - 15);

                            // Left Column: Box B
                            context.font = "bold 20px sans-serif";
                            context.fillStyle = "rgba(244, 63, 94, " + labelsOpacity + ")";
                            context.fillText("Side B²", 200, targetBY - sideB/2 - 40);
                            context.font = "14px sans-serif";
                            context.fillText("Vol = " + (b_units * b_units) + " units²", 200, targetBY - sideB/2 - 15);

                            // Right Column: Box C
                            context.font = "bold 20px sans-serif";
                            context.fillStyle = "rgba(16, 185, 129, " + labelsOpacity + ")";
                            context.fillText("Hypotenuse C²", 580, targetCY - sideC/2 - 40);
                            context.font = "14px sans-serif";
                            context.fillText("Vol = " + Math.round(a_units*a_units + b_units*b_units) + " units²", 580, targetCY - sideC/2 - 15);
                            
                            context.font = "italic 16px sans-serif";
                            context.fillStyle = "rgba(148, 163, 184, " + labelsOpacity + ")";
                            context.fillText("Empirical Density Match: " + countA + " + " + countB + " = " + countC, width / 2, 780);
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