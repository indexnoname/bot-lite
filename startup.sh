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
)

# install missing packages
for pkg in "${!REQUIRED_PACKAGES[@]}"; do
    import=${REQUIRED_PACKAGES[$pkg]}
    if ! python -c "import $import" &> /dev/null; then
        pip install "$pkg"
    fi
done

if ! command -v node &> /dev/null; then
    sudo apt install -y nodejs npm
    npm install mindustry-schematic-parser
fi

# run the bot script
python3 bot.py