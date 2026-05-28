"""
=============================================================================
MODULE: pages/components/visual_search_demo.py
AUTHOR: Kyle W. Killebrew, PhD & Data Science Mentorship Engine
STATUS: Active Production Blueprint (Lesson 5)
DESCRIPTION:
    A high-speed HTML5 Canvas reaction-time engine tracking Visual Search
    (Parallel vs. Serial processing). Replicates Treisman & Wolfe (1980/1994).
    
    --- MATLAB BRIDGE ---
    This script acts as our web equivalent to a Psychtoolbox (PTB) experiment 
    loop. Instead of Screen('DrawText') and Screen('Flip'), we utilize 
    HTML5 Canvas 2D contexts injected securely into the DOM.
=============================================================================
"""

import streamlit.components.v1 as components

def render_visual_search_demo(app_id, firebase_config, user_uid):
    """
    Renders the Visual Search paradigm canvas and handles native JS telemetry.
    """
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://www.gstatic.com/firebasejs/10.8.0/firebase-app-compat.js"></script>
        <script src="https://www.gstatic.com/firebasejs/10.8.0/firebase-auth-compat.js"></script>
        <script src="https://www.gstatic.com/firebasejs/10.8.0/firebase-firestore-compat.js"></script>
        <style>
            body {{ margin: 0; padding: 0; background-color: #0F172A; font-family: sans-serif; color: #F8FAFC; overflow: hidden; }}
            /* 2:1 Aspect Ratio Canvas Constraint per Blueprint Rules */
            canvas {{ display: block; margin: 10px auto; border-radius: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.55); cursor: crosshair; width: 100%; max-width: 1000px; height: auto; aspect-ratio: 2 / 1; background-color: #1E293B; }}
            #control-panel {{ text-align: center; margin-top: 5px; }}
            .btn {{ background-color: #6366F1; color: white; border: none; padding: 10px 20px; font-size: 14px; border-radius: 6px; cursor: pointer; font-weight: bold; transition: background 0.2s; }}
            .btn:hover {{ background-color: #4F46E5; }}
            #hud {{ display: flex; justify-content: space-around; max-width: 1000px; margin: 0 auto; font-size: 14px; color: #94A3B8; }}
        </style>
    </head>
    <body>
        <div id="hud">
            <div>Trial: <span id="lbl-trial" style="color: #38BDF8; font-weight:bold;">0 / 16</span></div>
            <div>Condition: <span id="lbl-cond" style="color: #10B981; font-weight:bold;">--</span></div>
            <div>Last RT: <span id="lbl-rt" style="color: #F59E0B; font-weight:bold;">-- ms</span></div>
        </div>
        
        <canvas id="canvas-search"></canvas>
        
        <div id="control-panel">
            <button id="btn-start" class="btn" onclick="initiateSession()">Start Visual Search Experiment</button>
        </div>

        <script>
            // 1. Asymmetric Database Connection Pipeline (Frontend Write Path)
            const firebaseConfig = JSON.parse('{firebase_config}'); 
            const appId = "{app_id}";
            const userUid = "{user_uid}";
            let db = null;

            try {{
                if (firebaseConfig && firebaseConfig.apiKey !== "PASTE_YOUR_API_KEY_HERE") {{
                    if (!firebase.apps.length) {{ firebase.initializeApp(firebaseConfig); }}
                    db = firebase.firestore();
                }}
            }} catch (e) {{ console.error("Database bypass: ", e); }}

            // 2. High-DPI Canvas Setup (MATLAB Screen Rect equivalent)
            const canvas = document.getElementById("canvas-search");
            const ctx = canvas.getContext("2d");
            const logicalWidth = 1000;
            const logicalHeight = 500;
            const dpr = window.devicePixelRatio || 1;
            
            canvas.width = logicalWidth * dpr;
            canvas.height = logicalHeight * dpr;
            ctx.scale(dpr, dpr);

            // 3. Experimental Parameters & State
            // Testing 4 conditions across 2 set sizes (25 and 100) twice = 16 trials
            const conditions = [
                {{ type: 'Color', setSize: 25 }}, {{ type: 'Color', setSize: 100 }},
                {{ type: 'Shape', setSize: 25 }}, {{ type: 'Shape', setSize: 100 }},
                {{ type: 'Spatial', setSize: 25 }}, {{ type: 'Spatial', setSize: 100 }},
                {{ type: 'Conjunction', setSize: 25 }}, {{ type: 'Conjunction', setSize: 100 }}
            ];
            // Duplicate and shuffle arrays for repeated measures
            let trialSequence = [...conditions, ...conditions].sort(() => Math.random() - 0.5);
            
            let currentTrialIdx = 0;
            let currentPhase = "HOME"; // HOME -> FIXATION -> SEARCH -> DONE
            let trialStartTime = 0;
            let sessionData = [];
            let targetItem = null;
            let distractorItems = [];

            // Helper to draw HUD overlays
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

            drawHUDMessage("Visual Feature Integration Task", "Find the unique target. Click it as fast as possible.");

            function initiateSession() {{
                currentTrialIdx = 0;
                sessionData = [];
                document.getElementById("btn-start").style.display = "none";
                nextTrial();
            }}

            function nextTrial() {{
                if (currentTrialIdx >= trialSequence.length) {{
                    currentPhase = "DONE";
                    commitSessionData();
                    return;
                }}
                
                let trialCond = trialSequence[currentTrialIdx];
                document.getElementById("lbl-trial").innerText = (currentTrialIdx + 1) + " / " + trialSequence.length;
                document.getElementById("lbl-cond").innerText = trialCond.type + " (N=" + trialCond.setSize + ")";
                
                // Show Fixation Cross for 500ms before stimuli drop
                currentPhase = "FIXATION";
                ctx.clearRect(0, 0, logicalWidth, logicalHeight);
                ctx.fillStyle = "#F8FAFC";
                ctx.font = "30px sans-serif";
                ctx.textAlign = "center";
                ctx.fillText("+", logicalWidth/2, logicalHeight/2);

                setTimeout(() => {{ generateStimuliGrid(trialCond); }}, 500);
            }}

            // MATLAB Analogy: Equivalent to generating a jittered coordinate matrix
            function generateStimuliGrid(cond) {{
                ctx.clearRect(0, 0, logicalWidth, logicalHeight);
                distractorItems = [];
                
                let cols = Math.ceil(Math.sqrt(cond.setSize * 2)); 
                let rows = Math.ceil(cond.setSize / cols);
                let cellW = logicalWidth / cols;
                let cellH = logicalHeight / rows;
                
                let positions = [];
                for(let i=0; i<cols; i++) {{
                    for(let j=0; j<rows; j++) {{
                        // Add organic spatial jitter (avoid perfect grid alignment)
                        let jx = (i * cellW) + (cellW/2) + (Math.random() * 20 - 10);
                        let jy = (j * cellH) + (cellH/2) + (Math.random() * 20 - 10);
                        positions.push({{x: jx, y: jy}});
                    }}
                }}
                positions = positions.sort(() => Math.random() - 0.5).slice(0, cond.setSize);
                
                // Pop the last position for the target
                let targetPos = positions.pop();
                targetItem = {{ x: targetPos.x, y: targetPos.y, r: 15, isTarget: true }};
                
                positions.forEach((pos, idx) => {{
                    distractorItems.push({{ x: pos.x, y: pos.y, r: 15, isTarget: false, idx: idx }});
                }});

                // Render based on condition rules
                distractorItems.forEach(d => drawElement(d, cond.type, false));
                drawElement(targetItem, cond.type, true);

                currentPhase = "SEARCH";
                trialStartTime = performance.now();
            }}

            function drawElement(item, condType, isTarget) {{
                ctx.save();
                ctx.translate(item.x, item.y);
                
                if (condType === 'Color') {{
                    ctx.beginPath(); ctx.arc(0, 0, item.r, 0, Math.PI * 2);
                    ctx.fillStyle = isTarget ? "#3B82F6" : "#EF4444";
                    ctx.fill();
                }} 
                else if (condType === 'Shape') {{
                    ctx.fillStyle = "#F8FAFC";
                    ctx.font = "bold 36px monospace"; // Increased by 50%
                    ctx.textAlign = "center";
                    ctx.textBaseline = "middle";
                    ctx.fillText(isTarget ? "O" : "X", 0, 0);
                }} 
                else if (condType === 'Spatial') {{
                    ctx.fillStyle = "#F8FAFC";
                    ctx.font = "bold 36px monospace"; // Increased by 50%
                    ctx.textAlign = "center";
                    ctx.textBaseline = "middle";
                    if (!isTarget) ctx.rotate((Math.floor(Math.random() * 4) * 90) * Math.PI / 180);
                    ctx.fillText(isTarget ? "T" : "L", 0, 0);
                }}
                else if (condType === 'Conjunction') {{
                    // FIX: Draw a full circle first, then overlay the half circle to prevent anti-aliasing gaps
                    if (isTarget) {{
                        ctx.beginPath(); ctx.arc(0, 0, item.r, 0, Math.PI*2); ctx.fillStyle = "#EF4444"; ctx.fill(); // Full Red
                        ctx.beginPath(); ctx.arc(0, 0, item.r, 0, Math.PI); ctx.fillStyle = "#3B82F6"; ctx.fill();   // Blue Bottom
                    }} else {{
                        ctx.beginPath(); ctx.arc(0, 0, item.r, 0, Math.PI*2); ctx.fillStyle = "#3B82F6"; ctx.fill(); // Full Blue
                        ctx.beginPath(); ctx.arc(0, 0, item.r, 0, Math.PI); ctx.fillStyle = "#EF4444"; ctx.fill();   // Red Bottom
                    }}
                }}
                ctx.restore();
            }}

            // Input Listener
            canvas.addEventListener("mousedown", function(e) {{
                if (currentPhase !== "SEARCH") return;

                const rect = canvas.getBoundingClientRect();
                const scaleX = logicalWidth / rect.width;
                const scaleY = logicalHeight / rect.height;
                const mouseX = (e.clientX - rect.left) * scaleX;
                const mouseY = (e.clientY - rect.top) * scaleY;

                // Hit detection (Generous 25px radius bound)
                let dist = Math.hypot(mouseX - targetItem.x, mouseY - targetItem.y);
                if (dist < 25) {{
                    let rt = performance.now() - trialStartTime;
                    document.getElementById("lbl-rt").innerText = Math.round(rt) + " ms";
                    
                    sessionData.push({{
                        condition: trialSequence[currentTrialIdx].type,
                        set_size: trialSequence[currentTrialIdx].setSize,
                        reaction_time: rt
                    }});
                    
                    currentTrialIdx++;
                    nextTrial();
                }} else {{
                    // Flash red for incorrect click, add 500ms penalty
                    canvas.style.backgroundColor = "#7F1D1D";
                    setTimeout(() => canvas.style.backgroundColor = "#1E293B", 150);
                }}
            }});

            function commitSessionData() {{
                if (!db) {{
                    drawHUDMessage("Experiment Complete", "Connect Firebase to log these empirical telemetry metrics.");
                    document.getElementById("btn-start").style.display = "inline";
                    document.getElementById("btn-start").innerText = "Restart Experiment";
                    return;
                }}

                drawHUDMessage("Writing Telemetry...", "Executing blind db.batch() write to Firestore.");

                const batch = db.batch();
                sessionData.forEach(trial => {{
                    const docRef = db.collection('artifacts').doc(appId).collection('public').doc('data').collection('visual_search_trials').doc();
                    batch.set(docRef, {{
                        user_id: userUid,
                        condition: trial.condition,
                        set_size: trial.set_size,
                        reaction_time: trial.reaction_time,
                        timestamp: firebase.firestore.FieldValue.serverTimestamp()
                    }});
                }});

                batch.commit().then(() => {{
                    drawHUDMessage("Data Synced Successfully", "Scroll down to view your cognitive processing analytics.");
                    document.getElementById("btn-start").style.display = "inline";
                    document.getElementById("btn-start").innerText = "Restart Experiment";
                }}).catch(err => drawHUDMessage("Sync Failure", err.message));
            }}
        </script>
    </body>
    </html>
    """
    # 650px height ensures full visibility on all responsive breakpoints
    components.html(html_code, height=650)