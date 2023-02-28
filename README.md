# Armadyne
Armadyne is a Discord bot that sends sunset reminders to users who opt-in to receive them. This bot is useful for groups of people who want to be reminded when it's time to finish up outdoor activities before sunset.

## Setup
1. Clone the repository: 
```bash
git clone https://github.com/TheSkeward/Armadyne.git
cd Armadyne
```
2. Create a virtual environment and install dependencies:
```bash
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```
3. Copy the example environment variables file and edit it to your liking:
```bash
cp .env.example .env
nano .env
```
- `DISCORD_TOKEN`: Your Discord bot token.
- `ANNOUNCE_CHANNEL_ID`: The ID of the channel where the bot will send sunset reminders.
- `LOCATION_NAME`: The name of the location where you want to calculate sunset times.
- `LOCATION_REGION`: The region of the location where you want to calculate sunset times.
- `LOCATION_TIMEZONE`: The timezone of the location where you want to calculate sunset times.
- `LOCATION_LAT`: The latitude of the location where you want to calculate sunset times.
- `LOCATION_LON`: The longitude of the location where you want to calculate sunset times.
4. Create the database tables:
```bash
sqlite3 armadyne.db < tables.sql
```
5. Run the bot:
```bash
python main.py
```
## Usage
Once the bot is running, users can opt-in to receive sunset reminders by typing `$optin` in any channel. They can opt-out at any time by typing `$optout`. The bot will automatically send a reminder to the specified channel 10 minutes before sunset every day. Users who have opted in will be mentioned in the reminder message.

## Contributing
If you find a bug or have a feature request, please open an issue on GitHub. Pull requests are welcome.
