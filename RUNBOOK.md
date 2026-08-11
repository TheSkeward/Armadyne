# Armadyne Runbook

Operating guide for the running bot. For setup on a new machine, see [README.md](README.md).

## What the bot does

- Pings opted-in users in the announcements channel about 15 minutes before sunset.
- Posts a daily rent reminder in the rent channel during the last 5 days of the month, until rent is marked paid.
- Resets the rent-paid status at the start of each month.

## Commands

Commands work in any channel the bot can read.

| Command | Effect |
| --- | --- |
| `$optin` | Receive sunset pings |
| `$optout` | Stop receiving sunset pings |
| `$mark_rent_paid` | Mark rent paid for this month; stops reminders |
| `$unmark_rent_paid` | Clear the paid mark |
| `$check_rent_status` | Show whether rent is marked paid |
| `$help` | List commands |

## Troubleshooting

The bot stays online only while its process is running; a reboot or crash takes it offline until it's started again. Restarting is always safe: stop any old process, then run `python main.py` in the bot's folder. To restart automatically, run it as a service.

Startup failures print a `Cannot start:` message naming the `.env` setting to fix. Other errors exit with a traceback; the last line is the actual error.

If Discord rejects the token, reset it at https://discord.com/developers/applications (the bot's application → **Bot** tab → **Reset Token**), update `DISCORD_TOKEN` in `.env`, and restart. Without access to the application, create a new one (see the README) - the bot keeps nothing that can't be recreated.

## Notes

- The database (`armadyne.db`) holds only opt-ins and the current month's rent status. If it's lost, users re-run `$optin`; no backups needed.
- `.env` contains the bot token; keep it private.
- Any always-on machine can host the bot.
