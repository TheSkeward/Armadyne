# Armadyne Runbook

Day-to-day guide for whoever looks after the bot. No programming knowledge needed.

## What the bot does
- About 15 minutes before sunset each day, it pings everyone who opted in, in the announcements channel.
- During the last 5 days of the month, it posts a rent reminder once a day in the rent channel, until someone marks rent as paid.
- When a new month starts, rent counts as "not paid yet" again automatically.

## Commands
| Command | What it does |
| --- | --- |
| `$optin` | Start getting sunset pings |
| `$optout` | Stop getting sunset pings |
| `$mark_rent_paid` | Rent is paid this month; stop the reminders |
| `$unmark_rent_paid` | Undo that, if it was marked by mistake |
| `$check_rent_status` | Ask whether rent is marked paid |
| `$help` | List all commands |

## If the bot is offline or not responding
Restart it: on the machine where it runs, stop the old process if one is still going, then run `python main.py` in the bot's folder. Restarting is always safe - the bot can't lose anything important. If it prints a message starting with "Cannot start:", that message names the exact setting to fix in the `.env` file. If it instead stops with a long wall of error text, read its last line - that's the actual problem; everything above it is just where it happened.

If Discord rejected the token, get a fresh one at https://discord.com/developers/applications (open the bot's application, Bot tab, "Reset Token"), put it in `.env` as `DISCORD_TOKEN`, and restart. No access to the old application? Create a new one - see the README's Setup section; nothing of value is lost.

## Good to know
- The bot needs an always-on computer, but any one will do. Setting it up on a new machine is the README's Setup section.
- It only runs while its terminal window stays open - if the window closes or the machine sleeps, the bot goes offline until someone starts it again.
- Its memory (`armadyne.db`) only stores who opted in and whether rent is paid this month. If it's ever lost, people just type `$optin` again - no backups needed.
- The `.env` file contains the bot's secret token. Don't share its contents.
