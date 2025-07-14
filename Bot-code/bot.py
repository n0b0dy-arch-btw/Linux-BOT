import discord
from discord.ext import commands
import random
import asyncio
import json
import os
import time

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)
bot.remove_command("help")  # Remove default help command

warns = {}  # Store warnings in memory

# ================================
# Admin System (per-server)
# ================================
ADMIN_FILE = "admins.json"

# Load function now expects a dict of dicts: {guild_id: {"admin": user_id, "server_name": name}}
def load_admins():
    if os.path.exists(ADMIN_FILE):
        with open(ADMIN_FILE, "r") as f:
            return json.load(f)
    return {}

def save_admins(admins):
    with open(ADMIN_FILE, "w") as f:
        json.dump(admins, f, indent=4)

server_admins = load_admins()

# Updated to check inside the nested "admin" key
def is_admin(ctx):
    guild_id = str(ctx.guild.id)
    admin_info = server_admins.get(guild_id)
    if admin_info:
        return str(ctx.author.id) == admin_info.get("admin")
    return False

@bot.command(help="Set the admin for this server (bot owner only).")
@commands.is_owner()
async def setadmin(ctx, member: discord.Member):
    guild_id = str(ctx.guild.id)
    server_admins[guild_id] = {
        "admin": str(member.id),
        "server_name": ctx.guild.name
    }
    save_admins(server_admins)
    await ctx.send(f"✅ {member.name} is now the admin for **{ctx.guild.name}**.")


#--------------------
#terms of service
#--------------------


@bot.command(name="terms", help="Display the Terms of Service and Privacy Policy.")
async def terms(ctx):
    tos_url = "https://wiki.world-compute.com/TermsofService.html"
    privacy_url = "https://wiki.world-compute.com/"

    embed = discord.Embed(
        title="📄 Terms of Service & Privacy Policy",
        color=discord.Color.blue(),
        description="Please read our Terms of Service and Privacy Policy at the links below."
    )
    embed.add_field(name="📘 Terms of Service", value=f"[View Terms of Service]({tos_url})", inline=False)
    embed.add_field(name="🔐 Privacy Policy", value=f"[View Privacy Policy]({privacy_url})", inline=False)

    await ctx.send(embed=embed)




# ================================
# Events
# ================================
@bot.event
async def on_ready():
    print(f"��� Linux-BOT is online as {bot.user}!")

@bot.event
async def on_member_join(member):
    channel = next((ch for ch in member.guild.text_channels if ch.permissions_for(member.guild.me).send_messages), None)
    if channel:
        await channel.send(f"���� Welcome to the server, {member.mention}!")

# ================================
# Moderation Commands
# ================================
@bot.command(help="Kick a member from the server.")
async def kick(ctx, member: discord.Member, *, reason="No reason provided"):
    if not is_admin(ctx):
        await ctx.send("��� You are not authorized to use this command.")
        return
    await member.kick(reason=reason)
    await ctx.send(f"���� {member} was kicked. Reason: {reason}")

@bot.command(help="Ban a member from the server.")
async def ban(ctx, member: discord.Member, *, reason="No reason provided"):
    if not is_admin(ctx):
        await ctx.send("��� You are not authorized to use this command.")
        return
    await member.ban(reason=reason)
    await ctx.send(f"���� {member} was banned. Reason: {reason}")

@bot.command(help="Warn a user (stored in memory).")
async def warn(ctx, member: discord.Member, *, reason="No reason provided"):
    if not is_admin(ctx):
        await ctx.send("��� You are not authorized to use this command.")
        return
    if member.bot:
        await ctx.send("���� You can't warn a bot.")
        return
    if member == ctx.author:
        await ctx.send("��� You can't warn yourself.")
        return

    user_id = str(member.id)
    if user_id not in warns:
        warns[user_id] = []
    warns[user_id].append(reason)

    await ctx.send(f"��� {member.mention} has been warned. Reason: {reason} (Total warnings: {len(warns[user_id])})")

# ================================
# Fun Commands
# ================================
@bot.command(name="8ball", help="Ask the magic 8-ball a question.")
async def eight_ball(ctx, *, question):
    responses = [
        "Yes.", "No.", "Maybe.", "Definitely!",
        "Ask again later.", "I'm not sure.", "Absolutely!", "Not likely."
    ]
    await ctx.send(f"���� {random.choice(responses)}")

@bot.command(help="Flip a coin.")
async def coinflip(ctx):
    await ctx.send(f"���� {random.choice(['Heads', 'Tails'])}")

@bot.command(help="true or false")
async def truefalse(ctx):
    await ctx.send(f"hmm true or false {random.choice(['True', 'False'])}")

@bot.command(help="Roll a number between 1 and the given max (default 100).")
async def roll(ctx, max_number: int = 100):
    await ctx.send(f"���� You rolled: {random.randint(1, max_number)}")

@bot.command(help="the bot will say text you enter")
async def say(ctx, *, message: str):
    await ctx.send(f"{ctx.author.display_name} says: {message}")

@bot.command(help="slots game")
async def slots(ctx):
    emojis = ["����", "����", "����", "����", "���", "����"]
    slot1 = random.choice(emojis)
    slot2 = random.choice(emojis)
    slot3 = random.choice(emojis)

    result = f"{slot1} | {slot2} | {slot3}"

    if slot1 == slot2 == slot3:
        await ctx.send(f"{result}\n���� JACKPOT! You won! ����")
    elif slot1 == slot2 or slot2 == slot3 or slot1 == slot3:
        await ctx.send(f"{result}\n���� Nice! You got two of a kind!")
    else:
        await ctx.send(f"{result}\n���� You lost. Try again!")

