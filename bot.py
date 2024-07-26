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
bot = discord.Bot(command_prefix='!', intents=intents)

# Function to execute a shell command and return the output
def execute_shell_command(command):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout

# Command to list all AI models in Ollama
@bot.command(name='ailist')
async def ailist(ctx):
    output = execute_shell_command('ollama show')
    await ctx.send(f"Available models:\n```\n{output}\n```")

# Command to run a specific model in Ollama
@bot.command(name='airun')
async def airun(ctx, model: str):
    # Check if the model exists
    model_list = execute_shell_command('ollama show')
    if model not in model_list:
        await ctx.send(f"Model '{model}' not found in Ollama.")
        return

    # Run the model
    await ctx.send(f"Running model '{model}'...")
    execute_shell_command(f'ollama run {model}')
    await ctx.send(f"Model '{model}' is running.")

# Run the bot with your token
bot.run(config['token'])
