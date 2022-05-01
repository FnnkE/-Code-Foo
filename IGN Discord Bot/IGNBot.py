#Code By Ethan Funk
#Adapted from https://github.com/FnnkE/MasonMenu

from optparse import Values
from pydoc import describe
from unittest import case
import discord
from discord import Member
from discord import message
from discord import channel
import requests
from discord.ext import commands, tasks
from discord.ext.commands import has_permissions
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from pytz import timezone
import sqlite3
import asyncio

#Data URLs
NewsURL = "https://www.ign.com/news"
videosURL = "https://www.ign.com/videos"
reviewsURL = "https://www.ign.com/reviews"

#Discord Inits
#WARNING: Requires TOKEN.txt to be created in the folder
#For mod settings: add lines below token to store user IDs
data = open('Tokens.txt', 'r')
TOKEN = data.readline()
#Below is for the implementation of mod commands
#user1 = data.readline()
#user2 = data.readline()
data.close()
bot = commands.Bot(command_prefix="!", help_command=None, case_insensitive=True)

#global footer 
footer = ""

newestTitle = ["News", "Reviews", "Videos"]

#Run on Bot Start
@bot.event
async def on_ready():
    db = sqlite3.connect('main.sqlite')
    cursor = db.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS main(
        guild_id TEXT,
        channel_id TEXT,
        name TEXT
        )
    ''')
    db.commit
    db.close
    await timeCalc()
    db = sqlite3.connect('main.sqlite')
    cursor = db.cursor()
    cursor.execute("SELECT channel_id FROM main WHERE guild_id = 0 AND name = 'system'")
    result = cursor.fetchone()
    if result is None:
        sql = ("INSERT INTO main(guild_id, channel_id, name) VALUES(?,?,?)")
        val = (0, time, 'system')
    elif result is not None:
        sql = ("UPDATE main SET channel_id = ? WHERE guild_id = ? AND name = ?")
        val = (time, 0, 'system')
    cursor.execute(sql,val)
    print(f'Time has been recorded')
    db.commit()
    cursor.close()
    db.close()
    await updateData()
    print('Bot Online')

async def changePresence():
    await bot.wait_until_ready()
    index = 0
    while not bot.is_closed():
        guilds = bot.guilds
        members = 0
        if (index == 0):
            for guild in guilds:
                members += guild.member_count
        statuses = [f"with {members} users | $help", f"on {len(bot.guilds)} servers | $help", "discord.py", 'with IGN', 'around in IGN HQ']
        status = statuses[index]

        await bot.change_presence(activity=discord.Game(name=status))
        index += 1
        if (index == len(statuses)): index = 0
        await asyncio.sleep(10)

async def timeCalc():
    global time
    #Calculate time
    print("Calculating time...")
    tz = timezone('US/Eastern')
    now = datetime.now(tz) #Get current time on East Coast
    time = now.minute % 15
    db = sqlite3.connect('main.sqlite') 
    cursor = db.cursor()
    cursor.execute(f"SELECT channel_id FROM main WHERE guild_id = 0 AND name = 'system'")
    result = cursor.fetchone()
    if result is None:
        sql = ("INSERT INTO main(guild_id, channel_id, name) VALUES(?,?,?)")
        val = (0, time, 'system')
    elif result is not None:
        sql = ("UPDATE main SET channel_id = ? WHERE guild_id = ? AND name = ?")
        val = (time, 0, 'system')
    cursor.execute(sql,val)
    db.commit()
    cursor.close()
    db.close()
    print("Time until next print: " + str(time))

async def updateData():
    global newsP
    global videosP
    global reviewsP
    global news
    global videosData
    global reviewsData
    global newsTitles
    global newsSubtitles
    #global newsThumbnails
    global newsLinks
    #global newsAuthors
    global videosTitles
    global videosSubtitles
    #global videosThumbnails
    global videosLinks
    global videosAuthors
    global reviewsTitles
    global reviewsSubtitles
    #global reviewsThumbnails
    global reviewsLinks
    #global reviewsAuthors

    valid = False
    while (valid == False):
        newsP = requests.get(NewsURL,headers={'User-Agent': 'Mozilla/5.0'})
        print("News Response Code: ", newsP.status_code)
        if newsP.status_code == 200: valid = True
    soupN = BeautifulSoup(newsP.content, "lxml")

    valid = False
    while (valid == False):
        videosP = requests.get(videosURL,headers={'User-Agent': 'Mozilla/5.0'})
        print("Videos Response Code: ", videosP.status_code)
        if videosP.status_code == 200: valid = True
    soupV = BeautifulSoup(videosP.content, "lxml")

    valid = False
    while (valid == False):
        reviewsP = requests.get(reviewsURL,headers={'User-Agent': 'Mozilla/5.0'})
        print("Reviews Response Code: ", reviewsP.status_code)
        if reviewsP.status_code == 200: valid = True
    soupR = BeautifulSoup(reviewsP.content, "lxml")


    news = soupN.findAll("section", class_="main-content")
    newsTitles = soupN.findAll("h3", class_="item-title")
    newsSubtitles = soupN.findAll("div", class_="item-subtitle")
    newsLinks = soupN.findAll("a", class_="item-body")
    #newsAuthors = soupN.findAll("div", class_="item-data item-more-data")[1::2]
    #newsThumbnails = soupN.findAll("img", class_="jsx-2920405963 progressive-image item-image jsx-294430442 rounded hover-opacity expand")

    videosData = soupV.find("section", class_="main-content")
    videosTitles = soupV.findAll("h3", class_="item-title")
    videosSubtitles = soupV.findAll("div", class_="item-subtitle")
    videosLinks = soupV.findAll("a", class_="item-body")
    #videosAuthors = soupV.findAll("div", class_="item-data item-more-data")[1::2]
    #videosThumbnails = soupV.findAll("img", class_="jsx-2920405963 progressive-image item-image jsx-294430442 rounded hover-opacity expand")

    reviewsData = soupR.find("section", class_="main-content")
    reviewsTitles = soupR.findAll("h3", class_="item-title")
    reviewsSubtitles = soupR.findAll("div", class_="item-subtitle")
    reviewsLinks = soupR.findAll("a", class_="item-body")
    #reviewsAuthors = soupR.findAll("div", class_="item-data item-more-data")[1::2]
    #reviewsThumbnails = soupR.findAll("img", class_="jsx-2920405963 progressive-image item-image jsx-294430442 rounded hover-opacity expand")

async def viewData(ctx, name):
    if name == 'news':
        title = 'News'
    elif name == 'videos':
        title = 'Videos'
    else:
        title = 'Reviews'
    db = sqlite3.connect('main.sqlite')
    cursor = db.cursor()
    cursor.execute(f"SELECT channel_id FROM main WHERE guild_id = {ctx.guild.id} AND name = '{name}'")
    result = cursor.fetchone()
    if result is None:
        print(f'{title} channel has not be set in {ctx.guild.id}')
        await ctx.send(f'{title} channel has not be set')
    elif result is not None:
        channelID = int(result[0])
        print(f"{title} channel set to <#{channelID}> in {ctx.guild.id}")
        await ctx.channel.send(f"{title} channel set to <#{channelID}>")
    cursor.close()
    db.close()    

async def setData(ctx, name):
    if name == 'news':
        title = 'News'
    elif name == 'videos':
        title = 'Videos'
    else:
        title = 'Reviews'
    db = sqlite3.connect('main.sqlite')
    cursor = db.cursor()
    cursor.execute(f"SELECT channel_id FROM main WHERE guild_id = {ctx.guild.id} AND name = '{name}'")
    result = cursor.fetchone()
    if result is None:
        sql = ("INSERT INTO main(guild_id, channel_id, name) VALUES(?,?,?)")
        val = (ctx.guild.id, ctx.channel.id, name)
        print(f"{title} channel has been set to {ctx.channel.mention} in {ctx.guild.id}")
        await ctx.send(f"{title} channel has been set to {ctx.channel.mention}")
    elif result is not None:
        sql = ("UPDATE main SET channel_id = ? WHERE guild_id = ? AND name = ?")
        val = (ctx.channel.id, ctx.guild.id, name)
        print(f"{title} channel has been updated to {ctx.channel.mention} in {ctx.guild.id}")
        await ctx.send(f"{title} channel has been updated to {ctx.channel.mention}")
    cursor.execute(sql,val)
    db.commit()
    cursor.close()
    db.close()

async def rmData(ctx, name):
    if name == 'news':
        title = 'News'
    elif name == 'videos':
        title = 'Videos'
    else:
        title = 'Reviews'
    db = sqlite3.connect('main.sqlite')
    cursor = db.cursor()
    cursor.execute(f"SELECT channel_id FROM main WHERE guild_id = {ctx.guild.id} AND name = '{name}'")
    result = cursor.fetchone()
    if result is None:
        print(f'{title} channel has not be set in {ctx.guild.id}')
        await ctx.send(f"{title} channel has not been set")
    elif result is not None:
        sql = ("DELETE FROM main WHERE channel_id = ? AND guild_id = ? AND name = ?")
        val = (ctx.channel.id, ctx.guild.id, name)
        print(f'{title} channel has been removed in {ctx.guild.id}')
        await ctx.send(f"{title} channel has been removed")
    cursor.execute(sql,val)
    db.commit()
    cursor.close()
    db.close()

async def printData(cursor, guild_id=0):
    if guild_id > 0:
        result = cursor.execute(f"SELECT * FROM main WHERE guild_id={guild_id}")
    else:
        result = cursor.execute("SELECT * FROM main")
    data = result.fetchall()
    for d in data:
        counter = 0
        print(d)
        if d[2] == 'news':
            channelID = int(d[1])
            message_channel = bot.get_channel(channelID)
            print(message_channel)
            index = 0
            titleList = newsTitles
            subtitles = newsSubtitles
            links = newsLinks
            #authors = newsAuthors
            #images = newsThumbnails
        elif d[2] == 'videos':
            channelID = int(d[1])
            message_channel = bot.get_channel(channelID)
            print(message_channel)
            index = 1
            titleList = videosTitles
            subtitles = videosSubtitles
            links = videosLinks
            #authors = videosAuthors
            #images = videosThumbnails
        elif d[2] == 'reviews': 
            channelID = int(d[1])
            message_channel = bot.get_channel(channelID)
            print(message_channel)
            index = 2
            titleList = reviewsTitles
            subtitles = reviewsSubtitles
            links = reviewsLinks
            #authors = reviewsAuthors
            #images = reviewsThumbnails
        else:
            continue
        oldTitle = newestTitle[index]
        for count, title in enumerate(titleList):
            if title.text == oldTitle:
                break
            else:
                if counter==0:
                    newestTitle[index] = title.text
                embed = discord.Embed(title = title.text, url="https://www.ign.com"+links[count]['href'], description=subtitles[count].text, colour=0xD51D29)
                #embed.set_image(url=images[count]['src'])
                #embed.set_author(name=authors[count].text)
                embed.set_footer(text=footer)
                counter+= 1
                await sendMessage(message_channel, embed)

async def sendMessage(message_channel, embed):
    msg = await message_channel.send(embed=embed)
    await msg.add_reaction("⬆️")
    await msg.add_reaction("🔻")

#Run on $News
@bot.command(name='news')
@has_permissions(manage_channels = True)
async def News(ctx):
    await setData(ctx, 'news')
    await timeCalc()

#Print channel set to Ike's
@bot.command(name='viewnews')
@has_permissions(manage_channels = True)
async def viewNews(ctx):
    await viewData(ctx, 'news')

@bot.command(name='rmnews')
@has_permissions(manage_channels = True)
async def rmNews(ctx):
    await rmData(ctx, 'news')

#Run on $videos
@bot.command(name='videos')
@has_permissions(manage_channels = True)
async def videos(ctx):
    await setData(ctx, 'videos')
    await timeCalc()
    
@bot.command(name='viewvideos')
@has_permissions(manage_channels = True)
async def viewSS(ctx):
    await viewData(ctx, 'videos')

@bot.command(name='rmvideos')
@has_permissions(manage_channels = True)
async def rmSS(ctx):
    await rmData(ctx, 'videos')

#Run on $reviews
@bot.command(name='reviews')
@has_permissions(manage_channels = True)
async def reviews(ctx):
    await setData(ctx, 'reviews')
    await timeCalc()

@bot.command(name='viewreviews')
@has_permissions(manage_channels = True)
async def viewReviews(ctx):
    await viewData(ctx, 'reviews')

@bot.command(name='rmreviews')
@has_permissions(manage_channels = True)
async def rmReviews(ctx):
    await rmData(ctx, 'reviews')

@bot.command(name='time') #should be removed - testing purpose only
@has_permissions(manage_channels = True)
async def timeCheck(ctx):
    print('checking time')
    message=''
    db = sqlite3.connect('main.sqlite')
    cursor = db.cursor()
    cursor.execute(f"SELECT channel_id FROM main WHERE guild_id = 0 AND name = 'system'")
    result = cursor.fetchone()
    if result is None:
        message = 'Error: Time not set'
    elif result is not None:
        for c in result:
            if c.isnumeric() == True:
                message += str(int(c)//60) + ':'
                if int(c)%60 < 10:
                    message += "0" + str(int(c)%60)
                else:
                    message += str(int(c)%60)
        message += ' until next print'
    cursor.close()
    db.close()
    print(message)
    await ctx.channel.send(message)

@bot.command(name='help')
@has_permissions(manage_channels = True)
async def help(ctx):
    message = """   Commands - \n
                    **$news** - Set channel to print news updates \n
                    **$videos** - Set channel to print new video \n
                    **$reviews** - Set channel to print new reviews \n
                    **$viewNews** - View the channel where news has been set to \n
                    **$viewVideos** - View the channel where videos have been set to \n
                    **$viewReviews** - View the channel where reviews have been set to \n
                    **$rmNews** - Remove the channel where news has been set to \n
                    **$rmVideos** - Remove the channel where videos have been set to \n
                    **$rmReviews** - Remove the channel where reviews have been set to \n
                    **$print** - Force print all videos for your server \n
                    **$SQL** - Print all SQL entries (Used for testing - can be made \"mod only\") \n
                    **$footer** - Set footer of embed (Used for fun messages during holidays - can be made \"mod only\") \n
                    """
    await ctx.channel.send(message)

@bot.command(name='print') #Print list of commands
@has_permissions(manage_channels = True)
async def forcePrint(ctx):
    db = sqlite3.connect('main.sqlite')
    cursor = db.cursor()
    await printData(cursor,guild_id=ctx.guild.id)
    db.close()

@bot.command(name='sql')
async def sqlPrint(ctx):
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        cursor.execute(f"SELECT * FROM main")
        result = cursor.fetchall()
        for r in result:
            await ctx.channel.send(r)
        db.close()

@bot.command(name='footer')
async def sqlPrint(ctx, arg1):
    global footer
    await ctx.channel.send("Footer set to: " + arg1)
    footer = arg1

''' 
### Mod only version
### Add two the id values below Token in TOKEN.txt to allow users
### to access these commands. Does not need to be 2 but in my case
### I have two discord accounts 
@bot.command(name='sql')
async def sqlPrint(ctx):
    if ctx.author.id == int(user1) or ctx.author.id == int(user2):
        if isinstance(ctx.channel, discord.channel.DMChannel):
            print("SQL Database viewed by: " + ctx.author.name)
            db = sqlite3.connect('main.sqlite')
            cursor = db.cursor()
            cursor.execute(f"SELECT * FROM main")
            result = cursor.fetchall()
            for r in result:
                await ctx.channel.send(r)
            db.close()

