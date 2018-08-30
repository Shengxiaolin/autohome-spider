import requests
from bs4 import BeautifulSoup
from downloader import ProgressBar
import os
from contextlib import closing

# url = 'https://www.autohome.com.cn/grade/carhtml/A.html'

def CarInfo():

    brand_url = 'http://www.autohome.com.cn/ashx/AjaxIndexCarFind.ashx?type=1'
    series_url = 'http://www.autohome.com.cn/ashx/AjaxIndexCarFind.ashx?type=3&value={}'
    # car_url = 'https://car.autohome.com.cn/pic/series/{}-1-p{}.html'  # 在售车型
    car_url = 'https://car.autohome.com.cn/pic/series-t/{}-1-p{}.html'  # 停产车型

    brand_json = requests.get(brand_url).json()
    for brand in brand_json['result']['branditems'][22:]:
        car_info = dict()
        car_info['brand name'] = brand['name']
        series_json = requests.get(series_url.format(brand['id'])).json()
        for factory in series_json['result']['factoryitems']:
            car_info['factory name'] = factory['name']
            for series in factory['seriesitems']:
                # car_info['car id'] = series['id']
                car_info['car name'] = series['name']
                page = 1
                while True:
                    car_html = requests.get(car_url.format(series['id'], page)).text
                    div_bs = BeautifulSoup(car_html, 'lxml')
                    # div = div_bs.findAll('div', attrs={'class': 'uibox-con carpic-list03 border-b-solid'})  #在售车型
                    div = div_bs.findAll('div', attrs={'class': 'uibox-con carpic-list03'})  # 停产车型
                    images_bs = BeautifulSoup(str(div), 'lxml')
                    images = images_bs.findAll('img')

                    if len(images) == 0:
                        break

                    for image in images:
                        car_info['car detail'] = image['title'].strip(' ')
                        car_info['pic'] = image['src'].replace('t_', '1024x0_1_q87_', 1)
                        yield car_info
                    page += 1


if __name__ == '__main__':

    dir_format = 'E:\\autohome-t\\{}\\{}\\{}\\{}'

    for car in CarInfo():
        url = 'http:{}'.format(car['pic'])
        dirname = dir_format.format(car['brand name'],
                                    car['factory name'],
                                    car['car name'],
                                    car['car detail'],
                                    car['pic'])
        filename = os.path.join(dirname, car['pic'].split('/')[-1])

        if os.path.exists(dirname) is False:
            os.makedirs(dirname)

        if os.path.exists(filename) is True:
            print('{} is existed.'.format(filename))
            continue

        with closing(requests.get(url, stream=True)) as response:
            chunk_size = 1024
            content_size = int(response.headers['content-length'])
            if response.status_code == 200:
                progress = ProgressBar("%s下载进度" % filename
                                       , total=content_size
                                       , unit="KB"
                                       , chunk_size=chunk_size
                                       , run_status="正在下载"
                                       , fin_status="下载完成")

                with open(filename, 'wb') as file:
                    for data in response.iter_content(chunk_size=chunk_size):
                        file.write(data)
                        progress.refresh(count=len(data))

            else:
                print('链接异常:', url)






