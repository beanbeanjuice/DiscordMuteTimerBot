import os
import discord
from discord import app_commands
from discord.ext import commands, tasks
import asyncio
from random import randrange

# Load the bot token from the environment
TOKEN: str = os.environ['BOT_TOKEN']

# Define the bot with the necessary intents
intents = discord.Intents.default()
intents.messages = True

# Create a bot instance
bot = commands.Bot(command_prefix="/", intents=intents)

# Dictionary to track mute tasks for users
mute_tasks = {}

# Counter for commands run
commands_run = 0

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

# Define the /mute-me command
@bot.tree.command(name="mute-me", description="Mute yourself after a specified duration.")
@app_commands.describe(duration="The time to wait until the bot server mutes you. (e.g., 10s, 5m, 2h, 1d)")
async def muteme(interaction: discord.Interaction, duration: str):
    global commands_run
    commands_run += 1

    if interaction.user.id in mute_tasks:
        await interaction.response.send_message(
            "You already have an active mute timer. Please cancel it first with /mute-me-cancel.", ephemeral=True
        )
        return

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

    async def mute_task():
        try:
            # Wait for the duration
            await asyncio.sleep(mute_duration)

            # Apply timeout to the user (requires permissions)
            await interaction.user.edit(mute=True)
            await interaction.user.send(f"You have been server muted after a wait of {duration}.")
        except asyncio.CancelledError:
            # Handle task cancellation
            await interaction.user.send("Your mute request has been canceled.")
        finally:
            # Remove the task from the dictionary when finished or canceled
            mute_tasks.pop(interaction.user.id, None)

    # Store the mute task
    task = asyncio.create_task(mute_task())
    mute_tasks[interaction.user.id] = task

# Define the /mute-me-cancel command
@bot.tree.command(name="mute-me-cancel", description="Cancel your mute timer.")
async def mute_me_cancel(interaction: discord.Interaction):
    global commands_run
    commands_run += 1

    if interaction.user.id in mute_tasks:
        mute_tasks[interaction.user.id].cancel()
        del mute_tasks[interaction.user.id]
        await interaction.response.send_message(
            "Your mute timer has been canceled.", ephemeral=True
        )
    else:
        await interaction.response.send_message(
            "You don't have an active mute timer to cancel.", ephemeral=True
        )

# Background task to update the bot's activity
@tasks.loop(minutes=10)
async def update_activity():
    activity_texts = [
        f"Watching over {len(bot.guilds)} servers!",
        f"Falling asleep {commands_run} times...",
    ]

    index: int = randrange(len(activity_texts))
    text: str = activity_texts[index]
    activity = discord.CustomActivity(name=text)
    await bot.change_presence(activity=activity)
    print(f"Updating Discord Presence: {text}")

# Sync slash commands on bot startup
@bot.event
async def on_ready():
    try:
        await bot.tree.sync()  # Sync commands to Discord
        update_activity.start()  # Start the activity updater task
        print(f"Logged in as {bot.user}! Slash commands synced.")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

# Run the bot
bot.run(TOKEN)
