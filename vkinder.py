import time
import requests
import config
import json
import re
from pprint import pprint
from connectiondb import datingdb as db


class User:
    token = '958eb5d439726565e9333aa30e50e0f937ee432e927f0dbd541c541887d919a7c56f95c04217915c32008'

    def __init__(self, user_id):
        params = {'access_token': self.token,
                  'user_ids': user_id,
                  'fields': config.fields,
                  'v': '5.101'}
        time.sleep(1)
        try:
            response = requests.get(
                'https://api.vk.com/method/users.get', params=params)
        except ConnectionError:
            print('Ошибка подключения')
        else:
            res = {}
            while 'response' not in res:
                res = response.json()
                if 'response' in res:
                    self.__dict__.update(res['response'][0])
                    self.weight = 0
                else:
                    self.token = input('токен неверный, введите токен: ')

    def search_list_ids_by_parameters(self, count=1000, age_from=0, age_to=0,
                                      id_city=0, sex=0, status=0):
        params = {'access_token': self.token,
                  'count': count,
                  'age_from': age_from,
                  'age_to': age_to,
                  'city': id_city,
                  'sex': sex,
                  'status': status,
                  'v': '5.52'}
        time.sleep(1)
        try:
            response = requests.get(
                'https://api.vk.com/method/users.search', params=params)
        except ConnectionError:
            pass
        else:
            res = response.json()
            search_list = []
            if 'response' in res:
                for item in res['response']['items']:
                    search_list.append(item['id'])
            return search_list

    def search(self, age_from=0, age_to=0,
               id_city=0):
        id_city = self.city['id']
       
        sexual_self = ''
        while sexual_self not in config.sexual:
            sexual_self = input(
                'Ориентация: введите hetersex, homosex или bisex - ')

        if hasattr(self, 'sex'):
            self_sex = self.sex
        else:
            self_sex = 0

        if sexual_self == 'homosex':
            search_sexes = [0, self_sex]
        elif sexual_self == 'bisex':
            search_sexes = config.sex
        else:
            search_sexes = list(set(config.sex).difference({0, self_sex}))

        age_from = input('введите диапазон возраста для поиска. От: ')
        age_to = input('До: ')

        list_ids_saved_to_db = []
        list_users_saved_to_db = list(db['users'].find())
        for user_saved in list_users_saved_to_db:
            list_ids_saved_to_db.append(user_saved.get('id'))
        print('list_ids_saved_to_db:')
        print(list_ids_saved_to_db)

        step = 0
        search_statuses = config.relation
        res_search = set()
        while (len(res_search) < 10) and (step < 10):
            for search_sex in search_sexes:
                for search_status in search_statuses:
                    set_ids = set(self.search_list_ids_by_parameters(count=5,
                                                                     age_from=age_from,
                                                                     age_to=age_to,
                                                                     id_city=id_city,
                                                                     sex=search_sex,
                                                                     status=search_status))
                    res_search.update(set_ids)
            step += 1
            res_search.difference_update(set(list_ids_saved_to_db))
        return list(res_search)

    def get_weight(self, other_user):
        weight = 0
        # общие друзья
        if hasattr(other_user, 'common_count'):
            if other_user.common_count > 0:
                weight += config.weight_common_friends
        # общие группы
        list_groups_self = self.get_list_ids_groups()
        list_groups_other = other_user.get_list_ids_groups()
        if set(list_groups_self).intersection(set(list_groups_other)):
            weight += config.weight_common_groups
        # общие интересы
        if self.get_intersection_interests(other_user, 'interests'):
            weight += config.weight_interests
        # общие музыкальные предпочтения
        if self.get_intersection_interests(other_user, 'music'):
            weight += config.weight_music
        # общие книги
        if self.get_intersection_interests(other_user, 'books'):
            weight += config.weight_books
        return weight

    def get_intersection_interests(self, other_user, iterest='interests'):
        if hasattr(self, iterest) and hasattr(other_user, iterest):
            pattern = "[\w]+"
            self_result = re.findall(pattern, getattr(self, iterest), re.U)
            other_user_result = re.findall(pattern, getattr(other_user, iterest), re.U)
            if set(self_result).intersection(set(other_user_result)):
                return 1
            else:
                return 0

    def get_list_users_with_weight(self):
        list_ids = self.search()
        print('list_ids_not_saved_to_database:')
        print(list_ids)
        list_users = []
        for id in list_ids:
            new_user = User(id)
            new_user.weight = self.get_weight(new_user)
            list_users.append(new_user)
            print(new_user.weight)
        return list_users

    def get_list_photo_profile(self):
        params = {'access_token': self.token,
                  'owner_id': self.id,
                  'album_id': 'profile',
                  'extended': 1,
                  'count': 1000,
                  'v': '5.101'}
        try:
            response = requests.get(
                'https://api.vk.com/method/photos.get', params=params)
        except ConnectionError:
            pass
        else:
            res = response.json()
            if 'response' in res:
                list_photos = res['response']['items']
                list_photos_top3 = sorted(list_photos,
                                          key=lambda x: x['likes']['count'],
                                          reverse=True)[0:3]
                list_photos_top3_only_url = []
                for photo in list_photos_top3:
                    list_photos_top3_only_url.append(photo['sizes'][-1]['url'])
                return list_photos_top3_only_url

    def get_list_top10_users(self):
        list_users = self.get_list_users_with_weight()
        list_dict = []
        for user in list_users:
            user_dict = user.__dict__
            for key in list(user_dict.keys()):
                if key not in ['id', 'weight']:
                    del user_dict[key]
            user_dict['photos_top3'] = user.get_list_photo_profile()
            list_dict.append(user_dict)

        sorted_list_top10_dict = sorted(list_dict,
                                        key=lambda user: user['weight'],
                                        reverse=True)[0:10]
        if sorted_list_top10_dict:
            with open('data.json', 'w', encoding='utf-8') as f:
                json.dump(sorted_list_top10_dict, f, ensure_ascii=False, indent=4)
            db['users'].insert_many(sorted_list_top10_dict)
        return sorted_list_top10_dict

    def get_list_ids_groups(self, extended='0'):
        params = {'access_token': self.token, 'user_id': self.id, 'v': '5.101', 'extended': extended,
                  'count': '1000'}
        while True:
            print('_')
            time.sleep(1)
            try:
                response = requests.get(
                    'https://api.vk.com/method/groups.get', params=params)
            except ConnectionError:
                pass
            else:
                res = response.json()
                if 'response' in res:
                    res_res = res['response']
                    if 'items' in res_res:
                        return res_res['items']
                    else:
                        return []
                else:
                    return []


if __name__ == '__main__':
    id_me = 360847139
    me = User(id_me)
    pprint(me.__dict__)
    print('Новый поиск')
    pprint(me.get_list_top10_users())
