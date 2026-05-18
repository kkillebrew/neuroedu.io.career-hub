"""
=============================================================================
MODULE: pages/components/vwm_encoding_demo.py
DESCRIPTION: 
    HTML5 Canvas rendering of the 3Hz and 5Hz visual frequency tags.
=============================================================================
"""
import streamlit.components.v1 as components

def render_vwm_demo():
    html_code = """
    <!DOCTYPE html>
    <html>
    <body style="background-color: #808080; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0;">
        <canvas id="vwmCanvas" width="800" height="400"></canvas>
        <script>
            const canvas = document.getElementById('vwmCanvas');
            const ctx = canvas.getContext('2d');
            const freqLeft = 3;  
            const freqRight = 5; 
            
            function drawLoop(timestamp) {
                const timeSec = timestamp / 1000;
                // MATLAB Bridge: Sine wave contrast modulation
                const contrastLeft = (Math.sin(2 * Math.PI * freqLeft * timeSec) + 1) / 2;
                const contrastRight = (Math.sin(2 * Math.PI * freqRight * timeSec) + 1) / 2;
                
                // Clear screen (Psychtoolbox 'Flip')
                ctx.fillStyle = '#808080';
                ctx.fillRect(0, 0, canvas.width, canvas.height);
                
                // Draw Left Stimulus (3Hz)
                ctx.fillStyle = `rgb(${contrastLeft*255}, ${contrastLeft*255}, ${contrastLeft*255})`;
                ctx.fillRect(200, 150, 100, 100);
                
                // Draw Right Stimulus (5Hz)
                ctx.fillStyle = `rgb(${contrastRight*255}, ${contrastRight*255}, ${contrastRight*255})`;
                ctx.fillRect(500, 150, 100, 100);
                
                // Fixation Cross
                ctx.fillStyle = '#000000';
                ctx.fillRect(390, 198, 20, 4);
                ctx.fillRect(398, 190, 4, 20);
                
                requestAnimationFrame(drawLoop);
            }
            requestAnimationFrame(drawLoop);
        </script>
    </body>
    </html>
    """
    components.html(html_code, height=450)