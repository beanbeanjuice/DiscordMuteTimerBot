import os
import discord
from discord import app_commands
from discord.ext import commands
import asyncio

# Load the bot token from the environment
TOKEN: str = os.environ['BOT_TOKEN']

# Define the bot with the necessary intents
intents = discord.Intents.default()
intents.messages = True

# Create a bot instance
bot = commands.Bot(command_prefix="/", intents=intents)


# Helper function to parse time input
def parse_duration(duration: str):
    time_units = {
        's': 1,  # seconds
        'm': 60,  # minutes
        'h': 3600,  # hours
        'd': 86400,  # days
    }
    try:
        unit = duration[-1].lower()  # Get the last character as the unit
        value = int(duration[:-1])  # Get the numeric part
        if unit in time_units:
            return value * time_units[unit]
    except ValueError:
        return None
    return None


# Define the /muteme slash command
@bot.tree.command(name="mute-me", description="Mute yourself after a specified duration.")
@app_commands.describe(duration="The time to wait until the bot server mutes you. (e.g., 10s, 5m, 2h, 1d)")
async def muteme(interaction: discord.Interaction, duration: str):
    mute_duration = parse_duration(duration)
    if mute_duration is None:
        await interaction.response.send_message(
            "Invalid duration format. Use something like '10s', '5m', '2h', or '1d'.", ephemeral=True
        )
        return

    # Acknowledge the command and start the timer
    await interaction.response.send_message(
        f"Got it! I'll mute you in {duration}.", ephemeral=True
    )

    # Wait for the duration
    await asyncio.sleep(mute_duration)

    # Apply timeout to the user (requires permissions)
    try:
        await interaction.user.edit(mute=True)
        await interaction.user.send(f"You have been server muted after a wait of {duration}.")
    except Exception as e:
        await interaction.followup.send(f"An error occurred: {e}", ephemeral=True)


# Sync slash commands on bot startup
@bot.event
async def on_ready():
    try:
        await bot.tree.sync()  # Sync commands to Discord
        print(f"Logged in as {bot.user}! Slash commands synced.")
    except Exception as e:
        print(f"Failed to sync commands: {e}")


# Run the bot
bot.run(TOKEN)
