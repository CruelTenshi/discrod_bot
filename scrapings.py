from datetime import datetime, timezone, timedelta
from bs4 import BeautifulSoup as bs
import requests
import random
import math
import json

from keys import neis_key, dict_key
from settings import places_code

headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'}

def get_html(url):
    response = requests.get(url, verify=False, headers=headers)
    if response.status_code == 200:
        soup = bs(response.text, 'html.parser')
        return soup
    else:
        print('실패')

def get_json(url):
    response = requests.get(url, verify=False)
    if response.status_code == 200:
        json_data = response.json()
        return json_data
    else:
        print('실패', response.status_code)
        return None

def get_day():
    now_utc = datetime.now(timezone.utc)
    timestamp = now_utc.timestamp()
    now_utc_from_timestamp = datetime.utcfromtimestamp(timestamp)
    now_kst = now_utc_from_timestamp + timedelta(hours=9)
    return now_kst.strftime('%Y%m%d')

class trending:
    def zum():
        url = 'https://search.zum.com/search.zum?query=실시간%20검색어'
        soup = get_html(url)
        searching_words = []
        words = soup.select('.ranking > li > a[title]')
        for word in words:
            searching_words.append(word['title'])
        list_zum = ''
        zum = searching_words
        for i in range(len(zum)):
            list_zum += f'{i + 1}위: {zum[i]}\n'
        return list_zum

    def nate():
        list_nate = ''
        url = 'https://www.nate.com/js/data/jsonLiveKeywordDataV1.js'
        nate = get_json(url)
        for i in range(len(nate)):
            list_nate += f'{i + 1}위: {nate[i][1]}\n'
        return list_nate

    def overall():
        table = f'**[ 줌 실시간 검색어 목록 ]**\n```{trending.zum()}```\n**[ 네이트 실시간 검색어 목록 ]**\n```{trending.nate()}```'
        return table

class weather:
    def overall(place):
        atmosphere, temperature, compare = weather.atmosphere(place)
        fine_dust, ultrafine_dust = weather.fine_dust(place)
        fine_dust_level, ultrafine_dust_level, fine_dust_emoji, ultrafine_dust_emoji = weather.leveling(fine_dust, ultrafine_dust)
        text = f'현재 {place}의 날씨입니다.\n\n날씨: {atmosphere}\n온도: {temperature} {compare}\n\n미세먼지: {fine_dust_level}{fine_dust_emoji} ({fine_dust}㎍/m³)\n초미세먼지: {ultrafine_dust_level}{ultrafine_dust_emoji} ({ultrafine_dust}㎍/m³)\n\n\\* 미세먼지 수준 구분은 WHO의 8단계 기준을 사용했습니다.'
        return text
    
    def fine_dust(place):
        global places_code
        url = f'https://search.naver.com/search.naver?query={places_code[place][1]}+{place}+미세먼지'
        soup = get_html(url)
        fine_dust = soup.select('div.state_info._fine_dust._info_layer')[0].select('span.num._value')[0].text
        ultrafine_dust = soup.select('div.state_info._ultrafine_dust._info_layer')[0].select('span.num._value')[0].text
        return fine_dust, ultrafine_dust

    def atmosphere(place):
        global places_code
        place = places_code[place][0]
        url = 'https://weather.naver.com/today/{place}'
        soup = get_html(url)
        weather = soup.select('p.summary > span.weather')[0].text
        temperature = soup.select('strong.current')[0].text.replace('\n', '').replace('현재 온도', '')
        compare = soup.select('p.summary')[0].text.split('\n')[2].split(' ')[1:]
        if compare[1] == '낮아요':
            compare[1] = '낮습니다.'
        elif compare[1] == '높아요':
            compare[1] = '높습니다.'
        else:
            return weather, temperature, ''
        return weather, temperature, f'(어제보다 {compare[0]} {compare[1]})'

    def leveling(fd, ufd):
        fd_norm = [15, 30, 40, 50, 75, 100, 150, 99999999]
        ufd_norm = [8, 15, 20, 25, 37, 50, 75, 99999999]
        norm_lvl = ['최고 좋음', '좋음', '양호', '보통', '나쁨', '상당히 나쁨', '매우 나쁨', '최악']
        emoji = [':laughing:', ':smile:', ':slight_smile:', ':neutral_face:', ':slight_frown:', ':fearful:', ':sob:', ':scream:']
        for i in range(len(fd_norm)):
            if int(fd) <= fd_norm[i]:
                fd_lvl = norm_lvl[i]
                fd_emoji = emoji[i]
                break
        for i in range(len(ufd_norm)):
            if int(ufd) <= ufd_norm[i]:
                ufd_lvl = norm_lvl[i]
                ufd_emoji = emoji[i]
                break
        return fd_lvl, ufd_lvl, fd_emoji, ufd_emoji

class menu:
    def info():
        date = str((get_day()))
        school_id = ''
        url = f'https://open.neis.go.kr/hub/mealServiceDietInfo?key={neis_key}&type=json&ATPT_OFCDC_SC_CODE=C10&SD_SCHUL_CODE={school_id}&MLSV_YMD={date}'
        menu_li = get_json(url)
        try:
            lunch = menu_li['mealServiceDietInfo'][1]['row'][0]['DDISH_NM'].replace('<br/>', '\n')
            dinner = menu_li['mealServiceDietInfo'][1]['row'][1]['DDISH_NM'].replace('<br/>', '\n')
            return f'{date[4:6]}월 {date[6:]}일의 급식 정보\n\n **[ 중 식 ]**\n```{lunch}```\n**[ 석 식 ]**\n```{dinner}```'
        except:
            return f'{date[4:6]}월 {date[6:]}일, 오늘의 급식 정보가 없습니다.'
