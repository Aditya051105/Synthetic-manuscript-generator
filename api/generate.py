import io
import os
import zipfile
import yaml
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS

from src.utils import set_seed
from src.dataset import find_font, generate_script_images_memory

app = Flask(__name__)
CORS(app)

# Catch both possible Vercel routed paths
@app.route('/api/generate', methods=['POST', 'GET'])
@app.route('/generate', methods=['POST', 'GET'])
def generate_api():
    if request.method == 'GET':
        return jsonify({"status": "API is online. Please use POST to generate datasets."}), 200

    req_data = request.json or {}
    
    script_name = req_data.get('script', 'devanagari')
    count = min(req_data.get('count', 1), 5) # Cap at 5 images for Vercel timeouts
    custom_text = req_data.get('custom_text', None)
    seed = req_data.get('seed', 42)
    
    set_seed(seed)
    
    # Load default config
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'config.yaml')
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
        
    config['generation']['random_seed'] = seed
    
    font_path = find_font(script_name) or ""

    try:
        # Generate images into memory
        results = generate_script_images_memory(config, script_name, count, font_path, custom_text)
        
        # Zip them in memory
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for idx, (img_bytes, text_data) in enumerate(results):
                base_name = f"{script_name}_{idx+1:03d}"
                zip_file.writestr(f"{base_name}.png", img_bytes.getvalue())
                zip_file.writestr(f"{base_name}.md", text_data)
                
        zip_buffer.seek(0)
        return send_file(
            zip_buffer,
            mimetype='application/zip',
            as_attachment=True,
            download_name=f"{script_name}_dataset.zip"
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Vercel requires the app instance to be exported sometimes or just defined in the module.
