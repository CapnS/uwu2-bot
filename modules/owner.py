from discord.ext import commands
import discord
from utils import errorhandler
import asyncpg
from datetime import datetime


staff_ids = [246938839720001536, 300088143422685185, 422181415598161921]

class owner:
    def __init__(self, bot):
        self.bot = bot

    async def __local_check(self, ctx):
        if ctx.author.id in staff_ids:
           return True

        raise(errorhandler.IsStaff(ctx))

    @commands.group(invoke_without_command=True, description="Does nothing without a subcommand")
    async def uwus(self, ctx):
        await ctx.send("owo")

    @uwus.command(hidden=True)
    async def plonk(self,ctx,user_id:int):
        await self.bot.pool.execute("DELETE FROM user_settings WHERE user_id = $1",user_id)
        guild = self.bot.get_guild(513888506498646052)
        channel = discord.utils.get(guild.text_channels, id=514246616459509760)
        await channel.send(
f"""```ini
[User Delete Log]
Mod {ctx.author}({ctx.author.id})
Affected {user_id}
Time {datetime.utcnow().strftime("%X on %x")}```
""")
        await ctx.send('Done')

    @commands.group(invoke_without_command=True, description="Does nothing without a subcommand")
    async def patreon(self, ctx):
        await ctx.send("owo")

    @patreon.command(hidden=True)
    async def set(self,ctx,user_id:int):
        try:
            await self.bot.pool.execute("INSERT INTO p_users (user_id) VALUES ($1)",user_id)
            guild = self.bot.get_guild(513888506498646052)
            channel = discord.utils.get(guild.text_channels, id=514246616459509760)
            await channel.send(
f"""```ini
[Patreon Add Log]
Mod {ctx.author}({ctx.author.id})
Affected {user_id}
Time {datetime.utcnow().strftime("%X on %x")}```
""")
            await ctx.send("Done")
        except asyncpg.UniqueViolationError:
            return await ctx.send(f"{user_id} is already a Patron")

    @patreon.command(hidden=True)
    async def remove(self,ctx,user_id:int):
        await self.bot.pool.execute("DELETE FROM p_users WHERE user_id = $1",user_id)
        guild = self.bot.get_guild(513888506498646052)
        channel = discord.utils.get(guild.text_channels, id=514246616459509760)
        await channel.send(
f"""```ini
[Patreon Remove Log]
Mod {ctx.author}({ctx.author.id})
Affected {user_id}
Time {datetime.utcnow().strftime("%X on %x")}```
""")
        await ctx.send("Done")

    @commands.group(invoke_without_command=True, description="Does nothing without a subcommand")
    async def timer(self, ctx):
        await ctx.send("owo")

    @timer.command(hidden=True)
    async def delete(self,ctx,user_id:int):
        await self.bot.pool.execute("DELETE FROM user_timers WHERE user_id = $1",user_id)
        guild = self.bot.get_guild(513888506498646052)
        channel = discord.utils.get(guild.text_channels, id=514246616459509760)
        await channel.send(
f"""```ini
[Timer Delete Log]
Mod {ctx.author}({ctx.author.id})
Affected {user_id}
Time {datetime.utcnow().strftime("%X on %x")}```
""")
        await ctx.send("Done")

def setup(bot):
    bot.add_cog(owner(bot))