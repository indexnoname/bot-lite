from discord.ext import commands
import discord
import subprocess
import json
import os

# Load configuration from JSON file
with open('config.json', 'r') as config_file:
    config = json.load(config_file)
CHANNEL_ID = int(config['channel_id'])

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

# Command to list all AI models in Ollama
@bot.command(name='ailist')
async def ailist(ctx):
    model_names = get_model_list()
    await ctx.send("Available models:\n```\n{}\n```".format('\n'.join(model_names)))

# Command to run a specific model in Ollama
@bot.command(name='airun')
async def airun(ctx, model: str, prompt: str):
    # Check if the model exists
    model_names = get_model_list()
    if model not in model_names:
        await ctx.send(f"Model '{model}' not found in Ollama.")
        return

    # Run the model
    await ctx.send(f"Running model '{model}'...")
    execute_shell_command(f'ollama run {model} {prompt}]')
    await ctx.send(f"Model '{model}' is running.")

# Run the bot with your token
bot.run(config['token'])