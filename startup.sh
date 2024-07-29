#!/bin/bash

# make this a coment if dont want autoupdate
git pull https://github.com/indexnoname/bot-lite.git


# create virtual environment if there is none
if [ ! -d botvenv ]; then
    python3 -m venv botvenv
fi

# activate the virtual environment
source botvenv/bin/activate

# check if discord.py is installed, if not, install it
if ! python -c "import discord" &> /dev/null; then
    pip3 install discord.py
fi
if ! python -c "import numpy as np" &> /dev/null; then
    pip3 install numpy
fi
if ! python -c "from PIL import image" &> /dev/null; then
    pip3 install Pillow
fi
if ! python -c "import pymsch" &> /dev/null; then
    pip3 install pymsch
fi
if ! python -c "import pyperclip" &> /dev/null; then
    pip3 install pyperclip
fi

# run the bot script
python3 bot.py
