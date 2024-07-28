#!/bin/bash
# create virtual environment if there is none
if [ ! -d botvenv ]; then
    python3 -m venv botvenv
fi

# Activate the virtual environment
source botvenv/bin/activate

# Check if discord.py is installed, if not, install it
if ! python -c "import discord" &> /dev/null; then
    pip3 install discord.py
fi

# Run the bot script
python3 bot.py