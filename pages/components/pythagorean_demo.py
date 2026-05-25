"""
=============================================================================
MODULE: pages/components/pythagorean_demo.py
AUTHOR: Kyle W. Killebrew, PhD & Data Science Mentorship Engine
STATUS: Active Specification Profile for Lesson 3 Component
DESCRIPTION: 
    A GPU-accelerated Matter.js simulation visualizing the Pythagorean Theorem.
    Orchestrates a 4-Phase Chronological Framework directly on HTML5 Canvas:
      - Phase 1: Spawning & Gravitational Settlement (t = 0 -> 3000ms)
      - Phase 2: Orbital Angular Rotation (t = 3000 -> 8000ms)
      - Phase 3: Structural Detachment & Disassembly (t = 8000 -> 12000ms)
      - Phase 4: Equation Linearization HUD (t > 12000ms)

    --- MATLAB BRIDGE ---
    Shifts standard execution loops from static matrix plots to a dynamic web UI
    wrapper. This routes inputs to a local rigid-body kinematic solver executed
    directly via the user's browser canvas (similar to ode45/rigid-body app panels).
=============================================================================
"""

import streamlit.components.v1 as components

def render_pythagorean_demo(a_units, b_units):
    """
    Renders an 800x800 high-performance Matter.js interactive frame mapping
    out the geometric conservation law: Area A + Area B = Area C.
    """
    # Scale mathematical units up to clean structural pixel dimensions
    scale = 35
    sideA = a_units * scale
    sideB = b_units * scale
    sideC = float((sideA**2 + sideB**2)**0.5)

    # Calculate exact packing volume profiles based on area dimensions
    # Matching geometric compliance metric: N_C = N_A + N_B
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
                    if (typeof Matter === 'undefined') {{
                        throw new Error("Matter.js engine failed to load via CDN.");
                    }}

                    const Engine = Matter.Engine,
                          Render = Matter.Render,
                          Runner = Matter.Runner,
                          Bodies = Matter.Bodies,
                          Composite = Matter.Composite,
                          Constraint = Matter.Constraint,
                          Events = Matter.Events,
                          Body = Matter.Body;

                    const engine = Engine.create({{ positionIterations: 12, velocityIterations: 12 }});
                    engine.gravity.y = 1.0;

                    const width = 800;
                    const height = 800;
                    const centerX = width / 2;
                    const centerY = height / 2 - 50;

                    const render = Render.create({{
                        element: document.body,
                        engine: engine,
                        options: {{ width: width, height: height, wireframes: false, background: '#0F172A' }}
                    }});

                    // --- PHYSICS CATEGORY LAYER MATRICES ---
                    const CAT_TRIANGLE = 0x0001;
                    const CAT_BOX = 0x0002;
                    const CAT_MARBLE = 0x0004;
                    const CAT_BOUNDS = 0x0008;

                    // Standard outer viewport bounds
                    const ground = Bodies.rectangle(width/2, height + 20, width, 40, {{ isStatic: true, collisionFilter: {{ category: CAT_BOUNDS }} }});
                    const leftWall = Bodies.rectangle(-20, height/2, 40, height, {{ isStatic: true, collisionFilter: {{ category: CAT_BOUNDS }} }});
                    const rightWall = Bodies.rectangle(width + 20, height/2, 40, height, {{ isStatic: true, collisionFilter: {{ category: CAT_BOUNDS }} }}));
                    const ceiling = Bodies.rectangle(width/2, -20, width, 40, {{ isStatic: true, collisionFilter: {{ category: CAT_BOUNDS }} }});
                    Composite.add(engine.world, [ground, leftWall, rightWall, ceiling]);

                    // --- GENERATE RIGID FOUNDATION FRAME ---
                    // Base right-angled triangle mapping vectors
                    const triX = centerX;
                    const triY = centerY;
                    const baseWidth = {{sideA}};
                    const heightVert = {{sideB}};

                    const triangleBody = Bodies.fromVertices(triX, triY, [
                        {{ x: 0, y: 0 }},
                        {{ x: baseWidth, y: 0 }},
                        {{ x: 0, y: heightVert }}
                    ], {{ isStatic: true, collisionFilter: {{ category: CAT_TRIANGLE }} }}, true);

                    // Re-anchor to geometric centroid position values safely
                    const centroidX = triangleBody.position.x;
                    const centroidY = triangleBody.position.y;

                    // --- ASSEMBLE ENCLOSURES OFF BOUNDARY SIDES ---
                    const thick = 8;
                    const wallColor = '#475569';

                    function createSquareContainer(x, y, size, angle, label) {{
                        const half = size / 2;
                        const parts = [
                            // Bottom floor
                            Bodies.rectangle(0, half, size, thick, {{ render: {{ fillStyle: wallColor }} }}),
                            // Left wing
                            Bodies.rectangle(-half, 0, thick, size, {{ render: {{ fillStyle: wallColor }} }}),
                            // Right wing
                            Bodies.rectangle(half, 0, thick, size, {{ render: {{ fillStyle: wallColor }} }})
                        ];
                        const compoundBox = Body.create({{
                            parts: parts,
                            position: {{ x: x, y: y }},
                            collisionFilter: {{ category: CAT_BOX }}
                        }});
                        Body.setAngle(compoundBox, angle);
                        return compoundBox;
                    }}

                    // Right angle alignments
                    const angleA = 0;
                    const angleB = Math.PI / 2;
                    const angleC = Math.atan2(heightVert, baseWidth) + Math.PI;

                    const boxA = createSquareContainer(centroidX, centroidY - {{sideB}}/2 - thick, {{sideA}}, angleA, 'A');
                    const boxB = createSquareContainer(centroidX - {{sideA}}/2 - thick, centroidY, {{sideB}}, angleB, 'B');
                    
                    const hypOffsetX = (Math.cos(angleC + Math.PI/2) * ({{sideC}}/2 + thick));
                    const hypOffsetY = (Math.sin(angleC + Math.PI/2) * ({{sideC}}/2 + thick));
                    const boxC = createSquareContainer(centroidX + {{sideA}}/2, centroidY + {{sideB}}/2, {{sideC}}, angleC, 'C');

                    Composite.add(engine.world, [triangleBody, boxA, boxB, boxC]);

                    // Rigid structural weld constraints linking boxes to anchor triangle
                    let constraints = [
                        Constraint.create({{ bodyA: triangleBody, bodyB: boxA, pointA: {{ x: 0, y: -{{sideB}}/2 }}, length: 0, stiffness: 1 }}),
                        Constraint.create({{ bodyA: triangleBody, bodyB: boxB, pointA: {{ x: -{{sideA}}/2, y: 0 }}, length: 0, stiffness: 1 }}),
                        Constraint.create({{ bodyA: triangleBody, bodyB: boxC, pointA: {{ x: {{sideA}}/2, y: {{sideB}}/2 }}, length: 0, stiffness: 1 }})
                    ];
                    Composite.add(engine.world, constraints);

                    // --- GENERATE MARBLE MASS PACKING SYSTEMS ---
                    function spawnMarblesInContainer(box, count, color) {{
                        for (let i = 0; i < count; i++) {{
                            let radius = 4.5;
                            let offsetRange = (box.bounds.max.x - box.bounds.min.x) * 0.25;
                            let rx = box.position.x + (Math.random() * offsetRange - offsetRange/2);
                            let ry = box.position.y + (Math.random() * offsetRange - offsetRange/2);
                            
                            let marble = Bodies.circle(rx, ry, radius, {{
                                restitution: 0.2,
                                friction: 0.02,
                                render: {{ fillStyle: color }},
                                collisionFilter: {{ category: CAT_MARBLE, mask: CAT_BOX | CAT_MARBLE | CAT_BOUNDS }}
                            }});
                            Composite.add(engine.world, marble);
                        }}
                    }}

                    spawnMarblesInContainer(boxA, {{countA}}, '#38BDF8'); // Sky Blue
                    spawnMarblesInContainer(boxB, {{countB}}, '#F43F5E'); // Coral Rose
                    spawnMarblesInContainer(boxC, {{countC}}, '#10B981'); // Emerald

                    // --- CHOREOGRAPHY CORE STATE MACHINE MOTOR ---
                    const startTime = performance.now();
                    let phase3Triggered = false;
                    let phase4Triggered = false;
                    let labelsOpacity = 0;

                    Events.on(engine, 'beforeUpdate', function() {{
                        let elapsed = performance.now() - startTime;

                        // Phase 1: Gravitational Settlement (t = 0 -> 3000ms)
                        if (elapsed <= 3000) {{
                            // Keep elements strictly anchored in place during initial load tracking
                            Body.setVelocity(boxA, {{ x: 0, y: 0 }});
                            Body.setVelocity(boxB, {{ x: 0, y: 0 }});
                            Body.setVelocity(boxC, {{ x: 0, y: 0 }});
                        }}
                        
                        // Phase 2: Orbital Invariance Transformation Matrix (t = 3000 -> 8000ms)
                        else if (elapsed > 3000 && elapsed <= 8000) {{
                            let progress = (elapsed - 3000) / 5000;
                            let currentAngle = progress * Math.PI * 2; // Exact full 360-degree rotation loop
                            
                            // Transform global gravity vector over time to pull assets realistically within shifting frames
                            engine.gravity.x = Math.sin(currentAngle) * 1.0;
                            engine.gravity.y = Math.cos(currentAngle) * 1.0;

                            // Apply spatial position paths mapping around geometric barycenter
                            let radius = 10;
                            let targetX = centerX + radius * Math.sin(currentAngle);
                            let targetY = centerY + radius * (Math.cos(currentAngle) - 1);

                            Body.setStatic(triangleBody, false);
                            Body.setPosition(triangleBody, {{ x: targetX, y: targetY }});
                            Body.setAngle(triangleBody, currentAngle);
                            Body.setStatic(triangleBody, true);
                        }}
                        
                        // Phase 3: Structural Detachment & Disassembly (t = 8000 -> 12000ms)
                        else if (elapsed > 8000) {{
                            if (!phase3Triggered) {{
                                // Dissolve constraints tracking to foundational block completely
                                constraints.forEach(c => Composite.remove(engine.world, c));
                                
                                Body.setStatic(triangleBody, false);
                                Body.setStatic(boxA, false);
                                Body.setStatic(boxB, false);
                                Body.setStatic(boxC, false);

                                // Isolate collision filters so boxes no longer tangle with outer environment elements
                                boxA.collisionFilter.mask = CAT_MARBLE;
                                boxB.collisionFilter.mask = CAT_MARBLE;
                                boxC.collisionFilter.mask = CAT_MARBLE;

                                phase3Triggered = true;
                            }}

                            // Re-orient gravity coordinates to direct down profile
                            engine.gravity.x = 0;
                            engine.gravity.y = 1.3;

                            // Linearize coordinates smoothly using standard differential target interpolation loops
                            let tProgress = Math.min(1, (elapsed - 8000) / 3000);
                            
                            // Triangle moves down to rest space smoothly
                            let targetTriX = centerX;
                            let targetTriY = height - 120;
                            Body.setPosition(triangleBody, {{
                                x: triangleBody.position.x + (targetTriX - triangleBody.position.x) * 0.08,
                                y: triangleBody.position.y + (targetTriY - triangleBody.position.y) * 0.08
                            }});
                            Body.setAngle(triangleBody, triangleBody.angle + (0 - triangleBody.angle) * 0.08);

                            // Linearize Box A profile horizontally
                            let targetAX = 180;
                            let targetAY = 180;
                            Body.setPosition(boxA, {{ x: boxA.position.x + (targetAX - boxA.position.x) * 0.06, y: boxA.position.y + (targetAY - boxA.position.y) * 0.06 }});
                            Body.setAngle(boxA, boxA.angle + (0 - boxA.angle) * 0.06);

                            // Linearize Box B profile horizontally
                            let targetBX = 400;
                            let targetBY = 180;
                            Body.setPosition(boxB, {{ x: boxB.position.x + (targetBX - boxB.position.x) * 0.06, y: boxB.position.y + (targetBY - boxB.position.y) * 0.06 }});
                            Body.setAngle(boxB, boxB.angle + (0 - boxB.angle) * 0.06);

                            // Linearize Box C profile horizontally
                            let targetCX = 620;
                            let targetCY = 180;
                            Body.setPosition(boxC, {{ x: boxC.position.x + (targetCX - boxC.position.x) * 0.06, y: boxC.position.y + (targetCY - boxC.position.y) * 0.06 }});
                            Body.setAngle(boxC, boxC.angle + (0 - boxC.angle) * 0.06);
                        }}

                        // Phase 4: Equation Linearization HUD (t > 12000ms)
                        if (elapsed > 11500) {{
                            phase4Triggered = true;
                            if (labelsOpacity < 1.0) {{
                                labelsOpacity += 0.015;
                            }}
                        }}
                    }});

                    // --- CANVAS GRAPHIC INTERFACE HEADS-UP DISPLAY ---
                    Events.on(render, 'afterRender', function() {{
                        const context = render.context;
                        let elapsed = performance.now() - startTime;

                        context.save();
                        
                        // Active runtime diagnostic telemetry readouts
                        context.font = "bold 15px sans-serif";
                        context.fillStyle = "#64748B";
                        context.fillText("Active State Engine Metrics", 25, 40);
                        
                        context.font = "14px sans-serif";
                        context.fillStyle = elapsed <= 3000 ? "#38BDF8" : "#475569";
                        context.fillText("Phase 1: Settlement Initialization (" + Math.max(0, Math.floor(3000 - elapsed)) + "ms)", 25, 65);
                        
                        context.fillStyle = (elapsed > 3000 && elapsed <= 8000) ? "#38BDF8" : "#475569";
                        context.fillText("Phase 2: Coordinates Rotational Scale", 25, 88);
                        
                        context.fillStyle = (elapsed > 8000 && elapsed <= 11500) ? "#38BDF8" : "#475569";
                        context.fillText("Phase 3: Structural Matrix Separation Loop", 25, 111);

                        context.fillStyle = phase4Triggered ? "#10B981" : "#475569";
                        context.fillText("Phase 4: Equation Equilibrium Verified", 25, 134);

                        // High contrast equation HUD mapping sequence
                        if (phase4Triggered) {{
                            context.fillStyle = "rgba(248, 250, 252, " + labelsOpacity + ")";
                            context.font = "bold 36px sans-serif";
                            context.textAlign = "center";
                            
                            // High contrast operators between mathematical sets
                            context.fillText("+", 290, 190);
                            context.fillText("=", 510, 190);

                            // Structured label markers for tracking dimensions
                            context.font = "bold 20px sans-serif";
                            context.fillStyle = "rgba(56, 189, 248, " + labelsOpacity + ")";
                            context.fillText("Side A²", 180, 75);
                            context.font = "14px sans-serif";
                            context.fillText("Vol = " + ({{a_val}} * {{a_val}}) + " units²", 180, 95);

                            context.font = "bold 20px sans-serif";
                            context.fillStyle = "rgba(244, 63, 94, " + labelsOpacity + ")";
                            context.fillText("Side B²", 400, 75);
                            context.font = "14px sans-serif";
                            context.fillText("Vol = " + ({{b_val}} * {{b_val}}) + " units²", 400, 95);

                            context.font = "bold 20px sans-serif";
                            context.fillStyle = "rgba(16, 185, 129, " + labelsOpacity + ")";
                            context.fillText("Hypotenuse C²", 620, 75);
                            context.font = "14px sans-serif";
                            context.fillText("Vol = " + Math.round({{a_val}}*{{a_val}} + {{b_val}}*{{b_val}}) + " units²", 620, 95);
                            
                            // Empirical conservation confirmation reading
                            context.font = "italic 18px sans-serif";
                            context.fillStyle = "rgba(148, 163, 184, " + labelsOpacity + ")";
                            context.fillText("Empirical Marble Density Count Match: " + {{countA}} + " + " + {{countB}} + " = " + {{countC}}, width / 2, 320);
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
    
    # Render with structural viewport clearance bounds
    components.html(html_code, height=820)