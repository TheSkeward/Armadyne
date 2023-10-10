# bot.py
import asyncio
from datetime import datetime, timedelta

import perpetuo
import uvloop

uvloop.install()
perpetuo.dwim()
import logging
import os

import discord
import pytz
from astral import LocationInfo
from astral.sun import sun
from discord.ext import commands
from dotenv import load_dotenv

from db_handler import DBHandler

logger = logging.getLogger("armadyne")

import load_config

config = load_config.ArmadyneConfig()

load_dotenv()

logger.setLevel(logging.INFO)

logger.addHandler(logging.StreamHandler())

intents = discord.Intents.all()


class SunsetReminderBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sunset_reminder_task = None


bot = SunsetReminderBot(intents=intents, command_prefix="$")

token = os.environ.get("DISCORD_TOKEN")
bot.announce_channel_id = int(os.environ.get("ANNOUNCE_CHANNEL_ID"))
location_name = os.environ.get("LOCATION_NAME")
location_region = os.environ.get("LOCATION_REGION")
location_timezone = os.environ.get("LOCATION_TIMEZONE")
location_lat = float(os.environ.get("LOCATION_LAT"))
location_lon = float(os.environ.get("LOCATION_LON"))

db_handler = DBHandler("armadyne.db")
location_info = LocationInfo(
    location_name, location_region, location_timezone, location_lat, location_lon
)


@bot.event
async def on_ready():
    """Initialization"""
    db_handler.create_tables("tables.sql")
    logger.info("Connected to armadyne.db")
    logger.info("Logged in as %s (%s)", bot.user.name, bot.user.id)

    if bot.sunset_reminder_task:
        bot.sunset_reminder_task.cancel()
        logger.info("Old sunset reminder task cancelled")

    bot.sunset_reminder_task = bot.loop.create_task(sunset_reminder())


@bot.command()
async def optin(ctx):
    if db_handler.is_user_opted_in(ctx.author.id):
        await ctx.send(
            f"{ctx.author.mention} has already opted in to receive sunset reminders."
        )
    else:
        db_handler.add_user(ctx.author.id)
        await ctx.send(
            f"{ctx.author.mention} has opted in to receive sunset reminders."
        )


@bot.command()
async def optout(ctx):
    db_handler.remove_user(ctx.author.id)
    await ctx.send(f"{ctx.author.mention} has opted out of sunset reminders.")


async def sunset_reminder():
    await bot.wait_until_ready()
    print("sunset_reminder function has started.")  # Debug point 1
    tz = pytz.timezone(location_timezone)

    current_date = datetime.now(tz).date()
    print(f"Current date set to {current_date}.")  # Debug point 2

    while not bot.is_closed():
        now = datetime.now(tz)
        s = sun(location_info.observer, date=current_date)
        sunset_time = s["sunset"]
        sunset_warning_time = sunset_time - timedelta(minutes=15)

        print(
            f"Now: {now}, Sunset Time: {sunset_time}, Sunset Warning Time: {sunset_warning_time}"
        )  # Debug point 3

        if now.date() == sunset_warning_time.date():
            print("Date condition met.")  # Debug point 4
            if sunset_warning_time <= now < sunset_time:
                print("Sending sunset reminder.")  # Debug point 5
                await send_sunset_reminder()
                current_date += timedelta(days=1)
                print(f"Incremented current_date to {current_date}.")  # Debug point 6
            elif now >= sunset_time:  # Check if current time is past sunset
                current_date += timedelta(days=1)
                print(
                    f"Incremented current_date to {current_date} because sunset time has passed."
                )  # New debug point
            else:
                time_until_warning = (sunset_warning_time - now).total_seconds()
                print(
                    f"Time until warning: {time_until_warning} seconds."
                )  # Debug point 7
                await asyncio.sleep(min(time_until_warning, 60))
        else:
            current_date += timedelta(days=1)
            print(
                f"Incremented current_date to {current_date} due to date mismatch."
            )  # New debug point

        await asyncio.sleep(1)  # Prevent 100% CPU usage


async def send_sunset_reminder():
    opted_in_users = db_handler.get_users()
    user_mentions = []
    for row in opted_in_users:
        user = bot.get_user(row[0])
        if user:
            user_mentions.append(user.mention)
            logger.info("Added user %s to sunset reminder", row[0])
    message = f"Just a reminder that the sun will set in fifteen minutes! {', '.join(user_mentions)}"
    channel = bot.get_channel(bot.announce_channel_id)
    await channel.send(message)
    logger.info("Sent sunset reminder to channel %s", bot.announce_channel_id)


logger.info("Running bot!")
bot.run(token)
