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
API_URL = os.getenv("API_URL")  # Spring Boot endpoint, fx: https://jeres-app.azurewebsites.net/api/schedule

# Lav bot
bot = commands.Bot(command_prefix="!", intents=discord.Intents.default())

@bot.event
async def on_ready():
    print(f"{bot.user} er logget ind!")
    send_schedule.start()  # starter loopet når botten logger ind

import datetime
import requests

def fetch_schedule():
    try:
        response = requests.get(API_URL, timeout=10)
        response.raise_for_status()
        data = response.json()

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
@tasks.loop(time=datetime.time(hour=15, minute=2, tzinfo=tz))
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
    schedule = fetch_schedule()
    print(fetch_schedule())
    if schedule:
        msg = "📅 Dagens skema:\n"
        for s in schedule:
            msg += f"- {s['subject']} ({s['start']} - {s['end']}) i {s['room']}\n"
        await ctx.send(msg)
    else:
        await ctx.send("Ingen undervisning i dag 🎉")

bot.run(TOKEN)
