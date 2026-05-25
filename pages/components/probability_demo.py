"""
=============================================================================
MODULE: pages/components/probability_demo.py
AUTHOR: Kyle W. Killebrew, PhD
DESCRIPTION: 
    A Matter.js Galton Board utilizing a full staggered rectangular matrix.
    Eliminates the pooling hopper in favor of a dynamic trickle spawn.
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

                    // --- 2. DYNAMIC BINS ---
                    const numBins = 30;
                    const binWidth = width / numBins; 
                    const binHeight = 200;
                    
                    for (let i = 1; i < numBins; i++) {{
                        bodiesToLoad.push(Bodies.rectangle(i * binWidth, height - (binHeight/2), 2, binHeight, {{
                            isStatic: true, render: {{ fillStyle: '#475569' }}, collisionFilter: {{ category: CAT_WALL }}
                        }}));
                    }}
                    bodiesToLoad.push(Bodies.rectangle(width/2, height + 10, width, 40, {{ isStatic: true, collisionFilter: {{ category: CAT_WALL }} }}));

                    // --- 3. STAGGERED RECTANGULAR MATRIX ---
                    const rows = 30; // 30 rows ensures the final row aligns with bin dividers
                    
                    for (let r = 0; r < rows; r++) {{
                        // Modulo logic to stagger rows. 
                        // Even rows (r=0, 2, 4...) have a gap at X=400.
                        // Odd rows (r=1, 3, 5...) have a peg at X=400.
                        // Row 29 is odd, meaning its pegs align PERFECTLY with the bin dividers!
                        let offset = (r % 2 === 0) ? (binWidth / 2) : 0;
                        
                        for (let c = -1; c <= numBins; c++) {{
                            let px = c * binWidth + offset;
                            let py = 100 + r * 16; 
                            
                            // Only draw pegs that are visibly inside the bounds
                            if (px > 5 && px < width - 5) {{
                                bodiesToLoad.push(Bodies.circle(px, py, 3, {{
                                    isStatic: true, render: {{ fillStyle: '#64748B' }},
                                    collisionFilter: {{ category: CAT_PEG, mask: CAT_MARBLE }}
                                }}));
                            }}
                        }}
                    }}

                    Composite.add(engine.world, bodiesToLoad);

                    // --- 4. CHOREOGRAPHY STATE MACHINE ---
                    let startTime = performance.now();
                    let marblesSpawned = 0;
                    const targetMarbles = {sample_count};
                    
                    Events.on(engine, 'beforeUpdate', function() {{
                        let elapsed = performance.now() - startTime;
                        
                        // SPAWNING TRICKLE: Dictates flow rate (1 marble every 15ms)
                        // This prevents pillar-stacking and physics explosions at the top gap.
                        let expectedMarbles = Math.min(targetMarbles, Math.floor(elapsed / 15));
                        
                        while(marblesSpawned < expectedMarbles) {{
                            // Drops directly over the center gap (X=400).
                            // A microscopic variance (+/- 4px) prevents mathematically perfect 
                            // vertical stacking while easily fitting through the 26px top gap.
                            let spawnX = (width / 2) + (Math.random() * 8 - 4);
                            let marble = Bodies.circle(spawnX, -15, 5, {{
                                restitution: 0.4, // Slight bounce
                                friction: 0.001,
                                render: {{ fillStyle: '#38BDF8' }},
                                collisionFilter: {{ category: CAT_MARBLE, mask: CAT_WALL | CAT_PEG | CAT_MARBLE }}
                            }});
                            Composite.add(engine.world, marble);
                            marblesSpawned++;
                        }}
                    }});

                    // --- 5. CANVAS HUD & BELL CURVE OVERLAY ---
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