start_time = time.time()

@bot.command(help="bots uptime")
async def uptime(ctx):
    current_time = time.time()
    uptime_seconds = int(current_time - start_time)

    hours, remainder = divmod(uptime_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    await ctx.send(f"���� Uptime: {hours}h {minutes}m {seconds}s")





# ================================
# Info Commands
# ================================
@bot.command(help="Show information about a user.")
async def userinfo(ctx, member: discord.Member = None):
    member = member or ctx.author
    embed = discord.Embed(title="���� User Info", color=discord.Color.blue())
    embed.add_field(name="Name", value=member.name, inline=True)
    embed.add_field(name="ID", value=member.id, inline=True)
    embed.add_field(name="Status", value=member.status, inline=True)
    embed.add_field(name="Joined", value=member.joined_at.strftime('%Y-%m-%d'), inline=True)
    embed.set_thumbnail(url=member.avatar.url if member.avatar else "")
    await ctx.send(embed=embed)

@bot.command(help="Show information about the server.")
async def serverinfo(ctx):
    guild = ctx.guild
    embed = discord.Embed(title="���� Server Info", color=discord.Color.gold())
    embed.add_field(name="Name", value=guild.name)
    embed.add_field(name="Owner", value=guild.owner)
    embed.add_field(name="Members", value=guild.member_count)
    embed.add_field(name="Created", value=guild.created_at.strftime('%Y-%m-%d'))
    embed.set_thumbnail(url=guild.icon.url if guild.icon else "")
    await ctx.send(embed=embed)




# ================================
# Media Commands
# ================================

@bot.command(help="Start a timed vote. Example: !vote Do you like pizza?")
async def vote(ctx, *, question: str):
    embed = discord.Embed(
        title="������� Vote Started",
        description=question,
        color=discord.Color.blue()
    )
    embed.set_footer(text="Vote ends in 8 mins...")
    vote_msg = await ctx.send(embed=embed)

    await vote_msg.add_reaction("���")
    await vote_msg.add_reaction("���")

    await asyncio.sleep(480)  # wait 480 seconds

    vote_msg = await ctx.channel.fetch_message(vote_msg.id)  # refresh message to get updated reactions

    yes_votes = 0
    no_votes = 0

    for reaction in vote_msg.reactions:
        if reaction.emoji == "���":
            async for user in reaction.users():
                if not user.bot:
                    yes_votes += 1
        elif reaction.emoji == "���":
            async for user in reaction.users():
                if not user.bot:
                    no_votes += 1

    result_embed = discord.Embed(
        title="������� Vote Results",
        description=question,
        color=discord.Color.green()
    )
    result_embed.add_field(name="��� Yes", value=str(yes_votes), inline=True)
    result_embed.add_field(name="��� No", value=str(no_votes), inline=True)
    result_embed.set_footer(text=f"Vote started by {ctx.author.display_name}")

    await ctx.send(embed=result_embed)



@bot.command(help="Create a yes/no poll.")
async def poll(ctx, *, question):
    embed = discord.Embed(title="���� Poll", description=question, color=discord.Color.purple())
    message = await ctx.send(embed=embed)
    await message.add_reaction("����")
    await message.add_reaction("����")

@bot.command(help="Send a random tux GIF.")
async def tux(ctx):
    tux_gifs = [
        "https://tenor.com/v6VaAYimPea.gif",
        "https://tenor.com/innH4NpIbfY.gif",
        "https://tenor.com/bQfNc.gif",
        "https://tenor.com/cZRwLAu0pmc.gif"
    ]
    await ctx.send(random.choice(tux_gifs))

@bot.command(help="Send a random cat GIF.")
async def cat(ctx):
    cat_gifs = [
        "https://tenor.com/mzF1AfLuqUT.gif",
        "https://tenor.com/tnE6JF92xi3.gif",
        "https://tenor.com/p56hT64wfgG.gif",
        "https://tenor.com/cva1i1Mjp8m.gif"
    ]
    await ctx.send(random.choice(cat_gifs))

@bot.command(help="Send a random dog GIF.")
async def dog(ctx):
    dog_gifs = [
        "https://tenor.com/sHLmJqelnfS.gif",
        "https://tenor.com/bHcwj.gif"
    ]
    await ctx.send(random.choice(dog_gifs))

@bot.command(help="Send a random meme.")
async def meme(ctx):
    memes = [
        "https://i.redd.it/a0v87gwzoge61.jpg",
        "https://i.redd.it/3v0fkrj0cs541.jpg",
        "https://i.imgur.com/f9XH9Zz.jpeg"
    ]
    await ctx.send(random.choice(memes))

# ================================
# Utility Commands
# ================================
@bot.command(help="Check the bot's latency.")
async def ping(ctx):
    await ctx.send(f"���� Pong! {round(bot.latency * 1000)}ms")

@bot.command(help="Say hello to the bot.")
async def hello(ctx):
    await ctx.send(f"���� Hello, {ctx.author.mention}!")

@bot.command(help="List all command names.")
async def listcommands(ctx):
    cmds = [f"`!{cmd.name}`" for cmd in bot.commands]
    await ctx.send(f"���� Commands: {', '.join(cmds)}")

@bot.command(name="help", help="Show this help message.")
async def help_command(ctx):
    embed = discord.Embed(title="���� Linux-BOT Help", color=discord.Color.green())
    for cmd in bot.commands:
        embed.add_field(name=f"!{cmd.name}", value=cmd.help or "No description.", inline=False)
    await ctx.send(embed=embed)


# ================================
# Run the bot
# ================================
bot.run("your auth code")

