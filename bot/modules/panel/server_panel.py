"""
服务器讯息打印
"""
from datetime import datetime, timezone, timedelta
from pyrogram import filters
from bot import bot, emby_line, whitelist_line
from bot.func_helper.emby import emby
from bot.func_helper.filters import user_in_group_on_filter
from bot.sql_helper.sql_emby import sql_get_emby
from bot.func_helper.fix_bottons import cr_page_server
from bot.func_helper.msg_utils import callAnswer, editMessage
import json  # 导入 json 模块

# 从 bot 模块中导入 config
from bot import config


@bot.on_callback_query(filters.regex('server') & user_in_group_on_filter)
async def server(_, call):
    data = sql_get_emby(tg=call.from_user.id)
    if not data:
        return await editMessage(call, '⚠️ 数据库没有你，请重新 /start录入')
    await callAnswer(call, '🌐查询中...')

    try:
        j = int(call.data.split(':')[1])
    except IndexError:
        # 第一次查看
        send = await editMessage(call, "▎🌐查询中...\n\nο(=•ω＜=)ρ⌒☆ 发送bibo电波~bibo~ \n⚡ 点击按钮查看相应服务器状态")
        if send is False:
            return

        keyboard, sever = await cr_page_server()
        server_info = sever[0]['server'] if sever == '' else ''
    else:
        keyboard, sever = await cr_page_server()
        server_info = ''.join([item['server'] for item in sever if item['id'] == j])

    pwd = '空' if not data.pwd else data.pwd

    # 读取 config.json 使用绝对路径 "/app/config.json"
    try:
      with open("/app/config.json", "r", encoding="utf-8") as f:
        config_data = json.load(f)
    except Exception as e:
        print(f"读取配置文件错误: {e}")
        return await editMessage(call, "⚠️ 读取配置文件错误")
    
    # 判断是否为白名单用户，并选择线路
    if data.lv == 'a':
        line = f'{config_data.get("whitelist_line", "未配置白名单线路")}'
    elif data.lv == 'b':
        line = f'{config_data.get("emby_line", "未配置线路")}'
    else:
        line = ' - **无权查看**'
    
    try:
        online = emby.get_current_playing_count()
    except:
        online = 'Emby服务器断连 ·0'
    text = f'**▎↓目前线路 & 用户密码：**`{pwd}`\n' \
           f'{line}\n\n' \
           f'{server_info}' \
           f'· 🎬 在线 | **{online}** 人\n\n' \
           f'**· 🌏 [{(datetime.now(timezone(timedelta(hours=8)))).strftime("%Y-%m-%d %H:%M:%S")}]**'
    await editMessage(call, text, buttons=keyboard)
