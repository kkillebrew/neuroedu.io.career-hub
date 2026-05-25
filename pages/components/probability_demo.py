"""
=============================================================================
MODULE: pages/components/probability_demo.py
AUTHOR: Kyle W. Killebrew, PhD
DESCRIPTION: 
    A Matter.js Galton Board utilizing a staggered rectangular matrix.
    Dynamically calculates empirical vs theoretical statistical moments (Mean & SD) 
    and fades the results into the Canvas HUD upon simulation completion.
    
    MATLAB Analogy: This is equivalent to running mean(X) and std(X) on a 
    result vector after an ode45 simulation finishes, and updating an 
    App Designer uilabel with dynamic alpha transparency.
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
                    const rows = 30; 
                    
                    for (let r = 0; r < rows; r++) {{
                        let offset = (r % 2 === 0) ? (binWidth / 2) : 0;
                        for (let c = -1; c <= numBins; c++) {{
                            let px = c * binWidth + offset;
                            let py = 100 + r * 16; 
                            
                            if (px > 5 && px < width - 5) {{
                                bodiesToLoad.push(Bodies.circle(px, py, 3, {{
                                    isStatic: true, render: {{ fillStyle: '#64748B' }},
                                    collisionFilter: {{ category: CAT_PEG, mask: CAT_MARBLE }}
                                }}));
                            }}
                        }}
                    }}

                    Composite.add(engine.world, bodiesToLoad);

                    // --- 4. CHOREOGRAPHY & CALCULATION STATE MACHINE ---
                    let startTime = performance.now();
                    let lastSpawnTime = 0; // Tracks when the final marble dropped
                    let marblesSpawned = 0;
                    const targetMarbles = {sample_count};
                    
                    // Statistical Tracking Variables
                    let simulationComplete = false;
                    let empiricalMean = 0;
                    let empiricalStdDev = 0;
                    let fadeOpacity = 0.0;
                    
                    Events.on(engine, 'beforeUpdate', function() {{
                        let elapsed = performance.now() - startTime;
                        
                        // SPAWNING TRICKLE
                        let expectedMarbles = Math.min(targetMarbles, Math.floor(elapsed / 15));
                        
                        while(marblesSpawned < expectedMarbles) {{
                            let spawnX = (width / 2) + (Math.random() * 8 - 4);
                            let marble = Bodies.circle(spawnX, -15, 5, {{
                                restitution: 0.4, 
                                friction: 0.001,
                                render: {{ fillStyle: '#38BDF8' }},
                                collisionFilter: {{ category: CAT_MARBLE, mask: CAT_WALL | CAT_PEG | CAT_MARBLE }}
                            }});
                            Composite.add(engine.world, marble);
                            marblesSpawned++;
                            lastSpawnTime = elapsed; // Log the timestamp of the latest spawn
                        }}

                        // TERMINATION & CALCULATION CHECK
                        // If all marbles have spawned AND 4 seconds have passed to let them fall to the bottom
                        if (marblesSpawned >= targetMarbles && !simulationComplete) {{
                            if (elapsed - lastSpawnTime > 4000) {{
                                simulationComplete = true;
                                
                                // Extract all marbles from the physics engine matrix
                                let allBodies = Composite.allBodies(engine.world);
                                let marblesArray = [];
                                for (let i = 0; i < allBodies.length; i++) {{
                                    if (allBodies[i].collisionFilter.category === CAT_MARBLE) {{
                                        marblesArray.push(allBodies[i]);
                                    }}
                                }}
                                
                                // Calculate Empirical Mean (Center of Mass X)
                                let sumX = 0;
                                for (let i = 0; i < marblesArray.length; i++) {{
                                    sumX += marblesArray[i].position.x;
                                }}
                                empiricalMean = sumX / marblesArray.length;
                                
                                // Calculate Empirical Standard Deviation (Spread)
                                let sumSq = 0;
                                for (let i = 0; i < marblesArray.length; i++) {{
                                    sumSq += Math.pow(marblesArray[i].position.x - empiricalMean, 2);
                                }}
                                empiricalStdDev = Math.sqrt(sumSq / marblesArray.length);
                            }}
                        }}
                    }});

                    // --- 5. CANVAS HUD & OVERLAYS ---
                    Events.on(render, 'afterRender', function() {{
                        const context = render.context;
                        
                        // Draw Ghost Bell Curve Overlay
                        context.beginPath();
                        context.strokeStyle = "rgba(74, 222, 128, 0.4)";
                        context.lineWidth = 2;
                        context.setLineDash([5, 5]);
                        
                        for (let x = 0; x <= width; x += 5) {{
                            let z = (x - 400) / 72; // Theoretical Sigma = 72
                            let y = 780 - (350 * Math.exp(-0.5 * z * z)); 
                            if (x === 0) context.moveTo(x, y);
                            else context.lineTo(x, y);
                        }}
                        context.stroke();
                        context.setLineDash([]);
                        
                        // Main Titles
                        context.font = "16px sans-serif";
                        context.fillStyle = "#F8FAFC";
                        context.textAlign = "left";
                        context.fillText("Expected Normal Distribution", 20, 30);
                        context.fillStyle = "#38BDF8";
                        context.fillText("N = " + marblesSpawned + " / " + targetMarbles, 20, 55);
                        
                        // Theoretical Stats (Always Visible)
                        context.fillStyle = "#94A3B8"; // Slate Gray
                        context.fillText("Theoretical μ: 400.0px | σ: 72.0px", 20, 80);
                        
                        // Empirical Stats (Fades in once calculation is complete)
                        if (simulationComplete) {{
                            if (fadeOpacity < 1.0) {{
                                fadeOpacity += 0.01; // Increase alpha channel each frame
                            }}
                            // We use string concatenation here instead of JS template literals 
                            // to ensure Python's f-string parser doesn't break.
                            context.fillStyle = "rgba(74, 222, 128, " + fadeOpacity + ")"; // Soft Green
                            context.fillText("Empirical μ: " + empiricalMean.toFixed(1) + "px | σ: " + empiricalStdDev.toFixed(1) + "px", 20, 105);
                        }}
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