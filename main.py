import asyncio
import datetime
import logging
import os
import sqlite3

import discord
import pytz
from astral import LocationInfo
from astral.sun import sun
from discord.ext import commands
from dotenv import load_dotenv

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

global conn


@bot.event
async def on_ready():
    """Initialization"""
    global conn
    conn = sqlite3.connect("armadyne.db")
    cur = conn.cursor()
    logger.info("Connected to armadyne.db")
    cur.executescript(open("tables.sql").read())
    conn.commit()
    logger.info("Logged in as %s (%s)", bot.user.name, bot.user.id)
    bot.loop.create_task(sunset_reminder())


@bot.command()
async def optin(ctx):
    global conn
    cur = conn.cursor()
    cur.execute(
        "SELECT user_id FROM sunset_reminder WHERE user_id = ?;", (ctx.author.id,)
    )
    result = cur.fetchone()
    if result:
        await ctx.send(
            f"{ctx.author.mention} has already opted in to receive sunset reminders."
        )
    else:
        cur.execute(
            "INSERT INTO sunset_reminder (user_id) VALUES (?);", (ctx.author.id,)
        )
        conn.commit()
        await ctx.send(
            f"{ctx.author.mention} has opted in to receive sunset reminders."
        )


@bot.command()
async def optout(ctx):
    global conn
    cur = conn.cursor()
    cur.execute("DELETE FROM sunset_reminder WHERE user_id = ?;", (ctx.author.id,))
    conn.commit()
    await ctx.send(f"{ctx.author.mention} has opted out of sunset reminders.")


async def sunset_reminder():
    await bot.wait_until_ready()
    while not bot.is_closed():
        tz = pytz.timezone(location_timezone)
        now = datetime.datetime.now(tz)
        s = sun(city.observer, date=now)
        sunset_time = s["sunset"]
        if now.date() < sunset_time.date():
            time_until_sunset = (
                sunset_time - now - datetime.timedelta(minutes=10)
            ).total_seconds()
            if time_until_sunset > 0:
                logger.info("Waiting for %s seconds until sunset", time_until_sunset)
                await asyncio.sleep(min(time_until_sunset, 60))
            else:
                logger.info("Sending sunset reminder immediately")
                await send_sunset_reminder()
        else:
            sunset_warning_time = sunset_time - datetime.timedelta(minutes=10)
            if now >= sunset_warning_time:
                await send_sunset_reminder()
                logger.info("Waiting until tomorrow")
                await asyncio.sleep(23 * 60 * 60)
            else:
                time_until_warning = (
                    sunset_warning_time - now - datetime.timedelta(minutes=10)
                ).total_seconds()
                logger.info(
                    "Waiting for %s seconds until sunset warning",
                    time_until_warning,
                )
                await asyncio.sleep(min(time_until_warning, 60))


async def send_sunset_reminder():
    cur = conn.cursor()
    cur.execute("SELECT user_id FROM sunset_reminder;")
    opted_in_users = []
    for row in cur.fetchall():
        user = bot.get_user(row[0])
        if user:
            opted_in_users.append(user.mention)
            logger.info("Added user %s to sunset reminder", row[0])
    message = f"Just a reminder that the sun will set in ten minutes! {', '.join(opted_in_users)}"
    channel = bot.get_channel(bot.announce_channel_id)
    await channel.send(message)
    logger.info("Sent sunset reminder to channel %s", bot.announce_channel_id)


city = LocationInfo(
    location_name, location_region, location_timezone, location_lat, location_lon
)

logger.info("Running bot!")
bot.run(token)
