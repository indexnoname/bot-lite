from discord.ext import commands
import discord
import subprocess
import json
import os

# Load configuration from JSON file
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

# Initialize the bot with a command prefix
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Function to execute a shell command and return the output
def execute(command):
    return subprocess.run(command, shell=True, capture_output=True, text=True).stdout

# Function to get the list of models from ollama list
def get_model_list():
    return [line.split()[0] for line in execute('ollama list').splitlines()[1:]]

@bot.event
async def on_ready():
    print(f'Bot is ready. Logged in as {bot.user}')

@bot.event
async def on_member_join(member):
    channel = bot.get_channel(config['welcome_channel_id'])
    if channel:
        await channel.send(f'Hello {member.mention}! Welcome to the server!')

# Command to list all AI models in Ollama
@bot.command(name='ailist')
async def ailist(ctx):
    await ctx.send(f"Available models:\n```\n{execute('ollama list')}\n```")

# Command to run a specific model in Ollama
@bot.command(name='airun')
async def airun(ctx, model: str, *, prompt: str):
    # Check if the model exists
    if model not in get_model_list():
        await ctx.send(f"Model '{model}' not found in Ollama.")
        return

    # Run the model
    await ctx.send(f"Running model '{model}'...")
    await ctx.send(execute(f'ollama run {model} {prompt}]'))

import numpy as np
from PIL import Image
import math
from pymsch import Schematic, Block, Content
import time

COLORS = {
    "copper": (217, 157, 115),
    "lead": (140, 127, 169),
    "metaglass": (235, 238, 245),
    "graphite": (178, 198, 210),
    "sand": (247, 203, 164),
    "coal": (39, 39, 39),
    "titanium": (141, 161, 227),
    "thorium": (249, 163, 199),
    "scrap": (119, 119, 119),
    "silicon": (83, 86, 92),
    "plastanium": (203, 217, 127),
    "phase-fabric": (244, 186, 110),
    "surge-alloy": (243, 233, 121),
    "spore-pod": (116, 87, 206),
    "blast-compound": (255, 121, 94),
    "pyratite": (255, 170, 95),
    "beryllium": (58, 143, 100),
    "fissile-matter": (94, 152, 141),
    "dormant-cyst": (223, 130, 77),
    "tungsten": (118, 138, 154),
    "oxide": (228, 255, 214),
    "carbide": (137, 118, 154),
}

MAX_WIDTH = 128
MAX_HEIGHT = 128

def majority_color_resize(image, scale):
    original_width, original_height = image.size
    scale = scale / 100
    scaleW = MAX_WIDTH / original_width
    scaleH = MAX_HEIGHT / original_height
    scale = min(scale, scaleW, scaleH)
    target_width = math.floor(original_width * scale)
    target_height = math.floor(original_height * scale)

    resized_image = Image.new('RGB', (target_width, target_height))
    pixels = np.array(image)

    for y in range(target_height):
        for x in range(target_width):
            block_pixels = pixels[
                math.floor(y * original_height / target_height): math.ceil((y + 1) * original_height / target_height),
                math.floor(x * original_width / target_width): math.ceil((x + 1) * original_width / target_width)
            ]
            flat_pixels = block_pixels.reshape(-1, block_pixels.shape[-1])
            unique, counts = np.unique(flat_pixels, axis=0, return_counts=True)
            majority_color = unique[np.argmax(counts)]
            resized_image.putpixel((x, y), tuple(majority_color))
    
    return resized_image, target_width, target_height

def resize_image(image, scale, resample_method='LANCZOS'):
    if resample_method == 'NEAREST':
        resample = Image.NEAREST
    elif resample_method == 'MAJORITY':
        return majority_color_resize(image, scale)
    else:
        resample = Image.LANCZOS

    original_width, original_height = image.size
    scale = scale / 100
    scaleW = MAX_WIDTH / original_width
    scaleH = MAX_HEIGHT / original_height
    scale = min(scale, scaleW, scaleH)
    target_width = math.floor(original_width * scale)
    target_height = math.floor(original_height * scale)

    return image.resize((target_width, target_height), resample), target_width, target_height

def convert_image_to_scheme(image):
    # Start timer for the entire function
    start_time = time.time()

    # Timer for color conversion
    color_conversion_start = time.time()

    # Convert image to 22 colors
    pixels = np.array(image, dtype=np.float32)
    color_array = np.array(list(COLORS.values()), dtype=np.float32)
    height, width, _ = pixels.shape
    
    # Vectorized computation of distances and finding the nearest color
    reshaped_pixels = pixels.reshape(-1, 3)
    distances = np.sum((color_array[None, :, :] - reshaped_pixels[:, None, :]) ** 2, axis=2)
    nearest_indices = np.argmin(distances, axis=1)
    nearest_colors = color_array[nearest_indices]
    
    # Reshape the result back to the original image shape
    new_pixels = nearest_colors.reshape(height, width, 3).astype(np.uint8)

    # End timer for color conversion
    color_conversion_end = time.time()
    print(f"Color conversion time: {color_conversion_end - color_conversion_start} seconds")

    # Timer for schematic creation
    schematic_creation_start = time.time()

    # Create the schematic
    scheme = Schematic()
    scheme.bounds = (height, width)

    for y in range(height):
        for x in range(width):
            color = (new_pixels[y, x])
            item = next((item for item, c in COLORS.items() if c == color), None)
            if item:
                block = Block(Content.SORTER, x, height - y - 1, None, 0)  # Flip the y-coordinate
                scheme.add_block(block)
                block.set_config(Content[item.upper().replace('-', '_')])

    scheme.name = "image"
    scheme.write_file("scheme.msch")

    # End timer for schematic creation
    schematic_creation_end = time.time()
    print(f"Schematic creation time: {schematic_creation_end - schematic_creation_start} seconds")

    # End timer for the entire function
    end_time = time.time()
    print(f"Total conversion time: {end_time - start_time} seconds")

    return "scheme.msch"

@bot.command(name='convertimage', brief='Кинь картинку напиши насколько изменить в процентах и вибери метод создания картинки например !convertimage 75 mix')
async def convert(ctx, scale: int = 100, resample_method: str = 'LANCZOS'):
    """
    Converts an attached image to a Mindustry schematic.
    
    Parameters:
    scale (int): The scale to resize the image. Default is 100 (no resizing).
    resample_method (str): The resampling method to use ('LANCZOS', 'NEAREST', 'MAJORITY'). Default is 'LANCZOS'.
    """
    if len(ctx.message.attachments) == 0:
        await ctx.send('Please attach an image.')
        return

    image_file = ctx.message.attachments[0].filename
    await ctx.message.attachments[0].save(image_file)
    
    image = Image.open(image_file).convert('RGB')

    if resample_method.lower() == 'mix':
        resample_method = 'LANCZOS'
    elif resample_method.lower() == 'majority':
        resample_method = 'MAJORITY'
    else:
        resample_method = 'NEAREST'

    resized_image, new_width, new_height = resize_image(image, scale, resample_method)
    output_file = convert_image_to_scheme(resized_image)

    await ctx.send(file=discord.File(output_file))

# Run the bot with your token
bot.run(config['token'])