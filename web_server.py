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

    def download_mod_files_with_ferium(self, valid_mods, mc_version, mod_loader):
        """Download mod files using Ferium directly into generated/gen-mods/ folder"""
        import subprocess
        from pathlib import Path
        
        # Use generated/gen-mods directory for downloads (ensure absolute path for Ferium)
        mods_dir = Path("generated/gen-mods").resolve()
        mods_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            print(f"📥 Downloading {len(valid_mods)} mods using Ferium...")
            print(f"📁 Download directory: {mods_dir}")
            
            # Create unique profile name
            profile_name = f"modsmith-web-{int(time.time())}"
            
            # Create Ferium profile with explicit output directory
            print(f"🔧 Creating Ferium profile: {profile_name}")
            create_cmd = [
                'ferium', 'profile', 'create',
                '--game-version', mc_version,
                '--mod-loader', mod_loader,
                '--output-dir', str(mods_dir),  # Set explicit mods directory
                '--name', profile_name
            ]
            
            print(f"Running: {' '.join(create_cmd)}")
            result = subprocess.run(create_cmd, capture_output=True, text=True, timeout=30)
            if result.returncode != 0:
                print(f"Create command stdout: {result.stdout}")
                print(f"Create command stderr: {result.stderr}")
                raise Exception(f"Failed to create Ferium profile: {result.stderr}")
            
            print(f"✅ Ferium profile created successfully")
            print(f"Profile output: {result.stdout}")
            
            # Switch to the new profile
            print(f"🔄 Switching to profile: {profile_name}")
            switch_cmd = ['ferium', 'profile', 'switch', profile_name]
            result = subprocess.run(switch_cmd, capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                print(f"Switch command stderr: {result.stderr}")
                raise Exception(f"Failed to switch to Ferium profile: {result.stderr}")
            
            # Add all mods to the profile
            print(f"📦 Adding {len(valid_mods)} mods to Ferium profile...")
            successful_adds = 0
            for i, mod in enumerate(valid_mods, 1):
                try:
                    print(f"[{i:2d}/{len(valid_mods):2d}] Adding: {mod.name}")
                    
                    add_cmd = ['ferium', 'add', mod.slug]
                    result = subprocess.run(add_cmd, capture_output=True, text=True, timeout=15)
                    
                    if result.returncode == 0:
                        print(f"    ✓ Added: {mod.name}")
                        successful_adds += 1
                    else:
                        print(f"    ⚠️  Failed to add {mod.name}: {result.stderr.strip()}")
                        
                except Exception as e:
                    print(f"    ❌ Error adding {mod.name}: {e}")
                    continue
            
            if successful_adds == 0:
                raise Exception("No mods were successfully added to Ferium profile")
            
            print(f"✅ Successfully added {successful_adds} mods to profile")
            
            # List profile to verify mods were added
            print(f"🔍 Verifying profile contents...")
            list_cmd = ['ferium', 'list']
            result = subprocess.run(list_cmd, capture_output=True, text=True, timeout=10)
            print(f"Profile contents:\n{result.stdout}")
            
            # Download all mods (including dependencies) with verbose output
            print(f"🚀 Downloading mods with Ferium (this includes dependencies automatically)...")
            download_cmd = ['ferium', 'upgrade']
            print(f"Running: {' '.join(download_cmd)}")
            
            result = subprocess.run(download_cmd, capture_output=True, text=True, timeout=300)  # 5 minute timeout
            
            print(f"Ferium upgrade output:\n{result.stdout}")
            if result.stderr:
                print(f"Ferium upgrade stderr:\n{result.stderr}")
            
            if result.returncode != 0:
                print(f"⚠️  Ferium upgrade had issues (return code: {result.returncode})")
                # Don't fail completely, some mods might still have downloaded
            
            # Check what was downloaded
            downloaded_files = []
            
            print(f"🔍 Checking for downloaded files in: {mods_dir}")
            if mods_dir.exists():
                jar_files = list(mods_dir.glob('*.jar'))
                print(f"Found {len(jar_files)} .jar files")
                
                for jar_file in jar_files:
                    file_size = jar_file.stat().st_size
                    downloaded_files.append({
                        'filename': jar_file.name,
                        'path': jar_file,
                        'size': file_size
                    })
                    print(f"    ✓ Downloaded: {jar_file.name} ({file_size // 1024} KB)")
            else:
                print(f"❌ Mods directory does not exist: {mods_dir}")
            
            # Also check the mods directory root for any additional files
            for jar_file in mods_dir.rglob('*.jar'):
                if jar_file not in [f['path'] for f in downloaded_files]:
                    file_size = jar_file.stat().st_size
                    downloaded_files.append({
                        'filename': jar_file.name,
                        'path': jar_file,
                        'size': file_size
                    })
                    print(f"    ✓ Found additional file: {jar_file.name} ({file_size // 1024} KB)")
            
            print(f"✅ Ferium download complete: {len(downloaded_files)} files found in {mods_dir}")
            
            # Clean up Ferium profile
            try:
                print(f"🧹 Cleaning up Ferium profile: {profile_name}")
                # First switch to a different profile if it exists, then delete
                list_result = subprocess.run(['ferium', 'profile', 'list'], capture_output=True, text=True, timeout=10)
                if 'modsmith-web-' in list_result.stdout:
                    # Try to switch to first available profile that's not ours, or create a dummy one
                    try:
                        subprocess.run(['ferium', 'profile', 'create', '--name', 'temp-cleanup', '--game-version', '1.20.1', '--mod-loader', 'forge'], capture_output=True, text=True, timeout=10)
                        subprocess.run(['ferium', 'profile', 'switch', 'temp-cleanup'], capture_output=True, text=True, timeout=10)
                    except:
                        pass
                
                delete_cmd = ['ferium', 'profile', 'delete', profile_name, '--force']
                delete_result = subprocess.run(delete_cmd, capture_output=True, text=True, timeout=10)
                if delete_result.returncode == 0:
                    print(f"✅ Cleaned up Ferium profile: {profile_name}")
                else:
                    print(f"⚠️  Could not delete profile: {delete_result.stderr}")
                    
                # Clean up temp profile too
                try:
                    subprocess.run(['ferium', 'profile', 'delete', 'temp-cleanup', '--force'], capture_output=True, text=True, timeout=10)
                except:
                    pass
                    
            except Exception as cleanup_error:
                print(f"⚠️  Could not clean up Ferium profile: {cleanup_error}")
            
            if not downloaded_files:
                # Try to get more info about why nothing downloaded
                print("🔍 Debug: Checking Ferium configuration...")
                config_cmd = ['ferium', 'profile', 'list']
                result = subprocess.run(config_cmd, capture_output=True, text=True, timeout=10)
                print(f"Ferium profiles: {result.stdout}")
                
                raise Exception("No mod files were downloaded by Ferium. This could be due to version compatibility issues or network problems.")
            
            return len(downloaded_files) > 0  # Return success status
            
        except subprocess.TimeoutExpired:
            raise Exception("Ferium download timed out (5 minutes). Try with fewer mods or check your internet connection.")
        except FileNotFoundError:
            raise Exception("Ferium not found. Please install Ferium: https://github.com/gorilla-devs/ferium")
        except Exception as e:
            print(f"❌ Error in Ferium download: {e}")
            raise Exception(f"Ferium download failed: {str(e)}")

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
                print(f"🚀 Starting Ferium download in background thread...")
                
                # Get mods data from result
                mods_data = result.get('mods', [])
                if not mods_data:
                    raise Exception("No mods found in result")
                
                print(f"📋 Downloading {len(mods_data)} mods:")
                for mod_data in mods_data:
                    print(f"  - {mod_data['name']} ({mod_data['slug']})")
                
                # Create temporary ModInfo objects for the download function
                class TempMod:
                    def __init__(self, data):
                        self.name = data['name']
                        self.slug = data['slug']
                        self.description = data.get('description', '')
                        self.downloads = data.get('downloads', 0)
                        self.categories = data.get('categories', [])
                
                temp_mods = [TempMod(mod_data) for mod_data in mods_data]
                
                # Use the generator's Ferium download method
                success = generator.download_mod_files_with_ferium(
                    temp_mods,
                    result['mcVersion'],
                    result['modLoader']
                )
                
                print(f"✅ Ferium download completed: Success = {success}")
                
                # Update progress with download result
                generator.progress['ferium_status'] = 'completed' if success else 'failed'
                generator.progress['ferium_success'] = success
                
            except Exception as e:
                print(f"❌ Error in Ferium download thread: {e}")
                import traceback
                traceback.print_exc()
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
