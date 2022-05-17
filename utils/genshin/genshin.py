import hashlib
import json
import string
import time
import uuid
from typing import List

from Cryptodome.Random import random
from khl_card.card import Card
from khl_card.modules import *
from khl_card.accessory import *
from khl_card.types import ThemeTypes
from mcdreforged.api.utils.serializer import Serializable

from utils.genshin.settings import Config, req


def hexdigest(text):
    md5 = hashlib.md5()
    md5.update(text.encode())
    return md5.hexdigest()


class Base:
    def __init__(self, cookies: str, logger):
        if not isinstance(cookies, str):
            raise TypeError('%s want a %s but got %s' %
                            (self.__class__, type(__name__), type(cookies)))
        self._cookie = cookies
        self.log = logger

    def get_header(self):
        header = {
            'User-Agent': Config.USER_AGENT,
            'Referer': Config.REFERER_URL,
            'Accept-Encoding': 'gzip, deflate, br',
            'Cookie': self._cookie
        }
        return header


class Roles(Base):
    async def get_awards(self):
        return await req('GET', Config.AWARD_URL, headers=self.get_header())

    async def get_roles(self):
        response = await req('GET', Config.ROLE_URL, headers=self.get_header())
        message = response['message']

        if response.get('retcode', 1) != 0 or response.get('data', None) is None:
            raise Exception(message)

        return response


class Sign(Base):

    def __init__(self, cookies: str, logger):
        super().__init__(cookies, logger)
        self._region_list = []
        self._region_name_list = []
        self._uid_list = []

    @staticmethod
    def get_ds():
        # v2.3.0-web @povsister & @journey-ad
        n = 'h8w582wxwgqvahcdkpvdhbh2w9casgfl'
        i = str(int(time.time()))
        r = ''.join(random.sample(string.ascii_lowercase + string.digits, 6))
        c = hexdigest('salt=' + n + '&t=' + i + '&r=' + r)
        return '{},{},{}'.format(i, r, c)

    def get_header(self):
        header = super(Sign, self).get_header()
        header.update({
            'x-rpc-device_id': str(uuid.uuid3(uuid.NAMESPACE_URL, self._cookie)).replace('-', '').upper(),
            # 1:  ios
            # 2:  android
            # 4:  pc web
            # 5:  mobile web
            'x-rpc-client_type': '5',
            'x-rpc-app_version': Config.APP_VERSION,
            'DS': self.get_ds(),
        })
        return header

    async def get_info(self):
        user_game_roles = await Roles(self._cookie, self.log).get_roles()
        role_list = user_game_roles.get('data', {}).get('list', [])

        # role list empty
        if not role_list:
            raise Exception(user_game_roles.get('message', 'Role list empty'))

        info_list = []
        # cn_gf01:  天空岛
        # cn_qd01:  世界树
        self._region_list = [(i.get('region', 'NA')) for i in role_list]
        self._region_name_list = [(i.get('region_name', 'NA'))
                                  for i in role_list]
        self._uid_list = [(i.get('game_uid', 'NA')) for i in role_list]

        for i in range(len(self._uid_list)):
            info_url = Config.INFO_URL.format(
                self._region_list[i], Config.ACT_ID, self._uid_list[i])
            try:
                content = await req('GET', info_url, headers=self.get_header())
                info_list.append(content)
            except Exception as e:
                raise Exception(e)

        if not info_list:
            raise Exception('User sign info list is empty')
        return info_list

    async def run(self) -> List[dict]:
        info_list = await self.get_info()
        message_list = []
        for i in range(len(info_list)):
            today = info_list[i]['data']['today']
            total_sign_day = info_list[i]['data']['total_sign_day']
            awards = await Roles(self._cookie, self.log).get_awards()
            awards = awards['data']['awards']
            uid = str(self._uid_list[i])

            # self.log.debug(f'准备为旅行者 {i + 1} 号签到...')
            message = {
                'today': today,
                'region_name': self._region_name_list[i],
                'uid': uid,
                'total_sign_day': total_sign_day,
                'end': '',
            }
            if info_list[i]['data']['is_sign'] is True:
                message['award_name'] = awards[total_sign_day - 1]['name']
                message['award_cnt'] = awards[total_sign_day - 1]['cnt']
                message['status'] = f'👀 旅行者 {i + 1} 号, 你已经签到过了哦'
                message_list.append(message)
                continue
            else:
                message['award_name'] = awards[total_sign_day]['name']
                message['award_cnt'] = awards[total_sign_day]['cnt']
            if info_list[i]['data']['first_bind'] is True:
                message['status'] = f'💪 旅行者 {i + 1} 号, 请先前往米游社App手动签到一次'
                message_list.append(message)
                continue

            data = {
                'act_id': Config.ACT_ID,
                'region': self._region_list[i],
                'uid': self._uid_list[i]
            }

            try:
                response = await req('post', Config.SIGN_URL, headers=self.get_header(),
                                     data=json.dumps(data, ensure_ascii=False))
            except Exception as e:
                raise Exception(e)
            code = response.get('retcode', 99999)
            # 0:      success
            # -5003:  already signed in
            if code != 0:
                message_list.append(response)
                continue
            message['total_sign_day'] = total_sign_day + 1
            message['status'] = response['message']
            message_list.append(message)
        # self.log.debug('签到完毕')
        card_list: List = []
        for i in message_list:
            modules = [
                Header('签到结果：'),
                Section(Kmarkdown((i['today']))),
                Section(Kmarkdown(f'[{i["region_name"]}] {i["uid"]}')),
                Section(Kmarkdown(f'今日奖励: {i["award_name"]} × {i["award_cnt"]}')),
                Section(Kmarkdown(f'本月累签: {i["total_sign_day"]} 天')),
                Section(Kmarkdown(f'签到结果: {i["status"]}'))
            ]
            card_list.append(Card(*modules, theme='info').build())

        return card_list


