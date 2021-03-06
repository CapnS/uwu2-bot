import discord
from discord.ext import commands
from discord.ext.commands import cooldown
from discord.ext.commands.cooldowns import BucketType
import time
import asyncio
import asyncpg
from datetime import datetime, timedelta
from random import randint
from utils import errorhandler

class patron:
    def __init__(self, bot):
        self.bot = bot

    async def __local_check(self, ctx):
        if await self.bot.pool.fetchrow("SELECT * FROM p_users WHERE user_id = $1", ctx.author.id):
            return True

        raise(errorhandler.NotPatron(ctx))

    async def p_has_timer(self,user_id):
        user = await self.bot.pool.fetchrow("SELECT * FROM p_user_timer WHERE user_id = $1;",user_id)
        if user is not None:
            return user['next_time'] >= datetime.utcnow()

    async def p_set_timer(self,user_id):
        time = timedelta(hours=1440) + datetime.utcnow()

        await self.bot.pool.execute('''
            INSERT INTO p_user_timer (user_id,next_time)
            VALUES ($1,$2)
            ON CONFLICT (user_id) DO UPDATE
            SET next_time = $2; 
        ''',user_id,time)

    @commands.group(invoke_without_command=True, description="Does nothing without a subcommand")
    async def patron(self, ctx):
        await ctx.send("owo")

    @patron.command(description="Check how long you have been a Patron")
    async def timecheck(self,ctx):
        patron = await self.bot.pool.fetchrow("SELECT * FROM p_users WHERE user_id = $1", ctx.author.id)
        await ctx.send(f"""You have been a Patron since {patron['patron_time'].strftime("%x at %X")}. Thanks for supporting me!""")

    @patron.command(description="Patron only. Claim your biweekly uwus")
    async def biweekly(self,ctx):
        user = await self.bot.pool.fetchrow("SELECT * FROM user_settings WHERE user_id = $1",ctx.author.id)
        if user is None:
            return await ctx.send("You don't have an uwulonian created.")
        if await self.p_has_timer(user_id=ctx.author.id):
            return await ctx.send("You already claimed your biweekly uwus.")

        await self.p_set_timer(ctx.author.id)
        await self.bot.pool.execute("UPDATE user_stats SET uwus = user_stats.uwus + 5000 WHERE user_id = $1",ctx.author.id)
        await ctx.send(f"Your uwulonian now has an extra 5000 uwus for being a Patron! Thanks for supporting me!")

def setup(bot):
    bot.add_cog(patron(bot))