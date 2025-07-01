# 🤖 ModSmith - AI-Powered Minecraft Modpack Generator

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Web%20Interface-Flask-red.svg)](https://flask.palletsprojects.com/)
[![Gemini](https://img.shields.io/badge/Powered%20by-Gemini%202.0%20Flash-orange.svg)](https://ai.google.dev/)
[![Modrinth](https://img.shields.io/badge/Validated%20on-Modrinth-green.svg)](https://modrinth.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Generate perfectly curated Minecraft modpacks using AI! ModSmith leverages Google's Gemini 2.0 Flash to intelligently select and validate mods from Modrinth based on your preferences. Now with a **professional web interface** for easy use!

## ✨ Features

- 🌐 **Professional Web Interface**: Modern, responsive UI with real-time progress tracking
- 🧠 **AI-Driven Curation**: Uses Gemini 2.0 Flash for intelligent mod selection
- 🎯 **Theme-Based Generation**: Tech, magic, adventure, or custom themes
- 🔧 **Version & Loader Aware**: Supports all major Minecraft versions and mod loaders
- ✅ **Modrinth Integration**: Validates all mods against Modrinth's database
- 📚 **Learning System**: Improves suggestions over time by learning from failures
- ⚡ **Ferium Integration**: Automatic mod downloads with one-click setup
- 📦 **Ready-to-Use Output**: Generates mod lists and downloads .jar files
- 🔄 **Real-Time Progress**: Live updates during generation with animated progress bars
- 📥 **Multiple Download Options**: Download mod lists, summaries, and actual .jar files
- 🎨 **Beautiful UI**: Dark theme with gradients, animations, and professional design
- 📊 **Comprehensive Diagnostics**: Clear insights into AI performance and failure attribution

## 🚀 Quick Start

### Option 1: Web Interface (Recommended)

1. **Clone & Setup**:
```bash
git clone https://github.com/BLAZExFURY/Mod-smith.git
cd Mod-smith
chmod +x start_web.sh
```

2. **Configure API Key**:
```bash
cp .env.example .env
# Edit .env and add your Gemini API key:
# GEMINI_API_KEY=your_api_key_here
```

3. **Launch Web Interface**:
```bash
./start_web.sh
```

The web interface will be available at `http://localhost:5000`

**Web Interface Features:**
- 🎨 Beautiful, responsive design with dark theme
- ⚡ Real-time progress tracking with animated steps
- 📊 Live progress bars and status updates
- 📥 Multiple download options (mod lists, summaries, .jar files)
- 🔄 Session-based generation with progress persistence
- 📱 Mobile-friendly responsive design

### Option 2: Command Line Interface

1. **Install Dependencies**:
```bash
pip install -r requirements.txt
```

2. **Setup API Key** (same as above)

3. **Generate Your Modpack**:
```bash
python mod_generator.py
```

Get your free Gemini API key: [Google AI Studio](https://makersuite.google.com/app/apikey)

## 🌐 Web Interface

The web interface provides a modern, user-friendly way to generate modpacks:

### Features:
- **🎨 Modern Design**: Professional dark theme with gradients and animations
- **📱 Responsive**: Works perfectly on desktop, tablet, and mobile devices
- **⚡ Real-Time Updates**: Live progress tracking with animated progress bars
- **🔄 Session Management**: Your progress is saved and can be resumed
- **📥 Multiple Downloads**: Get mod lists, summaries, or actual .jar files
- **🎯 Smart Forms**: Dropdown menus with popular options and validation
- **🔍 Progress Visualization**: Animated steps showing current generation phase

### Web Interface Screenshots:
- Beautiful hero section with gradient background
- Interactive configuration form with smart defaults
- Real-time progress tracking with animated steps
- Results dashboard with multiple download options
- Professional download cards for different file types

### API Endpoints:
The web interface uses a REST API with the following endpoints:
- `POST /api/generate` - Start modpack generation
- `GET /api/progress/<session_id>` - Get real-time progress
- `GET /api/download/<file_type>/<session_id>` - Download files
- `GET /api/download-mods/<session_id>` - Download mod .jar files as ZIP

## 🎮 Usage Example

```
Welcome to ModSmith - Your AI-Powered Mod Curator!

Enter Minecraft version: 1.20.1
Enter mod loader: fabric  
Enter modpack theme: tech automation

🎯 Configuration Summary:
   Minecraft Version: 1.20.1
   Mod Loader: Fabric
   Theme: tech automation

🤖 Generating mod suggestions using AI...
✓ Generated 24 mod suggestions!
🔍 Validating mods against Modrinth database...
✓ Found 22 valid mods out of 24 suggestions

🎉 Successfully generated a tech automation modpack!
   • 22 mods found and validated
   • Ready for installation with Ferium
   • Check generated/gen-mods.txt for the mod list

🔽 Ferium Integration Available!
Download mods automatically with Ferium? (y/N): y

🔽 Downloading mods with Ferium...
Creating temporary Ferium profile: modsmith-temp-1234567890
Adding 22 mods to profile...
[22/22] Adding: create                        ✓ Added
📥 Downloading mods...
✓ Downloaded 22 mod files to generated/gen-mods/

📦 Mod Download Complete!
   • Mods saved to: generated/gen-mods/
   • Copy .jar files to your Minecraft mods folder
```

## 📁 Output Files

All generated files are saved in the `generated/` folder:

| File/Folder | Description |
|-------------|-------------|
| `gen-mods.txt` | Mod slugs for Ferium installation |
| `gen-mods/` | Downloaded .jar files (when using Ferium integration) |
| `modpack-details.json` | Complete mod information and metadata |
| `modpack-summary.md` | Human-readable summary with installation guide |
| `learning_data.json` | AI learning data for improved future suggestions |

## 🌐 Web Interface Files

| File/Folder | Description |
|-------------|-------------|
| `web/index.html` | Main web interface with modern UI |
| `web_server.py` | Flask backend API server |
| `start_web.sh` | Quick start script for web interface |
| `sessions/` | Session data for web interface progress tracking |

### Download Options (Web Interface):
- **📄 Mod List**: Download `gen-mods.txt` for manual installation
- **📋 Summary**: Download `modpack-summary.md` with detailed information
- **📦 Mod Files**: Download actual .jar files as a ZIP archive
- **📊 Details**: Download `modpack-details.json` with complete metadata

## ⚡ Automatic Mod Downloads

ModSmith can automatically download mods using [Ferium](https://github.com/gorilla-devs/ferium):

### Quick Setup
```bash
# Install Ferium (choose one method)
cargo install ferium              # Rust/Cargo
brew install ferium              # macOS Homebrew  
# Or download from: https://github.com/gorilla-devs/ferium/releases

# Run ModSmith - it will offer to download mods automatically!
python mod_generator.py
```

### What Happens:
1. 🤖 ModSmith generates your modpack
2. 🔍 Detects if Ferium is installed
3. 💬 Asks if you want automatic download
4. 📥 Downloads all mods to `generated/gen-mods/`
5. 📂 Copy .jar files to your Minecraft mods folder

## ⚡ Manual Install with Ferium

If you prefer manual control or automatic download fails:

```bash
# Create a new profile
ferium profile create

# Add all mods from ModSmith
cat generated/gen-mods.txt | grep -v '^#' | xargs -I {} ferium add {}

# Download mods to your mods folder
ferium upgrade
```

## 🛠️ Supported Platforms

| Category | Supported |
|----------|-----------|
| **Minecraft Versions** | 1.12.2, 1.16.4, 1.16.5, 1.17.1, 1.18, 1.18.1, 1.18.2, 1.19, 1.19.2, 1.19.4, 1.20, 1.20.1, 1.20.2, 1.20.4, 1.20.6, 1.21, 1.21.1 |
| **Mod Loaders** | Fabric, Forge, Quilt, NeoForge |
| **Mod Platform** | Modrinth (primary validation) |

## 🔍 AI Diagnostics

ModSmith includes comprehensive diagnostics to track AI performance:

```
🔍 DIAGNOSTICS REPORT
============================================================
📊 OVERALL STATISTICS
  Total mod suggestions processed: 24
  Successfully found and added: 22
  Success rate: 91.7%

🤖 GEMINI FALSE SUGGESTIONS
  Mods suggested by Gemini that don't exist on Modrinth:
    • OutdatedMod
    • WrongPlatformMod
  Gemini false suggestion rate: 8.3%

💡 RECOMMENDATIONS
  🟢 LOW FALSE SUGGESTION RATE (8.3%)
     • Gemini is performing well with current prompts
```

## 🧠 How It Works

1. **🎯 User Input**: Specify Minecraft version, mod loader, and theme
2. **🤖 AI Generation**: Gemini 2.0 Flash generates contextual mod suggestions
3. **✅ Validation**: Each suggestion is validated against Modrinth's API
4. **📚 Learning**: Failed suggestions are remembered and avoided in future runs
5. **📦 Output**: Clean, ready-to-use mod lists in multiple formats

## 🔧 Requirements

- **Python**: 3.8 or higher
- **API Key**: Google Gemini API key ([Get one free](https://makersuite.google.com/app/apikey))
- **Internet**: Required for API calls and mod validation

## 📦 Dependencies

```
google-generativeai>=0.3.0
requests>=2.28.0
colorama>=0.4.6
python-dotenv>=0.19.0
flask>=2.0.0
flask-cors>=3.0.0
```

### For Web Interface:
- **Flask**: Web framework for the REST API
- **Flask-CORS**: Cross-origin resource sharing support
- **Werkzeug**: WSGI utilities for file handling

## 🎨 Themes & Examples

ModSmith works with any theme! Here are some popular examples:

| Theme | Example Mods Generated |
|-------|----------------------|
| **Tech & Automation** | Create, Applied Energistics 2, Thermal Expansion, Mekanism |
| **Magic & Mysticism** | Botania, Blood Magic, Ars Nouveau, Mystical Agriculture |
| **Adventure & Exploration** | Twilight Forest, Alex's Mobs, When Dungeons Arise, Biomes O' Plenty |
| **Performance & Optimization** | Sodium, Lithium, FerriteCore, LazyDFU |
| **Quality of Life** | JEI, Waystones, Iron Chests, Storage Drawers |

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🌟 Acknowledgments

- **[Google Gemini](https://ai.google.dev/)** - For providing the AI that powers intelligent mod curation
- **[Modrinth](https://modrinth.com)** - For the excellent mod platform and API
- **[Ferium](https://github.com/gorilla-devs/ferium)** - For the best Minecraft mod manager
- **Minecraft Modding Community** - For creating amazing mods that make this possible

## 🐛 Issues & Support

Found a bug or have a feature request? Please [open an issue](https://github.com/BLAZExFURY/Mod-smith/issues) on GitHub.

### 🔧 Troubleshooting

**Web Interface Issues:**
- If the web server won't start, ensure port 5000 is available
- Check that all dependencies are installed: `pip install -r requirements.txt`
- Verify your Gemini API key is set in the `.env` file
- For permission issues, run: `chmod +x start_web.sh`

**Common Solutions:**
- **Import Errors**: Activate virtual environment or reinstall dependencies
- **API Errors**: Check your Gemini API key and internet connection
- **Ferium Issues**: Ensure Ferium is installed and accessible in PATH
- **Download Issues**: Check file permissions in the `generated/` folder

### 📚 Documentation

For detailed documentation, see:
- [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) - Project organization and architecture
- [DEVELOPMENT.md](DEVELOPMENT.md) - Development setup and contribution guide
- [WEB_INTERFACE.md](WEB_INTERFACE.md) - Web interface technical details

---

⭐ **If ModSmith helps you create amazing modpacks, consider giving it a star!** ⭐