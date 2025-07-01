#!/usr/bin/env python3
"""
ModSmith Web Backend - Flask API for the web interface
Connects the beautiful frontend with the AI-powered modpack generation
"""

from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import os
import sys
import json
import threading
import time
from pathlib import Path
import zipfile
import io
import requests
import tempfile
import shutil
from urllib.parse import urlparse

# Import our existing ModSmith logic
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from mod_generator import MinecraftModGenerator

app = Flask(__name__, static_folder='web', static_url_path='')
CORS(app)

# Global storage for active generation sessions
active_sessions = {}

class WebModGenerator(MinecraftModGenerator):
    """Extended ModGenerator for web interface with progress tracking"""
    
    def __init__(self, session_id):
        super().__init__()
        self.session_id = session_id
        self.progress = {
            'step': 0,
            'total_steps': 5,
            'current_step': 'Initializing...',
            'percentage': 0,
            'status': 'starting',
            'details': [],
            'error': None
        }
        active_sessions[session_id] = self 
    
    def update_progress(self, step, step_name, percentage, details=None):
        """Update progress for web interface"""
        self.progress.update({
            'step': step,
            'current_step': step_name,
            'percentage': percentage,
            'status': 'processing'
        })
        if details:
            self.progress['details'].append(details)
    
    def web_generate_modpack(self, mc_version, mod_loader, theme):
        """Generate modpack with web progress tracking"""
        try:
            self.update_progress(1, 'Initializing AI system...', 10)
            time.sleep(1)  # Simulate processing time
            
            self.update_progress(2, 'Generating mod suggestions...', 30)
            mod_suggestions = self.generate_mod_suggestions(mc_version, mod_loader, theme)
            
            if not mod_suggestions:
                raise Exception("No mod suggestions generated")
            
            self.update_progress(3, 'Validating mods against Modrinth...', 70)
            
            # Store original mod count to track failures
            original_suggestions = mod_suggestions.copy()
            
            valid_mods = self.validate_mods(mod_suggestions, mc_version, mod_loader, theme)
            
            if not valid_mods:
                raise Exception("No valid mods found")
            
            # Calculate failed mods
            valid_mod_names = {mod.name.lower() for mod in valid_mods}
            failed_mods = []
            
            for suggestion in original_suggestions:
                suggestion_lower = suggestion.lower()
                # Check if this suggestion wasn't found in valid mods
                if not any(suggestion_lower in valid_name or valid_name in suggestion_lower 
                          for valid_name in valid_mod_names):
                    failed_mods.append(suggestion)
            
            self.update_progress(4, 'Creating output files...', 90)
            self.generate_output_files(valid_mods, mc_version, mod_loader, theme)
            
            self.update_progress(5, 'Completed successfully!', 100)
            
            # Prepare result data
            result = {
                'success': True,
                'theme': theme,
                'mcVersion': mc_version,
                'modLoader': mod_loader,
                'totalMods': len(valid_mods),
                'successRate': round((len(valid_mods) / len(original_suggestions)) * 100) if original_suggestions else 0,
                'mods': [
                    {
                        'name': mod.name,
                        'slug': mod.slug,
                        'description': mod.description,
                        'downloads': mod.downloads,
                        'categories': mod.categories
                    } for mod in valid_mods
                ],
                'failedMods': failed_mods,  # Include failed mods in response
                'generatedAt': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            self.progress['status'] = 'completed'
            self.progress['result'] = result
            
            return result
            
        except Exception as e:
            self.progress['status'] = 'error'
            self.progress['error'] = str(e)
            raise e

    def download_mod_files(self, valid_mods, mc_version, mod_loader):
        """Download actual mod .jar files from Modrinth"""
        downloaded_files = []
        temp_dir = Path(tempfile.mkdtemp(prefix='modsmith_mods_'))
        
        try:
            print(f"📥 Downloading {len(valid_mods)} mod files...")
            
            for i, mod in enumerate(valid_mods, 1):
                try:
                    print(f"[{i:2d}/{len(valid_mods):2d}] Downloading: {mod.name}")
                    
                    # Get mod versions from Modrinth
                    versions_url = f"https://api.modrinth.com/v2/project/{mod.slug}/version"
                    params = {
                        'game_versions': f'["{mc_version}"]',
                        'loaders': f'["{mod_loader}"]'
                    }
                    
                    response = requests.get(versions_url, params=params, timeout=10)
                    if response.status_code != 200:
                        print(f"    ⚠️  Failed to get versions for {mod.name}")
                        continue
                    
                    versions = response.json()
                    if not versions:
                        print(f"    ⚠️  No compatible versions found for {mod.name}")
                        continue
                    
                    # Get the latest version
                    latest_version = versions[0]
                    
                    # Find the primary file (usually the main mod file)
                    primary_file = None
                    for file_info in latest_version.get('files', []):
                        if file_info.get('primary', False):
                            primary_file = file_info
                            break
                    
                    # If no primary file, use the first file
                    if not primary_file and latest_version.get('files'):
                        primary_file = latest_version['files'][0]
                    
                    if not primary_file:
                        print(f"    ⚠️  No download file found for {mod.name}")
                        continue
                    
                    # Download the file
                    download_url = primary_file['url']
                    filename = primary_file['filename']
                    
                    file_response = requests.get(download_url, timeout=30)
                    if file_response.status_code == 200:
                        file_path = temp_dir / filename
                        with open(file_path, 'wb') as f:
                            f.write(file_response.content)
                        
                        downloaded_files.append({
                            'mod': mod,
                            'filename': filename,
                            'path': file_path,
                            'size': len(file_response.content)
                        })
                        print(f"    ✓ Downloaded: {filename} ({len(file_response.content) // 1024} KB)")
                    else:
                        print(f"    ⚠️  Failed to download {mod.name}")
                        
                except Exception as e:
                    print(f"    ❌ Error downloading {mod.name}: {e}")
                    continue
            
            print(f"✓ Successfully downloaded {len(downloaded_files)} out of {len(valid_mods)} mods")
            return downloaded_files, temp_dir
            
        except Exception as e:
            print(f"❌ Error in mod downloading: {e}")
            # Clean up temp directory on error
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
            return [], None

@app.route('/')
def index():
    """Serve the main web interface"""
    return send_file('web/index.html')

@app.route('/api/generate', methods=['POST'])
def generate_modpack():
    """Start modpack generation"""
    try:
        data = request.get_json()
        
        # Validate input
        required_fields = ['mcVersion', 'modLoader', 'theme']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Create unique session ID
        session_id = f"session_{int(time.time() * 1000)}"
        
        # Create generator instance
        generator = WebModGenerator(session_id)
        
        # Start generation in background thread
        def generate():
            try:
                generator.web_generate_modpack(
                    data['mcVersion'],
                    data['modLoader'],
                    data['theme']
                )
            except Exception as e:
                print(f"Generation error: {e}")
        
        thread = threading.Thread(target=generate)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'message': 'Generation started'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/progress/<session_id>')
def get_progress(session_id):
    """Get generation progress"""
    try:
        if session_id not in active_sessions:
            return jsonify({'error': 'Session not found'}), 404
        
        generator = active_sessions[session_id]
        return jsonify(generator.progress)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/download/<session_id>/<file_type>')
def download_file(session_id, file_type):
    """Download generated files"""
    try:
        if session_id not in active_sessions:
            return jsonify({'error': 'Session not found'}), 404
        
        generator = active_sessions[session_id]
        
        if generator.progress['status'] != 'completed':
            return jsonify({'error': 'Generation not completed'}), 400
        
        generated_dir = Path("generated")
        
        if file_type == 'mods':
            # Return gen-mods.txt
            file_path = generated_dir / 'gen-mods.txt'
            if file_path.exists():
                return send_file(file_path, as_attachment=True, download_name='gen-mods.txt')
        
        elif file_type == 'details':
            # Return modpack-details.json
            file_path = generated_dir / 'modpack-details.json'
            if file_path.exists():
                return send_file(file_path, as_attachment=True, download_name='modpack-details.json')
        
        elif file_type == 'summary':
            # Return modpack-summary.md
            file_path = generated_dir / 'modpack-summary.md'
            if file_path.exists():
                return send_file(file_path, as_attachment=True, download_name='modpack-summary.md')
        
        elif file_type == 'mod-files':
            # Download actual mod .jar files and create ZIP
            print(f"🔄 Starting mod files download for session {session_id}")
            
            result = generator.progress.get('result')
            if not result:
                print("❌ No result data available")
                return jsonify({'error': 'No result data available'}), 400
            
            # Get mod data from the result
            mods_data = result.get('mods', [])
            if not mods_data:
                print("❌ No mods found in result")
                return jsonify({'error': 'No mods found in result'}), 400
            
            print(f"📋 Found {len(mods_data)} mods to download")
            
            # Create temporary mod objects for downloading
            class TempMod:
                def __init__(self, data):
                    self.name = data['name']
                    self.slug = data['slug']
                    self.description = data.get('description', '')
                    self.downloads = data.get('downloads', 0)
                    self.categories = data.get('categories', [])
            
            temp_mods = [TempMod(mod_data) for mod_data in mods_data]
            
            # Download mod files
            print(f"🚀 Starting download of mod files...")
            downloaded_files, temp_dir = generator.download_mod_files(
                temp_mods, 
                result['mcVersion'], 
                result['modLoader']
            )
            
            if not downloaded_files:
                print("❌ Failed to download any mod files")
                return jsonify({'error': 'Failed to download any mod files'}), 500
            
            print(f"✅ Downloaded {len(downloaded_files)} mod files successfully")
            
            try:
                # Create ZIP with downloaded mod files
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                    # Add each downloaded mod file
                    for file_info in downloaded_files:
                        zip_file.write(file_info['path'], f"mods/{file_info['filename']}")
                    
                    # Add modpack info file
                    info_content = f"""# ModSmith Generated Modpack
Theme: {result['theme']}
Minecraft Version: {result['mcVersion']}
Mod Loader: {result['modLoader']}
Total Mods: {len(downloaded_files)}
Generated: {result['generatedAt']}

## Downloaded Mods:
"""
                    for file_info in downloaded_files:
                        mod = file_info['mod']
                        info_content += f"- {mod.name} ({file_info['filename']}) - {file_info['size'] // 1024} KB\n"
                    
                    zip_file.writestr('README.txt', info_content)
                
                # Clean up temp directory
                if temp_dir and temp_dir.exists():
                    shutil.rmtree(temp_dir)
                
                zip_buffer.seek(0)
                return send_file(
                    io.BytesIO(zip_buffer.read()),
                    mimetype='application/zip',
                    as_attachment=True,
                    download_name=f'modpack-{result["theme"]}-{result["mcVersion"]}.zip'
                )
                
            except Exception as e:
                # Clean up temp directory on error
                if temp_dir and temp_dir.exists():
                    shutil.rmtree(temp_dir)
                return jsonify({'error': f'Failed to create mod files ZIP: {str(e)}'}), 500

        elif file_type == 'all':
            # Create zip with all files
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for file_path in generated_dir.glob('*.txt'):
                    zip_file.write(file_path, file_path.name)
                for file_path in generated_dir.glob('*.json'):
                    zip_file.write(file_path, file_path.name)
                for file_path in generated_dir.glob('*.md'):
                    zip_file.write(file_path, file_path.name)
            
            zip_buffer.seek(0)
            return send_file(
                io.BytesIO(zip_buffer.read()),
                mimetype='application/zip',
                as_attachment=True,
                download_name='modpack-complete.zip'
            )
        
        return jsonify({'error': 'File not found'}), 404
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ferium/<session_id>', methods=['POST'])
def start_ferium_download(session_id):
    """Start Ferium download process"""
    try:
        if session_id not in active_sessions:
            return jsonify({'error': 'Session not found'}), 404
        
        generator = active_sessions[session_id]
        
        if generator.progress['status'] != 'completed':
            return jsonify({'error': 'Generation not completed'}), 400
        
        # Get the result data
        result = generator.progress.get('result')
        if not result:
            return jsonify({'error': 'No result data available'}), 400
        
        # Check if Ferium is installed
        if not generator.check_ferium_installed():
            return jsonify({
                'error': 'Ferium not installed',
                'message': 'Please install Ferium from https://github.com/gorilla-devs/ferium'
            }), 400
        
        # Start Ferium download in background
        def start_download():
            try:
                gen_mods_path = Path("generated/gen-mods.txt")
                success = generator.download_mods_with_ferium(
                    gen_mods_path,
                    result['mc_version'],
                    result['mod_loader']
                )
                
                # Update progress with download result
                generator.progress['ferium_status'] = 'completed' if success else 'failed'
                generator.progress['ferium_success'] = success
                
            except Exception as e:
                generator.progress['ferium_status'] = 'error'
                generator.progress['ferium_error'] = str(e)
        
        thread = threading.Thread(target=start_download)
        thread.daemon = True
        thread.start()
        
        generator.progress['ferium_status'] = 'downloading'
        
        return jsonify({
            'success': True,
            'message': 'Ferium download started'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cleanup/<session_id>', methods=['POST'])
def cleanup_session(session_id):
    """Clean up session data"""
    try:
        if session_id in active_sessions:
            del active_sessions[session_id]
        
        return jsonify({'success': True, 'message': 'Session cleaned up'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    return send_file('web/index.html')

if __name__ == '__main__':
    print("🚀 Starting ModSmith Web Server...")
    print("📱 Web Interface: http://localhost:5000")
    print("🔧 API Endpoints: http://localhost:5000/api/")
    print("✨ Features: Real-time progress, Ferium integration, File downloads")
    
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
