import discord
from discord.ext import commands
from discord.ext.commands import cooldown
from discord.ext.commands.cooldowns import BucketType
import time
import asyncio
import asyncpg
from datetime import datetime, timedelta
from random import randint

sorts = ['total_deaths','foes_killed','uwus','current_xp']

class uwulonian:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(description='Get an uwulonians or your stats', aliases=['bal', 'wallet'])
    async def stats(self,ctx,user: discord.Member=None):
        async with self.bot.pool.acquire() as conn:
            user = user or ctx.author
            uwulonian_name = await conn.fetchrow("SELECT * FROM user_settings WHERE user_id = $1",user.id)
            uwulonian = await conn.fetchrow("SELECT * FROM user_stats WHERE user_id = $1",user.id)
            if uwulonian is None:
                return await ctx.send("You or the user doesn't have an uwulonian created.")
            roles = "Yes"
            is_patron = await conn.fetchrow("SELECT * FROM p_users WHERE user_id = $1", user.id)
            if is_patron is None:
                roles = "No"

            e = discord.Embed(colour=0x7289da)

            e.add_field(name=f"Stats for {uwulonian_name['user_name']}", value=f"""Foes killed - {uwulonian['foes_killed']}\nDeaths - {uwulonian['total_deaths']}\nuwus - {uwulonian['uwus']}""")
            e.add_field(name="Levels", value=f"XP - {uwulonian['current_xp']}\n Level - {uwulonian['current_level']}")
            e.add_field(name='Time created', value=f"""{uwulonian_name['time_created'].strftime("%x at %X")}""")
            e.add_field(name='Is Patron?', value=roles)
            await ctx.send(embed=e)

    @commands.command(aliases=['lb','wowcheaterhenumber1onlb'])
    async def leaderboard(self,ctx,sort=None):
        if sort is None:
            sort = 'uwus'
        if sort not in sorts:
            return await ctx.send(f"Invalid type. Valid - total_deaths, foes_killed, uwus, and current_xp")

        lb = await self.bot.pool.fetch(f"SELECT * FROM user_stats INNER JOIN user_settings ON  user_stats.user_id = user_settings.user_id ORDER BY {sort} DESC LIMIT 5;")
        e = discord.Embed(colour=0x7289da)
        num = 0
        e.set_author(name=f"Leaderboard - {sort}")
        for i in lb:
            e.add_field(name=f"{lb[num]['user_name']}", value=f"{sort} - {lb[num][sort]}",inline=False)
            num += 1
        await ctx.send(embed=e)

def setup(bot):
    bot.add_cog(uwulonian(bot))