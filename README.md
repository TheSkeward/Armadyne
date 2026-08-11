# Armadyne
Armadyne is a Discord bot that sends sunset reminders to users who opt-in to receive them, plus rent reminders toward the end of each month. This bot is useful for groups of people who want to be reminded when it's time to finish up outdoor activities before sunset.

For day-to-day operation (checking on the bot, restarting it, fixing the token), see [RUNBOOK.md](RUNBOOK.md).

## Setup
1. Get the code (either `git clone` as below, or use GitHub's Code → Download ZIP button and unzip it):
```bash
git clone https://github.com/TheSkeward/Armadyne.git
cd Armadyne
```
2. In a terminal in that folder, create a virtual environment and install dependencies (requires Python 3.9 or newer):
```bash
python3 -m venv env          # on Windows: py -m venv env
source env/bin/activate      # on Windows: env\Scripts\activate
pip install -r requirements.txt
```
3. Copy `.env.example` to a new file named `.env` (a plain text file - any text editor works) and fill it in:
```bash
cp .env.example .env
```
- `DISCORD_TOKEN`: Your Discord bot token, from https://discord.com/developers/applications. If you're creating a new bot application there, enable all three Privileged Gateway Intents on its Bot tab, then invite the bot to your server: OAuth2 tab → URL Generator → tick `bot`, tick Send Messages → open the generated URL.
- `ANNOUNCE_CHANNEL_ID`: The ID of the channel where the bot will send sunset reminders. (Enable Developer Mode in Discord's settings, then right-click a channel to copy its ID.)
- `RENT_REMINDER_CHANNEL_ID`: The ID of the channel where the bot will send rent reminders.
- `LOCATION_NAME`: The name of the location where you want to calculate sunset times.
- `LOCATION_REGION`: The region of the location where you want to calculate sunset times.
- `LOCATION_TIMEZONE`: The timezone of the location (e.g. `America/Los_Angeles`).
- `LOCATION_LAT`: The latitude of the location where you want to calculate sunset times.
- `LOCATION_LON`: The longitude of the location where you want to calculate sunset times.
4. Run the bot:
```bash
python main.py
```
The bot creates its database (`armadyne.db`) automatically on first run.

## Usage
Once the bot is running, users can opt-in to receive sunset reminders by typing `$optin` in any channel. They can opt-out at any time by typing `$optout`. The bot will automatically send a reminder to the specified channel 15 minutes before sunset every day. Users who have opted in will be mentioned in the reminder message.

During the last 5 days of the month, the bot also posts a daily rent reminder until someone runs `$mark_rent_paid`. See `$help` for all commands, including `$unmark_rent_paid` and `$check_rent_status`.

## Contributing
If you find a bug or have a feature request, please open an issue on GitHub. Pull requests are welcome.
