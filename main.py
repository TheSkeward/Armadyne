import asyncio
import datetime
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

load_dotenv()

logger.setLevel(logging.INFO)

logger.addHandler(logging.StreamHandler())

intents = discord.Intents.all()
bot = commands.Bot(intents=intents, command_prefix="$")

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
    bot.loop.create_task(sunset_reminder())
    # Cancel the old sunset reminder task if it exists
    if bot.sunset_reminder_task:
        bot.sunset_reminder_task.cancel()
        # Start a new sunset reminder task
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
    while not bot.is_closed():
        tz = pytz.timezone(location_timezone)
        now = datetime.datetime.now(tz)
        s = sun(location_info.observer, date=now)
        sunset_time = s["sunset"]
        sunset_warning_time = sunset_time - datetime.timedelta(minutes=15)

        if now.date() == sunset_warning_time.date():
            if sunset_warning_time <= now < sunset_time:
                await send_sunset_reminder()
                time_until_tomorrow = (
                    (now + datetime.timedelta(days=1)).date() - now.date()
                ).total_seconds()
                logger.info("Waiting until tomorrow")
                await asyncio.sleep(time_until_tomorrow)
            else:
                time_until_warning = (sunset_warning_time - now).total_seconds()
                logger.info(
                    "Waiting for %s seconds until sunset warning",
                    time_until_warning,
                )
                await asyncio.sleep(min(time_until_warning, 60))
        else:
            time_until_tomorrow = (
                (now + datetime.timedelta(days=1)).date() - now.date()
            ).total_seconds()
            logger.info("Waiting until tomorrow")
            await asyncio.sleep(time_until_tomorrow)


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
