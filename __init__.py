from .pretty_handle import update_pretty_info, pretty_draw, reload_pretty_pool, get_gacha_pool
import hoshino
import asyncio
from hoshino import Service, priv
from .config import check_config
from .async_update_game_info import async_update_game
from .util import _check_dir

check_config()
loop = asyncio.get_event_loop()
loop.run_until_complete(async_update_game())
_check_dir()

sv_help = '''=====功能=====
（@bot就是@机器人）

[@bot马娘十连] 马娘池子十连
[@bot马之井] 马娘池子抽一井
[@bot育成卡十连] 育成卡池子十连
[@bot育成卡井] 育成卡池子抽一井

[查看马娘卡池] 看马娘池up的马娘
[查看育成卡池] 看卡池up的育成卡'''.strip()

sv = Service('uma_gacha', help_=sv_help, enable_on_default=True, bundle='马娘抽卡')

# 帮助界面
@sv.on_fullmatch("马娘抽卡帮助")
async def help(bot, ev):
    await bot.send(ev, sv_help)

# 马娘十连
@sv.on_fullmatch(('马娘十连', '马十连'), only_to_me=True)
async def uma_gacha_char_ten(bot, ev):
    msg = await pretty_draw(10, 'char')
    await bot.send(ev, msg, at_sender=True)

# 马娘井
@sv.on_fullmatch(('马之井', '马娘井', '马娘一井'), only_to_me=True)
async def uma_gacha_char_jing(bot, ev):
    msg = await pretty_draw(200, 'char')
    await bot.send(ev, msg, at_sender=True)

# 育成卡十连
@sv.on_fullmatch('育成卡十连', only_to_me=True)
async def uma_gacha_card_ten(bot, ev):
    msg = await pretty_draw(10, 'card')
    await bot.send(ev, msg, at_sender=True)

# 育成卡井
@sv.on_fullmatch(('育成卡井', '育成卡一井'), only_to_me=True)
async def uma_gacha_card_jing(bot, ev):
    msg = await pretty_draw(200, 'card')
    await bot.send(ev, msg, at_sender=True)

# 查看马娘卡池
@sv.on_fullmatch('查看马娘卡池')
async def see_uma_char_poor(bot, ev):
    msg = await get_gacha_pool('char')
    await bot.send(ev, msg, at_sender=True)

# 查看育成卡池
@sv.on_fullmatch('查看育成卡池')
async def see_uma_card_poor(bot, ev):
    msg = await get_gacha_pool('card')
    await bot.send(ev, msg, at_sender=True)

# 更新马娘信息
@sv.on_fullmatch('更新马娘信息')
async def uma_gacha_update(bot, ev):
    if not priv.check_priv(ev, priv.SUPERUSER):
        msg = '很抱歉您没有权限进行此操作，该操作仅限维护组'
        await bot.send(ev, msg)
        return
    try:
        await update_pretty_info()
    except Exception as e:
        msg = f'马娘信息更新失败：{e}'
        await bot.send(ev, msg)
        return
    msg = f'马娘信息更新完成！'
    await bot.send(ev, msg)

# 重载赛马娘卡池
@sv.on_fullmatch('重载赛马娘卡池')
async def uma_gacha_reload(bot, ev):
    if not priv.check_priv(ev, priv.SUPERUSER):
        msg = '很抱歉您没有权限进行此操作，该操作仅限维护组'
        await bot.send(ev, msg)
        return
    try:
        text = await reload_pretty_pool()
    except Exception as e:
        msg = f'马娘卡池重载失败：{e}'
        await bot.send(ev, msg)
        return
    msg = f'马娘卡池重载成功！\n{text}'
    await bot.send(ev, msg)

# 每天四点重载赛马娘up卡池
@sv.scheduled_job('cron', hour='4', minute='00')
async def auto_update():
    bot = hoshino.get_bot()
    superid = hoshino.config.SUPERUSERS[0]
    sv.logger.info('正在重载赛马娘up卡池')
    try:
        reload_pretty_pool()
    except Exception as e:
        sv.logger.info(f'重载赛马娘up卡池失败，{e}')
        msg = f'重载赛马娘up卡池失败，{e}'
        await bot.send_private_msg(user_id=superid, message=msg)
        return
    sv.logger.info('重载赛马娘up卡池成功')
    msg = '重载赛马娘up卡池成功'
    await bot.send_private_msg(user_id=superid, message=msg)