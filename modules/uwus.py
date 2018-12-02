import discord
from discord.ext import commands
from discord.ext.commands import cooldown
from discord.ext.commands.cooldowns import BucketType
import time
import asyncio
import asyncpg
from datetime import datetime
from utils import errorhandler
import secrets
from random import choice

heads = '<:uwuheads:517079577072238624>'
tails = '<:uwutails:517081802246979616>'

class uwus:
    def __init__(self, bot):
        self.bot = bot

    async def __local_check(self, ctx):
        if await self.bot.pool.fetchrow("SELECT * FROM user_settings WHERE user_id = $1", ctx.author.id):
           return True

        raise(errorhandler.hasUwU(ctx))

    @commands.command(aliases=['coinflip'])
    async def coin(self, ctx, choice, amount:int):
        async with self.bot.pool.acquire() as conn:
            user_amount = await conn.fetchrow("SELECT * FROM user_stats WHERE user_id = $1", ctx.author.id)
            choice = choice.lower()
            if amount < 50 or amount >= 50000:
                return await ctx.send("You may not bet less then 50 uwus or more than 50000 on a coinflip")
            if choice != "heads" and choice != "tails":
                return await ctx.send("Please only use heads or tails")
            if amount > user_amount['uwus']:
                return await ctx.send("You don't have the funds to bet that much")

            status = await ctx.send("Flipping the coin...")
            await asyncio.sleep(3)
            await status.delete()
            side = secrets.choice(["heads", "tails"])
            if side == "heads":
                emote = heads
            else:
                emote = tails

            if choice == side:
                await conn.execute("UPDATE user_stats SET uwus = user_stats.uwus + $1 WHERE user_id = $2", amount, ctx.author.id)
                return await ctx.send(f"{emote} You won {amount} uwus!")
            else:
                await conn.execute("UPDATE user_stats SET uwus = user_stats.uwus - $1 WHERE user_id = $2", amount, ctx.author.id)
                return await ctx.send(f"{emote} You lost.")

    @commands.command(description="Start a guessing game.")
    async def guess(self, ctx):
        async with self.bot.pool.acquire() as conn:
            if await conn.fetchrow("SELECT * FROM guessing WHERE guild_id = $1 AND channel_id = $2", ctx.guild.id, ctx.channel.id):
                return await ctx.send("There is already a guessing game in this channel.")

            await conn.execute("INSERT INTO guessing (guild_id, channel_id, host_id) VALUES ($1, $2, $3)", ctx.guild.id, ctx.channel.id, ctx.author.id)
            e = discord.Embed(description=
"""
Welcome to uwu's guessing game! To win guess the users name based off their avatar and discriminator(#0000)            
You have 60 seconds to guess! Good luck!
""")
            e.set_author(name="Guessing game")

            members = [member for member in ctx.guild.members if member.id is not ctx.author.id and not member.bot]
            if len(members) < 15:
                return await ctx.send("You can only play guessing game if you are in a server with more then 15 members. Join uwus support server if you want to play but don't have 15 members.")
            randmem = choice(members)

            e.add_field(name="Info", value=f"The users discriminator is {randmem.discriminator}")
            e.set_image(url=randmem.avatar_url_as(static_format="png"))
            embed = await ctx.send(embed=e)

            def check(amsg):
                return amsg.content == randmem.name
            try:
                name = await self.bot.wait_for('message', timeout=60, check=check)
            except asyncio.TimeoutError:
                await embed.delete()
                await conn.execute("DELETE FROM guessing WHERE guild_id = $1 AND channel_id = $2", ctx.guild.id, ctx.channel.id)
                return await ctx.send(f"Times up! The user was {randmem.name}.".replace('@','@\u200b'))

            await conn.execute("DELETE FROM guessing WHERE guild_id = $1 AND channel_id = $2", ctx.guild.id, ctx.channel.id)
            await conn.execute("UPDATE user_stats SET uwus = user_stats.uwus + 1000 WHERE user_id = $1", name.author.id)
            await embed.delete()
            await ctx.send(f"{name.author} guessed correctly and got 1000 uwus! It was {randmem.name}")

def setup(bot):
    bot.add_cog(uwus(bot))