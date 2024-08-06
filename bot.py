from PIL import Image
import numpy as np
from discord.ext import commands
import discord, subprocess, json, os, struct, zlib, base64, time, math, io


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

COLORS = {
    0: (217, 157, 115),
    1: (140, 127, 169),
    2: (235, 238, 245),
    3: (178, 198, 210),
    4: (247, 203, 164),
    5: (39, 39, 39),
    6: (141, 161, 227),
    7: (249, 163, 199),
    8: (119, 119, 119),
    9: (83, 86, 92),
    10: (203, 217, 127),
    11: (244, 186, 110),
    12: (243, 233, 121),
    13: (116, 87, 206),
    14: (255, 121, 94),
    15: (255, 170, 95),
    16: (58, 143, 100),
    17: (118, 138, 154),
    18: (228, 255, 214),
    19: (137, 118, 154),
    20: (94, 152, 141),
    21: (223, 130, 77),
}

def resmet(method = str):
    return getattr(Image, method.upper())

def txtbin(txt = str):
    return struct.pack(">H", len(txt))+txt.encode("UTF-8")
    
def majority_color_resize(image, scale, target_width, target_height, original_width, original_height):

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
def resize_image(image, scale, resample_method):
    
    original_width, original_height = image.size

    scale = min(scale / 100, 256 / original_width, 256 / original_height)
    target_width = math.floor(original_width * scale)
    target_height = math.floor(original_height * scale)

    if resample_method == 'MAJORITY':
        return majority_color_resize(image, scale, target_width, target_height, original_width, original_height)
    return image.resize((target_width, target_height), resmet(resample_method)), target_width, target_height

def convert_image_to_scheme(image, name):
    # Start timer for the entire function
    start_time = time.time()
    
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
    
    # Precompute configurations
    config_map = {tuple(v): k for k, v in COLORS.items()}

    # Create the schematic
    buffer = bytearray()
    buffer += struct.pack(">HHb", width, height, 2) + txtbin("name") + txtbin(name) + txtbin("description") + txtbin("desc") + struct.pack(">b", 1) + txtbin('sorter') + struct.pack(">i", height * width)

    # Optimize the inner loop
    buffer.extend(
        struct.pack(">bHHbbHb", 0, x, height - y - 1, 5, 0, config_map[tuple(new_pixels[y, x])], 0)
        for y in range(height)
        for x in range(width)
    )

    # End timer for schematic creation
    schematic_creation_end = time.time()
    print(f"Schematic creation time: {schematic_creation_end - schematic_creation_start} seconds")
    
    # End timer for the entire function
    end_time = time.time()
    print(f"Total conversion time: {end_time - start_time} seconds")
    return io.BytesIO(b"msch\x01" + zlib.compress(buffer))
    
@bot.command(name='convertimage', brief='Кинь картинку напиши насколько изменить в процентах и вибери метод создания картинки например !convertimage 75 mix')
async def convert(ctx, scale: int = 100, resample_method: str = 'LANCZOS'):
    """
    Converts an attached image to a Mindustry schematic.
    
    Parameters:
    scale (int): The scale to resize the image. Default is 100 (no resizing).
    resample_method (str): The resampling method to use ('LANCZOS', 'NEAREST', 'MAJORITY'). Default is 'LANCZOS'.
    """

    if not ctx.message.attachments: return await ctx.send('Please attach an image.')

    image = Image.open(io.BytesIO(await ctx.message.attachments[0].read())).convert('RGB')
    resized_image, new_width, new_height = resize_image(image, scale, resample_method.upper())
    scheme_file = convert_image_to_scheme(resized_image, ctx.message.attachments[0].filename)
    await ctx.send(file=discord.File(fp=scheme_file, filename="scheme.msch"))
# Run the bot with your token

bot.run(config['token'])