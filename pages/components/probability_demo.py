"""
=============================================================================
MODULE: pages/components/probability_demo.py
AUTHOR: Kyle W. Killebrew, PhD
DESCRIPTION: 
    Injects a Matter.js Galton Board (Plinko) simulation into Streamlit.
    Demonstrates the Central Limit Theorem and Normal Distribution.

    MATLAB Analogy: This replaces standard histogram generation (histogram(X)) 
    with a live rigid-body differential equation solver (ode45) rendered 
    in real-time via HTML5 Canvas.
=============================================================================
"""

import streamlit.components.v1 as components

def render_probability_demo(sample_count=200):
    """
    Renders the Matter.js Plinko Board. 
    Accepts `sample_count` to dictate how many bodies the state machine spawns.
    """
    
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/matter-js/0.19.0/matter.min.js"></script>
        <style>
            body {{ margin: 0; padding: 0; overflow: hidden; background-color: #0F172A; font-family: sans-serif; }}
            canvas {{ display: block; margin: 0 auto; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }}
            #debug-console {{ color: #F87171; padding: 20px; font-size: 14px; }}
        </style>
    </head>
    <body>
        <div id="debug-console"></div>
        
        <script>
            // Wait for the iframe DOM to completely construct before firing the engine
            window.addEventListener('DOMContentLoaded', function() {{
                try {{
                    // 1. FAILSAFE CHECK
                    if (typeof Matter === 'undefined') {{
                        throw new Error("Matter.js library failed to load. A firewall or AdBlocker might be blocking the CDN.");
                    }}

                    // 2. ENGINE & RENDER SETUP
                    const Engine = Matter.Engine,
                          Render = Matter.Render,
                          Runner = Matter.Runner,
                          Bodies = Matter.Bodies,
                          Composite = Matter.Composite,
                          Events = Matter.Events;

                    // Initialize engine with higher iterations to prevent tunneling
                    const engine = Engine.create({{
                        positionIterations: 16,
                        velocityIterations: 16
                    }});
                    
                    // Safely apply gravity
                    if (engine.gravity) {{
                        engine.gravity.y = 1.2;
                    }}

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

                    // 3. BITMASK COLLISION CATEGORIES
                    const CAT_WALL = 0x0001;
                    const CAT_PEG = 0x0002;
                    const CAT_MARBLE = 0x0004;

                    // 4. ENVIRONMENT GENERATION
                    const bodiesToLoad = [];
                    
                    // Top Funnel
                    bodiesToLoad.push(Bodies.rectangle(250, 50, 400, 20, {{ 
                        isStatic: true, angle: Math.PI / 6, 
                        render: {{ fillStyle: '#334155' }},
                        collisionFilter: {{ category: CAT_WALL }}
                    }}));
                    bodiesToLoad.push(Bodies.rectangle(550, 50, 400, 20, {{ 
                        isStatic: true, angle: -Math.PI / 6, 
                        render: {{ fillStyle: '#334155' }},
                        collisionFilter: {{ category: CAT_WALL }}
                    }}));

                    // The Quincunx (Peg Array)
                    const rows = 9;
                    const pegSpacing = 45;
                    for (let r = 0; r < rows; r++) {{
                        for (let c = 0; c <= r; c++) {{
                            let px = (width / 2) + (c - r / 2) * pegSpacing;
                            let py = 150 + r * pegSpacing;
                            bodiesToLoad.push(Bodies.circle(px, py, 4, {{
                                isStatic: true,
                                render: {{ fillStyle: '#94A3B8' }},
                                collisionFilter: {{ category: CAT_PEG, mask: CAT_MARBLE }}
                            }}));
                        }}
                    }}

                    // The Bins
                    const numBins = 15;
                    const binWidth = width / numBins;
                    for (let i = 0; i <= numBins; i++) {{
                        bodiesToLoad.push(Bodies.rectangle(i * binWidth, height - 75, 4, 150, {{
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

                    // 5. THE STATE MACHINE (Marble Spawning)
                    let startTime = performance.now();
                    let marblesSpawned = 0;
                    const targetMarbles = {sample_count}; // Safely injected by Python
                    
                    Events.on(engine, 'beforeUpdate', function() {{
                        let timeNow = performance.now();
                        let elapsed = timeNow - startTime;
                        
                        if (marblesSpawned < targetMarbles && elapsed > 1000) {{
                            if (Math.floor(elapsed) % 50 < 15) {{
                                let spawnX = (width / 2) + (Math.random() * 10 - 5);
                                let marble = Bodies.circle(spawnX, 10, 6, {{
                                    restitution: 0.4, 
                                    friction: 0.001,
                                    render: {{ fillStyle: '#38BDF8' }},
                                    collisionFilter: {{ 
                                        category: CAT_MARBLE, 
                                        mask: CAT_WALL | CAT_PEG | CAT_MARBLE 
                                    }}
                                }});
                                Composite.add(engine.world, marble);
                                marblesSpawned++;
                            }}
                        }}
                    }});

                    // 6. CANVAS HUD OVERLAY
                    Events.on(render, 'afterRender', function() {{
                        const context = render.context;
                        
                        // Ghost Funnel (Bell Curve Overlay)
                        context.beginPath();
                        context.strokeStyle = "rgba(74, 222, 128, 0.4)";
                        context.lineWidth = 3;
                        context.setLineDash([5, 5]);
                        
                        for (let x = 0; x <= width; x += 10) {{
                            let z = (x - (width/2)) / 120;
                            let y = 520 - (300 * Math.exp(-0.5 * z * z)); 
                            if (x === 0) context.moveTo(x, y);
                            else context.lineTo(x, y);
                        }}
                        context.stroke();
                        context.setLineDash([]);
                        
                        // Text Elements (Converted to concat to avoid Python f-string collisions)
                        context.font = "16px sans-serif";
                        context.fillStyle = "#F8FAFC";
                        context.textAlign = "left";
                        context.fillText("Expected Distribution", 20, 30);
                        
                        context.fillStyle = "#38BDF8";
                        context.fillText("N = " + marblesSpawned + " / " + targetMarbles, 20, 55);
                    }});

                    // 7. EXECUTE
                    Render.run(render);
                    const runner = Runner.create();
                    Runner.run(runner, engine);

                }} catch (error) {{
                    // If ANYTHING fails, print it in big red text to the UI
                    document.getElementById('debug-console').innerHTML = "<strong>CRITICAL ENGINE FAILURE:</strong><br>" + error.message;
                }}
            }});
        </script>
    </body>
    </html>
    """
    
    components.html(html_code, height=620)