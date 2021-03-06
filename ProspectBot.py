#####ProspectBot#####
####By: Iwan####
import discord
from discord.ext import commands
import asyncio
import sys
import random
import time
import configparser
import os
import sqlite3
from cleverwrap import CleverWrap

##Variables & Objects##

#Globals
VERSION = "0.4"
DEBUG = True
SERVER = "507275577925828667"
botChannel = "543633717097267217"
botID = "543622344896282644"
inoutChan = "514626001716903965"
blankDeck = list(())

#Vars
op_roles = []
commanderID = "142076624072867840"
userCommands = ["startpokerrun", "draw", "roll", "flip", "remind", "addquote", "quote", "pfp", "info", "version", "changelog"]
operatorCommands = ["terminate"]
killResponses = ["%s 'accidentally' fell in a ditch... RIP >:)", "Oh, %s did that food taste strange? Maybe it was.....*poisoned* :wink:", "I didn't mean to shoot %s, I swear the gun was unloaded!", "Hey %s, do me a favor? Put this rope around your neck and tell me if it feels uncomfortable.", "*stabs %s* heh.... *stabs again*....hehe, stabby stabby >:D", "%s fell into the ocean whilst holding an anvil...well that was stupid."]

#Objs
bot = commands.Bot(command_prefix="!")
connection = sqlite3.connect('LostData.db')
cur = connection.cursor()


#Remove Default Help cmd#
bot.remove_command('help')

#Util funcs
def getTokens():
    config = configparser.ConfigParser()
    if not os.path.isfile("tokens.cfg"):
        print("tokens file missing. ")
        print("Creating one now.")
        config.add_section("Tokens")
        config.set("Tokens", "Bot", "null")
        config.set("Tokens", "Cleverbot", "null")
        with open ('tokens.cfg', 'w') as configfile:
            config.write(configfile)
        print("File created.")
        print("Please edit tokens.cfg and then restart.")
        _ = input()
    else:
        config.read('tokens.cfg')
        global botToken
        botToken = config.get('Tokens', 'Bot')
        global cb
        cb = CleverWrap(config.get('Tokens', 'Cleverbot'))
        
def isOp(member):
    if member.id == commanderID:
        return True
    for r in member.roles:
        if r.id in op_roles:
            return True
            return
    return False
    
def debug(msg):
    if DEBUG == True:
        print(msg)
        
def create_tables():
    cur.execute('''CREATE TABLE IF NOT EXISTS transactions
                     (user TEXT, trans INT, location TEXT)''')

    cur.execute('''CREATE TABLE IF NOT EXISTS quoteList
                     (QUOTES TEXT)''')
                     
def register_quote(usr, quote):
    quote = usr.display_name + ': "' + quote + '"'
    cur.execute("INSERT INTO quoteList (quotes) VALUES (?)", (quote,))
    connection.commit()
    
def load_quotes():
    print("Loading Quotes...")
    cur.execute('''SELECT * FROM quoteList''')
    global quotes
    quotes = cur.fetchall()
def get_quote():
    quote = random.choice(quotes)
    quote = str(quote)
    quote = quote.strip("('',)")
    return quote
    
def get_changelog(ver):
    with open ('changelogs/' + ver + '.txt', 'r') as changelog:
        changelog = changelog.read()
        changelog = changelog.splitlines()
    changelog = str(changelog)
    changelog = changelog.replace("',", "\n")
    changelog = changelog.split("['],")
    return changelog
    
def register_transaction(usr, trans, loc):
    usr = usr.display_name
    cur.execute("INSERT INTO transactions (user, trans, location) VALUES (?, ?, ?)", (usr, trans, loc))
    connection.commit()
    
def get_translog(usr):
    usr = usr.display_name
    cur.execute("SELECT user, trans, location FROM transactions WHERE user = (?)", (usr,))
    translog = str(cur.fetchall())
    translog = translog.strip("[(',)]")
    translog = translog.replace(", (", "")
    translog = translog.replace(")", "\n")
    translog = "Transaction History for " + usr + ": " + "\n" + translog
    return translog
    
def startPokerRun(chan, deck):
    print("Starting Poker run!")
    print("Clearing old deck...")
    deck.clear()
    print("Building new deck...")
    rank = ['A','2','3','4','5','6','7','8','9','10','J','K','Q']
    suit = [':clubs:',':hearts:',':diamonds:',':spades:']
    for x in rank:
        for y in suit:
            card = x + y
            deck.append(card)
            print(card)
    print("Deck built.")
    return deck
    
