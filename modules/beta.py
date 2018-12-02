import discord
from discord.ext import commands
from discord.ext.commands import cooldown
from discord.ext.commands.cooldowns import BucketType
from utils import errorhandler
import asyncpg
import asyncio
from random import choice

beta_servers = [513888506498646052, 336642139381301249]

class beta:
    def __init__(self, bot):
        self.bot = bot

    async def __local_check(self, ctx):
        if ctx.guild.id in beta_servers:
           return True

        raise(errorhandler.isBeta(ctx))

    @commands.command()
    async def trivia(self, ctx):
        async with self.bot.pool.acquire() as conn:
            if await conn.fetchrow("SELECT * FROM trivia_channels WHERE guild_id = $1 AND channel_id = $2", ctx.guild.id, ctx.channel.id):
                return await ctx.send("There is already a trivia game in this channel.")
            if await conn.fetchrow("SELECT * FROM user_settings WHERE user_id = $1", ctx.author.id) is None:
                return await ctx.send("You need an uwulonian for this command.")

            await conn.execute("INSERT INTO trivia_channels (guild_id, channel_id, host_id) VALUES ($1, $2, $3)", ctx.guild.id, ctx.channel.id, ctx.author.id)
            start = await ctx.send("Starting trivia game...")
            await asyncio.sleep(3)
            await start.delete()
            ids_used = []
            counter = 1
            ques = await conn.fetchrow("SELECT * FROM trivia_questions ORDER BY RANDOM() LIMIT 1;")
            ids_used.append(ques['question_id'])
            e = discord.Embed()
            e.set_author(name='Trivia')

def setup(bot):
    bot.add_cog(beta(bot))