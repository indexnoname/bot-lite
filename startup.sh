#!/bin/bash

# make this a comment if you don't want autoupdate
git pull https://github.com/indexnoname/bot-lite.git

# create virtual environment if there is none
if [ ! -d botvenv ]; then
    python3 -m venv botvenv
fi

# activate the virtual environment
source botvenv/bin/activate

# list of required packages
REQUIRED_PACKAGES=(
    discord.py
    numpy
    Pillow
    pymsch
    pyperclip
)

# install missing packages
for package in "${REQUIRED_PACKAGES[@]}"; do
    if ! pip list | grep -F "$package" &> /dev/null; then
        pip install "$package"
    fi
done

# run the bot script
python3 bot.py