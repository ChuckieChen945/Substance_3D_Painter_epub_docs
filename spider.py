# -*- coding: utf-8 -*-
'''
'''

import datetime
import json
import ssl
import time
import warnings
import msvcrt

import requests
import os, re
from urllib.parse import urljoin
from pyquery import PyQuery as pq



ssl._create_default_https_context = ssl._create_unverified_context
warnings.filterwarnings("ignore")

def get_input_in_one_second(timeout=0.5):
    """
    获取一秒钟内的用户输入。只在windows Terminal中有效，在pyCharm Terminal中无效
    """
    start_time = time.time()
    input = ''
    while True:
        if msvcrt.kbhit():
            char = msvcrt.getch().decode('utf-8')
            if char == '\r':  # 如果输入回车键，结束输入
                break
            else:
                input += char
        if (time.time() - start_time) > timeout:
            break
    return input


def write_log(log_file, content, with_time=True, mode='a+', print_line=True):
    # 输出日志
    if print_line:
        print(content)
    file_path = get_file_path(log_file)
    if not os.path.exists(os.path.join(os.getcwd(), file_path)):
        os.makedirs(file_path)
    with open(log_file, mode, encoding='utf-8') as f:
        if with_time:
            f.write(f'输出时间：{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} {content}')
        else:
            f.write(content)

        f.close()


def get_file_path(full_path):
    # 根据文件路径，获取所在目录
    """
    根据文件名称获取目录
    :param full_path:
    :return:
    """
    return full_path[0:full_path.rfind(os.path.sep) + 1]



def clean_filename(filename):
    # 定义无效字符的正则表达式
    invalid_chars = r'[\\/:*?"<>|]'
    # 使用正则表达式替换无效字符为空字符
    cleaned_filename = re.sub(invalid_chars, '', filename)
    return cleaned_filename



def download_file(file_path, download_url, headers={}, check_exists=True):
    # 下载文件
    print('*' * 100)
    if os.path.exists(file_path) and check_exists:
        print(file_path, '文件已存在')
        return False
    print(f"保存路径：{file_path}")
    rindex1 = file_path.rfind(os.path.sep)
    rindex2 = file_path.rfind('/')
    rindex = rindex1 if rindex1 > rindex2 else rindex2
    file_folder = file_path[0:rindex + 1]
    # print(file_folder)
    if not os.path.exists(file_folder) and file_folder != '':
        os.makedirs(file_folder)
    # print(f'下载URL：{download_url}')
    try:
        response = requests.get(url=download_url, headers=headers, stream=True, timeout=600, verify=False)
        response.encoding = 'utf-8'
    except Exception as e:
        print(str(e))
        return False
    else:
        try:
            if not response.status_code == 200:
                print(download_url, f'响应码为{response.status_code}')
                return None
            # print(response.headers)
            if not "content-length" in response.headers.keys():
                # print(download_url, '下载失败')
                # return None
                content_size = len(response.content)
            else:
                content_size = int(response.headers["content-length"])
            size = 0
            with open(file_path, "ab+") as file:
                for data in response.iter_content(chunk_size=1024):
                    file.write(data)
                    file.flush()
                    size += len(data)
                    print("\r文件下载进度:%d%%(%0.2fMB/%0.2fMB)" % (
                        float(size / content_size * 100), (size / 1024 / 1024),
                        (content_size / 1024 / 1024)),
                          end=" ")
            print()
            return True
        except:
            return False



