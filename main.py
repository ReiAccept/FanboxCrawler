import os
import time
import httpx

headers = {
    'authority': 'api.fanbox.cc',
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
    'cache-control': 'no-cache',
    'cookie': '在这里填入你的Cookies',
    'dnt': '1',
    'origin': 'https://www.fanbox.cc',
    'pragma': 'no-cache',
    'referer': 'https://www.fanbox.cc/',
    'sec-ch-ua': '" Not;A Brand";v="99", "Microsoft Edge";v="103", "Chromium";v="103"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.53 Safari/537.36 Edg/103.0.1264.37',
}


def save_data(title: str, text: str, images, cover_image: str):
    if os.path.exists(title) == False:
        os.makedirs(title)
    file = open(f'{title}/{title}.md', 'w', encoding='utf-8')
    file.write(f'## {title} \n {text}')
    file.close()
    if cover_image != None:
        file = open(f'{title}/cover_image.jpg', 'wb')
        pic = httpx.get(url=cover_image, headers=headers)
        file.write(pic.content)
        file.close()
    if images != None:
        img_path = f'{title}/images'
        if os.path.exists(img_path) == False:
            os.makedirs(img_path)
        for image in images:
            filename = f'{image["id"]}.{image["extension"]}'
            url = image['originalUrl']
            pic = httpx.get(url=url, headers=headers)
            file = open(f'{img_path}/{filename}', 'wb')
            file.write(pic.content)
            file.close()


def getpost(id: str):
    url = f'https://api.fanbox.cc/post.info?postId={id}'
    r = httpx.get(url=url, headers=headers)
    json = r.json
    body = json()['body']
    title = body['title']
    try:
        text = body['body']['text']
    except:
        text = None
    try:
        images = body['body']['images']
    except:
        images = None
    try:
        cover_image = body['coverImageUrl']
    except:
        cover_image = None
    if text == None and images == None:
        print(f'SKIP {id} {title}')
    else:
        save_data(title, text, images, cover_image)
        print(f'{title} OK')
    return body['nextPost']['id']


def main():
    id = '在这里填入你要爬取的作者的第一篇文章的ID'
    while id != None:
        time.sleep(1)
        try:
            id = getpost(id)
        except :
            print(f'Retry {id}')
            continue


main()
