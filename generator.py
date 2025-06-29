#!/usr/bin/env python3
"""
Daily English Exercise Generator for Marlene
Generates personalized English exercises using OpenAI based on unit selection and error history.
"""

import os
import sys
import subprocess
import platform
from datetime import datetime
from pathlib import Path
from typing import Optional
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# File paths
BASE_DIR = Path(__file__).parent
PROMPT_FILE = BASE_DIR / "03 Prompt" / "prompt.md"
ERROR_FILE = BASE_DIR / "02 Fehlerheft" / "marlene_fehlerheft.txt"
FERSTERER_FILE = BASE_DIR / "01 Lernmaterial" / "a Paket von Fersterer" / "Fersterer Stoff für Marlene Englisch Sommer 2025.md"
SUMMARY_BY_UNIT_FILE = BASE_DIR / "01 Lernmaterial" / "a Paket von Fersterer" / "summary_by_unit.md"
SUMMARY_SHORT_FILE = BASE_DIR / "01 Lernmaterial" / "a Paket von Fersterer" / "summary_short.md"
SUMMARY_LONG_FILE = BASE_DIR / "01 Lernmaterial" / "a Paket von Fersterer" / "summary_long.md"
OUTPUT_DIR = BASE_DIR / "04 Uebungen"

def setup_openai() -> bool:
    """Setup OpenAI client with API key from environment."""
    api_key = os.getenv("OPEN_AI_KEY")
    if not api_key:
        print("❌ Error: OPEN_AI_KEY not found in environment variables.")
        print("Please make sure your .env file contains: OPEN_AI_KEY=your_key_here")
        return False
    
    openai.api_key = api_key
    return True

def validate_unit(unit_str: str) -> Optional[int]:
    """Validate unit input is between 1-13."""
    try:
        unit = int(unit_str)
        if 1 <= unit <= 13:
            return unit
        else:
            print(f"❌ Unit must be between 1 and 13. You entered: {unit}")
            return None
    except ValueError:
        print(f"❌ Please enter a valid number. You entered: {unit_str}")
        return None

def read_file_safely(file_path: Path) -> str:
    """Read file content with error handling."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"❌ Error: File not found: {file_path}")
        return ""
    except Exception as e:
        print(f"❌ Error reading {file_path}: {e}")
        return ""

def get_unit_from_user() -> Optional[int]:
    """Prompt user for unit selection with validation."""
    # ANSI color codes
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'
    
    print(f"\n{CYAN}{'='*60}{END}")
    print(f"{CYAN}{BOLD}🎯 Welcome to Marlene's Daily English Exercise Generator! 🎯{END}")
    print(f"{CYAN}{'='*60}{END}")
    print(f"{GREEN}📚 Available units: {YELLOW}{BOLD}1-13{END}")
    print(f"{GREEN}📖 Choose a unit to create personalized exercises for Marlene{END}")
    print(f"{CYAN}{'='*60}{END}\n")
    
    while True:
        try:
            unit_input = input(f"{BOLD}{GREEN}➤ Which unit would you like to work on today? {YELLOW}(1-13): {END}").strip()
            unit = validate_unit(unit_input)
            if unit is not None:
                print(f"\n{GREEN}✅ Great! Working on Unit {BOLD}{unit}{END}{GREEN} for Marlene!{END}\n")
                return unit
            print(f"{RED}❌ Please try again.{END}\n")
        except KeyboardInterrupt:
            print(f"\n{YELLOW}👋 Goodbye!{END}")
            return None

def build_context(unit: int) -> str:
    """Build the complete context for OpenAI including all required files."""
    print(f"📖 Reading learning materials for Unit {unit}...")
    
    # Read all required files
    prompt_content = read_file_safely(PROMPT_FILE)
    error_content = read_file_safely(ERROR_FILE)
    fersterer_content = read_file_safely(FERSTERER_FILE)
    summary_by_unit_content = read_file_safely(SUMMARY_BY_UNIT_FILE)
    summary_short_content = read_file_safely(SUMMARY_SHORT_FILE)
    summary_long_content = read_file_safely(SUMMARY_LONG_FILE)
    
    # Check if critical files are available
    if not prompt_content:
        raise Exception("Could not read prompt file - this is required!")
    
    # Build the complete context
    context = f"""
