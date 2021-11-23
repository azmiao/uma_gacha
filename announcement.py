import aiohttp
from bs4 import BeautifulSoup
import re
from datetime import datetime
from .config import DRAW_PATH
from pathlib import Path
from asyncio.exceptions import TimeoutError
import hoshino
from hoshino import log

logger = log.new_logger('announcement', hoshino.config.DEBUG)

try:
    import ujson as json
except ModuleNotFoundError:
    import json

headers = {'User-Agent': '"Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; TencentTraveler 4.0)"'}
pretty_up_char = Path(DRAW_PATH + "/draw_card_up/pretty_up_char.json")
pretty_url = "https://wiki.biligame.com/umamusume/%E5%85%AC%E5%91%8A"

# 是否过时
def is_expired(data: dict):
    times = data['time'].split('-')
    for i in range(len(times)):
        times[i] = str(datetime.now().year) + '-' + times[i].split('日')[0].strip().replace('月', '-')
    start_date = datetime.strptime(times[0], '%Y-%m-%d').date()
    end_date = datetime.strptime(times[1], '%Y-%m-%d').date()
    now = datetime.now().date()
    return start_date <= now <= end_date


# 检查写入
def check_write(data: dict, up_char_file):
    try:
        if not is_expired(data['char']):
            for x in list(data.keys()):
                data[x]['title'] = ''
        else:
            with open(up_char_file, 'w', encoding='utf8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        if not up_char_file.exists():
            with open(up_char_file, 'w', encoding='utf8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        else:
            with open(up_char_file, 'r', encoding='utf8') as f:
                old_data = json.load(f)
            if is_expired(old_data['char']):
                return old_data
            else:
                with open(up_char_file, 'w', encoding='utf8') as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)
    except ValueError:
        pass
    return data

class PrettyAnnouncement:

    def __init__(self):
        self.game_name = '赛马娘'

    async def _get_announcement_text(self):
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(pretty_url, timeout=7) as res:
                soup = BeautifulSoup(await res.text(), 'lxml')
                divs = soup.find('div', {'id': 'mw-content-text'}).find('div').find_all('div')
                for div in divs:
                    a = div.find('a')
                    try:
                        title = a['title']
                    except (KeyError, TypeError):
                        continue
                    if title.find('支援卡卡池') != -1:
                        url = a['href']
                        break
            async with session.get(f'https://wiki.biligame.com/{url}', timeout=7) as res:
                return await res.text(), title[:-2]

    async def update_up_char(self):
        data = {
            'char': {'up_char': {'3': {}, '2': {}, '1': {}}, 'title': '', 'time': '', 'pool_img': ''},
            'card': {'up_char': {'3': {}, '2': {}, '1': {}}, 'title': '', 'time': '', 'pool_img': ''}
        }
        try:
            text, title = await self._get_announcement_text()
            soup = BeautifulSoup(text, 'lxml')
            context = soup.find('div', {'class': 'toc-sticky'})
            if not context:
                context = soup.find('div', {'class': 'mw-parser-output'})
            data['char']['title'] = title
            data['card']['title'] = title
            for big in context.find_all('big'):
                r = re.search(r'\d{1,2}/\d{1,2} \d{1,2}:\d{1,2}', str(big.text))
                if r:
                    time = str(big.text)
                    break
            else:
                logger.info('赛马娘UP无法找到活动日期....取消更新UP池子...')
                return
            time = time.replace('～', '-').replace('/', '月').split(' ')
            time = time[0] + '日 ' + time[1] + ' - ' + time[3] + '日 ' + time[4]
            data['char']['time'] = time
            data['card']['time'] = time
            for p in context.find_all('p'):
                if str(p).find('当期UP赛马娘') != -1 and str(p).find('■') != -1:
                    if not data['char']['pool_img']:
                        try:
                            data['char']['pool_img'] = p.find('img')['src']
                        except TypeError:
                            for center in context.find_all('center'):
                                try:
                                    img = center.find('img')
                                    if img and str(img['alt']).find('新马娘') != -1 and str(img['alt']).find('总览') == 1:
                                        data['char']['pool_img'] = img['src']
                                except (TypeError, KeyError):
                                    pass
                    r = re.findall(r'.*?当期UP赛马娘([\s\S]*)＜奖励内容＞.*?', str(p))
                    if r:
                        for x in r:
                            x = str(x).split('\n')
                            for msg in x:
                                if msg.find('★') != -1:
                                    msg = msg.replace('<br/>', '')
                                    char_name = msg[msg.find('['):].strip()
                                    if (star := len(msg[:msg.find('[')].strip())) == 3:
                                        data['char']['up_char']['3'][char_name] = '70'
                                    elif star == 2:
                                        data['char']['up_char']['2'][char_name] = '70'
                                    elif star == 1:
                                        data['char']['up_char']['1'][char_name] = '70'
                if str(p).find('（当期UP对象）') != -1 and str(p).find('赛马娘') == -1 and str(p).find('■') != -1:
                    # data['card']['pool_img'] = p.find('img')['src']
                    if not data['char']['pool_img']:
                        try:
                            data['char']['pool_img'] = p.find('img')['src']
                        except TypeError:
                            for center in context.find_all('center'):
                                try:
                                    img = center.find('img')
                                    if img and str(img['alt']).find('新卡') != -1 and str(img['alt']).find('总览') == 1:
                                        data['card']['pool_img'] = img['src']
                                except (TypeError, KeyError):
                                    pass
                    r = re.search(r'■全?新?支援卡（当期UP对象）([\s\S]*)</p>', str(p))
                    if r:
                        rmsg = r.group(1).strip()
                        rmsg = rmsg.split('<br/>')
                        rmsg = [x for x in rmsg if x]
                        for x in rmsg:
                            x = x.replace('\n', '').replace('・', '')
                            star = x[:x.find('[')].strip()
                            char_name = x[x.find('['):].strip()
                            if star == 'SSR':
                                data['card']['up_char']['3'][char_name] = '70'
                            if star == 'SR':
                                data['card']['up_char']['2'][char_name] = '70'
                            if star == 'R':
                                data['card']['up_char']['1'][char_name] = '70'
            # 日文->中文
            with open(DRAW_PATH + 'pretty_card.json', 'r', encoding='utf8') as f:
                all_data = json.load(f)
            for star in data['card']['up_char'].keys():
                for name in list(data['card']['up_char'][star].keys()):
                    char_name = name.split(']')[1].strip()
                    tp_name = name[name.find('['): name.find(']') + 1].strip().replace('[', '【').replace(']', '】')
                    for x in all_data.keys():
                        if all_data[x]['名称'].find(tp_name) != -1 and all_data[x]['关联角色'] == char_name:
                            data['card']['up_char'][star].pop(name)
                            data['card']['up_char'][star][all_data[x]['中文名']] = '70'
        except TimeoutError:
            logger.info(f'更新赛马娘UP池信息超时...')
            if pretty_up_char.exists():
                with open(pretty_up_char, 'r', encoding='utf8') as f:
                    data = json.load(f)
        except Exception as e:
            logger.info(f'赛马娘up更新未知错误 {type(e)}：{e}')
            if pretty_up_char.exists():
                with open(pretty_up_char, 'r', encoding='utf8') as f:
                    data = json.load(f)
        return check_write(data, pretty_up_char)