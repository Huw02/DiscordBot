from ekSkemaScraper import scrapeTo as scrape_kea
import requests
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8')


def main_job():
    all_jobs = []

    print("\n=== Scraping KEA ===", file=sys.stderr)
    try:
        all_jobs += scrape_kea()
    except Exception as e:
        print(f"⚠️ KEA scraper failed: {e}", file=sys.stderr)

    if all_jobs:
        print(f"🎉 Total scraped: {len(all_jobs)} jobs", file=sys.stderr)
        # Kun JSON printes til stdout
        print(all_jobs := all_jobs)  # dette kan bruges til Spring Boot, men bedre: json.dumps(all_jobs)
        import json
        print(json.dumps(all_jobs))
        return all_jobs
    else:
        print("🚫 No jobs scraped.", file=sys.stderr)



import discord
from discord.ext import commands, tasks
import datetime
import requests
import os
from dotenv import load_dotenv

# Load environment variables fra .env
load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")   # jeres bot token
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))  # ID på Discord kanal

# Lav bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"{bot.user} er logget ind!")
    send_schedule.start()  # starter loopet når botten logger ind

import datetime
import requests

def fetch_schedule():
    try:

        data = main_job()

        print("DEBUG API:", data)  # kan slettes senere

        # Dagens dato som streng i formatet dd.mm.yyyy
        today_str = datetime.date.today().strftime("%d.%m.%Y")

        # Filtrér kun de elementer, der matcher dagens dato
        today_schedule = [item for item in data if today_str in item["time"]]
        return today_schedule

    except Exception as e:
        print("Fejl ved API kald:", e)
        return []


tz = datetime.timezone(datetime.timedelta(hours=2))  # dansk sommertid
@tasks.loop(time=datetime.time(hour=7, minute=00, tzinfo=tz))
async def send_schedule():
    await bot.wait_until_ready()  # sikrer at botten er klar
    channel = bot.get_channel(CHANNEL_ID)
    if channel is None:
        print("FEJL: Kanalen findes ikke!")
        return

    schedule = fetch_schedule()
    today = datetime.date.today().strftime("%d.%m.%Y")

    if schedule:
        msg = f"📅 Skema for {today}:\n"
        for s in schedule:
            time_only = s['time'].split()[1] if ' ' in s['time'] else s['time']
            msg += f"- {s['subject']} kl. {time_only} i {s['room']}\n"
        await channel.send(msg)
    else:
        await channel.send(f"🎉 Ingen undervisning i dag ({today})")



# Ekstra: manuel kommando til test
@bot.command()
async def skema(ctx):
    """Sender dagens skema på kommando (!skema)"""
    await bot.wait_until_ready()  # sikrer at botten er klar
    channel = bot.get_channel(CHANNEL_ID)
    if channel is None:
        print("FEJL: Kanalen findes ikke!")
        return

    schedule = fetch_schedule()
    today = datetime.date.today().strftime("%d.%m.%Y")

    if schedule:
        msg = f"📅 Skema for {today}:\n"
        for s in schedule:
            time_only = s['time'].split()[1] if ' ' in s['time'] else s['time']
            msg += f"- {s['subject']} kl. {time_only} i {s['room']}\n"
        await channel.send(msg)
    else:
        await channel.send(f"🎉 Ingen undervisning i dag ({today})")

bot.run(TOKEN)
