import discord
from discord.ext import commands, tasks
from discord.ext.commands import Bot
from discord.voice_client import VoiceClient
import random
import asyncio
import json
import os

from itertools import cycle
import youtube_dl


class kraltr(commands.Cog):

    def __init__(self, client):
        self.client = client

        self.client.loop.create_task(self.save_users())

        with open(r'C:\Users\xKral_Tr\Desktop\DiscordBot\users.json', 'r') as f:
            self.users = json.load(f)


    @commands.Cog.listener()
    async def save_users(self):
        await self.client.wait_until_ready()
        while not self.client.is_closed():
            with open(r'C:\Users\xKral_Tr\Desktop\DiscordBot\users.json', 'w') as f:
                json.dump(self.users, f, indent=4)

            await asyncio.sleep(5)

    def lvl_up(self, author_id):
        cur_xp = self.users[author_id]['exp']
        cur_lvl = self.users[author_id]['level']

        if cur_xp >= round((4 * (cur_lvl ** 3)) / 5):
            self.users[author_id]['level'] += 1
            return True
        else:
            return False

    @commands.Cog.listener()
    async def on_message(self, message):

        kotu_kelimeler = ['amk', 'sikeyim', 'aq', 'yıldo']

        if message.author == self.client.user:
            return

        messageTemp = message.content.split(" ")

        for i in range(len(messageTemp)):
            print(messageTemp[i].lower())
            if messageTemp[i].lower() in kotu_kelimeler:
                await message.delete()
                await message.channel.send("Küfür etme lan")

        else:
            author_id = str(message.author.id)
            if not author_id in self.users:
                self.users[author_id] = {}
                self.users[author_id]['level'] = 1
                self.users[author_id]['exp'] = 0

            self.users[author_id]['exp'] += 1

            if self.lvl_up(author_id):
                await message.channel.send(f"{message.author.mention} level {self.users[author_id]['level']} oldu")

    @commands.command()
    async def level(self, ctx, member: discord.Member = None):
        member = ctx.author if not member else member
        member_id = str(member.id)
        if not member_id in self.users:
            await ctx.send("Seviyen yok!")

        else:
            embed = discord.Embed(color=member.color, timestamp=ctx.message.created_at)

            embed.set_author(name=f"Level - {member}", icon_url=self.client.user.avatar_url)

            embed.add_field(name="Level", value=self.users[member_id]['level'])
            embed.add_field(name="XP", value=self.users[member_id]['exp'])

            await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild = member.guild
        if guild.system_channel is not None:
            to_send = 'Hoşgeldin {0.mention} kral!'.format(member, guild)
            await guild.system_channel.send(to_send)

    @commands.Cog.listener()
    async def on_ready(self, ):
        # await self.client.change_presence(status=discord.Status.idle, activity=discord.Game('Herkese Çay!'))
        # self.change_status.start()
        print("Bot is ready.")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):  # Genel error
        # if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Kardesim düzgün komut gir. Komutlar için ".help" yazabilirsin')

    @commands.command(aliases=['clear'])
    @commands.has_permissions(manage_messages=True)
    async def temizle(self, ctx, amount=2):
        await ctx.channel.purge(limit=amount)

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        await member.kick(reason=reason)

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        await member.ban(reason=reason)

    @commands.command()
    async def github(self, ctx):
        await ctx.send(f'GitHub: https://github.com/talhaucarr')

    # def is_it_me(self,ctx):
    # return ctx.author.id == 'Author id'

    @commands.command()
    # @commands.check(is_it_me)
    async def admin(self, ctx):
        await ctx.send(f'Admin: {ctx.author.name}')

    @commands.command()
    async def join(self, ctx, *, channel: discord.VoiceChannel):
        """Joins a voice channel"""

        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)

        await channel.connect()


def setup(client):
    client.add_cog(kraltr(client))
