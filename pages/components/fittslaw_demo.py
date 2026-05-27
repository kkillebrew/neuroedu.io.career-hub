"""
=============================================================================
MODULE: pages/components/fittslaw_demo.py
AUTHOR: Kyle W. Killebrew, PhD & Data Science Mentorship Engine
STATUS: Active Production Blueprint (Lesson 4)
DESCRIPTION:
    A high-speed HTML5 Canvas reaction-time engine tracking Fitts's Law.
    Includes High-DPI (Retina) display scaling and dynamic responsive resizing.
=============================================================================
"""

import streamlit.components.v1 as components

def render_fittslaw_demo(app_id, firebase_config, user_uid):
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://www.gstatic.com/firebasejs/10.8.0/firebase-app-compat.js"></script>
        <script src="https://www.gstatic.com/firebasejs/10.8.0/firebase-auth-compat.js"></script>
        <script src="https://www.gstatic.com/firebasejs/10.8.0/firebase-firestore-compat.js"></script>
        <style>
            body {{ margin: 0; padding: 0; background-color: #0F172A; font-family: sans-serif; color: #F8FAFC; overflow: hidden; }}
            canvas {{ display: block; margin: 10px auto; border-radius: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.55); cursor: crosshair; width: 100%; max-width: 1000px; height: auto; aspect-ratio: 2 / 1; }}
            #control-panel {{ text-align: center; margin-top: 5px; }}
            .btn {{ background-color: #6366F1; color: white; border: none; padding: 10px 20px; font-size: 14px; border-radius: 6px; cursor: pointer; font-weight: bold; transition: background 0.2s; }}
            .btn:hover {{ background-color: #4F46E5; }}
            #hud {{ display: flex; justify-content: space-around; max-width: 1000px; margin: 0 auto; font-size: 14px; color: #94A3B8; }}
        </style>
    </head>
    <body>
        <div id="hud">
            <div>Trial: <span id="lbl-trial" style="color: #38BDF8; font-weight:bold;">0 / 10</span></div>
            <div>Current ID: <span id="lbl-id" style="color: #10B981; font-weight:bold;">-- bits</span></div>
            <div>Mean MT: <span id="lbl-mt" style="color: #F59E0B; font-weight:bold;">-- ms</span></div>
        </div>
        
        <canvas id="canvas-fitts"></canvas>
        
        <div id="control-panel">
            <button id="btn-start" class="btn" onclick="initiateSession()">Start Experiment Session</button>
        </div>

        <script>
            const firebaseConfig = JSON.parse('{firebase_config}'); 
            const appId = "{app_id}";
            const userUid = "{user_uid}";

            let db = null;

            try {{
                if (firebaseConfig && firebaseConfig.apiKey !== "PASTE_YOUR_API_KEY_HERE") {{
                    if (!firebase.apps.length) {{
                        firebase.initializeApp(firebaseConfig);
                    }}
                    db = firebase.firestore();
                    console.log("Firebase connected successfully.");
                }}
            }} catch (e) {{
                console.error("Database bypass: ", e);
            }}

            const canvas = document.getElementById("canvas-fitts");
            const ctx = canvas.getContext("2d");
            
            // --- HIGH-DPI (RETINA) SCALING MATRICES ---
            const logicalWidth = 800;
            const logicalHeight = 400;
            const dpr = window.devicePixelRatio || 1;
            
            // Multiply internal memory grid by screen pixel density
            canvas.width = logicalWidth * dpr;
            canvas.height = logicalHeight * dpr;
            // Scale rendering engine to map 1 logical unit to DPR physical pixels
            ctx.scale(dpr, dpr);

            let trialCount = 0;
            const maxTrials = 10;
            let activeTarget = null; 
            let homePosition = {{ x: 400, y: 350, r: 25 }}; 
            let trialStartTime = 0;
            let currentPhase = "HOME"; 
            let sessionData = [];

            function drawHUDMessage(msg, submsg) {{
                ctx.clearRect(0, 0, logicalWidth, logicalHeight);
                ctx.fillStyle = "#F8FAFC";
                ctx.font = "bold 24px sans-serif";
                ctx.textAlign = "center";
                ctx.fillText(msg, logicalWidth/2, logicalHeight/2 - 20);
                
                ctx.fillStyle = "#94A3B8";
                ctx.font = "16px sans-serif";
                ctx.fillText(submsg, logicalWidth/2, logicalHeight/2 + 15);
            }}

            drawHUDMessage("Fitts's Law Neuro-Motor Control Rig", "Click 'Start Experiment Session' below to begin testing your visual-motor bandwidth.");

            function initiateSession() {{
                trialCount = 0;
                sessionData = [];
                document.getElementById("btn-start").style.display = "none";
                currentPhase = "HOME";
                drawFrame();
            }}

            function drawFrame() {{
                ctx.clearRect(0, 0, logicalWidth, logicalHeight);

                if (currentPhase === "HOME") {{
                    ctx.beginPath();
                    ctx.arc(homePosition.x, homePosition.y, homePosition.r, 0, Math.PI * 2);
                    ctx.fillStyle = "#6366F1";
                    ctx.shadowBlur = 15;
                    ctx.shadowColor = "#6366F1";
                    ctx.fill();
                    ctx.shadowBlur = 0;

                    ctx.fillStyle = "#F8FAFC";
                    ctx.font = "bold 14px sans-serif";
                    ctx.textAlign = "center";
                    ctx.fillText("TAP HERE", homePosition.x, homePosition.y + 5);
                }} 
                else if (currentPhase === "TARGET") {{
                    ctx.beginPath();
                    ctx.arc(activeTarget.x, activeTarget.y, activeTarget.w / 2, 0, Math.PI * 2);
                    ctx.fillStyle = "#EF4444";
                    ctx.shadowBlur = 15;
                    ctx.shadowColor = "#EF4444";
                    ctx.fill();
                    ctx.shadowBlur = 0;

                    ctx.fillStyle = "#F8FAFC";
                    ctx.font = "bold 12px sans-serif";
                    ctx.fillText("CLICK!", activeTarget.x, activeTarget.y + 4);
                }}
            }}

            canvas.addEventListener("mousedown", function(e) {{
                const rect = canvas.getBoundingClientRect();
                
                // Maps the dynamically stretched CSS bounds directly back to the 800x400 grid
                const scaleX = logicalWidth / rect.width;
                const scaleY = logicalHeight / rect.height;
                
                const mouseX = (e.clientX - rect.left) * scaleX;
                const mouseY = (e.clientY - rect.top) * scaleY;

                if (currentPhase === "HOME") {{
                    let dist = Math.hypot(mouseX - homePosition.x, mouseY - homePosition.y);
                    if (dist < homePosition.r) {{
                        const amplitudes = [150, 200, 250, 300];
                        const widths = [16, 24, 32, 48];
                        
                        const a = amplitudes[Math.floor(Math.random() * amplitudes.length)];
                        const w = widths[Math.floor(Math.random() * widths.length)];
                        
                        const angle = Math.PI + (Math.random() * Math.PI); 
                        const tx = homePosition.x + Math.cos(angle) * a;
                        const ty = homePosition.y + Math.sin(angle) * a;

                        activeTarget = {{ x: tx, y: ty, w: w, a: a }};
                        currentPhase = "TARGET";
                        trialStartTime = performance.now();
                        
                        let id = Math.log2((2 * a) / w).toFixed(2);
                        document.getElementById("lbl-id").innerText = id + " bits";
                        
                        drawFrame();
                    }}
                }} 
                else if (currentPhase === "TARGET") {{
                    let dist = Math.hypot(mouseX - activeTarget.x, mouseY - activeTarget.y);
                    if (dist < (activeTarget.w / 2)) {{
                        let movementTime = performance.now() - trialStartTime;
                        trialCount++;
                        
                        sessionData.push({{
                            amplitude: activeTarget.a,
                            width: activeTarget.w,
                            index_difficulty: Math.log2((2 * activeTarget.a) / activeTarget.w),
                            movement_time: movementTime,
                            timestamp: Date.now()
                        }});

                        document.getElementById("lbl-trial").innerText = trialCount + " / " + maxTrials;
                        
                        let sumMT = sessionData.reduce((acc, val) => acc + val.movement_time, 0);
                        document.getElementById("lbl-mt").innerText = Math.round(sumMT / sessionData.length) + " ms";

                        if (trialCount < maxTrials) {{
                            currentPhase = "HOME";
                            drawFrame();
                        }} else {{
                            currentPhase = "DONE";
                            commitSessionData();
                        }}
                    }}
                }}
            }});

            function commitSessionData() {{
                if (!db) {{
                    drawHUDMessage("Session Complete (Sandbox Mode)", "Connect your Firebase credentials to unlock live database writing.");
                    document.getElementById("btn-start").style.display = "inline";
                    document.getElementById("btn-start").innerText = "Restart Session";
                    return;
                }}

                drawHUDMessage("Writing Empirical Metrics...", "Synchronizing spatial trial logs securely with database.");

                const batch = db.batch();
                sessionData.forEach(trial => {{
                    const docRef = db.collection('artifacts').doc(appId).collection('public').doc('data').collection('fitts_trials').doc();
                    batch.set(docRef, {{
                        user_id: userUid,
                        amplitude: trial.amplitude,
                        width: trial.width,
                        index_difficulty: trial.index_difficulty,
                        movement_time: trial.movement_time,
                        timestamp: firebase.firestore.FieldValue.serverTimestamp()
                    }});
                }});

                batch.commit().then(() => {{
                    drawHUDMessage("Session Synced!", "Data posted. Click anywhere outside the module to compile OLS plots.");
                    document.getElementById("btn-start").style.display = "inline";
                    document.getElementById("btn-start").innerText = "Restart Session";
                }}).catch(err => {{
                    console.error("Database Write Error: ", err);
                    drawHUDMessage("Sync Failure", err.message);
                }});
            }}
        </script>
    </body>
    </html>
    """
    # Increased iFrame wrapper height to 650px to ensure the button is never clipped
    components.html(html_code, height=650)