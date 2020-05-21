import discord
from discord.ext import commands, tasks
from discord.ext.commands import Bot
from discord.voice_client import VoiceClient
import random
import asyncio
import json
import os
import requests
from bs4 import BeautifulSoup
from riotwatcher import LolWatcher, ApiError
from prettytable import PrettyTable
import pandas as pd


class kraltr(commands.Cog):

    def __init__(self, client):
        self.client = client

        # golbal variables
        self.api_key = 'RGAPI-c7ee15b3-8dee-496b-a01c-77124f2175ee'
        self.watcher = LolWatcher(self.api_key)
        self.my_region = 'tr1'

        self.client.loop.create_task(self.save_users())

        with open(r'C:\Users\xKral_Tr\Desktop\DiscordBot\users.json', 'r') as f:
            self.users = json.load(f)

    @commands.command()
    async def game(self, ctx):

        msgTemp2 = ctx.message.content.split(".game ")

        print(msgTemp2)

        me = self.watcher.summoner.by_name(self.my_region, msgTemp2[1])
        print(msgTemp2[1])
        # Return the rank status for the username that has been entered

        current_game = self.watcher.spectator.by_summoner(self.my_region, me['id'])

        for i in current_game["participants"]:

            my_ranked_stats = self.watcher.league.by_summoner(self.my_region, i['summonerId'])
            embed = discord.Embed(color=0x14efef, timestamp=ctx.message.created_at)
            embed.set_author(name=f"deneme", icon_url=self.client.user.avatar_url)
            for a in my_ranked_stats:

                embed.add_field(name="Lig", value=a["tier"])

            await ctx.send(embed=embed)

    @commands.command()
    async def gameinfo(self, ctx):

        msgTemp2 = ctx.message.content.split(".game ")

        print(msgTemp2)

        me = self.watcher.summoner.by_name(self.my_region, msgTemp2[1])
        print(msgTemp2[1])
        # Return the rank status for the username that has been entered

        current_game = self.watcher.spectator.by_summoner(self.my_region, me['id'])

        participants = []
        print(current_game['gameMode'])
        print(current_game['gameType'])
        table = PrettyTable(['team', 'summonerName', 'champion', 'spell1Id', 'spell2Id'])
        for i in current_game["participants"]:
            table.add_row([i['teamId'], i['summonerName'], i['championId'], i['spell1Id'], i['spell2Id']])
            """participants_row = {}
            participants_row['team'] = i['teamId']
            participants_row['summonerName'] = i['summonerName']
            participants_row['champion'] = i['championId']
            participants_row['spell1Id'] = i['spell1Id']
            participants_row['spell2Id'] = i['spell2Id']
            participants.append(participants_row)"""
        # df = pd.DataFrame(participants)

        await ctx.send(table)

    @commands.command()
    async def rank(self, ctx):

        msgTemp = ctx.message.content.split(".rank ")

        me = self.watcher.summoner.by_name(self.my_region, msgTemp[1])

        # Return the rank status for the username that has been entered

        my_ranked_stats = self.watcher.league.by_summoner(self.my_region, me['id'])

        for i in my_ranked_stats:
            win_rate = (i["wins"] / (i["wins"] + i["losses"])) * 100

            queueTypeTemp = i['queueType'].split("_")
            rankTemp = i["tier"] + " " + i["rank"]

            embed = discord.Embed(color=0x14efef, timestamp=ctx.message.created_at)
            embed.set_author(name=f"{msgTemp[1]} - {queueTypeTemp[1]}", icon_url=self.client.user.avatar_url)

            embed.add_field(name="Rank", value=rankTemp)

            embed.add_field(name="Win", value=i["wins"])
            embed.add_field(name="Lose", value=i["losses"])
            embed.add_field(name="LP", value=i["leaguePoints"], inline=False)
            embed.add_field(name="Win Rate(%)", value=int(win_rate))
            await ctx.send(embed=embed)

    @commands.command()
    async def warmup(self, ctx):
        url = "http://www.warmupserver.net/servers.php"  # Site linkimiz

        response = requests.get(url)  # Web sayfamızı çekiyoruz.

        html_icerigi = response.content  # Web sayfamızın içeriğini alıyoruz.

        soup = BeautifulSoup(html_icerigi,
                             "html.parser")  # Web sayfamızı parçalamak için BeautifulSoup objesine atıyoruz.

        # Bu kullanımın anlamı div etiketlerinden class'ı article al anlamına geliyor.
        for i in soup.find_all("article"):
            for a in i.find_all("a"):
                temp = a.get("href")
                temp = temp.split("/")

                await ctx.send(f'Warmup CS Sw: {temp[4]}')

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
            to_send = 'Hoşgeldin {0.mention}. Eğer nickiniz olarak kendi ad ve soyadınızı kullanmıyorsanız lütfen değiştiriniz. Aksi takdirde kanaldan atılacaksınız.'.format(member, guild)
            await guild.system_channel.send(to_send)

    @commands.Cog.listener()
    async def on_ready(self, ):
        print("Bot is ready.")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):  # Genel error
        # if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Komutlar için ".help" yazabilirsin')

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
        await ctx.send(f'GitHub: https://github.com/talhaucarr/xKral_Tr-DiscordBot')

    @commands.command()
    async def iletisim(self, ctx):
        embed = discord.Embed(title="İletisim",color=0x14efef)
        embed.add_field(name="Ali Buldu", value="alibuldu@marmara.edu.tr", inline=False)
        embed.add_field(name="BUKET DOĞAN ", value="buketb@marmara.edu.tr", inline=False)
        embed.add_field(name="ÖNDER DEMİR", value="odemir@marmara.edu.tr", inline=False)
        embed.add_field(name="KAZIM YILDIZ", value="kazim.yildiz@marmara.edu.tr", inline=False)
        embed.add_field(name="ÖMER AKGÜN", value="oakgun@marmara.edu.tr", inline=False)
        embed.add_field(name="EYÜP EMRE ÜLKÜ", value=" emre.ulku@marmara.edu.tr", inline=False)
        embed.add_field(name="ABDULSAMET AKTAŞ", value="abdulsamet.aktas@marmara.edu.tr", inline=False)
        embed.add_field(name="ANIL BAŞ", value="anil.bas@marmara.edu.tr", inline=False)
        embed.add_field(name="ABDULLAH BAL", value="abdullah.bal@marmara.edu.tr", inline=False)
        await ctx.send(embed=embed)

    @commands.command()
    async def mufredat(self, ctx):
        await ctx.send(f'GitHub: http://dosya.marmara.edu.tr/tf/blm/Bilgisayar_M_hendisli_i_M_fredat_Program_.pdf')

def setup(client):
    client.add_cog(kraltr(client))