def drawCard(deck):
    if deck:
        card = random.choice(deck)
        deck.remove(card)
        return card
    else:
        return None
   
 
#Bot Events
@bot.event
async def on_ready():
    print("Logged in as: " + bot.user.name)
    print("ID: " + bot.user.id)
    print("------------------")
    await bot.change_presence(game=discord.Game(name="on a steel horse"))
    #_chan = bot.get_server(SERVER).get_channel(botChannel)
    #await bot.send_message(_chan, "ProspectBot v" + VERSION + " coming online...")
    

#OPERATOR-ONLY COMMANDS
@bot.command(pass_context = True)
async def terminate(ctx):
    if isOp(ctx.message.author) == True:
        await bot.say("ProspectBot going offline...")
        await bot.change_presence(status=discord.Status.offline)
        sys.exit()
    else:
        await bot.say("ERROR: UNAUTHORIZED!")
    
@bot.command(pass_context = True)
async def botFight(ctx):
    if isOp(ctx.message.author) == True:
        await bot.say("As you wish...I will now fight myself.")
        await asyncio.sleep(3)
        await bot.say(ctx.message.server.get_member(botID).mention + " Let's Fight.")
    else:
        await bot.say("ERROR: UNAUTHORIZED!")
    
#USER COMMANDS
@bot.command(pass_context = True)
async def help(ctx):
    usrCmds = '\n'.join("!" + str(c) for c in userCommands)
    em = discord.Embed(title='', description=usrCmds, colour=0xFF0000)
    em.set_author(name='Commands:', icon_url=bot.user.avatar_url)
    await bot.send_message(ctx.message.channel, embed=em)
    #If  user is operator, send dm with op commands
    if isOp(ctx.message.author) == True:
        opCmds = '\n'.join("!" + str(c) for c in operatorCommands)
        em = discord.Embed(title='', description=opCmds, colour=0xFF0000)
        em.set_author(name='Operator Commands:', icon_url=bot.user.avatar_url)
        await bot.send_message(ctx.message.author, embed=em)

@bot.command()
async def version():
    await bot.say("I am currently on version " + VERSION)
      
@bot.command(pass_context = True)
async def changelog(ctx, ver: str=VERSION):
    await bot.say("Changelog for version " + ver + ":")
    for x in get_changelog(ver):
        await bot.say("`" + str(x).strip("['],").replace("'", "") + "`")
      
@bot.command()
async def roll(dice : str=None):
    if dice == None:
        await bot.say('Format has to be in NdN!')
        return
    try:
        rolls, limit = map(int, dice.split('d'))
    except Exception:
        await bot.say('Format has to be in NdN!')
        return

    result = ', '.join(str(random.randint(1, limit)) for r in range(rolls))
    await bot.say(result)
      
@bot.command(pass_context = True)
async def flip(ctx):
    await bot.say("Okay, I'll flip it!")
    await bot.send_typing(ctx.message.channel)
    await asyncio.sleep(3)
    if random.choice([True, False]) == True:
        await bot.say(ctx.message.author.mention + ": the result is.......**HEADS**!")
    else:
        await bot.say(ctx.message.author.mention + ": the result is.......**TAILS**!")
      
@bot.group(pass_context = True)
async def remind(ctx, time: str = "0", *, reminder: str=None):
    time = int(time)
    if time == 0 or reminder == None:
        await bot.say("Correct Usage: !remind <time in minutes> <reminder>")
        await bot.say("Example: !remind 5 Tell me how reminders work")
        return
    else:
        await bot.delete_message(ctx.message)
        await bot.say("Okay, " + ctx.message.author.mention + "! I'll remind you :smile:")
        await asyncio.sleep(time * 60)
        await bot.send_message(ctx.message.author, "You wanted me to remind you: " + reminder)
    
@bot.command(pass_context = True)
async def addquote(ctx, member: discord.Member = None, *, quote: str=None):
    if member == None or quote == None:
        await bot.say("You must mention a user and add a quote!")
        await bot.say("Example: `!addquote @Iwan I love quotes`")
    elif member.id == botID and isOp(ctx.message.author) == False:
        await bot.say("ERROR: UNAUTHORIZED! You are not allowed to quote me. Muahahaha!")
        return
    else:
        register_quote(member, quote)
        await bot.delete_message(ctx.message)
        await bot.say("Quote added :thumbsup:")
        load_quotes()
       
@bot.command()
async def quote():
    await bot.say(get_quote())
    
@bot.command(pass_context = True)
async def pfp(ctx, member: discord.Member=None):
    if member==None:
        member = ctx.message.author
