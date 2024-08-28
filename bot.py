from PIL import Image
import numpy as np
from discord.ext import commands
import discord, subprocess, json, os, struct, zlib, base64, time, math, io, gc



with open('json/config.json', 'r') as config_file:
    config = json.load(config_file)
with open('json/colors.json', 'r') as colors_file:
    COLORS = {int(k): tuple(v) for k, v in json.load(colors_file).items()}

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)


def execute(command: str = "echo 'nothing inputed'"):
    """cmd execution just input full string"""
    return subprocess.run(command.split(), capture_output=True, text=True).stdout

def get_model_list():
    """ollama list output from console maybe replace by python"""
    return [line.split()[0] for line in execute('ollama list').splitlines()[1:]]

@bot.event
async def on_ready():
    print(f'Bot is ready. Logged in as {bot.user}') #remove?

@bot.event
async def on_member_join(member):
    """welcome msg when player joined"""
    channel = bot.get_channel(config['welcome_channel_id'])
    if channel: await channel.send(f'Hello {member.mention}! Welcome to the server!')

@bot.command(name='ailist')
async def ailist(ctx):
    """returns installed llms list"""
    await ctx.send(f"Available models:\n```\n{execute('ollama list')}\n```")

@bot.command(name='airun')
async def airun(ctx, model: str = "iforgortoinput", *, prompt: str = "you've been prompted without any messege please type back that user forgot to type message"):
    """runs ollama llm needs upgrade"""
    if model not in get_model_list(): return await ctx.send(f"Model '{model}' not found in Ollama.")
    await ctx.send(f"Running model '{model}'...")
    await ctx.send(execute(f'ollama run {model} {prompt}]'))

def resmet(method: str = ""): 
    """returns image method number when inputed the text"""
    return getattr(Image, method.upper()) #remove?

def txtbin(txt: str = ""):
    """text converter for mindustry basically just len of text + text in utf encoding"""
    return struct.pack(">H", len(txt))+txt.encode("UTF-8")
    
def majority_color_resize(image, scale, target_width, target_height, original_width, original_height):
    start_time = time.perf_counter()

    pixels = np.array(image)
    resized_image = np.zeros((target_height, target_width, 3), dtype=np.uint8)

    # Calculate the scaling ratios
    y_scale = original_height / target_height
    x_scale = original_width / target_width

    for y in range(target_height):
        y_start = int(y * y_scale)
        y_end = int(y_start + y_scale)

        for x in range(target_width):
            x_start = int(x * x_scale)
            x_end = int(x_start + x_scale)

            # Extract the block and flatten it
            block_pixels = pixels[y_start:y_end, x_start:x_end].reshape(-1, 3)
            if block_pixels.size == 0:
                continue  # skip empty blocks

            # Use a tuple as a hashable object for counting unique colors
            unique_colors, counts = np.unique(block_pixels, axis=0, return_counts=True)
            majority_color = unique_colors[np.argmax(counts)]

            # Assign the majority color to the resized image
            resized_image[y, x] = majority_color

    end_time = time.perf_counter()
    print(f"Color majority resize time: {end_time - start_time} seconds")

    # Convert back to PIL Image
    return Image.fromarray(resized_image, 'RGB')
def resize_image(image, scale, resample_method):
    original_width, original_height = image.size

    scale = min(scale / 100, 256 / original_width, 256 / original_height)
    target_width, target_height = int(original_width * scale), int(original_height * scale)

    if resample_method == 'MAJORITY': return majority_color_resize(image, scale, target_width, target_height, original_width, original_height)
    return image.resize((target_width, target_height), resmet(resample_method))

def convert_image_to_scheme(image, name):
    start_time = time.perf_counter()
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

    color_conversion_end = time.perf_counter()

    config_map = {tuple(v): k for k, v in COLORS.items()}


    buffer = io.BytesIO()
    buffer.write(struct.pack(">HHb", width, height, 2)
    +txtbin("name")+txtbin(name)
    +txtbin("description")+txtbin("this scheme created by bot-lite check git indexnoname")
    +struct.pack(">b", 1,)+txtbin('sorter')
    +struct.pack(">i", height*width))
    for y in range(height):
        for x in range(width):
            buffer.write(struct.pack(">bHHbbHb", 0, x, height - y - 1, 5, 0, config_map[tuple(new_pixels[y, x])], 0))

    end_time = time.perf_counter()
    print(f"Color conversion time: {color_conversion_end - start_time} seconds\nSchematic creation time: {end_time - color_conversion_end} seconds\nTotal conversion time: {end_time - start_time} seconds")
    return io.BytesIO(b"msch\x01" + zlib.compress(buffer.getvalue()))

@bot.command(name='convertimage', brief='!convertimage int majority/box/lanczos/mix/else')
async def convert(ctx, scale: int = 100, resample_method: str = 'LANCZOS'):
    """
    Converts attached image to mindustry schematic in sorters
    
    Parameters:
    scale (int): The scale to resize the image. Default is 100 (no resizing). if it is scaled bigger than 256 blocks it will make 256 blocks
    resample_method (str): The resampling method (majority box lanczos) default is lanczos
    """

    if not ctx.message.attachments: return await ctx.send('Please attach an image.')

    imageio = io.BytesIO(await ctx.message.attachments[0].read())

    with Image.open(imageio).convert('RGB') as image:
        image = resize_image(image, scale, resample_method.upper())
        image = convert_image_to_scheme(image, ctx.message.attachments[0].filename)

        await ctx.send(file=discord.File(fp=image, filename="scheme.msch"))

    del imageio, image
    gc.collect()

@bot.command(name='publish', brief='!publish after attach file or ctrl-c from clipboard')
async def convert_scheme(ctx, *, scheme: str = None):
    if scheme:
        with open('scheme.msch', 'wb') as f:
            f.write(base64.b64decode(scheme))
    elif ctx.message.attachments:
        attachment = ctx.message.attachments[0]
        if attachment.filename.endswith('.msch'):
            await attachment.save('scheme.msch')
        elif attachment.filename.endswith('.txt'):
            scheme = io.BytesIO(await ctx.message.attachments[0].read())
            with open('scheme.msch', 'wb') as f:
                f.write(base64.b64decode(scheme))

        else: return await ctx.send('Please provide a valid .msch file.')

    else: return await ctx.send('Please provide a base64 scheme or attach a .msch file.')

    # Run the Node.js script to convert the scheme to an image and get info
    SchematicInfo = execute("node schemecompiler.js")
    
    if SchematicInfo == False: return await ctx.send('There was an error processing the scheme.')
    
    SchematicInfo = json.loads(SchematicInfo)
    # Format the schematic info for the message
    schematic_info_message = (
        f"**Название:** {SchematicInfo.get('name')}\n"
        f"**Описание:** {SchematicInfo.get('description', 'none')}\n"
    )

    # Send the generated image and schematic info back to the specified channel
    channel = bot.get_channel(config['scheme_channel_id'])
    if channel:
        files = [discord.File('scheme.png')]
        if os.path.isfile('scheme.msch'): files.append(discord.File('scheme.msch', filename='scheme.msch'))
        await channel.send(content=schematic_info_message, files=files)
    else: await ctx.send('Failed to send the image to the specified channel.')

bot.run(config['token'])