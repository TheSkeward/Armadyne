# bot.py


import asyncio
import calendar
import logging
import os
from datetime import datetime, timedelta

import discord
import pytz
from astral import LocationInfo
from astral.sun import sun
from discord.ext import commands
from dotenv import load_dotenv

from db_handler import DBHandler

# command handler class


class CommandHandler:

    # constructor

    def __init__(self, client):
        self.client = client
        self.commands = []

    def add_command(self, command):
        self.commands.append(command)

    async def command_handler(self, message):
        for command in self.commands:
            if message.content.startswith(command["trigger"]):
                args = message.content.split(" ")
                if args[0] == command["trigger"]:
                    args.pop(0)
                    if command["arg_num"] == 0:
                        if command["async"]:
                            return await command["function"](message, self.client, args)
                        else:
                            return await message.channel.send(
                                str(command["function"](message, self.client, args))
                            )
                    else:
                        if len(args) >= command["args_num"]:
                            if command["async"]:
                                return await command["function"](
                                    message, self.client, args
                                )
                            else:
                                return await message.channel.send(
                                    str(command["function"](message, self.client, args))
                                )
                        else:
                            return await message.channel.send(
                                'command "{}" requires {} argument(s) "{}"'.format(
                                    command["trigger"],
                                    command["args_num"],
                                    ", ".join(command["args_name"]),
                                )
                            )


load_dotenv()

logger = logging.getLogger("armadyne")
logger.setLevel(logging.INFO)

intents = discord.Intents.all()


class SunsetReminderBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sunset_reminder_task = None


bot = SunsetReminderBot(intents=intents, command_prefix="$")

token = os.environ.get("DISCORD_TOKEN")
bot.announce_channel_id = int(os.environ.get("ANNOUNCE_CHANNEL_ID"))
bot.rent_reminder_channel_id = int(os.environ.get("RENT_REMINDER_CHANNEL_ID"))
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


@bot.command()
async def mark_rent_paid(ctx):
    """Marks rent as paid for the month."""
    db_handler.set_rent_paid(True)
    await ctx.send("Rent has been marked as paid. Thank you!")


@bot.command()
async def unmark_rent_paid(ctx):
    """Unmarks rent as paid for the month."""
    db_handler.set_rent_paid(False)
    await ctx.send("Rent has been unmarked as paid for this month.")


@bot.command()
async def check_rent_status(ctx):
    """Checks if rent has been marked as paid for the month."""
    if db_handler.is_rent_paid():
        await ctx.send("Rent has been marked as paid for this month.")
    else:
        await ctx.send("Rent has not been marked as paid yet for this month.")


async def sunset_reminder():
    await bot.wait_until_ready()
    tz = pytz.timezone(location_timezone)

    while not bot.is_closed():
        now = datetime.now(tz)
        today = now.date()

        if now.day == 2:
            db_handler.set_rent_paid(False)
            logger.info("Reset rent paid status for the new month.")

        s = sun(location_info.observer, date=today)
        sunset_time = s["sunset"]
        logger.info(f"Sunset time today is {sunset_time} for {location_name}.")
        sunset_warning_time = sunset_time - timedelta(minutes=15)

        if sunset_warning_time <= now < sunset_time:
            await send_sunset_reminder()
            await asyncio.sleep((sunset_time - now).total_seconds())
        elif now < sunset_warning_time:
            await asyncio.sleep((sunset_warning_time - now).total_seconds())

        await check_and_send_rent_reminder(now)

        tomorrow = datetime.combine(
            today + timedelta(days=1), datetime.min.time()
        ).replace(tzinfo=tz)
        await asyncio.sleep((tomorrow - now).total_seconds())


async def check_and_send_rent_reminder(now):
    last_day_of_month = calendar.monthrange(now.year, now.month)[1]
    days_until_end_of_month = last_day_of_month - now.day

    if days_until_end_of_month <= 5 and not db_handler.is_rent_paid():
        await send_rent_reminder()


async def send_rent_reminder():
    rent_message = "A friendly reminder: Rent is due soon!"
    rent_channel = bot.get_channel(bot.rent_reminder_channel_id)

    tz = pytz.timezone(location_timezone)
    if not db_handler.reminder_sent_today(tz):
        await rent_channel.send(rent_message)
        db_handler.log_reminder_sent(tz)
        logger.info("Sent rent reminder to channel %s", bot.rent_reminder_channel_id)
    else:
        logger.info("Rent reminder already sent today, skipping")


async def send_sunset_reminder():
    opted_in_users = db_handler.get_users()
    user_mentions = [
        bot.get_user(row[0]).mention for row in opted_in_users if bot.get_user(row[0])
    ]

    sunset_message = f"Just a reminder that the sun will set in fifteen minutes! {', '.join(user_mentions)}"
    sunset_channel = bot.get_channel(bot.announce_channel_id)
    await sunset_channel.send(sunset_message)
    logger.info("Sent sunset reminder to channel %s", bot.announce_channel_id)


logger.info("Running bot!")
bot.run(token)
