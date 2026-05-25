"""
=============================================================================
MODULE: pages/components/probability_demo.py
AUTHOR: Kyle W. Killebrew, PhD
DESCRIPTION: 
    A structurally refined Matter.js Galton Board.
    Fixes mesh-grid bias by perfectly aligning the peg array with bin dividers.
    Implements a pooling "hopper" with granular arching prevention (vibration)
    and single-file trickle mechanics.
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
                    bodiesToLoad.push(Bodies.rectangle(0, height/2, 10, height, {{ isStatic: true, render: {{ visible: false }}, collisionFilter: {{ category: CAT_WALL }} }}));
                    bodiesToLoad.push(Bodies.rectangle(width, height/2, 10, height, {{ isStatic: true, render: {{ visible: false }}, collisionFilter: {{ category: CAT_WALL }} }}));

                    // --- 2. THE HOPPER (V-Funnel) ---
                    // LOWERED: Moved Y from 65 to 85. 
                    // TIP: Forms a tight seal (1.8px overlap) at exactly Y=160.
                    const doorL = Bodies.rectangle(271, 85, 300, 4, {{ 
                        isStatic: true, angle: Math.PI / 6, render: {{ fillStyle: '#94A3B8' }}, collisionFilter: {{ category: CAT_WALL }}
                    }});
                    const doorR = Bodies.rectangle(529, 85, 300, 4, {{ 
                        isStatic: true, angle: -Math.PI / 6, render: {{ fillStyle: '#94A3B8' }}, collisionFilter: {{ category: CAT_WALL }}
                    }});
                    bodiesToLoad.push(doorL, doorR);

                    // --- 3. DYNAMIC BINS ---
                    const numBins = 30;
                    const binWidth = width / numBins; 
                    const binHeight = 200;
                    
                    for (let i = 1; i < numBins; i++) {{
                        bodiesToLoad.push(Bodies.rectangle(i * binWidth, height - (binHeight/2), 2, binHeight, {{
                            isStatic: true, render: {{ fillStyle: '#475569' }}, collisionFilter: {{ category: CAT_WALL }}
                        }}));
                    }}
                    bodiesToLoad.push(Bodies.rectangle(width/2, height + 10, width, 40, {{ isStatic: true, collisionFilter: {{ category: CAT_WALL }} }}));

                    // --- 4. PERFECTLY ALIGNED QUINCUNX ---
                    const rows = 29;
                    // Starts at r=1 (Y=175). Gap between hopper tip (160) and first pegs (175) is perfectly tight.
                    for (let r = 1; r < rows; r++) {{
                        for (let c = 0; c <= r; c++) {{
                            let px = (width / 2) + (c - r / 2) * binWidth;
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
                    let gateOffset = 0; 
                    const targetMarbles = {sample_count};
                    
                    Events.on(engine, 'beforeUpdate', function() {{
                        let elapsed = performance.now() - startTime;
                        
                        // PHASE 1: Spawning Pool
                        let expectedMarbles = Math.min(targetMarbles, Math.floor((elapsed / 3000) * targetMarbles));
                        
                        while(marblesSpawned < expectedMarbles) {{
                            let spawnX = (width / 2) + (Math.random() * 80 - 40);
                            let marble = Bodies.circle(spawnX, -15, 5, {{
                                restitution: 0.3, // Lowered bounciness to prevent exploding scattering
                                friction: 0.001,  // Extremely low friction to slide easily
                                render: {{ fillStyle: '#38BDF8' }},
                                collisionFilter: {{ category: CAT_MARBLE, mask: CAT_WALL | CAT_PEG | CAT_MARBLE }}
                            }});
                            Composite.add(engine.world, marble);
                            marblesSpawned++;
                        }}

                        // PHASE 2: Sliding Gate & Anti-Arching Vibration
                        // RESTRICTED: Max offset is now 7. Creates a 12px gap (Marbles are 10px).
                        if (elapsed > 3500) {{
                            if (gateOffset < 7) {{
                                gateOffset += 0.1; // Opens slower
                            }}
                            
                            // HACK: Microscopic lateral vibration to prevent granular arching (clogs)
                            let jiggle = Math.sin(elapsed / 30) * 0.3; 
                            
                            Body.setPosition(doorL, {{ x: 271 - gateOffset + jiggle, y: 85 }});
                            Body.setPosition(doorR, {{ x: 529 + gateOffset - jiggle, y: 85 }});
                        }}
                    }});

                    // --- 6. CANVAS HUD & BELL CURVE OVERLAY ---
                    Events.on(render, 'afterRender', function() {{
                        const context = render.context;
                        
                        context.beginPath();
                        context.strokeStyle = "rgba(74, 222, 128, 0.4)";
                        context.lineWidth = 2;
                        context.setLineDash([5, 5]);
                        
                        for (let x = 0; x <= width; x += 5) {{
                            let z = (x - 400) / 72;
                            let y = 780 - (350 * Math.exp(-0.5 * z * z)); 
                            if (x === 0) context.moveTo(x, y);
                            else context.lineTo(x, y);
                        }}
                        context.stroke();
                        context.setLineDash([]);
                        
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
    
    # We increase the Streamlit IFrame height to accommodate the 800px physics canvas
    components.html(html_code, height=820)