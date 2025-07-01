#!/usr/bin/env python3
"""
Minecraft Mod Generator - A tool to generate curated modpacks using AI
Author: ModSmith Team
Description: Uses Google Gemini API to generate relevant mods based on theme, 
             Minecraft version, and mod loader, then validates them against Modrinth API
"""

import os
import sys
import json
import time
import requests
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from dotenv import load_dotenv
import google.generativeai as genai
from colorama import init, Fore, Back, Style
import re

# Initialize colorama for cross-platform colored output
init(autoreset=True)

# Load environment variables
load_dotenv()

@dataclass
class ModInfo:
    """Data class to store mod information"""
    name: str
    slug: str
    description: str
    mod_id: str
    categories: List[str]
    downloads: int
    updated: str
    versions: List[str]
    loaders: List[str]
    
class MinecraftModGenerator:
    """Main class for generating Minecraft mod recommendations"""
    
    def __init__(self):
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        self.modrinth_base_url = "https://api.modrinth.com/v2"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'ModSmith/1.0 (https://github.com/your-username/mod-smith)'
        })
        
        # Track successful and failed mod searches for learning
        self.successful_mods = set()
        self.failed_mods = set()
        
        # Enhanced diagnostics tracking
        self.gemini_false_suggestions = set()  # Mods Gemini suggested but don't exist
        self.api_errors = []  # Network/API issues during validation
        self.version_incompatible = []  # Mods that exist but don't support version/loader
        # Load previously learned data
        self.load_learning_data()
        self.gemini_suggestions_history = []  # Track all Gemini suggestions
        self.validation_failures = {
            'not_found': [],      # Mod doesn't exist at all
            'wrong_loader': [],   # Exists but wrong loader
            'wrong_version': [],  # Exists but wrong version
            'api_errors': []      # Network/API issues
        }
        self.gemini_quality_score = 0.0  # Track Gemini's accuracy over time
        
        # Initialize Gemini
        if not self.gemini_api_key:
            self.print_error("GEMINI_API_KEY not found in environment variables!")
            self.print_info("Please create a .env file with your Gemini API key:")
            self.print_info("GEMINI_API_KEY=your_api_key_here")
            sys.exit(1)
            
        genai.configure(api_key=self.gemini_api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Supported versions and loaders
        self.supported_versions = [
            "1.21.1", "1.21", "1.20.6", "1.20.4", "1.20.2", "1.20.1", "1.20",
            "1.19.4", "1.19.2", "1.19", "1.18.2", "1.18.1", "1.18", "1.17.1",
            "1.16.5", "1.16.4", "1.12.2"
        ]
        
        self.supported_loaders = [
            "fabric", "forge", "quilt", "neoforge"
        ]
        
        # Load previous learning data
        self.load_learning_data()
    
    def print_header(self, text: str):
        """Print styled header"""
        print(f"\n{Fore.CYAN}{Style.BRIGHT}{'='*60}")
        print(f"{Fore.CYAN}{Style.BRIGHT}{text.center(60)}")
        print(f"{Fore.CYAN}{Style.BRIGHT}{'='*60}")
        
    def print_success(self, text: str):
        """Print success message"""
        print(f"{Fore.GREEN}{Style.BRIGHT}✓ {text}")
        
    def print_error(self, text: str):
        """Print error message"""
        print(f"{Fore.RED}{Style.BRIGHT}✗ {text}")
        
    def print_warning(self, text: str):
        """Print warning message"""
        print(f"{Fore.YELLOW}{Style.BRIGHT}⚠ {text}")
        
    def print_info(self, text: str):
        """Print info message"""
        print(f"{Fore.BLUE}{Style.BRIGHT}ℹ {text}")
        
    def get_user_input(self) -> Tuple[str, str, str]:
        """Get user input for mod generation"""
        self.print_header("MINECRAFT MOD GENERATOR")
        
        print(f"{Fore.MAGENTA}{Style.BRIGHT}Welcome to ModSmith - Your AI-Powered Mod Curator!")
        print(f"{Fore.WHITE}Generate the perfect modpack tailored to your preferences\n")
        
        # Get Minecraft version
        while True:
            choice = input(f"\n{Fore.YELLOW}Enter Minecraft version (e.g., 1.20.1, 1.19.2): {Style.RESET_ALL}").strip()
            
            # Check if it's a direct version match
            if choice in self.supported_versions:
                mc_version = choice
                break
            else:
                self.print_error(f"'{choice}' is not supported. Supported versions: {', '.join(self.supported_versions[:5])}... (and more)")
        
        # Get mod loader
        while True:
            choice = input(f"\n{Fore.YELLOW}Enter mod loader (fabric, forge, quilt, neoforge): {Style.RESET_ALL}").strip().lower()
            
            # Check if it's a direct loader match
            if choice in self.supported_loaders:
                mod_loader = choice
                break
            else:
                self.print_error(f"'{choice}' is not supported. Available: {', '.join(self.supported_loaders)}")
        
        # Get theme
        theme = input(f"\n{Fore.YELLOW}Enter modpack theme (e.g., tech, magic, adventure, or custom): {Style.RESET_ALL}").strip()
        
        # If empty, default to a general theme
        if not theme:
            theme = "General Minecraft Enhancement"
        
        return mc_version, mod_loader, theme
    
    def generate_mod_suggestions(self, mc_version: str, mod_loader: str, theme: str) -> List[str]:
        """Use Gemini to generate mod suggestions based on theme, version, and loader"""
        
        self.print_info("🤖 Generating mod suggestions using AI...")
        
        # Get context-specific examples
        loader_examples = self.get_loader_specific_examples(mod_loader, mc_version)
        
        # Add learning context from previous searches
        learning_context = self.get_learning_context(mod_loader)
        
        prompt = f"""
        You are an expert Minecraft modpack curator with comprehensive knowledge of Modrinth's current mod database. You must generate ONLY mods that definitely exist on Modrinth for the EXACT specifications below.

        MANDATORY CONTEXT - READ CAREFULLY:
        - Minecraft Version: {mc_version} (EXACT version compatibility required)
        - Mod Loader: {mod_loader} (MUST support this specific loader)
        - Theme: {theme} (Primary focus for mod selection)

        VERIFIED {mod_loader.upper()} MODS FOR {mc_version} ON MODRINTH:
        {loader_examples}

        {learning_context}

        CRITICAL REQUIREMENTS - NO EXCEPTIONS:
        1. Every mod MUST be verified to exist on Modrinth.com
        2. Every mod MUST explicitly support {mod_loader} mod loader
        3. Every mod MUST explicitly support Minecraft {mc_version}
        4. DO NOT suggest mods from other platforms (CurseForge only, etc.)
        5. DO NOT suggest discontinued or outdated mods
        6. DO NOT suggest mods that are exclusive to other loaders
        7. ONLY suggest mods you are absolutely certain exist on Modrinth

        THEME INTERPRETATION - {theme}:
        Focus heavily on this theme while including essential utility mods.

        VALIDATION STEP:
        Before including any mod, mentally verify:
        ✓ Does this mod exist on Modrinth?
        ✓ Does it support {mod_loader}?
        ✓ Does it support {mc_version}?
        ✓ Is it actively maintained?

        Generate 20-25 mods that pass ALL these checks. Be conservative - it's better to suggest fewer mods that definitely exist than many mods that might not exist.

        OUTPUT: JSON array only
        ["Exact Modrinth Mod Name 1", "Exact Modrinth Mod Name 2", ...]
        """
        
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                mod_names = json.loads(json_str)
                self.print_success(f"Generated {len(mod_names)} mod suggestions!")
                return mod_names
            else:
                mod_names = json.loads(response_text)
                self.print_success(f"Generated {len(mod_names)} mod suggestions!")
                return mod_names
        except json.JSONDecodeError as e:
            self.print_error(f"Failed to parse AI response as JSON: {e}")
            self.print_warning("Using fallback mod list...")
            return self.get_fallback_mods(theme, mod_loader, mc_version)
        except Exception as e:
            self.print_error(f"Error generating suggestions: {e}")
            self.print_warning("Using fallback mod list...")
            return self.get_fallback_mods(theme, mod_loader, mc_version)

    def get_loader_specific_examples(self, mod_loader: str, mc_version: str) -> str:
        """Get verified examples of mods for the specific loader and version"""
        
        examples = {
            "fabric": [
                "Sodium", "Lithium", "Iris Shaders", "FerriteCore", "LazyDFU",
                "Fabric API", "JEI", "REI", "WTHIT", "AppleSkin",
                "Create Fabric", "Botania", "Biomes O' Plenty", "Xaero's Minimap",
                "JourneyMap", "Waystones", "Iron Chests: Restocked", "Storage Drawers"
            ],
            "forge": [
                "JEI", "OptiFine", "Iron Chests", "Waystones", "Storage Drawers",
                "Create", "Botania", "Biomes O' Plenty", "Twilight Forest",
                "Applied Energistics 2", "Thermal Expansion", "JourneyMap",
                "Xaero's Minimap", "HWYLA", "AppleSkin", "Cooking for Blockheads"
            ],
            "quilt": [
                "Sodium", "Lithium", "Iris Shaders", "FerriteCore", "Quilted Fabric API",
                "JEI", "REI", "WTHIT", "AppleSkin", "Xaero's Minimap"
            ],
            "neoforge": [
                "JEI", "Iron Chests", "Waystones", "Storage Drawers", "JourneyMap",
                "Xaero's Minimap", "AppleSkin", "Create", "Botania"
            ]
        }
        
        loader_mods = examples.get(mod_loader, examples["fabric"])
        return "Examples: " + ", ".join(loader_mods[:10]) + f"\n(These are verified to exist on Modrinth for {mod_loader})"
    
    def get_learning_context(self, mod_loader: str) -> str:
        """Generate learning context based on previous successful and failed searches"""
        context = []
        
        if self.successful_mods:
            successful_list = list(self.successful_mods)[:15]  # Limit to avoid huge prompts
            context.append(f"RECENTLY VERIFIED MODS (use these as reference): {', '.join(successful_list)}")
        
        if self.failed_mods:
            failed_list = list(self.failed_mods)[:10]
            context.append(f"AVOID THESE MODS (not found on Modrinth): {', '.join(failed_list)}")
        
        return "\n".join(context) if context else ""
    
    def validate_mods_with_learning(self, mod_suggestions: List[str], mc_version: str, mod_loader: str, theme: str) -> List[ModInfo]:
        """Validate mods and learn from results to improve future suggestions"""
        
        self.print_info("🔍 Validating mods against Modrinth database...")
        
        valid_mods = []
        failed_this_round = []
        
        for i, mod_name in enumerate(mod_suggestions, 1):
            print(f"{Fore.CYAN}[{i:2d}/{len(mod_suggestions)}] Checking: {mod_name:<30}", end="")
            
            mod_info = self.search_modrinth_mod(mod_name, mc_version, mod_loader)
            
            if mod_info:
                valid_mods.append(mod_info)
                self.successful_mods.add(mod_info.name)  # Learn from success
                print(f"{Fore.GREEN}✓ Found: {mod_info.name}")
            else:
                self.failed_mods.add(mod_name)  # Learn from failure
                failed_this_round.append(mod_name)
                print(f"{Fore.RED}✗ Not found")
            
            # Rate limiting - be nice to the API
            time.sleep(0.2)
        
        # If we have too many failures, try to get more suggestions
        success_rate = len(valid_mods) / len(mod_suggestions) if mod_suggestions else 0
        
        if success_rate < 0.7 and failed_this_round:  # Less than 70% success rate
            self.print_warning(f"Low success rate ({success_rate:.1%}). Trying to get better suggestions...")
            additional_mods = self.get_improved_suggestions(mc_version, mod_loader, theme, failed_this_round)
            
            if additional_mods:
                self.print_info(f"🔄 Validating {len(additional_mods)} improved suggestions...")
                for i, mod_name in enumerate(additional_mods, 1):
                    print(f"{Fore.CYAN}[+{i:2d}] Checking: {mod_name:<30}", end="")
                    
                    mod_info = self.search_modrinth_mod(mod_name, mc_version, mod_loader)
                    
                    if mod_info:
                        valid_mods.append(mod_info)
                        self.successful_mods.add(mod_info.name)
                        print(f"{Fore.GREEN}✓ Found: {mod_info.name}")
                    else:
                        self.failed_mods.add(mod_name)
                        print(f"{Fore.RED}✗ Not found")
                    
                    time.sleep(0.2)
        
        self.print_success(f"Found {len(valid_mods)} valid mods out of {len(mod_suggestions)} suggestions")
        return valid_mods
    
    def get_improved_suggestions(self, mc_version: str, mod_loader: str, theme: str, failed_mods: List[str]) -> List[str]:
        """Get improved suggestions based on what failed"""
        
        improvement_prompt = f"""
        The following mods were NOT found on Modrinth for {mod_loader} {mc_version}:
        {', '.join(failed_mods)}

        Generate 10 alternative mods for the theme "{theme}" that:
        1. Definitely exist on Modrinth
        2. Support {mod_loader} 
        3. Support {mc_version}
        4. Are similar to the failed mods but actually available

        Focus on well-established, popular mods only.

        JSON array: ["replacement mod 1", "replacement mod 2", ...]
        """
        
        try:
            response = self.model.generate_content(improvement_prompt)
            response_text = response.text.strip()
            json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                return json.loads(json_str)
        except:
            pass
        
        return []
    
    def get_fallback_mods(self, theme: str, mod_loader: str, mc_version: str = None) -> List[str]:
        """Generate fallback mods using AI if primary generation fails"""
        
        self.print_warning("Primary AI generation failed, trying simpler approach...")
        
        fallback_prompt = f"""
        EMERGENCY MODE: Generate 15 absolutely verified mods for Modrinth.

        EXACT REQUIREMENTS:
        - Minecraft: {mc_version or 'latest'}
        - Loader: {mod_loader}
        - Theme: {theme}
        - Platform: Modrinth ONLY

        For {mod_loader} {mc_version or 'latest'}, only suggest mods you are 100% certain exist on Modrinth.

        Common {mod_loader} mods for {mc_version or 'latest'}:
        - Performance: Sodium (Fabric), Lithium (Fabric), FerriteCore
        - Utility: JEI, REI, WTHIT, AppleSkin
        - Adventure: Better structures, biome mods, mob mods

        JSON only: ["verified mod 1", "verified mod 2", ...]
        """
        
        try:
            response = self.model.generate_content(fallback_prompt)
            response_text = response.text.strip()
            json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                mod_names = json.loads(json_str)
                self.print_info(f"Generated {len(mod_names)} fallback suggestions!")
                return mod_names
        except Exception as e:
            self.print_warning(f"Fallback AI also failed: {e}")
        
        # Ultimate fallback - let AI generate basic mod suggestions
        basic_prompt = f"List 10 popular {mod_loader} mods in JSON format: [\"mod1\", \"mod2\"]"
        try:
            response = self.model.generate_content(basic_prompt)
            response_text = response.text.strip()
            json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                return json.loads(json_str)
        except:
            pass
            
        # Final emergency fallback - empty list will trigger error handling
        self.print_error("All AI generation methods failed!")
        return []
    
    def search_modrinth_mod(self, mod_name: str, mc_version: str, mod_loader: str) -> Optional[ModInfo]:
        """Search for a mod on Modrinth and return mod info if found, with enhanced error tracking"""
        
        try:
            # Try multiple search strategies
            search_queries = [
                mod_name,  # Exact name
                mod_name.lower(),  # Lowercase
                mod_name.replace(" ", "-"),  # Hyphenated
                mod_name.replace("'", ""),  # Remove apostrophes
                mod_name.split()[0] if " " in mod_name else mod_name  # First word only
            ]
            
            for query in search_queries:
                search_url = f"{self.modrinth_base_url}/search"
                params = {
                    'query': query,
                    'facets': f'[["categories:{mod_loader}"],["versions:{mc_version}"]]',
                    'limit': 10
                }
                
                response = self.session.get(search_url, params=params, timeout=10)
                response.raise_for_status()
                
                search_data = response.json()
                
                if search_data['hits']:
                    # Find the best match
                    best_match = None
                    best_score = 0
                    
                    for hit in search_data['hits']:
                        # Calculate match score based on name similarity and downloads
                        name_similarity = self.calculate_similarity(mod_name.lower(), hit['title'].lower())
                        download_score = min(hit['downloads'] / 1000000, 1.0)  # Normalize downloads
                        combined_score = name_similarity * 0.8 + download_score * 0.2
                        
                        if combined_score > best_score:
                            best_score = combined_score
                            best_match = hit
                    
                    if best_match and best_score > 0.4:  # Minimum similarity threshold
                        return ModInfo(
                            name=best_match['title'],
                            slug=best_match['slug'],
                            description=best_match.get('description', ''),
                            mod_id=best_match['project_id'],
                            categories=best_match.get('categories', []),
                            downloads=best_match.get('downloads', 0),
                            updated=best_match.get('date_modified', ''),
                            versions=best_match.get('versions', []),
                            loaders=best_match.get('loaders', [])
                        )
                
                # Small delay between search attempts
                time.sleep(0.1)
            
            # If we get here, no queries worked - track as potential Gemini false suggestion
            self.gemini_false_suggestions.add(mod_name)
            return None
            
        except requests.RequestException as e:
            # Track network/API errors separately from false suggestions
            self.api_errors.append({
                'mod_name': mod_name,
                'error': str(e),
                'error_type': 'network_error'
            })
            self.print_warning(f"Network error searching for {mod_name}: {e}")
            return None
        except Exception as e:
            # Track parsing/other errors
            self.api_errors.append({
                'mod_name': mod_name,
                'error': str(e),
                'error_type': 'parsing_error'
            })
            self.print_warning(f"Error searching for {mod_name}: {e}")
            return None
    
    def calculate_similarity(self, str1: str, str2: str) -> float:
        """Calculate string similarity using a simple algorithm"""
        if str1 == str2:
            return 1.0
        
        # Check if one string contains the other
        if str1 in str2 or str2 in str1:
            return 0.8
        
        # Simple word overlap calculation
        words1 = set(str1.split())
        words2 = set(str2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    def validate_mods(self, mod_suggestions: List[str], mc_version: str, mod_loader: str, theme: str) -> List[ModInfo]:
        """Validate mod suggestions against Modrinth database with learning"""
        return self.validate_mods_with_learning(mod_suggestions, mc_version, mod_loader, theme)
    
    def generate_output_files(self, valid_mods: List[ModInfo], mc_version: str, mod_loader: str, theme: str):
        """Generate output files for the modpack"""
        
        self.print_info("📝 Generating output files...")
        
        # Ensure generated directory exists
        generated_dir = Path("generated")
        generated_dir.mkdir(exist_ok=True)
        
        # Create gen-mods.txt with slug names for Ferium
        gen_mods_path = generated_dir / 'gen-mods.txt'
        with open(gen_mods_path, 'w', encoding='utf-8') as f:
            f.write(f"# Generated Modpack: {theme}\n")
            f.write(f"# Minecraft Version: {mc_version}\n")
            f.write(f"# Mod Loader: {mod_loader.title()}\n")
            f.write(f"# Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"# Total Mods: {len(valid_mods)}\n\n")
            f.write("# Mod slugs for Ferium (one per line):\n")
            
            for mod in sorted(valid_mods, key=lambda x: x.downloads, reverse=True):
                f.write(f"{mod.slug}\n")
        
        # Create detailed mod list
        details_path = generated_dir / 'modpack-details.json'
        with open(details_path, 'w', encoding='utf-8') as f:
            modpack_data = {
                "modpack_info": {
                    "theme": theme,
                    "minecraft_version": mc_version,
                    "mod_loader": mod_loader,
                    "generated_on": time.strftime('%Y-%m-%d %H:%M:%S'),
                    "total_mods": len(valid_mods)
                },
                "mods": []
            }
            
            for mod in sorted(valid_mods, key=lambda x: x.downloads, reverse=True):
                modpack_data["mods"].append({
                    "name": mod.name,
                    "slug": mod.slug,
                    "description": mod.description,
                    "mod_id": mod.mod_id,
                    "categories": mod.categories,
                    "downloads": mod.downloads,
                    "last_updated": mod.updated
                })
            
            json.dump(modpack_data, f, indent=2, ensure_ascii=False)
        
        # Create human-readable summary
        summary_path = generated_dir / 'modpack-summary.md'
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(f"# {theme} Modpack\n\n")
            f.write(f"**Minecraft Version:** {mc_version}  \n")
            f.write(f"**Mod Loader:** {mod_loader.title()}  \n")
            f.write(f"**Total Mods:** {len(valid_mods)}  \n")
            f.write(f"**Generated:** {time.strftime('%Y-%m-%d %H:%M:%S')}  \n\n")
            
            f.write("## Installation with Ferium\n\n")
            f.write("1. Install [Ferium](https://github.com/gorilla-devs/ferium)\n")
            f.write("2. Create a new profile: `ferium profile create`\n")
            f.write("3. Add mods from gen-mods.txt: `cat generated/gen-mods.txt | grep -v '^#' | xargs -I {} ferium add {}`\n")
            f.write("4. Download mods: `ferium upgrade`\n\n")
            
            f.write("## Mod List\n\n")
            f.write("| Mod Name | Downloads | Categories | Description |\n")
            f.write("|----------|-----------|------------|-------------|\n")
            
            for mod in sorted(valid_mods, key=lambda x: x.downloads, reverse=True):
                categories_str = ", ".join(mod.categories[:3])  # Limit categories shown
                description = mod.description[:100] + "..." if len(mod.description) > 100 else mod.description
                downloads_formatted = f"{mod.downloads:,}"
                
                f.write(f"| {mod.name} | {downloads_formatted} | {categories_str} | {description} |\n")
        
        self.print_success("Generated files:")
        self.print_info(f"  • {gen_mods_path} - Mod slugs for Ferium")
        self.print_info(f"  • {details_path} - Detailed mod information")
        self.print_info(f"  • {summary_path} - Human-readable summary")
    
    def print_diagnostics_report(self):
        """Print comprehensive diagnostics to help identify issues"""
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"🔍 DIAGNOSTICS REPORT")
        print(f"{'='*60}{Style.RESET_ALL}")
        
        # Gemini accuracy assessment
        total_suggestions = len(self.successful_mods) + len(self.failed_mods)
        if total_suggestions > 0:
            success_rate = len(self.successful_mods) / total_suggestions * 100
            print(f"\n{Fore.GREEN}📊 OVERALL STATISTICS{Style.RESET_ALL}")
            print(f"  Total mod suggestions processed: {total_suggestions}")
            print(f"  Successfully found and added: {len(self.successful_mods)}")
            print(f"  Failed to find/add: {len(self.failed_mods)}")
            print(f"  Success rate: {success_rate:.1f}%")
        
        # Gemini false suggestions analysis
        if self.gemini_false_suggestions:
            print(f"\n{Fore.RED}🤖 GEMINI FALSE SUGGESTIONS{Style.RESET_ALL}")
            print(f"  Mods suggested by Gemini that don't exist on Modrinth:")
            for mod in sorted(self.gemini_false_suggestions):
                print(f"    • {mod}")
            print(f"  Total false suggestions: {len(self.gemini_false_suggestions)}")
            
            if total_suggestions > 0:
                false_rate = len(self.gemini_false_suggestions) / total_suggestions * 100
                print(f"  Gemini false suggestion rate: {false_rate:.1f}%")
        
        # Version/Loader compatibility issues
        if self.version_incompatible:
            print(f"\n{Fore.YELLOW}⚠ VERSION/LOADER COMPATIBILITY ISSUES{Style.RESET_ALL}")
            print(f"  Mods that exist but don't support {self.minecraft_version} with {self.mod_loader}:")
            for issue in self.version_incompatible:
                print(f"    • {issue['suggested_name']} → Found: {issue['found_name']}")
                print(f"      Reason: {issue['reason']}")
        
        # API/Network errors
        if self.api_errors:
            print(f"\n{Fore.MAGENTA}🚨 API/NETWORK ERRORS{Style.RESET_ALL}")
            network_errors = [e for e in self.api_errors if e['error_type'] == 'network_error']
            parsing_errors = [e for e in self.api_errors if e['error_type'] == 'parsing_error']
            
            if network_errors:
                print(f"  Network errors ({len(network_errors)}):")
                for error in network_errors[:5]:  # Show max 5 examples
                    print(f"    • {error['mod_name']}: {error['error']}")
                if len(network_errors) > 5:
                    print(f"    ... and {len(network_errors) - 5} more")
            
            if parsing_errors:
                print(f"  Parsing errors ({len(parsing_errors)}):")
                for error in parsing_errors[:5]:  # Show max 5 examples
                    print(f"    • {error['mod_name']}: {error['error']}")
                if len(parsing_errors) > 5:
                    print(f"    ... and {len(parsing_errors) - 5} more")
        
        # Recommendations
        print(f"\n{Fore.CYAN}💡 RECOMMENDATIONS{Style.RESET_ALL}")
        
        if self.gemini_false_suggestions:
            false_rate = len(self.gemini_false_suggestions) / total_suggestions * 100 if total_suggestions > 0 else 0
            if false_rate > 20:
                print(f"  🔴 HIGH FALSE SUGGESTION RATE ({false_rate:.1f}%)")
                print(f"     • Consider refining the Gemini prompt to be more specific about Modrinth availability")
                print(f"     • The AI may be suggesting mods from other platforms or outdated mod names")
            elif false_rate > 10:
                print(f"  🟡 MODERATE FALSE SUGGESTION RATE ({false_rate:.1f}%)")
                print(f"     • Some improvement needed in Gemini prompt specificity")
            else:
                print(f"  🟢 LOW FALSE SUGGESTION RATE ({false_rate:.1f}%)")
                print(f"     • Gemini is performing well with current prompts")
        
        if self.api_errors:
            print(f"  🌐 API/Network issues detected:")
            print(f"     • Check internet connection and Modrinth API status")
            print(f"     • Some failures may not be Gemini's fault")
        
        if self.version_incompatible:
            print(f"  🔄 Version compatibility issues:")
            print(f"     • Gemini found valid mods but they don't support your version/loader")
            print(f"     • Consider using a more popular Minecraft version")
        
        if not self.gemini_false_suggestions and not self.api_errors and not self.version_incompatible:
            print(f"  🎉 No issues detected - system working optimally!")
        
        print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    
    def run(self):
        """Main application loop"""
        try:
            # Get user input
            mc_version, mod_loader, theme = self.get_user_input()
            
            print(f"\n{Fore.MAGENTA}{Style.BRIGHT}🎯 Configuration Summary:")
            print(f"   Minecraft Version: {Fore.CYAN}{mc_version}")
            print(f"   Mod Loader: {Fore.CYAN}{mod_loader.title()}")
            print(f"   Theme: {Fore.CYAN}{theme}")
            
            # Generate suggestions using AI
            mod_suggestions = self.generate_mod_suggestions(mc_version, mod_loader, theme)
            
            # Check if we got any suggestions
            if not mod_suggestions:
                self.print_error("No mod suggestions generated! Please check your API key and try again.")
                return
            
            # Validate mods against Modrinth
            valid_mods = self.validate_mods(mod_suggestions, mc_version, mod_loader, theme)
            
            if not valid_mods:
                self.print_error("No valid mods found! This might be due to:")
                self.print_info("  • Incompatible version/loader combination")
                self.print_info("  • Network connectivity issues")
                self.print_info("  • API limitations")
                self.print_warning("Please try again with different parameters.")
                return
            
            # Generate output files
            self.generate_output_files(valid_mods, mc_version, mod_loader, theme)
            
            self.print_header("GENERATION COMPLETE!")
            print(f"{Fore.GREEN}{Style.BRIGHT}🎉 Successfully generated a {theme} modpack!")
            print(f"{Fore.GREEN}   • {len(valid_mods)} mods found and validated")
            print(f"{Fore.GREEN}   • Ready for installation with Ferium")
            print(f"{Fore.YELLOW}   • Check generated/gen-mods.txt for the mod list")
            
            # Show learning summary
            if self.failed_mods:
                print(f"\n{Fore.BLUE}{Style.BRIGHT}📚 Learning Summary:")
                print(f"{Fore.BLUE}   • Tracked {len(self.failed_mods)} mods that don't exist on Modrinth")
                print(f"{Fore.BLUE}   • Next run will avoid these and suggest better alternatives")
            
            # Print comprehensive diagnostics report
            self.print_diagnostics_report()
            
            # Save learning data for future runs
            self.save_learning_data()
            
        except KeyboardInterrupt:
            self.print_warning("\n\nOperation cancelled by user.")
            sys.exit(0)
        except Exception as e:
            self.print_error(f"An unexpected error occurred: {e}")
            sys.exit(1)

    def load_learning_data(self):
        """Load previously learned data from disk"""
        learning_file = Path("generated/learning_data.json")
        if learning_file.exists():
            try:
                with open(learning_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.failed_mods = set(data.get('failed_mods', []))
                    self.successful_mods = set(data.get('successful_mods', []))
                    print(f"{Fore.BLUE}📚 Loaded learning data: {len(self.failed_mods)} known failures, {len(self.successful_mods)} known successes{Style.RESET_ALL}")
            except Exception as e:
                self.print_warning(f"Could not load learning data: {e}")
    
    def save_learning_data(self):
        """Save learning data to disk for future runs"""
        # Ensure generated directory exists
        generated_dir = Path("generated")
        generated_dir.mkdir(exist_ok=True)
        
        learning_file = generated_dir / "learning_data.json"
        try:
            data = {
                'failed_mods': list(self.failed_mods),
                'successful_mods': list(self.successful_mods),
                'last_updated': datetime.now().isoformat(),
                'gemini_false_suggestions': list(self.gemini_false_suggestions),
                'total_runs': getattr(self, 'total_runs', 0) + 1
            }
            with open(learning_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"{Fore.BLUE}💾 Saved learning data for future runs{Style.RESET_ALL}")
        except Exception as e:
            self.print_warning(f"Could not save learning data: {e}")

def main():
    """Entry point of the application"""
    generator = MinecraftModGenerator()
    generator.run()

if __name__ == "__main__":
    main()