def time_to_str(recovery_time: int):
    h = recovery_time // 3600
    m = (recovery_time - h * 3600) // 60
    if h < 10:
        h = '0' + str(h)
    else:
        h = str(h)
    if m < 10:
        m = '0' + str(m)
    else:
        m = str(m)
    return f'剩余 **{h}** 时 **{m}** 分'


class RecordData(Serializable):
    current_resin: int = 0
    max_resin: int = 160
    resin_recovery_time: str = ''
    finished_task_num: int = 0
    total_task_num: int = 0
    is_extra_task_reward_received: bool = False
    remain_resin_discount_num: int = 0
    resin_discount_num_limit: int = 0
    current_expedition_num: int = 0
    max_expedition_num: int = 0
    expeditions: list = []
    current_home_coin: int = 0
    max_home_coin: int = 0
    home_coin_recovery_time: str = ''

    @classmethod
    def load(cls, data: dict):
        return cls.deserialize(data)


class Record(Base):
    def __init__(self, cookies: str, logger):
        super(Record, self).__init__(cookies, logger)
        self._region_list = []
        self._region_name_list = []
        self._uid_list = []
        self._level_list = []
        self._name_list = []

    @staticmethod
    def get_ds(url: str):
        n = 'xV8v4Qu54lUKrEYFZkJhB8cuOh9Asafs'
        i = str(int(time.time()))
        r = ''.join(random.sample(string.ascii_lowercase + string.digits, 6))
        c = hexdigest('salt=' + n + '&t=' + i + '&r=' + r + '&b=&q=' + url.split('?')[1])
        return '{},{},{}'.format(i, r, c)

    def get_headers(self, url):
        headers = {
            'Cookie': self._cookie,
            'DS': self.get_ds(url),
            'x-rpc-app_version': '2.20.1',
            'x-rpc-client_type': '5'
        }
        return headers

    async def get_info(self) -> List[RecordData]:
        user_game_roles = await Roles(self._cookie, self.log).get_roles()
        role_list = user_game_roles.get('data', {}).get('list', [])

        # role list empty
        if not role_list:
            raise Exception(user_game_roles.get('message', 'Role list empty'))

        record_list: List[RecordData] = []
        # cn_gf01:  天空岛
        # cn_qd01:  世界树
        self._region_list = [(i.get('region', 'NA')) for i in role_list]
        self._region_name_list = [(i.get('region_name', 'NA'))
                                  for i in role_list]
        self._uid_list = [(i.get('game_uid', 'NA')) for i in role_list]
        self._level_list = [(i.get('level', 'NA')) for i in role_list]
        self._name_list = [(i.get('nickname', 'NA')) for i in role_list]

        for i in range(len(self._uid_list)):
            record_url = Config.RECORD_URL.format(self._uid_list[i], self._region_list[i])
            try:
                content = await req('get', record_url, headers=self.get_headers(record_url))
                record_list.append(RecordData.load(content['data']))
            except Exception as e:
                raise Exception(e)
        return record_list

    async def run(self):
        card_list = []
        record_list = await self.get_info()
        for i in range(len(record_list)):
            print(record_list[i].serialize())
            data = record_list[i]
            card = Card(theme=ThemeTypes.INFO)
            card.append(Header(f'原神便筏 {time.strftime("%H:%M", time.localtime())}更新'))
            card.append(Section(Kmarkdown(f'**{self._level_list[i]}** 级 - {self._name_list[i]}')))
            l1 = '·原粹树脂\n\n·洞天宝钱\n\n·每日委托\n·周本减半\n·探索派遣'
            l2 = f'已累计 **{data.current_resin}** 个\n{"已达上限！" if data.current_resin >= data.max_resin else time_to_str(int(data.resin_recovery_time))}\n已积累 **{data.current_home_coin}**\n{"已达上限！" if data.current_home_coin >= data.max_home_coin else time_to_str(int(data.home_coin_recovery_time))}\n已完成 **{data.finished_task_num}** 个\n还剩余 **{data.remain_resin_discount_num}** 次\n已派出 **{data.current_expedition_num}** 人'
            card.append(Section(Paragraph(3, [Kmarkdown(l1), Kmarkdown(l2), PlainText('')])))
            for expedition in data.expeditions:
                card.append(Section(Kmarkdown(
                    f'剩余时间: {time_to_str(int(expedition["remained_time"])) if expedition["status"] == "Ongoing" else "**已完成！**"}'),
                    mode='left', accessory=Image(expedition['avatar_side_icon'], circle=True)))
            card_list.append(card.build())
        return card_list