UNIT TO FOCUS ON TODAY: {unit}

{prompt_content}

=== MARLENE'S ERROR HISTORY ===
{error_content}

=== SUMMARY BY UNIT ===
{summary_by_unit_content}

=== SHORT SUMMARY ===
{summary_short_content}

=== LONG SUMMARY ===
{summary_long_content}

=== COMPLETE CURRICULUM MATERIAL ===
{fersterer_content}
"""
    
    return context

def generate_exercises(context: str) -> str:
    """Generate exercises using OpenAI GPT-4o."""
    print("🤖 Generating personalized exercises with OpenAI...")
    
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system", 
                    "content": "You are an expert English teacher creating personalized daily exercises for a German student. Follow the instructions in the provided context exactly. Focus on the specified unit and target the student's known errors."
                },
                {
                    "role": "user", 
                    "content": context
                }
            ],
            max_tokens=2000,
            temperature=0.7
        )
        
        return response.choices[0].message.content
        
    except openai.APIError as e:
        raise Exception(f"OpenAI API error: {e}")
    except openai.RateLimitError:
        raise Exception("OpenAI rate limit exceeded. Please try again later.")
    except openai.AuthenticationError:
        raise Exception("OpenAI authentication failed. Please check your API key.")
    except Exception as e:
        raise Exception(f"Unexpected error calling OpenAI: {e}")

def save_exercises(exercises: str, unit: int) -> Path:
    """Save generated exercises to timestamped file."""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{timestamp}_unit_{unit}.md"
    output_file = OUTPUT_DIR / filename
    
    # Ensure output directory exists
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            # Write the proper German header with actual date
            current_date = datetime.now().strftime('%d. %B %Y')
            # Convert English month names to German
            month_translation = {
                'January': 'Januar', 'February': 'Februar', 'March': 'März',
                'April': 'April', 'May': 'Mai', 'June': 'Juni',
                'July': 'Juli', 'August': 'August', 'September': 'September',
                'October': 'Oktober', 'November': 'November', 'December': 'Dezember'
            }
            for eng, ger in month_translation.items():
                current_date = current_date.replace(eng, ger)
            
            f.write(f"# Englisch Übungen für Marlene\n")
            f.write(f"**Datum:** {current_date}  \n")
            f.write(f"**Unit:** {unit}\n\n")
            f.write(exercises)
        
        return output_file
        
    except Exception as e:
        raise Exception(f"Error saving exercises: {e}")

def open_file(file_path: Path) -> None:
    """Open the generated file with the default application."""
    try:
        system = platform.system()
        if system == "Darwin":  # macOS
            subprocess.run(["open", str(file_path)], check=True)
        elif system == "Windows":
            subprocess.run(["start", str(file_path)], shell=True, check=True)
        elif system == "Linux":
            subprocess.run(["xdg-open", str(file_path)], check=True)
        else:
            print(f"⚠️ Cannot automatically open file on {system}. Please open manually: {file_path}")
    except subprocess.CalledProcessError:
        print(f"⚠️ Could not open file automatically. Please open manually: {file_path}")
    except Exception as e:
        print(f"⚠️ Error opening file: {e}. Please open manually: {file_path}")

def main():
    """Main function to orchestrate the exercise generation."""
    try:
        # Setup OpenAI
        if not setup_openai():
            sys.exit(1)
        
        # Get unit selection
        unit = get_unit_from_user()
        if unit is None:
            sys.exit(0)
        
        # Build context
        context = build_context(unit)
        
        # Generate exercises
        exercises = generate_exercises(context)
        
        # Save exercises
        output_file = save_exercises(exercises, unit)
        
        # Success!
        print(f"✅ Exercises generated successfully!")
        print(f"📁 Saved to: {output_file}")
        print(f"🎯 Unit {unit} exercises are ready for Marlene!")
        
        # Open the file
        print(f"📖 Opening file in default application...")
        open_file(output_file)
        
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()