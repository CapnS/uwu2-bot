import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
import traceback
import asyncio
import asyncpg
import yaml  # removed aiofiles because its not needed
from datetime import datetime
import os
import sys
import logging
import aiohttp
import psutil

try:
    import uvloop
except ImportError:
    if sys.platform == "linux":  # alert the user to install uvloop if they are on a linux system
        print("UVLoop not detected")
else:
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

description = """uwu. A RPG bot made by mellowmarshe#0001"""

startup_extensions = ['jishaku',
                      'utils.errorhandler',
                      'modules.create',
                      'modules.exploring',
                      'modules.database',
                      'modules.owner',
                      'modules.uwulonian',
                      'modules.misc',
                      'modules.patron',
                      'modules.DBL',
                      'modules.marriage',
                      'modules.beta',
                      'modules.uwus']

class uwu(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned_or('uwu '), case_insensitive=True, description=description, reconnect=True)
        self.launch_time = datetime.utcnow()
        self.config = yaml.load(open("config.yml"))
        self.pool = None  # pool is unset till the bot is ready
        self.session = aiohttp.ClientSession(loop=self.loop)
        self.bot_version = '0.0.3 cat'
        self.process = psutil.Process(os.getpid())

    async def start(self):
        await self.create_pool()
        for ext in startup_extensions:
            try:
                self.load_extension(ext)
            except BaseException as e:
                print(f"Failed to load {ext}\n{type(e).__name__}: {e}")
        super().start(self.config['token'])

    async def create_pool(self):
        credentials = {"user": self.config['dbuser'], "password": self.config['dbpassword'],"database": self.config['dbname'], "host": "127.0.0.1"}
        self.pool = await asyncpg.create_pool(**credentials, max_size=100)

    async def on_ready(self):
        await self.create_pool()
        with open("utils/schema.sql") as f:
            await self.pool.execute(f.read())
        print("Bot ready!")
        game = discord.Game("with fwends")
        await self.change_presence(status=discord.Status.dnd, activity=game)

    async def on_command_completion(self, ctx):
        await self.pool.execute("UPDATE commands_used SET commands_used = commands_used + 1;")

    async def on_command_error(self, ctx, exc):
        if hasattr(ctx.command, "on_error"):
            return
        if hasattr(ctx.cog, f"_{ctx.cog}__local_check"):
            return  # ignore cog error handlers

        exc = getattr(exc, "original", exc)  # CommandInvokeError

        if isinstance(exc, commands.CommandOnCooldown):  # cooldown
            seconds = exc.retry_after
            seconds = round(seconds, 2)
            hours, remainder = divmod(int(seconds), 3600)
            minutes, seconds = divmod(remainder, 60)
            return await ctx.send(f'You are on cooldown for {hours} hrs {minutes} min {seconds} sec')

        print(f"Ignoring error in command '{ctx.command}'.")  # print otherwise
        traceback.print_exception(type(exc), exc, exc.__traceback__)

    @commands.is_owner()
    @commands.command(hidden=True, aliases=['kys', 'exit'])
    async def die(self, ctx):
        await ctx.send("Bye cruel world...")
        await self.logout()

if __name__ == "__main__":
    uwu().run()