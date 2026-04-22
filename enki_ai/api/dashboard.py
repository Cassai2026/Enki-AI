from flask import Flask, render_template_string
import json

app = Flask(__name__)

@app.route('/')
def index():
    # Fetching the 'Official' state from the Manifest and the 7 Equations
    with open('enki_ai/manifest.json', 'r') as f: manifest = json.load(f)
    
    html = """
    <html>
        <head><title>ENKI AI | Sovereign Dashboard</title></head>
        <body style="background:#000; color:#0f0; font-family:monospace; padding:50px;">
            <h1>🏛️ ENKI AI: SOVEREIGN STATE v{{v}}</h1>
            <hr>
            <h3>GENESIS STATUS: {{status}}</h3>
            <ul>
                <li>CORE: {{layers.core}}</li>
                <li>GOVERNANCE: {{layers.governance}}</li>
                <li>NODES: 128 Active</li>
            </ul>
            <hr>
            <h3>7 SUMERIAN EQUATIONS: OPTIMAL</h3>
            <p>OUSH. <3</p>
        </body>
    </html>
    """
    return render_template_string(html, **manifest)

if __name__ == "__main__":
    app.run(port=5000)
