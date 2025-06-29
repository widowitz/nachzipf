#!/bin/bash

# Activate the .widoenv virtual environment
source .widoenv/bin/activate

# Run the generator
python3 generator.py

# Deactivate the virtual environment
deactivate