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
    
    # The normal distribution probability density function (PDF) for reference:
    # f(x) = (1 / (sigma * sqrt(2*pi))) * exp(-0.5 * ((x - mu) / sigma)^2)
    
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/matter-js/0.19.0/matter.min.js"></script>
        <style>
            body {{ margin: 0; padding: 0; overflow: hidden; background-color: #0F172A; }}
            canvas {{ display: block; margin: 0 auto; border-radius: 8px; }}
        </style>
    </head>
    <body>
        <script>
            // 1. ENGINE & RENDER SETUP
            const Engine = Matter.Engine,
                  Render = Matter.Render,
                  Runner = Matter.Runner,
                  Bodies = Matter.Bodies,
                  Composite = Matter.Composite,
                  Events = Matter.Events;

            const engine = Engine.create();
            // Version-safe gravity
            const gravity = engine.gravity || engine.world.gravity;
            gravity.y = 1.2; 
            
            // Critical fix: Prevent small, fast marbles from tunneling through thin bin walls
            engine.positionIterations = 16;
            engine.velocityIterations = 16;

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

            // 2. BITMASK COLLISION CATEGORIES
            const CAT_WALL = 0x0001;
            const CAT_PEG = 0x0002;
            const CAT_MARBLE = 0x0004;
            const CAT_GHOST_BELL = 0x0008; // Visual only, marbles pass through

            // 3. ENVIRONMENT GENERATION
            const bodiesToLoad = [];
            
            // A. The Top Funnel (Hatch)
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

            // B. The Quincunx (Peg Array)
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

            // C. The Bins (Histogram Buckets)
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

            // 4. THE CHOREOGRAPHY STATE MACHINE
            let startTime = performance.now();
            let marblesSpawned = 0;
            const targetMarbles = {{sample_count}}; // Passed from Streamlit via Python f-string
            
            Events.on(engine, 'beforeUpdate', function() {{
                let timeNow = performance.now();
                let elapsed = timeNow - startTime;
                
                // Spawn Phase: Drip marbles from the top hatch randomly
                if (marblesSpawned < targetMarbles && elapsed > 1000) {{
                    // Modulo logic to stagger spawns (~every 50ms)
                    if (Math.floor(elapsed) % 50 < 15) {{
                        let spawnX = (width / 2) + (Math.random() * 10 - 5);
                        let marble = Bodies.circle(spawnX, 10, 6, {{
                            restitution: 0.4, // Bounciness
                            friction: 0.001,
                            render: {{ fillStyle: '#38BDF8' }}, // Neuromorphic Blue
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

            // 5. HTML5 CANVAS RENDERING (Overlaying the Bell Curve & Text)
            Events.on(render, 'afterRender', function() {{
                const context = render.context;
                
                // Draw Bell Curve Overlay (Ghost Funnel)
                context.beginPath();
                context.strokeStyle = "rgba(74, 222, 128, 0.4)"; // Soft Green
                context.lineWidth = 3;
                context.setLineDash([5, 5]); // Dashed line
                
                for (let x = 0; x <= width; x += 10) {{
                    // Calculate a visual gaussian bell outline
                    // using an inverted normal distribution curve formula
                    let z = (x - (width/2)) / 120;
                    let y = 520 - (300 * Math.exp(-0.5 * z * z)); 
                    if (x === 0) context.moveTo(x, y);
                    else context.lineTo(x, y);
                }}
                context.stroke();
                context.setLineDash([]); // Reset dash
                
                // Draw Anti-Jitter HUD Text
                context.font = "16px 'Inter', sans-serif";
                context.fillStyle = "#F8FAFC";
                context.textAlign = "left";
                context.fillText("Expected Distribution", 20, 30);
                
                context.fillStyle = "#38BDF8";
                // Template Literal requires ${{var}} in Python f-string
                context.fillText(`N = ${{marblesSpawned}} / ${{targetMarbles}}`, 20, 55);
            }});

            // 6. RUN THE ENGINE
            Render.run(render);
            const runner = Runner.create();
            Runner.run(runner, engine);

        </script>
    </body>
    </html>
    """
    
    # We mount the component with a fixed height to prevent Streamlit iframe scrollbars
    components.html(html_code, height=620)