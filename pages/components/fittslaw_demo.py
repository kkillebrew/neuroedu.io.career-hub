"""
=============================================================================
MODULE: pages/components/fittslaw_demo.py
AUTHOR: Kyle W. Killebrew, PhD & Data Science Mentorship Engine
STATUS: Active Production Blueprint (Lesson 4)
DESCRIPTION:
    A high-speed HTML5 Canvas reaction-time engine tracking Fitts's Law.
    Captures target amplitude (A), width (W), and movement time (MT).
    Writes empirical data records directly to Firestore.
=============================================================================
"""

import streamlit.components.v1 as components

def render_fittslaw_demo(app_id, firebase_config, user_uid):
    """
    Renders an interactive reaction grid inside a Streamlit HTML5 iFrame.
    Pipes Firebase connection metadata directly into client-side JS.
    """
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script src="[https://www.gstatic.com/firebasejs/10.8.0/firebase-app-compat.js](https://www.gstatic.com/firebasejs/10.8.0/firebase-app-compat.js)"></script>
        <script src="[https://www.gstatic.com/firebasejs/10.8.0/firebase-auth-compat.js](https://www.gstatic.com/firebasejs/10.8.0/firebase-auth-compat.js)"></script>
        <script src="[https://www.gstatic.com/firebasejs/10.8.0/firebase-firestore-compat.js](https://www.gstatic.com/firebasejs/10.8.0/firebase-firestore-compat.js)"></script>
        <style>
            body {{ margin: 0; padding: 0; background-color: #0F172A; font-family: sans-serif; color: #F8FAFC; overflow: hidden; }}
            canvas {{ display: block; margin: 10px auto; border-radius: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.55); cursor: crosshair; }}
            #control-panel {{ text-align: center; margin-top: 5px; }}
            .btn {{ background-color: #6366F1; color: white; border: none; padding: 10px 20px; font-size: 14px; border-radius: 6px; cursor: pointer; font-weight: bold; transition: background 0.2s; }}
            .btn:hover {{ background-color: #4F46E5; }}
            #hud {{ display: flex; justify-content: space-around; max-width: 800px; margin: 0 auto; font-size: 14px; color: #94A3B8; }}
        </style>
    </head>
    <body>
        <div id="hud">
            <div>Trial: <span id="lbl-trial" style="color: #38BDF8; font-weight:bold;">0 / 10</span></div>
            <div>Current ID: <span id="lbl-id" style="color: #10B981; font-weight:bold;">-- bits</span></div>
            <div>Mean MT: <span id="lbl-mt" style="color: #F59E0B; font-weight:bold;">-- ms</span></div>
        </div>
        <canvas id="canvas-fitts" width="800" height="400"></canvas>
        <div id="control-panel">
            <button id="btn-start" class="btn" onclick="initiateSession()">Start Experiment Session</button>
        </div>

        <script>
            // --- FIREBASE CLOUD SETUP (Rule 1 & Rule 3 Compliance) ---
            const firebaseConfig = {firebase_config};
            const appId = "{app_id}";
            const userUid = "{user_uid}";

            firebase.initializeApp(firebaseConfig);
            const db = firebase.firestore();
            const auth = firebase.auth();

            let currentUser = null;
            auth.signInAnonymously().then(cred => {{
                currentUser = cred.user;
                console.log("Authenticated as: ", currentUser.uid);
            }}).catch(err => console.error("Rule 3 Auth Violation: ", err));

            // --- EXPERIMENTAL CONTROL STATE VARIABLES ---
            const canvas = document.getElementById("canvas-fitts");
            const ctx = canvas.getContext("2d");
            
            let trialCount = 0;
            const maxTrials = 10;
            let activeTarget = null; // Contains {{x, y, w, d}}
            let homePosition = {{ x: 400, y: 350, r: 25 }}; // Baseline finger position
            let trialStartTime = 0;
            let currentPhase = "HOME"; // Phases: HOME, TARGET, DONE
            let sessionData = [];

            function drawHUDMessage(msg, submsg) {{
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                ctx.fillStyle = "#F8FAFC";
                ctx.font = "bold 24px sans-serif";
                ctx.textAlign = "center";
                ctx.fillText(msg, canvas.width/2, canvas.height/2 - 20);
                
                ctx.fillStyle = "#94A3B8";
                ctx.font = "16px sans-serif";
                ctx.fillText(submsg, canvas.width/2, canvas.height/2 + 15);
            }}

            drawHUDMessage("Fitts's Law Neuro-Motor Control Rig", "Click 'Start Experiment Session' below to begin testing your visual-motor bandwith.");

            function initiateSession() {{
                trialCount = 0;
                sessionData = [];
                document.getElementById("btn-start").style.display = "none";
                currentPhase = "HOME";
                drawFrame();
            }}

            function drawFrame() {{
                ctx.clearRect(0, 0, canvas.width, canvas.height);

                if (currentPhase === "HOME") {{
                    // Draw start baseline circle
                    ctx.beginPath();
                    ctx.arc(homePosition.x, homePosition.y, homePosition.r, 0, Math.PI * 2);
                    ctx.fillStyle = "#6366F1";
                    ctx.shadowBlur = 15;
                    ctx.shadowColor = "#6366F1";
                    ctx.fill();
                    ctx.shadowBlur = 0; // Reset shadow

                    ctx.fillStyle = "#F8FAFC";
                    ctx.font = "bold 14px sans-serif";
                    ctx.textAlign = "center";
                    ctx.fillText("TAP HERE", homePosition.x, homePosition.y + 5);
                }} 
                else if (currentPhase === "TARGET") {{
                    // Draw visual goal target circle
                    ctx.beginPath();
                    ctx.arc(activeTarget.x, activeTarget.y, activeTarget.w / 2, 0, Math.PI * 2);
                    ctx.fillStyle = "#EF4444";
                    ctx.shadowBlur = 15;
                    ctx.shadowColor = "#EF4444";
                    ctx.fill();
                    ctx.shadowBlur = 0; // Reset shadow

                    ctx.fillStyle = "#10B981";
                    ctx.font = "bold 12px sans-serif";
                    ctx.fillText("CLICK!", activeTarget.x, activeTarget.y + 4);
                }}
            }}

            canvas.addEventListener("mousedown", function(e) {{
                const rect = canvas.getBoundingClientRect();
                const mouseX = e.clientX - rect.left;
                const mouseY = e.clientY - rect.top;

                if (currentPhase === "HOME") {{
                    let dist = Math.hypot(mouseX - homePosition.x, mouseY - homePosition.y);
                    if (dist < homePosition.r) {{
                        // Calculate next random index parameters
                        const amplitudes = [150, 200, 250, 300];
                        const widths = [16, 24, 32, 48];
                        
                        const a = amplitudes[Math.floor(Math.random() * amplitudes.length)];
                        const w = widths[Math.floor(Math.random() * widths.length)];
                        
                        // Spawn target radially around home base to maintain natural reach vectors
                        const angle = Math.PI + (Math.random() * Math.PI); // Upper hemisphere arc
                        const tx = homePosition.x + Math.cos(angle) * a;
                        const ty = homePosition.y + Math.sin(angle) * a;

                        activeTarget = {{ x: tx, y: ty, w: w, a: a }};
                        currentPhase = "TARGET";
                        trialStartTime = performance.now();
                        
                        let id = Math.log2((2 * a) / w).toFixed(2);
                        document.getElementById("lbl-id").innerText = id + " bits";
                        
                        drawFrame();
                    }}
                } 
                else if (currentPhase === "TARGET") {{
                    let dist = Math.hypot(mouseX - activeTarget.x, mouseY - activeTarget.y);
                    if (dist < (activeTarget.w / 2)) {{
                        let movementTime = performance.now() - trialStartTime;
                        trialCount++;
                        
                        // Cache empirical metrics
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
                drawHUDMessage("Writing Empirical Metrics...", "Synchronizing local spatial trial logs securely with global Firestore repository.");

                if (!currentUser) {{
                    drawHUDMessage("Network Access Failure", "Authentication channel is disconnected. Please refresh the page.");
                    return;
                }}

                // Assemble batch storage updates (Strict Rule 1 Compliance)
                const batch = db.batch();
                sessionData.forEach(trial => {{
                    const docRef = db.collection('artifacts').doc(appId).collection('public').document('data').collection('fitts_trials').doc();
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
                    drawHUDMessage("Session Synced Successfully!", "Results uploaded to cohort model. Please click outside to compile regression plots.");
                    document.getElementById("btn-start").style.display = "inline";
                    document.getElementById("btn-start").innerText = "Restart Experiment";
                }}).catch(err => {{
                    console.error("Database Write Crash: ", err);
                    drawHUDMessage("Database Sync Interrupted", err.message);
                }});
            }}
        </script>
    </body>
    </html>
    """
    # Large 820px wrapper to cleanly accommodate canvas and stats widgets
    components.html(html_code, height=520)