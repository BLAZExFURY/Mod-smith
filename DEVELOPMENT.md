# 🛠️ ModSmith Development Guide

Quick reference for developers working on ModSmith.

## 🚀 Quick Start

```bash
# Clone and setup
git clone https://github.com/BLAZExFURY/Mod-smith.git
cd Mod-smith
./setup.sh

# Configure
cp .env.example .env
# Add your GEMINI_API_KEY to .env

# Run
python mod_generator.py
```

## 🧪 Testing

```bash
# Test with different configurations
python mod_generator.py
# Try: 1.20.1, fabric, optimized
# Try: 1.19.2, forge, tech
# Try: 1.18.2, quilt, magic

# Test Ferium integration (requires Ferium installed)
# Answer 'y' when prompted for automatic download
```

## 🔧 Key Components

### Main Classes
- `MinecraftModGenerator` - Core application logic
- `ModInfo` - Data structure for mod information

### Key Methods
- `generate_mod_suggestions()` - AI-powered mod generation
- `validate_mods_with_learning()` - Modrinth API validation
- `download_mods_with_ferium()` - Ferium integration
- `verify_downloaded_mods()` - Post-download verification

### Learning System
- Tracks successful/failed mod searches
- Improves AI prompts over time
- Stores data in `generated/learning_data.json`

## 📝 Adding Features

### New Mod Loader Support
1. Add to `supported_loaders` list
2. Update `get_loader_specific_examples()`
3. Test with that loader's popular mods

### New Minecraft Version
1. Add to `supported_versions` list
2. Test mod availability for that version
3. Update documentation

### Enhanced AI Prompts
1. Modify prompts in `generate_mod_suggestions()`
2. Test with various themes
3. Monitor false suggestion rates

## 🐛 Debugging

### Common Issues
- **No mods found**: Check API key, network connection
- **Ferium fails**: Verify Ferium installation, check paths
- **AI errors**: Check Gemini API status, prompt format

### Debug Outputs
- Comprehensive diagnostics report after each run
- Learning data tracking for continuous improvement
- Detailed error messages with context

### Logging
```python
# Add debug prints
self.print_info("Debug: Your message here")
self.print_warning("Warning: Issue detected")
self.print_error("Error: Something failed")
```

## 📊 Performance

### Optimization Tips
- Rate limiting: 0.2s between API calls
- Timeout handling: All subprocess calls have timeouts
- Caching: Learning system reduces repeated failures
- Efficient search: Multiple search strategies for mod validation

### Monitoring
- Success rates tracked and reported
- API error tracking
- Performance metrics in diagnostics

## 🎯 Best Practices

### Code Style
- Type hints for better IDE support
- Comprehensive error handling
- Clear method documentation
- Consistent naming conventions

### User Experience
- Colored terminal output
- Progress indicators
- Clear error messages
- Helpful suggestions

### Data Safety
- Never commit API keys
- Graceful error handling
- Automatic cleanup (temp profiles)
- User confirmation for destructive actions

## 📈 Future Enhancements

### Potential Features
- Multiple mod platform support
- Modpack export formats (MultiMC, etc.)
- GUI interface
- Mod compatibility checking
- Automated testing

### Integration Ideas
- CI/CD for testing
- Docker containerization
- Web API version
- Discord bot integration

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Test thoroughly
4. Update documentation
5. Submit pull request

Happy coding! 🎉
