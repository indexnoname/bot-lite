#!/bin/bash

# make this a comment if you don't want autoupdate
git pull https://github.com/indexnoname/bot-lite.git

# create virtual environment if there is none
if [ ! -d botvenv ]; then
    python3 -m venv botvenv
fi

# activate the virtual environment
source botvenv/bin/activate

# list of required packages and their import checks
declare -A REQUIRED_PACKAGES
REQUIRED_PACKAGES=(
    ["discord"]="discord"
    ["numpy"]="numpy"
    ["Pillow"]="PIL"
    ["pymsch"]="pymsch"
    ["pyperclip"]="pyperclip"
)

# install missing packages
for package in "${!REQUIRED_PACKAGES[@]}"; do
    if ! python -c "import ${REQUIRED_PACKAGES[$package]}" &> /dev/null; then
        pip3 install "$package"
    fi
done

# run the bot script
python3 bot.py