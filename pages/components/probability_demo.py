"""
=============================================================================
MODULE: pages/components/probability_demo.py
AUTHOR: Kyle W. Killebrew, PhD
DESCRIPTION: 
    A fully robust Matter.js simulation for the Probability Spoke.
    Features a Plinko board with collision masking, gate mechanics, 
    real-time Bell Curve HUD overlay, and comprehensive error handling.
=============================================================================
"""

import streamlit.components.v1 as components

def render_probability_demo(sample_count=200):
    """
    Renders the Matter.js Plinko Board. 
    This component uses a self-contained HTML5/JS lifecycle to ensure 
    the engine only executes after the DOM is fully loaded.
    """
    
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
            // 0. DOM Lifecycle Management
            window.addEventListener('DOMContentLoaded', function() {{
                try {{
                    // Dependency verification
                    if (typeof Matter === 'undefined') {{
                        throw new Error("Matter.js library failed to load via CDN.");
                    }}

                    // 1. ENGINE & RENDER SETUP
                    const Engine = Matter.Engine,
                          Render = Matter.Render,
                          Runner = Matter.Runner,
                          Bodies = Matter.Bodies,
                          Composite = Matter.Composite,
                          Events = Matter.Events,
                          Body = Matter.Body;

                    // Initialize physics engine with high iteration counts to prevent tunneling
                    const engine = Engine.create({{ 
                        positionIterations: 16, 
                        velocityIterations: 16 
                    }});
                    
                    // Standard Earth gravity for natural drop behavior
                    engine.gravity.y = 1.2;

                    const width = 800;
                    const height = 600;

                    const render = Render.create({{
                        element: document.body,
                        engine: engine,
                        options: {{ 
                            width: width, 
                            height: height, 
                            wireframes: false, 
                            background: '#0F172A' 
                        }}
                    }});

                    // 2. BITMASK COLLISION CATEGORIES (Ensures efficient physics calculation)
                    const CAT_WALL = 0x0001;
                    const CAT_PEG = 0x0002;
                    const CAT_MARBLE = 0x0004;

                    // 3. ENVIRONMENT GENERATION
                    const bodiesToLoad = [];
                    
                    // Funnel Gates (Slimmed lines: Height 4)
                    const doorL = Bodies.rectangle(250, 50, 400, 4, {{ 
                        isStatic: true, angle: Math.PI / 6, render: {{ fillStyle: '#94A3B8' }},
                        collisionFilter: {{ category: CAT_WALL }}
                    }});
                    const doorR = Bodies.rectangle(550, 50, 400, 4, {{ 
                        isStatic: true, angle: -Math.PI / 6, render: {{ fillStyle: '#94A3B8' }},
                        collisionFilter: {{ category: CAT_WALL }}
                    }});
                    bodiesToLoad.push(doorL, doorR);

                    // Quincunx Peg Array
                    const rows = 9;
                    const pegSpacing = 45;
                    for (let r = 0; r < rows; r++) {{
                        for (let c = 0; c <= r; c++) {{
                            let px = (width / 2) + (c - r / 2) * pegSpacing;
                            let py = 150 + r * pegSpacing;
                            bodiesToLoad.push(Bodies.circle(px, py, 4, {{
                                isStatic: true,
                                render: {{ fillStyle: '#475569' }},
                                collisionFilter: {{ category: CAT_PEG, mask: CAT_MARBLE }}
                            }}));
                        }}
                    }}

                    // Bins (Slimmed lines: Width 2)
                    const numBins = 15;
                    const binWidth = width / numBins;
                    for (let i = 0; i <= numBins; i++) {{
                        bodiesToLoad.push(Bodies.rectangle(i * binWidth, height - 75, 2, 150, {{
                            isStatic: true,
                            render: {{ fillStyle: '#475569' }},
                            collisionFilter: {{ category: CAT_WALL }}
                        }}));
                    }}
                    
                    // Floor
                    bodiesToLoad.push(Bodies.rectangle(width/2, height + 10, width, 40, {{ 
                        isStatic: true,
                        collisionFilter: {{ category: CAT_WALL }}
                    }}));

                    Composite.add(engine.world, bodiesToLoad);

                    // 4. THE STATE MACHINE (Choreography)
                    let startTime = performance.now();
                    let marblesSpawned = 0;
                    let gateOpened = false;
                    const targetMarbles = {sample_count}; // Passed from Python
                    
                    Events.on(engine, 'beforeUpdate', function() {{
                        let elapsed = performance.now() - startTime;
                        
                        // GATE LOGIC: Open hatch at exactly 2 seconds
                        if (elapsed > 2000 && !gateOpened) {{
                            gateOpened = true;
                            // Teleport the gate doors off-screen
                            Body.setPosition(doorL, {{ x: -200, y: 50 }});
                            Body.setPosition(doorR, {{ x: width + 200, y: 50 }});
                        }}

                        // SPAWN LOGIC: Drop marbles only after gate opens, staggered
                        if (gateOpened && marblesSpawned < targetMarbles && Math.floor(elapsed) % 50 < 15) {{
                            let spawnX = (width / 2) + (Math.random() * 20 - 10);
                            let marble = Bodies.circle(spawnX, 10, 6, {{
                                restitution: 0.4, 
                                friction: 0.001,
                                render: {{ fillStyle: '#38BDF8' }},
                                collisionFilter: {{ category: CAT_MARBLE, mask: CAT_WALL | CAT_PEG | CAT_MARBLE }}
                            }});
                            Composite.add(engine.world, marble);
                            marblesSpawned++;
                        }}
                    }});

                    // 5. CANVAS HUD & OVERLAYS
                    Events.on(render, 'afterRender', function() {{
                        const context = render.context;
                        
                        // Draw Ghost Bell Curve Overlay
                        context.beginPath();
                        context.strokeStyle = "rgba(74, 222, 128, 0.4)";
                        context.lineWidth = 2;
                        context.setLineDash([5, 5]);
                        for (let x = 0; x <= width; x += 10) {{
                            let z = (x - (width/2)) / 120;
                            let y = 520 - (300 * Math.exp(-0.5 * z * z)); 
                            if (x === 0) context.moveTo(x, y);
                            else context.lineTo(x, y);
                        }}
                        context.stroke();
                        context.setLineDash([]);
                        
                        // HUD Text
                        context.font = "16px sans-serif";
                        context.fillStyle = "#F8FAFC";
                        context.textAlign = "left";
                        context.fillText("Expected Distribution", 20, 30);
                        context.fillStyle = "#38BDF8";
                        context.fillText("N = " + marblesSpawned + " / " + targetMarbles, 20, 55);
                    }});

                    // 6. EXECUTION
                    Render.run(render);
                    const runner = Runner.create();
                    Runner.run(runner, engine);

                }} catch (error) {{
                    // Fallback for JS runtime errors
                    document.getElementById('debug-console').innerHTML = "<strong>CRITICAL FAILURE:</strong> " + error.message;
                }}
            }});
        </script>
    </body>
    </html>
    """
    
    components.html(html_code, height=620)