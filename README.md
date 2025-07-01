# 🤖 ModSmith - AI-Powered Minecraft Modpack Generator

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Gemini](https://img.shields.io/badge/Powered%20by-Gemini%202.0%20Flash-orange.svg)](https://ai.google.dev/)
[![Modrinth](https://img.shields.io/badge/Validated%20on-Modrinth-green.svg)](https://modrinth.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Generate perfectly curated Minecraft modpacks using AI! ModSmith leverages Google's Gemini 2.0 Flash to intelligently select and validate mods from Modrinth based on your preferences.

## ✨ Features

- 🧠 **AI-Driven Curation**: Uses Gemini 2.0 Flash for intelligent mod selection
- 🎯 **Theme-Based Generation**: Tech, magic, adventure, or custom themes
- 🔧 **Version & Loader Aware**: Supports all major Minecraft versions and mod loaders
- ✅ **Modrinth Integration**: Validates all mods against Modrinth's database
- 📚 **Learning System**: Improves suggestions over time by learning from failures
- ⚡ **Ferium Compatible**: Generates ready-to-use mod lists for Ferium
- 📊 **Comprehensive Diagnostics**: Clear insights into AI performance and failure attribution

## 🚀 Quick Start

### 1. Clone & Install
```bash
git clone https://github.com/blazexfury/modsmith.git
cd modsmith
pip install -r requirements.txt
```

### 2. Setup API Key
```bash
cp .env.example .env
# Edit .env and add your Gemini API key:
# GEMINI_API_KEY=your_api_key_here
```

Get your free Gemini API key: [Google AI Studio](https://makersuite.google.com/app/apikey)

### 3. Generate Your Modpack
```bash
python mod_generator.py
```

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
```

## 📁 Output Files

All generated files are saved in the `generated/` folder:

| File | Description |
|------|-------------|
| `gen-mods.txt` | Mod slugs for Ferium installation |
| `modpack-details.json` | Complete mod information and metadata |
| `modpack-summary.md` | Human-readable summary with installation guide |
| `learning_data.json` | AI learning data for improved future suggestions |

## ⚡ Install with Ferium

[Ferium](https://github.com/gorilla-devs/ferium) is the fastest way to install your generated modpack:

```bash
# Install Ferium (one-time setup)
cargo install ferium

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
```

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

Found a bug or have a feature request? Please [open an issue](https://github.com/your-username/modsmith/issues) on GitHub.

---

⭐ **If ModSmith helps you create amazing modpacks, consider giving it a star!** ⭐