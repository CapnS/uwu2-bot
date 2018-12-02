import discord
from discord.ext import commands
from discord.ext.commands import cooldown
from discord.ext.commands.cooldowns import BucketType
import time
import asyncio
import asyncpg
from datetime import datetime, timedelta
from random import randint
from random import choice
import psutil
import os
import sys

colors = [0xe56b6b,0xdd5151,0xba3434,0xab1f1f,0x940808]
online = '<:online_status:506963324391653387>'
offline = '<:offline_status:506963324521414661>'
dnd = '<:dnd_status:506963324634791936>'
idle = '<:idle_status:506963324529803264>'

class misc:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(description='Give someone a slap', brief='Slap', usage='slap [user]')
    async def slap(self, ctx, *, user: discord.Member):
        embed = discord.Embed(colour=choice(colors))
        embed.set_author(name=f"{ctx.author.name} slapped {user.name}! Ouch!")
        embed.set_image(url="https://media.giphy.com/media/RXGNsyRb1hDJm/giphy.gif")
        await ctx.send(embed=embed)

    @commands.command(description='Give someone a hug! Awwww', brief='Hug', usage='hug [user]')
    async def hug(self, ctx, *, user: discord.Member):
        embed = discord.Embed(colour=choice(colors))
        embed.set_author(name=f"{ctx.author.name} gave {user.name} hug! How cute!")
        embed.set_image(url="https://media.giphy.com/media/lXiRKBj0SAA0EWvbG/giphy.gif")
        await ctx.send(embed=embed)

    @commands.command(aliases=['pong'],description='Check the bots latency to Discord Websockets',brief='Check the bots ping',usage='ping')
    async def ping(self, ctx):
        t_1 = time.perf_counter()
        await ctx.trigger_typing()
        t_2 = time.perf_counter()
        time_delta = round((t_2-t_1)*1000)
        await ctx.send(f':ping_pong: Websocket: {round(self.bot.latency*1000)} ms. Typing: {time_delta} ms')

    @commands.command(aliases=["avy"],description='Get a users or your avatar',usage='avatar [user]',brief='Get a users or your avatar')
    async def avatar(self, ctx,*,user:discord.Member=None):
        user = user or ctx.author
        embed = discord.Embed(colour=0x7289da,description=f"[Link]({user.avatar_url})")
        embed.set_author(name=f"{user.name}'s avatar",url=user.avatar_url)
        embed.set_image(url=user.avatar_url_as(static_format="png"))
        await ctx.send(embed=embed)

    @commands.command(aliases=['about'],description='Get stats about the bot',brief='Check bot stats',usage='info')
    async def info(self, ctx):
        cmds_used = await self.bot.pool.fetchval('''SELECT * FROM commands_used;''')
        uwulonian = await self.bot.pool.fetchval("SELECT count(user_id) FROM user_settings;")
        delta_uptime = datetime.utcnow() - self.bot.launch_time
        hours, remainder = divmod(int(delta_uptime.total_seconds()),3600)
        minutes, seconds = divmod(remainder,60)
        days, hours = divmod(hours,24)
        member_count = 0
        offline_members = set()
        idle_members = set()
        dnd_members = set()
        online_members = set()
        cpu_usage = self.bot.process.cpu_percent()
        cpu_count = psutil.cpu_count()
        memory_usage = self.bot.process.memory_full_info().uss / (1024 ** 2)
        version = sys.version_info
        for g in self.bot.guilds:
            member_count += g.member_count
            for m in g.members:
                if m.status is discord.Status.offline:
                    offline_members.add(m.id)
                if m.status is discord.Status.idle:
                    idle_members.add(m.id)
                if m.status is discord.Status.dnd:
                    dnd_members.add(m.id)
                if m.status is discord.Status.online:
                    online_members.add(m.id)
        offline_count = len(offline_members)
        idle_count = len(idle_members)
        dnd_count = len(dnd_members)
        online_count = len(online_members)
        user_count = len(self.bot.users)
        embed = discord.Embed(color=0x7289da)
        embed.set_author(name='Bot Stats')
        embed.add_field(name='Owner',value=f'<@300088143422685185> (mellowmarshe#0001)')
        embed.add_field(name='Library',value=f'[discord.py\\[rewrite\\]](https://github.com/Rapptz/discord.py/tree/rewrite)')
        embed.add_field(name='Language',value=f'Python {version.major}.{version.minor}.{version.micro}')
        embed.add_field(name='Uptime',value=f'{days}d {hours}h {minutes}m')
        embed.add_field(name='Servers', value=len(self.bot.guilds))
        embed.add_field(name='Process',value=f'Memory {round(memory_usage, 2)}MiB\nCPU {cpu_usage/cpu_count}%')
        embed.add_field(name='Bot Usage',value=f'{cmds_used} commands used\n{uwulonian} uwulonians')
        embed.add_field(name='Members',value=f'{online}{online_count} {idle}{idle_count} {dnd}{dnd_count} {offline}{offline_count}')
        embed.add_field(name='Links',value='[Invite](https://discordapp.com/oauth2/authorize?client_id=508725128427995136&scope=bot&permissions=201718983) | [Support](https://discord.gg/494uEhN) | [Donate](https://www.patreon.com/mellOwO?alert=2) | [Vote](https://discordbots.org/bot/508725128427995136/vote)')
        await ctx.send(embed=embed)

    @commands.command(description="Get the link to the support server")
    async def support(self,ctx):
        await ctx.send("The link to the support server is https://discord.gg/494uEhN")

    @commands.command(description="Check our lovely Patrons!")
    async def patrons(self,ctx):
        e = discord.Embed(color=0x7289da, description="Patreon https://www.patreon.com/mellOwO?alert=2")
        e.set_author(name="Our awesome Patrons")
        e.add_field(name="Capn", value=
"""
Supporter since 11/19/18 at 20:42:35 UTC
- [His bot](https://discordapp.com/oauth2/authorize?&client_id=448915931507458048&scope=bot&permissions=8)
""", inline=False)
        e.add_field(name="Arika", value=
"""
Supporter since 11/28/18 at 02:06:13 UTC
""", inline=False)
        e.add_field(name="Mary Johanna", value=
"""
Awesome since 11/29/18 at 17:21:28 UTC
""", inline=False)
        e.add_field(name="XiuhcoatlSlayer", value=
"""
Supporter since 11/30/18 at 02:14:11 UTC
""", inline=False)
        await ctx.send(embed=e)

    @commands.command(description="Send voting link")
    async def vote(self,ctx):
        await ctx.send("You can vote for me here! https://discordbots.org/bot/508725128427995136/vote I greatly appreciate voting as it helps the bot a lot")

    @commands.command(description="Bot rules", aliases=['tos'])
    async def rules(self, ctx):
        await ctx.send(       
"""
uwu rules. You must follow these or we will take action
`-` Don't spam or abuse commands with the intent to harm or slow the bot down. We want the best experience for our users anything to harm this is a problem.
`-` Don't rename or create an uwulonian with a harmful, racist, or any name that can offend someone. We will most likely delete your uwulonian if you do this.
`-` The use of scripts or anything to gain an advantage is forbidden.
`-` DM staff if you are having problems with the bot don't DM regular members unless they say you can.
""")

def setup(bot):
    bot.add_cog(misc(bot))