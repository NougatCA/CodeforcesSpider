import json
import logging
import os
import random
import time
import sys
from fake_useragent import UserAgent
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

''' Proxy pool endpoints, powered by https://github.com/jhao104/proxy_pool'''
''' Attention! You should have the proxy pool service running in background!
> See the blog: https://zhuanlan.zhihu.com/p/497011455
1. Clone the project. `git clone git@github.com:jhao104/proxy_pool.git`
2. Run with docker! `docker-compose up -d`
3. You will have the services powered by proxy_pool.
> view http://127.0.0.1:5010 and see the documentation.
'''


def get_proxy():
    return requests.get("http://127.0.0.1:5010/get/").json()


def delete_proxy(proxy):
    requests.get("http://127.0.0.1:5010/delete/?proxy={}".format(proxy))


logging.basicConfig(filename="crawl.log", filemode="w", format="%(asctime)s %(name)s:%(levelname)s:%(message)s",
                    datefmt="%d-%M-%Y %H:%M:%S", level=logging.DEBUG)
# User Agent for anti-spider
ua = UserAgent()
# USER_AGENT = "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.2 (KHTML, like Gecko) Chrome/22.0.1216.0 Safari/537.2"
MAX_RETRY_COUNT = 300


def save_code(submission_id, code):
    with open(os.path.join(save_code_dir, f"{submission_id}.txt"), mode="w", encoding="utf-8") as f:
        f.write(code)


def fetch_code(contest_id, submission_id):

    url = f"https://codeforces.com/contest/{contest_id}/submission/{submission_id}"

    # Get the random ip proxy
    num_retry = 0
    while num_retry < MAX_RETRY_COUNT:
        ans = get_proxy()
        while ans.get("proxy") is None or ans.get("proxy") == "":
            ans = get_proxy()
            time.sleep(5)

        user_agent = ua.random
        if ans.get("https"):
            proxy = {"https": "https://{}".format(ans.get("proxy"))}
        else:
            proxy = {"http": "http://{}".format(ans.get("proxy"))}

        logging.info(f"Current proxy: http://{proxy}.")

        try:
            # use proxy ip for the access to the website
            response = requests.get(
                url=url,
                timeout=5,
                headers={
                    'User-Agent': user_agent
                },
                proxies=proxy
            )

            if response.status_code != 200:
                raise ValueError(f"Request status error, status code: {response.status_code}. "
                                 f"Request URL: {url}.")

            soup = BeautifulSoup(response.content, "html.parser")
            code = soup.find(id="program-source-text")
            if code is None:
                raise ValueError(f"Source code not found. url: {url}")

            code = code.text
            save_code(submission_id, code.strip())
            break

        except Exception:
            delete_proxy(proxy)
            num_retry += 1

            if num_retry > 200:
                time.sleep(20)
            elif num_retry > 100:
                time.sleep(10)
            elif num_retry > 50:
                time.sleep(5)
            else:
                time.sleep(2)


def main():

    for split_id in range_list:
        contest_submission_ids = []
        # with open(f"required/{lang}_required_split_{split_id}.jsonl", mode="r", encoding="utf-8") as f:
        with open(f"required/{lang}_required.jsonl", mode="r", encoding="utf-8") as f:
            for line in f.readlines():
                data = json.loads(line)
                submission_id = data["id"]
                contest_id = data["contest_id"]
                contest_submission_ids.append((contest_id, submission_id))

        # crawl code from website
        for contest_id, submission_id in tqdm(contest_submission_ids, ascii=True, desc=f"Split {split_id}"):
            if os.path.exists(os.path.join(save_code_dir, f"{submission_id}.txt")):
                continue
            fetch_code(contest_id=contest_id, submission_id=submission_id)
            time.sleep(2 + random.random())


if __name__ == "__main__":
    lang = sys.argv[1]
    splits = sys.argv[2]
    range_list = [int(splits)] if "-" not in splits \
        else range(int(splits.split("-")[0]), int(splits.split("-")[1]) + 1)

    save_code_dir = f"./saved_txt/{lang}"
    os.makedirs(save_code_dir, exist_ok=True)
    main()
