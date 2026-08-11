# Armadyne

A Discord bot for a shared household:

- **Sunset reminders** - pings opted-in users in an announcement channel 15 minutes before sunset, calculated for a configured location.
- **Rent reminders** - posts in a rent channel daily during the last 5 days of the month until rent is marked paid. The paid status resets each month.

To operate a bot that's already running, see [RUNBOOK.md](RUNBOOK.md).

## Prerequisites

- Python 3.9 or newer.
- A Discord bot application. To create one at https://discord.com/developers/applications:
  - On the **Bot** tab, enable all three Privileged Gateway Intents and copy the token.
  - Invite the bot to your server: **OAuth2 → URL Generator**, select the `bot` scope with the Send Messages permission, and open the generated URL.

## Setup

Get the code (`git clone https://github.com/TheSkeward/Armadyne.git`, or download a ZIP from GitHub). From the project folder:

```bash
python3 -m venv env              # Windows: py -m venv env
source env/bin/activate          # Windows: env\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Fill in `.env`:

- `DISCORD_TOKEN`: the bot token.
- `ANNOUNCE_CHANNEL_ID`, `RENT_REMINDER_CHANNEL_ID`: channels for sunset and rent reminders. To copy an ID, enable **Settings → Advanced → Developer Mode** in Discord, then right-click the channel.
- `LOCATION_TIMEZONE`: an IANA timezone, e.g. `America/Los_Angeles`.
- `LOCATION_LAT`, `LOCATION_LON`: coordinates for the sunset calculation.
- `LOCATION_NAME`, `LOCATION_REGION`: display labels; any text.

Run:

```bash
python main.py
```

The bot creates its database (`armadyne.db`) on first run. If a required setting is missing, it exits with a `Cannot start:` message naming the setting.

## Usage

Users opt in to sunset pings with `$optin` and out with `$optout`. Rent is tracked with `$mark_rent_paid`, `$unmark_rent_paid`, and `$check_rent_status`. [RUNBOOK.md](RUNBOOK.md) has the full command reference and troubleshooting.

## Contributing

If you find a bug or have a feature request, please open an issue on GitHub. Pull requests are welcome.
