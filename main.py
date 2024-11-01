import os
import time
import httpx
import json

headers = {
    "authority": "api.fanbox.cc",
    "accept": "application/json, text/plain, */*",
    "accept-language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
    "cache-control": "no-cache",
    "cookie": "your_cookies",
    "dnt": "1",
    "origin": "https://www.fanbox.cc",
    "pragma": "no-cache",
    "referer": "https://www.fanbox.cc/",
    "sec-ch-ua": '" Not;A Brand";v="99", "Microsoft Edge";v="103", "Chromium";v="103"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.53 Safari/537.36 Edg/103.0.1264.37",
}


def save_data(json_data, post_id, title, text, images, cover_image, proxy):
    PATH = f"posts/{post_id}_{title}"
    
    if os.path.exists(PATH) == False:
        os.makedirs(PATH)

    file = open(f"{PATH}/data.json", "w", encoding="utf-8")
    file.write(json.dumps(json_data))
    file.close

    if len(text) > 0:
        file = open(f"{PATH}/{title}.md", "w", encoding="utf-8")
        file.write(f"## {title} \n {text}")
        file.close()

    if cover_image != None:
        file = open(f"{PATH}/cover_image.jpg", "wb")
        pic = httpx.get(url=cover_image, headers=headers, proxy=proxy)
        file.write(pic.content)
        file.close()

    if len(images) > 0:
        img_path = f"{PATH}/images"
        if os.path.exists(img_path) == False:
            os.makedirs(img_path)
        for image in images:
            filename = f'{image["id"]}.{image["extension"]}'
            url = image["originalUrl"]
            pic = httpx.get(url=url, headers=headers, proxy=proxy)
            file = open(f"{img_path}/{filename}", "wb")
            file.write(pic.content)
            file.close()


def getpost(id, proxy):
    url = f"https://api.fanbox.cc/post.info?postId={id}"
    r = httpx.get(url=url, headers=headers, proxy=proxy)
    if r.status_code != 200:
        print(f"Error: Faild at HTTP GET {id}")
    json = r.json()
    body = json["body"]
    title = body.get("title", f"POST{id}")
    cover_image = body.get("coverImageUrl", None)
    body2 = body.get("body", {})

    text = body2.get("text", "")
    images = body2.get("images", [])
    blocks = body2.get("blocks", [])
    for block in blocks:
        if block["type"] == "p":
            text = text + str(block["text"]) + "\n"

    imageMap = body2.get("", {})
    for image in imageMap:
        images.append(imageMap[image])

    save_data(json, id, title, text, images, cover_image, proxy=proxy)
    print(f"SUCCESS: {id} {title}")

    next_post = body.get("nextPost", None)
    if next_post is not None:
        return next_post.get("id", None)


def main():
    with open("config.json") as config_json:
        config = json.load(config_json)
        start_id = config.get("start_id", 1)
        sleep_time = config.get("sleep_time", 10)
        cookies = config.get("cookies", None)
        if config is None:
            print("ERROR, cookes is required")
            exit(0)
        else:
            headers["cookie"] = cookies

        proxy = config.get("proxy", None)

        while start_id != None:
            time.sleep(sleep_time)
            try:
                start_id = getpost(start_id, proxy=proxy)
            except Exception as e:
                print(e)
                print(f"Retry {start_id}")
                continue


if __name__ == "__main__":
    main()