#        await bot.say("You forgot to give me a user! try mentioning someone with @ next time!")
#        await bot.say("Example: `!pfp @Katyusha`")
#        return
    await bot.say(ctx.message.author.mention + ": Here you go!\n" + member.avatar_url)
        
@bot.command(pass_context = True)
async def info(ctx, member: discord.Member=None):
    if member == None:
        member = ctx.message.author
    info = "Joined server on: " + member.joined_at.strftime("%A %B %d, %Y at %I:%M%p")
    em = discord.Embed(title='', description=info, colour=0xFF0000)
    em.set_author(name=member.name, icon_url=member.avatar_url)
    await bot.send_message(ctx.message.channel, embed=em)
    
@bot.command(pass_context = True)
async def kill (ctx, *, member: discord.Member = None):
    if member is None:
        await bot.say(ctx.message.author.mention + ": I need a target!")
        return

    if member.id == ctx.message.author.id:
        await bot.say(ctx.message.author.mention + ": Why do you want me to kill you? :open_mouth:")
    elif member.id == botID:
        await bot.say(ctx.message.author.mention + ": Hah! Don't get cocky kid, I could end you in less than a minute! :dagger:")
    else:
        random.seed(time.time())
        choice = killResponses[random.randrange(len(killResponses))] % member.mention
        await bot.say(choice)
        

@bot.command(pass_context = True)
async def transaction(ctx, trans: int=None, *, loc: str=None):
    user = ctx.message.author
    await bot.delete_message(ctx.message)
    if trans == None or loc == None:
        await bot.say(ctx.message.author.mention + "-" + "Error: you're missing a required field!" + "\n" + "Examples: `!transaction 10520 carson` `!transaction -20000 paleto`")
    else:
        register_transaction(user, trans, loc)
        await bot.say("Transaction Logged.")
        
@bot.command(pass_context = True)
async def translog(ctx, user: discord.Member=None):
    if user==None:
        await bot.send_message(ctx.message.author, get_translog(ctx.message.author))
        
        
@bot.command(pass_context = True)
async def startpokerrun(ctx):
    global deck
    deck = startPokerRun(ctx.message.channel, blankDeck)
    msg = "\nA poker run is starting!\nRemember to use `!draw` to draw a card!"
    em = discord.Embed(title='', description=msg, colour=0xFF0000)
    em.set_author(name='Poker Run:', icon_url="https://i.imgur.com/2r4ARoe.jpg")
    await bot.send_message(ctx.message.channel, embed=em)

@bot.command(pass_context = True)
async def draw(ctx):
    try:
        card = drawCard(deck)
        if card == None:
            await bot.say("Deck is empty! Build a new one with `!startpokerrun`")
        else:
            await bot.say(ctx.message.author.mention + " drew: " + card)
    except NameError:
        await bot.say("Deck is empty! Build a new one with `!startpokerrun`")


@bot.event
async def on_member_join(member):
    print(member.name + " has joined the server...assigning rank...")
    _role = discord.utils.get(bot.get_server(SERVER).roles, name="Associate")
    await bot.add_roles(member, _role)
    print("Role added to " + member.name)
    _chan = bot.get_server(SERVER).get_channel(inoutChan)
    await bot.send_message(_chan, ":thumbsup: " + member.mention + " has checked into LOXSTEEL'S Resort and Spa.")
    
@bot.event
async def on_member_remove(member):
    _chan = bot.get_server(SERVER).get_channel(inoutChan)
    await bot.send_message(_chan, ":thumbsdown: " + member.name + " has checked out of LOXSTEEL'S Resort and Spa.")        
        
        
#Cleverbot integration
@bot.event
async def on_message(message):
    await bot.process_commands(message)
    if message.content.startswith(message.server.get_member(botID).mention):
        await bot.send_typing(message.channel)
        stripmsg = message.content.replace('ProspectBot, ', "")
        stripmsg = stripmsg.strip(str(message.server.get_member(botID).mention))
        stripmsg = stripmsg.strip("@")
        stripmsg = stripmsg.strip("<")
        stripmsg = stripmsg.strip(">")
        debug("Saying to CB: " + stripmsg)
        botmsg = cb.say(stripmsg)
        await bot.send_message(message.channel, message.author.mention + ': ' + botmsg)
        

#Runtime, baby! Let's go!    
print ('Getting ready...')
print('Loading ProspectBot v' + VERSION)
getTokens()
create_tables()
load_quotes()
bot.run(botToken)