@bot.command(name='footer')
async def sqlPrint(ctx, arg1):
    if ctx.author.id == int(user1) or ctx.author.id == int(user2):
        if isinstance(ctx.channel, discord.channel.DMChannel):
            global footer
            print("Footer set to: " + arg1 + " by " + ctx.author.name)
            await ctx.channel.send("Footer set to: " + arg1)
            footer = arg1
'''

#Run every 15 minutes
@tasks.loop(minutes=1)
async def calledPerDay():
    global time
    #Put time var on SQL database
    db = sqlite3.connect('main.sqlite')
    cursor = db.cursor()
    cursor.execute(f"SELECT channel_id FROM main WHERE guild_id = 0 AND name = 'system'")
    result = cursor.fetchone()
    if result is None:
        message = 'Error: Time not set'
        print(message)
    elif result is not None:
        for c in result:
            if c.isnumeric() == True:
                time = int(c)
    time -= 1
    sql = ("UPDATE main SET channel_id = ? WHERE guild_id = ? AND name = ?")
    val = (time, 0, 'system')
    cursor.execute(sql,val)
    if time == 0:
        time = 15 #Reset Loop - SQL update
        sql = ("UPDATE main SET channel_id = ? WHERE guild_id = ? AND name = ?")
        val = (time, 0, 'system')
        cursor.execute(sql,val)
        await updateData()
        await printData(cursor)
    db.commit()
    cursor.close()
    db.close()

@calledPerDay.before_loop
async def before():
    await bot.wait_until_ready()

calledPerDay.start()
bot.loop.create_task(changePresence())
bot.run(TOKEN)
