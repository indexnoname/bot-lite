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
def execute_shell_command(command):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout

# Function to get the list of models from ollama list
def get_model_list():
    output = execute_shell_command('ollama list')
    lines = output.splitlines()
    model_names = [line.split()[0] for line in lines[1:]]  # Skip the header line and get the first word of each line
    return model_names

@bot.event
async def on_ready():
    print(f'Bot is ready. Logged in as {bot.user}')

@bot.event
async def on_member_join(member):
    channel = bot.get_channel(info['welcome_channel_id'])
    if channel:
        await channel.send(f'Hello {member.mention}! Welcome to the server!')

# Command to list all AI models in Ollama
@bot.command(name='ailist')
async def ailist(ctx):
    output = execute_shell_command('ollama list')
    await ctx.send(f"Available models:\n```\n{output}\n```")



# Command to run a specific model in Ollama
@bot.command(name='airun')
async def airun(ctx, model: str, *, prompt: str):
    # Check if the model exists
    model_names = get_model_list()
    if model not in model_names:
        await ctx.send(f"Model '{model}' not found in Ollama.")
        return

    # Run the model
    await ctx.send(f"Running model '{model}'...")
    out = execute_shell_command(f'ollama run {model} {prompt}]')
    await ctx.send(out)

# Run the bot with your token
bot.run(config['token'])