class DzSpider(object):
    def __init__(self):
        self.folder = fr'{os.getcwd()}'
        self.spider_num = 1
        self.req_url = 'https://helpx.adobe.com/'
        self.headers_str = '''
accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
accept-encoding: gzip, deflate, br, zstd
accept-language: zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6
cache-control: max-age=0
cookie: reba_sid=c80540e2-b4c2-479f-843f-844f555ef2f0; OptanonAlertBoxClosed=2024-10-29T07:01:54.639Z; OptanonConsent=groups=C0001%3A1%2CC0002%3A1%2CC0003%3A1%2CC0004%3A1; _fbp=fb.1.1730619522655.289889027; AMCVS_D6FAAFAD54CA9F560A4C98A5%40AdobeOrg=1; OptanonChoice=1; AMCVS_9E1005A551ED61CA0A490D45%40AdobeOrg=1; s_cc=true; adobeHit=3; kndctr_9E1005A551ED61CA0A490D45_AdobeOrg_identity=CiYxMTgzNTM3MjE4NDkwMDI5NTgxMjQ3Mzc5MDQ1MjAxODYzMjAwMVIRCLuMk6azMhgBKgRJUkwxMAPwAbuMk6azMg%3D%3D; kndctr_9E1005A551ED61CA0A490D45_AdobeOrg_consent=general%3Din; RDC=AVAwZZnmYIadvgKwJ5lwM6ngF71gWeEMjTeh7ffm-vmV-TRT9ome0lq946I-A-LDdrtmAJeKAAtJptfU1i4p94jRGlNgH6wnJZVTlew9K7R229FZ6St-ljiFGjW8quJeDr9hiKB670ADl7CBsObVLPh47nTI; international=cn; creative-cloud-loc=en-US; s_sq=%5B%5BB%5D%5D; fltk=segID%3D13330890; _rdt_uuid=1731757142010.9911fbbf-2cca-4631-873d-6432ee22a5bd; s_ppv=[%22community.adobe.com/t5/substance-3d-painter/ct-p/ct-substance-3d-painter%22%2C30%2C0%2C1042.7272644042969%2C1489%2C770%2C1646%2C926%2C1.92%2C%22P%22]; reba_sid=062ca3f4-5e06-4d4d-bf3d-cc061b5b2781; AMCV_D6FAAFAD54CA9F560A4C98A5%40AdobeOrg=-637568504%7CMCIDTS%7C20044%7CMCMID%7C60680055392613408808702842433208429816%7CMCOPTOUT-1731811025s%7CNONE%7CvVersion%7C5.1.1%7CMCAAMLH-1732408625%7C11%7CMCAAMB-1732408625%7Cj8Odv6LonN4r3an7LhD3WZrU1bUpAkFkkiY1ncBR96t2PTI%7CMCSYNCSOP%7C411-20052; creative-cloud-referrer=; _cs_c=0; _gcl_au=1.1.1589557855.1731805860; _mkto_trk=id:360-KCI-804&token:_mch-adobe.com-8530d8f9a5ba487212e39e2c2f9cf2d0; _scid=r1Xy26GkXTLf0tWH8ega2MVqvlbljvLC; _ScCbts=%5B%5D; _sctr=1%7C1731772800000; _scid_r=utXy26GkXTLf0tWH8ega2MVqvlbljvLCvNAnGQ; _uetsid=ce42b760a48011ef9f95c7e71987c615; _uetvid=ce42b0c0a48011ef8c5913bb02e349c5; AMCV_9E1005A551ED61CA0A490D45%40AdobeOrg=1585540135%7CMCMID%7C11835372184900295812473790452018632001%7CMCAID%7CNONE%7CMCOPTOUT-1731814763s%7CNONE%7CvVersion%7C4.4.0%7CMCIDTS%7C20044; mbox=session%2311835372184900295812473790452018632001%2DdqkwiW%231731809798; acomsis=1; ak_bmsc=1B60B64ABEFF7A4E7DCAE3794DA41919~000000000000000000000000000000~YAAQV0XcF9O88CaTAQAALCzuNxlKPk4Y0lMVIbN/2Zj3GMCGWREiLvOuUvZRO+tw8IcNfkXn6B4enuOa0GUUZVTvZnfGi3xkGevAKJbHTFilDEHMtFGX/CSNF+FJvmnI42ANPGMSwvOv3o1jxN0xac7834VCDJMhgWv9fcQrNpwz7fnuY1oskPWmM3DjIQxPwMz9YW9TH0ADpDtnExTaYgV7yFLPv3dDNMGhUPYlXcrBJ6wwAnZYDZFMNZMaTR5+4poJs4Rlmjrr0ouH4PmZRR/JQHE38/N7FISwoIENfOnoS4taIHrn5EVDj4pszFsvJaM2kC1WcXTgq26Ys0FyGkdf33qTnsV+nTQ/Fhhs55IeRmIpT66JILSiSaCxbCSO2gAqfu23a0KC6A==; fg=Y6VO4SCWVPP54HEKXMQV4HAAII======; aux_sid=ASEXRfG7UorqNPlSRZuIQZwLYJO33Ngc2NlhNSAXjvhX7alTOyB-kF09fSKYaFjhGCgwXFi4Wz4Z5dG3XW9yMvav7AMRX_VRT0HMXKwp6brVblCtA3Fw2YOG9oFUdoKYGmyyPI0hn0H1ioh3uoSPeAJymG_fW_PQYR7m3dxD9oR1fA1P0bClm9ilBI__cMGZPyyyjF_PFSG43fmSgZ7qb63zPAoFZfuuXuei-oDwz6qO7afhfPg4WRxeEkcuWzqhqpafOm-d3N5FV59wPvrte5gqhk_ukbB1vaYV7TdHiJG08L_lsjptExoYRIS2U8fAGK7PE46jDSOC37rMaGodmhypEZ3kOH3d571QWRG3bpKPxMzBn6GNER9cbMvDFLHd5kKaDKAA24YMTzq-s3M4IF2hBvWLn7O21rQkTtmgq3svh8UhA7p0_Zz2EvoYFYmuYyuZ5E6T6yiwwv9e-FBe50szFUsCXoZMIaZIBL9touuJetA1DE0YZNDPTxCAfrgIrO9BCAPN_I4ji5nuL-K8B7GealBsU7bjZJVUG_1hDqp8VGF2IbHjGSDxtHET9SitHnMEEg3_bGLn7_APc3PNdP-Jq5rbQKZ_eGJ3DrcOEgpMkpcMwIeH1VlaZjz3nB_3gkBvQx48FSzc66RwF99QIfmxNDkkD6Sd8r1CwDMPqsS_yJT5UeqqqQqvn06QgCeAAFNUlWqHBPE4NCfQJSJYM6kDJ9hNV2zgUvPNdOJmged5NdK3XvuLb07eh1Ve9gQlXfx7QsoZ5SiQvUKkUgMyoQnWhMVwUg; bm_sv=16E01B1DF2AB86319393BE58A7FB13BE~YAAQUEXcF67lUCiTAQAAaEfuNxnm+fl4GJQg8s3r7YwQiqefhuiwmakCqZFIsK4gposy4EPpEhd+TvF0oA/gMa8ac4Lu07FNndSM/tAq2pZTLm/8w0yH80ZzkYIKV67sAZNQIFkoEgdOtz4tVGDUhnIwrt6ydDt4+rCM5OhViRCMksFUlSgDmlD7J14venA2rQmQb6pkxyAR9iIUZ00Aa4vpOtJA4CQCuSEYLXRa61K1GGEHKzbM1xDDg9d7Eww=~1; s_nr=1731810182648-Repeat; akaas_helpx_audience_segmentation_default=1733019784~rv=83~id=a12e7f14728d58eb8eba4a2ff14bbb9c~rn=; QSI_S_ZN_3n5vYIa1VY8b4LY=r:12:66; _cs_id=fbf0d513-49c1-a6e8-e267-407f01f46425.1731805859.1.1731810190.1731805859.1717775740.1765969859708.1; _cs_s=24.0.0.1731814801006
priority: u=0, i
sec-ch-ua: "Chromium";v="130", "Microsoft Edge";v="130", "Not?A_Brand";v="99"
sec-ch-ua-mobile: ?0
sec-ch-ua-platform: "Windows"
sec-fetch-dest: document
sec-fetch-mode: navigate
sec-fetch-site: none
sec-fetch-user: ?1
upgrade-insecure-requests: 1
user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0
            '''
        self.headers = dict(
            [[y.strip() for y in x.strip().split(':', 1)] for x in self.headers_str.strip().split('\n') if x.strip()])

    def run_task(self):

        with open('./toc.html','r',encoding='utf-8' ) as f:
            html= f.read()
        doc = pq(html)

        # Start parsing from the root list
        root_items = doc(".tableOfContents-list > li")
        self.get_content(root_items)

        # # 一秒内输入‘p’则暂停程序.不能用q来判断，q会和ffmpeg的退出命令重合
        # keyboard_input = get_input_in_one_second()
        # if 'l' in keyboard_input:
        #     user_input = input("输入任意内容并按回车继续：")
        # continue

    def get_content(self, items, level=1):

        for item in items:
            toc_item = pq(item)
            link = toc_item.children(".tocLink-label")
            if link:
                title = link.find(".tocLink-line-item").text().strip()
                href = link.attr("href")
                # 如果链接不为空，说明有内容，则下载html
                # 有一个'.tocLinkNA'节点的href为'#',忽略这个节点
                if href and href!= '#':
                    item_link = urljoin(self.req_url, href)
                    print(f'========================================\n'
                        f'第{self.spider_num}条\n'
                        f'{title}\n'
                        f'{item_link}\n')
                        # f'========================================\n')
                    self.download_html(href, item_link)
                    self.spider_num += 1
            
            # Check for children
            # 如果有子节点，继续获取内容
            sub_items = toc_item.find("ol.subLink-items > li")
            if sub_items:
                self.get_content(sub_items, level + 1)

    def download_html(self, file_name, link):
        # file_name = clean_filename(file_name)
        html_folder = fr'{self.folder}{os.path.sep}html'
        if os.path.exists(fr'{html_folder}{file_name}'):
            print(fr'***页面已存在:{html_folder}{file_name}')
            return
        try:
            # html = requests.get(link, headers=self.headers, timeout=10).text
            html = requests.get(link, timeout=10).text
        except:
            time.sleep(2)
            self.download_html(file_name,link)
            return
        # 删除页面无关元素等
        print('html获取完成')
        pq_html = pq(html)
        pq_html('.globalnavheader').remove()
        pq_html('.legalNotices').remove()
        pq_html('.feedback').remove()
        pq_html('.helpxFooter').remove()
        pq_html('.globalnavfooter').remove()

        pq_html('.titleBar').remove()
        pq_html('.internalBanner').remove()
        pq_html('.dexter-FlexContainer-Items').children().eq(1).remove()
        # 因为删一次后次序会发生变化，所以第二次删的还是eq(1)，
        pq_html('.dexter-FlexContainer-Items').children().eq(1).remove()
        pq_html('.modalContainer.parsys').eq(1).remove()
        pq_html('.modalContainer.static').eq(1).remove()
        pq_html('.toc').remove()
        html = self.correct_urls(pq_html, link,file_name.count('/'))

        print('图片等下载完成')
        if not os.path.exists(html_folder):
            os.makedirs(html_folder)

        if not os.path.exists(fr'{html_folder}{file_name}'):
            directory = os.path.dirname(fr'{html_folder}{file_name}')
            os.makedirs(directory, exist_ok=True)
            write_log(fr'{html_folder}{file_name}', html, with_time=False, print_line=False)
        print('保存成功')

    def correct_urls(self, pq_html, base_url,n):
        # 处理html页面中的链接及图片信息
        # doc('meta[name="helpsystempath"]').remove()

        for a in pq_html('a').items():
            href = a.attr('href')
            if href and not href.startswith('http'):
                a.attr('href', urljoin(base_url, href))

        # TODO:将下载到的文件按原链接的目录结构存放在硬盘上
        for a in pq_html('img').items():
            href = a.attr('src')
            if href:
                img_name = self.replace_url_and_download_file(href,base_url,'images')
                a.attr('src', '../'*n+f'images/{img_name}')

        for a in pq_html('link').items():
            href = a.attr('href')
            if href:
                style_name = self.replace_url_and_download_file(href,base_url,'style')
                a.attr('href', '../'*n+f'style/{style_name}')

        for a in pq_html('script').items():
            href = a.attr('src')
            if href:
                script_name = self.replace_url_and_download_file(href,base_url,'scripts')
                a.attr('src','../'*n+f'scripts/{script_name}')

        return pq_html.outer_html()

    def replace_url_and_download_file(self, raw_url, base_url, path):

        if not raw_url.startswith('http'):
            download_url = urljoin(base_url, raw_url)
        elif raw_url.startswith('http'):
            download_url = raw_url

        file_name = clean_filename(download_url[download_url.rfind('/')+1:])
        save_name = fr'{self.folder}{os.path.sep}{path}{os.path.sep}{file_name}'
        download_file(save_name,download_url)
        return file_name

if __name__ == '__main__':
    spider = DzSpider()
    spider.run_task()

'''
安装python以下模块：
requests
pyquery
'''

