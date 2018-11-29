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
from utils import extras


class exploring:
    def __init__(self, bot):
        self.bot = bot
        self.task = self.bot.loop.create_task(self.waiter_e())
        self.task1 = self.bot.loop.create_task(self.waiter_a())

    async def __local_check(self, ctx):
        if await self.bot.pool.fetchrow("SELECT * FROM user_settings WHERE user_id = $1", ctx.author.id):
            return True

        raise (errorhandler.hasUwU(ctx))

    def __unload(self):
        self.task.cancel()
        self.task1.cancel()

    async def has_timer(self,user_id):
        user = await self.bot.pool.fetchrow("SELECT * FROM user_timers WHERE user_id = $1;",user_id)
        if user is not None:
            return True

    async def set_timer(self,user_id,time:int,type):

        time = timedelta(seconds=time) + datetime.utcnow()

        await self.bot.pool.execute('''
            INSERT INTO user_timers (user_id,end_time,timer_type)
            VALUES ($1,$2,$3) 
        ''',user_id,time,type)

    async def waiter_e(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            rows = await self.bot.pool.fetchrow('SELECT * FROM user_timers WHERE timer_type = 0 LIMIT 1;')
            if not rows:
                await asyncio.sleep(1)
            await extras.sleep_time(rows['end_time'])
            e = discord.Embed()
            #0 is explore
            user = await self.bot.get_user_info(rows['user_id'])
            if rows['timer_type'] is 0:
                deaths = randint(1,2)
                foes_killed = randint(10,120)
                xp = ((foes_killed * 10) - (deaths * 25)) / 2
                uwus_earned = (foes_killed * 10) - (deaths * 25)
                e.set_author(name=f"Your uwulonian is back from exploring")
                e.add_field(name='Explore Stats',value=f"Foes killed - {foes_killed}\nDeaths - {deaths}(-50 per death)\nXP Earned - {xp}\nuwus Earned - {uwus_earned}")
                e.set_footer(text='Good luck on your next exploration!')
            else:
                pass
            await self.bot.pool.execute('''
            UPDATE user_stats
            SET uwus = user_stats.uwus + $2, foes_killed = user_stats.foes_killed + $3, total_deaths = user_stats.total_deaths + $4, current_xp = user_stats.current_xp + $5
            ''',rows['user_id'],uwus_earned,foes_killed,deaths,xp)
            try:
                await user.send(embed=e)
            except discord.Forbidden:
                pass
            e = discord.Embed()
            guild = self.bot.get_guild(513888506498646052)
            channel = discord.utils.get(guild.text_channels, id=515577306283245569)
            e.set_author(name=f"""{user.name}'s uwulonian is back from an Exploration""")
            e.add_field(name='Stats',value=f"Foes killed - {foes_killed}\nDeaths - {deaths}(-50 per death)\nXP Earned - {xp}\nuwus Earned - {uwus_earned}")

            await channel.send(embed=e)
            await self.bot.pool.execute("DELETE FROM user_timers WHERE user_id = $1 AND timer_type = $2",rows['user_id'], rows['timer_type'])

    async def waiter_a(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            rows = await self.bot.pool.fetchrow('SELECT * FROM user_timers WHERE timer_type = 1 LIMIT 1;')
            if not rows:
                await asyncio.sleep(1)
            await extras.sleep_time(rows['end_time'])
            e = discord.Embed()
            #0 is explore
            user = await self.bot.get_user_info(rows['user_id'])
            if rows['timer_type'] is 1:
                deaths = randint(1,4)
                foes_killed = randint(45,320)
                uwus_earned = (foes_killed * 10) - (deaths * 50)
                xp = ((foes_killed * 10) - (deaths * 50)) / 2
                e.set_author(name=f"Your uwulonian is back from their adventure")
                e.add_field(name='Adventure Stats',value=f"Foes killed - {foes_killed}\nDeaths - {deaths}(-50 per death)\nXP Earned - {xp}\nuwus Earned - {uwus_earned}")
                e.set_footer(text='Good luck on your next adventure!')
            else:
                pass
            await self.bot.pool.execute('''
            UPDATE user_stats
            SET uwus = user_stats.uwus + $2, foes_killed = user_stats.foes_killed + $3, total_deaths = user_stats.total_deaths + $4, current_xp = user_stats.current_xp + $5
            ''',rows['user_id'],uwus_earned,foes_killed,deaths,xp)
            try:
                await user.send(embed=e)
            except discord.Forbidden:
                pass
            e = discord.Embed()
            guild = self.bot.get_guild(513888506498646052)
            channel = discord.utils.get(guild.text_channels, id=515577306283245569)
            e.set_author(name=f"""{user.name}'s uwulonian is back from an Adventure""")
            e.add_field(name='Stats',value=f"Foes killed - {foes_killed}\nDeaths - {deaths}(-50 per death)\nXP Earned - {xp}\nuwus Earned - {uwus_earned}")
            await channel.send(embed=e)
            await self.bot.pool.execute("DELETE FROM user_timers WHERE user_id = $1 AND timer_type = $2",rows['user_id'], rows['timer_type'])

    @commands.command(description='Set your uwulonian out on an adventure', aliases=['adv'])
    async def adventure(self,ctx):
        user = await self.bot.pool.fetchrow("SELECT * FROM user_settings WHERE user_id = $1",ctx.author.id)
        if await self.has_timer(user_id=ctx.author.id):
            return await ctx.send("You already have an adventure/exploration. Wait for your uwulonian to return for a new adventure.")

        await self.set_timer(user_id=ctx.author.id,time=3600,type=1)
        guild = self.bot.get_guild(513888506498646052)
        channel = discord.utils.get(guild.text_channels, id=514246616459509760)
        await channel.send(
f"""```ini
[Adventure Set]
User {ctx.author}({ctx.author.id})
Time {datetime.utcnow().strftime("%X on %x")}```
""")
        await ctx.send(f"Sending {user['user_name']} on an adventure! Your uwulonian will be back in an hour. Make sure your DMs are open so I can DM you once your uwulonian is back.")

    @commands.command(description='Make your uwulonian explore')
    async def explore(self,ctx):
        user = await self.bot.pool.fetchrow("SELECT * FROM user_settings WHERE user_id = $1",ctx.author.id)
        if await self.has_timer(user_id=ctx.author.id):
            return await ctx.send("Your uwulonian is already exploring/adventuring. Wait for your uwulonian to return for a new exploration.")

        await self.set_timer(user_id=ctx.author.id,time=1800,type=0)
        guild = self.bot.get_guild(513888506498646052)
        channel = discord.utils.get(guild.text_channels, id=514246616459509760)
        await channel.send(
f"""```ini
[Explore Set]
User {ctx.author}({ctx.author.id})
Time {datetime.utcnow().strftime("%X on %x")}```
""")
        await ctx.send(f"Sending {user['user_name']} to explore! Your uwulonian will be back in thirty minutes. Make sure your DMs are open so I can DM you once your uwulonian is back.")

def setup(bot):
    bot.add_cog(exploring(bot))