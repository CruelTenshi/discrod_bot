from discord.ext import commands
import discord
import warnings

from scrapings import weather, trending, menu
from db_manage import db

from keys import discord_token
from settings import *

intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix=prefix, intents=intents)
warnings.filterwarnings('ignore')
client.remove_command('help')

def get_nick(author):
    try:
        author.nick[0]
        return author.nick
    except:
        return author.global_name

def check_manager(roles):
    for role in roles:
        if role.id == admin_role_id or role.id == manager_role_id:
            return True
    return False

def check_admin(roles):
    for role in roles:
        if role.id == admin_role_id:
            return True
    return False

@client.event
async def on_ready():    
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="가브릴 드롭아웃"))
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    global guild_id
    if message.author == client.user or not get_nick(message.author):
        return 
    try:
        str(message.guild.id)[0]
    except:
        print(f'접근 거부 / {message.author.global_name} says {message.content}')
        await message.channel.send('개인챗에서의 사용이 금지되어 있습니다.', reference=message)
        return

    is_command = message.content[0:len(prefix)] == prefix
    if message.guild.id == guild_id:
        user_id = str(message.author.id)
        if db.exist_user(user_id):
            db.check_name(user_id, get_nick(message.author))
            if 4 < len(message.content) and not is_command:
                db.point.plus(user_id, 3)
        else:
            db.register(user_id, get_nick(message.author))
            await message.channel.send(f"{get_nick(message.author)}님의 첫 메시지입니다! 50포인트가 지급되었습니다.", reference=message)
            db.point.plus(user_id, 50)

    await client.process_commands(message)

@client.command(aliases=['날씨'])
async def get_weather(ctx, *, place):
    global places_code
    try:
        for s in places_code:
            if s == place:
                await ctx.reply(weather.overall(place))
                return
            elif s == place + '동':
                await ctx.reply(weather.overall(place+'동'))
                return
        await ctx.reply(f'{place}(은)는 등록되지 않은 장소입니다..')
    except Exception as e:
        await ctx.reply('날씨 정보를 가져오는 도중 오류가 발생했습니다.')
        print('날씨 오류', e)

@client.command(aliases=['급식', '점심', '저녁', '중식', '석식', '메뉴'])
async def get_menu(ctx):
    try:
        await ctx.reply(menu.info())
    except Exception as e:
        await ctx.reply('급식 정보를 가져오는 도중 오류가 발생했습니다.')
        print('급식 오류', e)

@client.command(aliases=['실검'])
async def get_treding(ctx):
    try:
        await ctx.reply(trending.overall())
    except Exception as e:
        await ctx.reply('실검 정보를 가져오는 도중 오류가 발생했습니다.')
        print('실검 오류', e)

@client.command(aliases=['나'])
async def get_my_info(ctx):
    try:
        await ctx.reply(db.user_info((str(ctx.message.author.id))))
    except Exception as e:
        await ctx.reply('유저의 정보를 가져오는 도중 오류가 발생했습니다.')
        print('유저 정보 오류', e)

@client.command(aliases=['순위', '랭크', '랭킹'])
async def get_rank_table(ctx):
    try:
        await ctx.reply(db.point.rank_table())
    except Exception as e:
        await ctx.reply('랭크를 가져오는 도중 오류가 발생했습니다.')
        print('랭크 오류', e)

@client.command(aliases=['공지'])
async def to_notice(ctx, *, text):
    global notice_channel_id
    try:
        if check_manager(ctx.message.author.roles):
            await client.get_channel(notice_channel_id).send(text)
    except Exception as e:
        await ctx.reply('공지 도중 오류가 발생')
        print('공지 오류', e)

@client.command(aliases=['채팅'])
async def to_chat(ctx, *, text):
    global chat_channel_id
    try:
        if check_manager(ctx.message.author.roles):
            await client.get_channel(chat_channel_id).send(text)
    except Exception as e:
        await ctx.reply('채팅 도중 오류가 발생.')
        print('채팅 오류', e)

@client.command(aliases=['명령어', '명령', '도움말', '커맨드', 'help', '도움', 'command', 'commands'])
async def list_commands(ctx):
    await ctx.reply(commands_des)

@client.command(aliases=['점수'])
async def edit_point(ctx, target_id, point):
    try:
        if check_admin(ctx.message.author.roles) and db.exist_user(target_id):
            db.point.plus(target_id, int(point))
            await ctx.reply(f'성공적으로 \'{db.get_name(target_id)}\'에게 {point}점을 부여했습니다.')
    except Exception as e:
        await ctx.reply('점수 추가중 오류가 발생')
        print('점수 추가 오류', e)

@client.event
async def on_command_error(ctx, error):
    if ctx.message.content.replace(' ', '') == f'{prefix}날씨':
        await ctx.reply('장소 정보가 누락되었습니다.')
    else:
        await ctx.reply(f'**"{ctx.message.content[len(prefix):]}"**은(는) 존재하지 않는 명령어입니다.\n\n> {prefix}명령어\n위 커맨드를 사용하여 명령어를 확인해주세요.')

client.run(discord_token)