import discord
from discord.ext import commands
import random
import json
import os

TOKEN = os.getenv("TOKEN")
PREFIX = "!"

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

DATA_FILE = "data.json"

# -----------------------
# Economy Helpers
# -----------------------
def load_data():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump({}, f)
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def get_user(data, user_id):
    uid = str(user_id)
    if uid not in data:
        data[uid] = {"cash": 100}
    return data[uid]

# -----------------------
# Events
# -----------------------
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

# -----------------------
# Economy Commands
# -----------------------
@bot.command()
async def balance(ctx):
    data = load_data()
    user = get_user(data, ctx.author.id)
    await ctx.send(f"💰 **{ctx.author.name}** has **{user['cash']} coins**")

@bot.command()
async def daily(ctx):
    data = load_data()
    user = get_user(data, ctx.author.id)
    reward = random.randint(50, 150)
    user["cash"] += reward
    save_data(data)
    await ctx.send(f"🆓 You received **{reward} coins**!")

@bot.command()
async def coinflip(ctx, choice: str, bet: int):
    choice = choice.lower()
    if choice not in ["heads", "tails"]:
        return await ctx.send("Use `heads` or `tails`")

    if bet <= 0:
        return await ctx.send("❌ Invalid bet")

    data = load_data()
    user = get_user(data, ctx.author.id)

    if user["cash"] < bet:
        return await ctx.send("❌ Not enough money")

    result = random.choice(["heads", "tails"])

    if choice == result:
        user["cash"] += bet
        msg = f"🪙 **{result}** — You won **{bet} coins**!"
    else:
        user["cash"] -= bet
        msg = f"🪙 **{result}** — You lost **{bet} coins**!"

    save_data(data)
    await ctx.send(msg)

@bot.command()
async def dice(ctx, bet: int):
    if bet <= 0:
        return await ctx.send("❌ Invalid bet")

    data = load_data()
    user = get_user(data, ctx.author.id)

    if user["cash"] < bet:
        return await ctx.send("❌ Not enough money")

    player = random.randint(1, 6)
    bot_roll = random.randint(1, 6)

    if player > bot_roll:
        user["cash"] += bet
        result = f"🎲 You rolled **{player}**, bot rolled **{bot_roll}** — **You win {bet} coins!**"
    elif player < bot_roll:
        user["cash"] -= bet
        result = f"🎲 You rolled **{player}**, bot rolled **{bot_roll}** — **You lose {bet} coins!**"
    else:
        result = f"🎲 Both rolled **{player}** — **Draw!**"

    save_data(data)
    await ctx.send(result)

# -----------------------
bot.run(TOKEN)

