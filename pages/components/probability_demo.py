"""
=============================================================================
MODULE: pages/components/probability_demo.py
AUTHOR: Kyle W. Killebrew, PhD
DESCRIPTION: 
    A structurally refined Matter.js Galton Board.
    Fixes mesh-grid bias by perfectly aligning the peg array with bin dividers.
    Implements a pooling "hopper" and sliding gate mechanics.
=============================================================================
"""

import streamlit.components.v1 as components

def render_probability_demo(sample_count=200):
    """
    Renders the expanded 800x800 Matter.js Plinko Board.
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
            window.addEventListener('DOMContentLoaded', function() {{
                try {{
                    if (typeof Matter === 'undefined') {{
                        throw new Error("Matter.js library failed to load via CDN.");
                    }}

                    const Engine = Matter.Engine,
                          Render = Matter.Render,
                          Runner = Matter.Runner,
                          Bodies = Matter.Bodies,
                          Composite = Matter.Composite,
                          Events = Matter.Events,
                          Body = Matter.Body;

                    const engine = Engine.create({{ positionIterations: 16, velocityIterations: 16 }});
                    engine.gravity.y = 1.2;

                    // Expanded Canvas to hold 29 rows of pegs + 30 taller bins
                    const width = 800;
                    const height = 800;

                    const render = Render.create({{
                        element: document.body,
                        engine: engine,
                        options: {{ width: width, height: height, wireframes: false, background: '#0F172A' }}
                    }});

                    const CAT_WALL = 0x0001;
                    const CAT_PEG = 0x0002;
                    const CAT_MARBLE = 0x0004;

                    const bodiesToLoad = [];
                    
                    // --- 1. INVISIBLE BOUNDARY WALLS ---
                    // Prevents marbles from bouncing out of the screen
                    bodiesToLoad.push(Bodies.rectangle(0, height/2, 10, height, {{ isStatic: true, render: {{ visible: false }}, collisionFilter: {{ category: CAT_WALL }} }}));
                    bodiesToLoad.push(Bodies.rectangle(width, height/2, 10, height, {{ isStatic: true, render: {{ visible: false }}, collisionFilter: {{ category: CAT_WALL }} }}));

                    // --- 2. THE HOPPER (V-Funnel) ---
                    // Angled to form a perfect point at X=400, Y=140
                    const doorL = Bodies.rectangle(268, 65, 300, 4, {{ 
                        isStatic: true, angle: Math.PI / 6, render: {{ fillStyle: '#94A3B8' }}, collisionFilter: {{ category: CAT_WALL }}
                    }});
                    const doorR = Bodies.rectangle(532, 65, 300, 4, {{ 
                        isStatic: true, angle: -Math.PI / 6, render: {{ fillStyle: '#94A3B8' }}, collisionFilter: {{ category: CAT_WALL }}
                    }});
                    bodiesToLoad.push(doorL, doorR);

                    // --- 3. DYNAMIC BINS (Double the bins, 30% taller) ---
                    const numBins = 30;
                    const binWidth = width / numBins; // ~26.66px
                    const binHeight = 200;
                    
                    // Internal dividers only (edges handled by invisible walls)
                    for (let i = 1; i < numBins; i++) {{
                        bodiesToLoad.push(Bodies.rectangle(i * binWidth, height - (binHeight/2), 2, binHeight, {{
                            isStatic: true, render: {{ fillStyle: '#475569' }}, collisionFilter: {{ category: CAT_WALL }}
                        }}));
                    }}
                    // Solid Floor
                    bodiesToLoad.push(Bodies.rectangle(width/2, height + 10, width, 40, {{ isStatic: true, collisionFilter: {{ category: CAT_WALL }} }}));

                    // --- 4. PERFECTLY ALIGNED QUINCUNX (Triangle Peg Array) ---
                    // 29 rows ensures the bottom row has 29 pegs, aligning EXACTLY with the 29 bin dividers
                    const rows = 29;
                    for (let r = 0; r < rows; r++) {{
                        for (let c = 0; c <= r; c++) {{
                            // Math magic: ties horizontal peg spacing explicitly to binWidth
                            let px = (width / 2) + (c - r / 2) * binWidth;
                            // Start below hopper (Y=160), space down by 15px. Bottom row hits Y=580 (just above bins!)
                            let py = 160 + r * 15; 
                            
                            bodiesToLoad.push(Bodies.circle(px, py, 3, {{
                                isStatic: true, render: {{ fillStyle: '#64748B' }},
                                collisionFilter: {{ category: CAT_PEG, mask: CAT_MARBLE }}
                            }}));
                        }}
                    }}

                    Composite.add(engine.world, bodiesToLoad);

                    // --- 5. CHOREOGRAPHY STATE MACHINE ---
                    let startTime = performance.now();
                    let marblesSpawned = 0;
                    let gateOffset = 0; // Tracks how far the doors have slid
                    const targetMarbles = {sample_count};
                    
                    Events.on(engine, 'beforeUpdate', function() {{
                        let elapsed = performance.now() - startTime;
                        
                        // PHASE 1: Spawning Pool (0 to 3 seconds)
                        // Uses a dynamic catch-up loop so frame drops don't result in missing marbles
                        let expectedMarbles = Math.min(targetMarbles, Math.floor((elapsed / 3000) * targetMarbles));
                        
                        while(marblesSpawned < expectedMarbles) {{
                            // Spawn spread out across the top of the hopper
                            let spawnX = (width / 2) + (Math.random() * 80 - 40);
                            let marble = Bodies.circle(spawnX, -10, 5, {{ // Shrunk radius to 5 to prevent jamming
                                restitution: 0.5, // slightly bouncier
                                friction: 0.001,
                                render: {{ fillStyle: '#38BDF8' }},
                                collisionFilter: {{ category: CAT_MARBLE, mask: CAT_WALL | CAT_PEG | CAT_MARBLE }}
                            }});
                            Composite.add(engine.world, marble);
                            marblesSpawned++;
                        }}

                        // PHASE 2: Sliding Gate (Opens at 3.5 seconds)
                        if (elapsed > 3500 && gateOffset < 20) {{
                            gateOffset += 0.3; // Sliding velocity
                            // Translates the rectangles horizontally apart
                            Body.setPosition(doorL, {{ x: 268 - gateOffset, y: 65 }});
                            Body.setPosition(doorR, {{ x: 532 + gateOffset, y: 65 }});
                        }}
                    }});

                    // --- 6. CANVAS HUD & BELL CURVE OVERLAY ---
                    Events.on(render, 'afterRender', function() {{
                        const context = render.context;
                        
                        context.beginPath();
                        context.strokeStyle = "rgba(74, 222, 128, 0.4)";
                        context.lineWidth = 2;
                        context.setLineDash([5, 5]);
                        
                        // The Mathematical Expected Distribution Curve
                        // Adjusted StdDev (sigma) and Amplitude to perfectly match the 30-bin spread
                        for (let x = 0; x <= width; x += 5) {{
                            let z = (x - 400) / 72; // Sigma perfectly mapped to physical variance
                            let y = 780 - (350 * Math.exp(-0.5 * z * z)); 
                            if (x === 0) context.moveTo(x, y);
                            else context.lineTo(x, y);
                        }}
                        context.stroke();
                        context.setLineDash([]);
                        
                        // Text Layout
                        context.font = "16px sans-serif";
                        context.fillStyle = "#F8FAFC";
                        context.textAlign = "left";
                        context.fillText("Expected Normal Distribution", 20, 30);
                        context.fillStyle = "#38BDF8";
                        context.fillText("N = " + marblesSpawned + " / " + targetMarbles, 20, 55);
                    }});

                    Render.run(render);
                    const runner = Runner.create();
                    Runner.run(runner, engine);

                }} catch (error) {{
                    document.getElementById('debug-console').innerHTML = "<strong>CRITICAL FAILURE:</strong> " + error.message;
                }}
            }});
        </script>
    </body>
    </html>
    """
    
    // We increase the Streamlit IFrame height to accommodate the 800px physics canvas
    components.html(html_code, height=820)