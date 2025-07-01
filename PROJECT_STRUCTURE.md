# 📁 ModSmith Project Structure

This document outlines the organization and structure of the ModSmith project.

## 🏗️ Project Layout

```
Mod-smith/
├── 📄 README.md                 # Main project documentation
├── 📄 LICENSE                   # MIT License
├── 📄 requirements.txt          # Python dependencies
├── 📄 setup.sh                  # Auto-setup script
├── 🐍 mod_generator.py          # Main application
├── 🔧 .env.example              # Environment template
├── 🔧 .gitignore               # Git exclusions
├── 📁 generated/               # Output files (auto-created)
│   └── 📄 .gitkeep             # Keeps folder in Git
└── 📁 .git/                    # Git repository data
```

## 📝 File Descriptions

### Core Files
- **`mod_generator.py`** - Main Python application with AI-powered mod generation and Ferium integration
- **`requirements.txt`** - Python package dependencies for the project
- **`setup.sh`** - Automated setup script for dependencies and environment
- **`README.md`** - Comprehensive project documentation with usage examples

### Configuration
- **`.env.example`** - Template for environment variables (copy to `.env` and add your API key)
- **`.gitignore`** - Specifies files and folders to exclude from Git tracking

### Generated Output (created during runtime)
- **`generated/gen-mods.txt`** - Ferium-compatible mod slug list
- **`generated/modpack-details.json`** - Detailed mod information and metadata
- **`generated/modpack-summary.md`** - Human-readable modpack summary
- **`generated/learning_data.json`** - AI learning data for improved suggestions
- **`generated/gen-mods/`** - Downloaded mod JAR files (when using Ferium)
- **`generated/download-report.txt`** - Detailed download verification report

## 🎯 Usage Flow

1. **Setup**: Run `./setup.sh` to install dependencies
2. **Configure**: Copy `.env.example` to `.env` and add Gemini API key
3. **Generate**: Run `python mod_generator.py`
4. **Input**: Specify Minecraft version, mod loader, and theme
5. **AI Processing**: ModSmith generates and validates mods
6. **Download**: Optionally use Ferium integration for automatic downloads
7. **Output**: Find all generated files in `generated/` folder

## 🧹 Maintenance

### Clean Generated Files
```bash
rm -f generated/*.txt generated/*.json generated/*.md
rm -rf generated/gen-mods/
```

### Reset Learning Data
```bash
rm -f generated/learning_data.json
```

### Update Dependencies
```bash
pip install -r requirements.txt --upgrade
```

## 📊 Project Statistics

- **Main Script**: ~1000 lines of Python code
- **Features**: AI generation, Modrinth validation, Ferium integration, learning system
- **Supported Loaders**: Fabric, Forge, Quilt, NeoForge
- **Supported Versions**: 1.12.2 to 1.21.1
- **Output Formats**: TXT, JSON, Markdown

## 🔄 Version Control

The project uses Git with the following exclusions:
- Generated mod files (`generated/gen-mods/`)
- Python cache (`__pycache__/`)
- Virtual environments (`venv/`, `env/`, `mc/`)
- Environment variables (`.env`)
- Log files (`*.log`)

## 🎉 Ready for Use!

The project is clean, organized, and ready for:
- ✅ Development and contributions
- ✅ Public distribution
- ✅ End-user adoption
- ✅ Automated workflows
