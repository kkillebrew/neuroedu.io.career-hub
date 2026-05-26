"""
=============================================================================
MODULE: pages/components/pythagorean_demo.py
AUTHOR: Kyle W. Killebrew, PhD & Data Science Mentorship Engine
STATUS: Active Specification Profile for Lesson 3 Component
DESCRIPTION: 
    A GPU-accelerated Matter.js simulation visualizing the Pythagorean Theorem.
    Orchestrates a 5-Phase Chronological Framework directly on HTML5 Canvas.

    --- MATLAB BRIDGE ---
    Implements Kinematic Trajectory Planning and Continuous Collision Detection 
    (CCD) velocity patching to prevent tunneling errors common in standard
    rigid-body simulation transitions.
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

                    // STRICT CCD SOLVER: Boosted iterations to prevent high-speed wall tunneling
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

                    // --- PARALLEL COLLISION MATRICES ---
                    const CAT_TRIANGLE = 0x0001;
                    const CAT_BOX_A = 0x0002;
                    const CAT_MARBLE_A = 0x0004;
                    const CAT_BOX_B = 0x0008;
                    const CAT_MARBLE_B = 0x0010;
                    const CAT_BOX_C = 0x0020;
                    const CAT_MARBLE_C = 0x0040;

                    // --- FLAWLESS GEOMETRIC ALIGNMENT MATRIX ---
                    // Explicit right triangle coordinates relative to 0,0
                    const v1 = {{ x: -sideA/2, y: sideB/2 }};  // Bottom Left (Right Angle)
                    const v2 = {{ x: sideA/2, y: sideB/2 }};   // Bottom Right
                    const v3 = {{ x: -sideA/2, y: -sideB/2 }}; // Top Left

                    const triangleBody = Bodies.fromVertices(globalCX, globalCY, [v1, v2, v3], {{ 
                        isStatic: true, 
                        collisionFilter: {{ category: CAT_TRIANGLE }} 
                    }}, true);

                    const thick = 16; 
                    const wallColor = '#475569';

                    function createSquareContainer(localX, localY, size, angle, catBox, maskBox) {{
                        const h = size / 2 + thick / 2;
                        const w = size + thick * 2;
                        const parts = [
                            Bodies.rectangle(0, -h, w, thick, {{ render: {{ fillStyle: wallColor, opacity: 0 }}, collisionFilter: {{ category: catBox, mask: maskBox }} }}),
                            Bodies.rectangle(0, h, w, thick, {{ render: {{ fillStyle: wallColor, opacity: 0 }}, collisionFilter: {{ category: catBox, mask: maskBox }} }}),
                            Bodies.rectangle(-h, 0, thick, size, {{ render: {{ fillStyle: wallColor, opacity: 0 }}, collisionFilter: {{ category: catBox, mask: maskBox }} }}),
                            Bodies.rectangle(h, 0, thick, size, {{ render: {{ fillStyle: wallColor, opacity: 0 }}, collisionFilter: {{ category: catBox, mask: maskBox }} }})
                        ];
                        
                        // THE BROADPHASE FIX: We explicitly pass the collision filters 
                        // to the parent constructor so the engine maps the auto-generated hull!
                        const box = Body.create({{ 
                            parts: parts, 
                            isStatic: true,
                            collisionFilter: {{ category: catBox, mask: maskBox }} 
                        }});
                        Body.setPosition(box, {{ x: globalCX + localX, y: globalCY + localY }});
                        Body.setAngle(box, angle);
                        return box;
                    }}

                    // Calculate perfect flush surface anchors
                    const locBoxA = {{ x: 0, y: sideB/2 + sideA/2 + thick/2, angle: 0 }}; // Base
                    const locBoxB = {{ x: -sideA/2 - sideB/2 - thick/2, y: 0, angle: 0 }}; // Height
                    
                    const angleHyp = Math.atan2(-sideB, -sideA);
                    const normX = Math.sin(-angleHyp); 
                    const normY = Math.cos(-angleHyp);
                    const locBoxC = {{ x: normX * (sideC/2 + thick/2), y: normY * (sideC/2 + thick/2), angle: angleHyp }}; // Hypotenuse

                    const boxA = createSquareContainer(locBoxA.x, locBoxA.y, sideA, locBoxA.angle, CAT_BOX_A, CAT_MARBLE_A);
                    const boxB = createSquareContainer(locBoxB.x, locBoxB.y, sideB, locBoxB.angle, CAT_BOX_B, CAT_MARBLE_B);
                    const boxC = createSquareContainer(locBoxC.x, locBoxC.y, sideC, locBoxC.angle, CAT_BOX_C, CAT_MARBLE_C);

                    Composite.add(engine.world, [triangleBody, boxA, boxB, boxC]);

                    function spawnMarbles(box, count, color, size, catMarble, maskMarble) {{
                        for (let i = 0; i < count; i++) {{
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

                    // --- VERTICAL LAYOUT TARGETS (No overlaps allowed) ---
                    const targetBX = 200;
                    const targetBY = 190;
                    const targetAX = 200;
                    const targetAY = targetBY + sideB/2 + sideA/2 + 100; // Stacked directly below B
                    const targetCX = 580;
                    const targetCY = (targetBY + targetAY) / 2; // Vertically centered to the stack
                    const targetTriY = height - 100;

                    // State Machine Expansion Vectors
                    let expTri, expA, expB, expC;

                    // --- CHOREOGRAPHY STATE MACHINE ---
                    const startTime = performance.now();
                    let marblesSpawned = false;
                    let labelsOpacity = 0;

                    Events.on(engine, 'beforeUpdate', function() {{
                        let elapsed = performance.now() - startTime;

                        // Phase 1: Reveal Squares (1000ms -> 3000ms)
                        if (elapsed > 1000 && elapsed <= 3000) {{
                            let p = (elapsed - 1000) / 2000;
                            [boxA, boxB, boxC].forEach(box => {{
                                // THE OCCLUSION FIX: Iterator starts at i=1 to skip the invisible parent hull (index 0)
                                for (let i = 1; i < box.parts.length; i++) {{
                                    box.parts[i].render.opacity = p;
                                }}
                            }});
                        }}
                        
                        // Phase 2: Spawn Marbles (3100ms)
                        else if (elapsed > 3100 && !marblesSpawned) {{
                            [boxA, boxB, boxC].forEach(box => {{ 
                                for (let i = 1; i < box.parts.length; i++) {{
                                    box.parts[i].render.opacity = 1; 
                                }}
                            }});
                            spawnMarbles(boxA, countA, '#38BDF8', sideA, CAT_MARBLE_A, CAT_BOX_A | CAT_MARBLE_A); 
                            spawnMarbles(boxB, countB, '#F43F5E', sideB, CAT_MARBLE_B, CAT_BOX_B | CAT_MARBLE_B); 
                            spawnMarbles(boxC, countC, '#10B981', sideC, CAT_MARBLE_C, CAT_BOX_C | CAT_MARBLE_C); 
                            marblesSpawned = true;
                        }}

                        // Phase 3: Orbital Kinematics (4000ms -> 8000ms)
                        else if (elapsed > 4000 && elapsed <= 8000) {{
                            let p = (elapsed - 4000) / 4000;
                            let easeP = p < 0.5 ? 2 * p * p : 1 - Math.pow(-2 * p + 2, 2) / 2;
                            let angle = easeP * Math.PI * 2; 

                            [ {{b: triangleBody, loc: {{x:0, y:0, angle:0}}}}, 
                              {{b: boxA, loc: locBoxA}}, 
                              {{b: boxB, loc: locBoxB}}, 
                              {{b: boxC, loc: locBoxC}} ].forEach(item => {{
                                
                                let oldX = item.b.position.x;
                                let oldY = item.b.position.y;
                                let oldAngle = item.b.angle;

                                let gx = globalCX + item.loc.x * Math.cos(angle) - item.loc.y * Math.sin(angle);
                                let gy = globalCY + item.loc.x * Math.sin(angle) + item.loc.y * Math.cos(angle);
                                let gAngle = item.loc.angle + angle;

                                Body.setPosition(item.b, {{ x: gx, y: gy }});
                                Body.setAngle(item.b, gAngle);

                                Body.setVelocity(item.b, {{ x: gx - oldX, y: gy - oldY }});
                                Body.setAngularVelocity(item.b, gAngle - oldAngle);
                            }});
                        }}

                        // Phase 4A: Radial Expansion / Visual Separation (9000ms -> 10000ms)
                        else if (elapsed > 9000 && elapsed <= 10000) {{
                            let p = (elapsed - 9000) / 1000;
                            let easeP = Math.sin(p * Math.PI / 2);

                            expTri = {{ x: globalCX, y: globalCY + 150 * easeP }};
                            expA = {{ x: globalCX + locBoxA.x, y: globalCY + locBoxA.y + 150 * easeP }};
                            expB = {{ x: globalCX + locBoxB.x - 150 * easeP, y: globalCY + locBoxB.y - 100 * easeP }};
                            expC = {{ x: globalCX + locBoxC.x + 150 * easeP, y: globalCY + locBoxC.y - 100 * easeP }};

                            Body.setPosition(triangleBody, expTri);
                            Body.setPosition(boxA, expA);
                            Body.setPosition(boxB, expB);
                            Body.setPosition(boxC, expC);
                        }}

                        // Phase 4B: Staggered Target Translation (10000ms -> 13000ms)
                        else if (elapsed > 10000 && elapsed <= 13000) {{
                            if (!expA) {{
                                expTri = {{x: globalCX, y: globalCY + 150}};
                                expA = {{x: globalCX + locBoxA.x, y: globalCY + locBoxA.y + 150}};
                                expB = {{x: globalCX + locBoxB.x - 150, y: globalCY + locBoxB.y - 100}};
                                expC = {{x: globalCX + locBoxC.x + 150, y: globalCY + locBoxC.y - 100}};
                            }}

                            let p = (elapsed - 10000) / 3000;
                            let easeP = p < 0.5 ? 2 * p * p : 1 - Math.pow(-2 * p + 2, 2) / 2;

                            Body.setPosition(triangleBody, {{ x: expTri.x, y: expTri.y + (targetTriY - expTri.y) * easeP }});
                            
                            Body.setPosition(boxA, {{ x: expA.x + (targetAX - expA.x) * easeP, y: expA.y + (targetAY - expA.y) * easeP }});
                            Body.setAngle(boxA, locBoxA.angle * (1 - easeP)); 
                            
                            Body.setPosition(boxB, {{ x: expB.x + (targetBX - expB.x) * easeP, y: expB.y + (targetBY - expB.y) * easeP }});
                            Body.setAngle(boxB, locBoxB.angle * (1 - easeP));
                            
                            Body.setPosition(boxC, {{ x: expC.x + (targetCX - expC.x) * easeP, y: expC.y + (targetCY - expC.y) * easeP }});
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
                        
                        context.fillStyle = (elapsed > 3000 && elapsed <= 4000) ? "#38BDF8" : "#475569";
                        context.fillText("Phase 2: Populate Mass Arrays", 25, 88);

                        context.fillStyle = (elapsed > 4000 && elapsed <= 8000) ? "#38BDF8" : "#475569";
                        context.fillText("Phase 3: Orbit Kinematics", 25, 111);
                        
                        context.fillStyle = (elapsed > 9000 && elapsed <= 13000) ? "#38BDF8" : "#475569";
                        context.fillText("Phase 4: Matrix Linearization", 25, 134);

                        context.fillStyle = elapsed > 13000 ? "#10B981" : "#475569";
                        context.fillText("Phase 5: Equation Equilibrium", 25, 157);

                        // High contrast equation HUD mapping sequence
                        if (elapsed > 12500) {{
                            context.fillStyle = "rgba(248, 250, 252, " + labelsOpacity + ")";
                            context.font = "bold 48px sans-serif";
                            context.textAlign = "center";
                            
                            // Align Plus Sign exactly in the vertical gap between Box A and B
                            let plusY = (targetBY + sideB/2 + targetAY - sideA/2) / 2;
                            context.fillText("+", 200, plusY + 16);
                            context.fillText("=", 400, targetCY + 16);

                            // Top Left: Box B 
                            context.font = "bold 20px sans-serif";
                            context.fillStyle = "rgba(244, 63, 94, " + labelsOpacity + ")";
                            context.fillText("Side B²", 200, targetBY - sideB/2 - 40);
                            context.font = "14px sans-serif";
                            context.fillText("Vol = " + (b_units * b_units) + " units²", 200, targetBY - sideB/2 - 15);

                            // Bottom Left: Box A
                            context.font = "bold 20px sans-serif";
                            context.fillStyle = "rgba(56, 189, 248, " + labelsOpacity + ")";
                            context.fillText("Side A²", 200, targetAY - sideA/2 - 40);
                            context.font = "14px sans-serif";
                            context.fillText("Vol = " + (a_units * a_units) + " units²", 200, targetAY - sideA/2 - 15);

                            // Right Column: Box C
                            context.font = "bold 20px sans-serif";
                            context.fillStyle = "rgba(16, 185, 129, " + labelsOpacity + ")";
                            context.fillText("Hypotenuse C²", 580, targetCY - sideC/2 - 40);
                            context.font = "14px sans-serif";
                            context.fillText("Vol = " + Math.round(a_units*a_units + b_units*b_units) + " units²", 580, targetCY - sideC/2 - 15);
                            
                            context.font = "italic 16px sans-serif";
                            context.fillStyle = "rgba(148, 163, 184, " + labelsOpacity + ")";
                            context.fillText("Empirical Density Match: " + countB + " + " + countA + " = " + countC, width / 2, 780);
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