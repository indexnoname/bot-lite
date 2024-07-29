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

# Run the bot with your token
bot.run(config['token'])