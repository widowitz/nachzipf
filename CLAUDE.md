# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This repository contains English learning materials and resources for Marlene, a German student preparing for her supplementary English exam ("Nachzipf"). The materials are organized to support structured daily English practice sessions.

## Repository Structure

### Core Learning Materials
- **`01 Lernmaterial/`** - Main learning content
  - `Fersterer Stoff für Marlene Englisch Sommer 2025.md` - Complete curriculum content (Units 1-13)
  - `summary_by_unit.md` - Content organized by units
  - `summary_long.md` & `summary_short.md` - Detailed and overview summaries
  
### Error Tracking
- **`02 Fehlerheft/`** - Error history and practice focus
  - `marlene_fehlerheft.txt` - Log of common mistakes to target in practice

### Instructions
- **`03 Prompt/`** - Contains guidance for creating daily practice sessions
  - `prompt.md` - Instructions for generating individualized exercises

### Generated Exercises
- **`04 Uebungen/`** - Generated daily exercise files
  - Files named with timestamp format: `yyyy-mm-dd_hh-mm-ss_unit_X.md`

## Key Learning Content

The curriculum covers 4 major tests across 13 units:

1. **Test 1 (Units 1-3)**: Present/Past tense, irregular verbs, adjectives
2. **Test 2 (Units 4-6)**: Comparatives/superlatives, prepositions, have to
3. **Test 3 (Units 7-10)**: Future tenses, some/any, restaurant vocabulary
4. **Test 4 (Units 11-13)**: Present perfect, possessive pronouns, adverbs

## Tools and Scripts

### Exercise Generator (`generator.py`)
Automated daily exercise generator using OpenAI GPT-4o:

```bash
python3 generator.py
```

**Requirements:**
- Python 3.x with packages: `openai`, `python-dotenv`
- `.env` file with `OPEN_AI_KEY=your_openai_api_key`

**Features:**
- Prompts for unit selection (1-13)
- Combines error history with unit-specific content
- Generates personalized exercises targeting known weaknesses
- Saves timestamped exercise files

## Working with This Repository

### Daily Practice Session Generation
When asked to create practice exercises:
1. Check `marlene_fehlerheft.txt` for recent errors to target
2. Select a unit (1-13) to focus on - ask which unit if not specified
3. Reference the appropriate content from the Fersterer materials
4. Create exercises that combine:
   - Targeted practice of recent mistakes
   - Unit-specific vocabulary and grammar
   - Text copying exercises (≈10 sentences)

### Content Organization
- All core content is in German with English exercises
- Materials follow Austrian Gymnasium curriculum structure
- Focus on practical application rather than theory
- Error-driven learning approach (targeting known weaknesses)

### File Dependencies
- Main content source: `Fersterer Stoff für Marlene Englisch Sommer 2025.md`
- Error tracking: `marlene_fehlerheft.txt` 
- Unit summaries provide quick reference for content selection
- Prompt file contains format and approach guidelines

## Development Setup

Install dependencies:
```bash
pip3 install -r requirements.txt
```

Environment setup:
```bash
# Create .env file with:
OPEN_AI_KEY=your_openai_api_key_here
```

## Content Safety
This repository contains educational materials for language learning. All content is pedagogical and appropriate for academic use.