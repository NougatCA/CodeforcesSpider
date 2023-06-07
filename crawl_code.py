import html
import json
import logging
import os
import re
import time

import requests
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
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.57'
}
MAX_RETRY_CNT = 500
CODE_START_PATTERN = r"<pre id=\"program-source-text\" class=\"prettyprint.+?program-source\" style=\"padding: 0\.5em;\">"


def fetch_code(contest_id, submission_id) -> str:
    url = f"https://codeforces.com/contest/{contest_id}/submission/{submission_id}"

    # Get the random ip proxy
    proxy = get_proxy().get("proxy")
    logging.info(f"Current proxy: http://{proxy}.")
    retry_count = MAX_RETRY_CNT
    match = None
    code = None
    while retry_count > 0:
        try:
            # use proxy ip for the access to the website
            response = requests.get(
                url=url, timeout=5, headers=HEADERS, proxies={"http": "http://{}".format(proxy)})

            if response.status_code != 200:
                # renew proxy
                delete_proxy(proxy)
                proxy = get_proxy().get("proxy")
                logging.warning(f"Retry proxy: http://{proxy}.")
                raise ValueError(f"Request status error, status code: {response.status_code}. "
                                 f"Request URL: {url}.")
            content = response.text

            match = re.search(CODE_START_PATTERN, content)
            if match is None:
                # renew proxy
                delete_proxy(proxy)
                proxy = get_proxy().get("proxy")
                logging.warning(f"Retry proxy: http://{proxy}.")
                raise ValueError(f"Source code not found. url: {url}")

            start_pos = match.end()
            end_pos = content.find("</pre>", start_pos)
            result = content[start_pos: end_pos]
            code = html.unescape(result)
            return code

        except Exception:
            retry_count -= 1

    # delete broken proxy ip address
    delete_proxy(proxy)
    raise ValueError(
        f"Failed after {MAX_RETRY_CNT} times retry. url: {url}")
    return None


def main():

    # langs = ["C++", "Java", "Python", "Rust"]
    langs = ["Rust"]

    save_code_dir = "./saved/"
    os.makedirs(save_code_dir, exist_ok=True)

    for lang in langs:
        print(f"********** {lang} **********")

        # load all submissions
        all_submissions = []
        with open(f"{lang}_required.jsonl", mode="r", encoding="utf-8") as f:
            for line in f.readlines():
                data = json.loads(line)
                all_submissions.append(data)

        # crawl code from website
        with open(os.path.join(save_code_dir, f"{lang}_code.jsonl"), mode="a", encoding="utf-8", buffering=1) as f:
            for submission in tqdm(all_submissions, ascii=True):
                submission_id = submission["id"]
                contest_id = submission["contest_id"]

                code = fetch_code(contest_id=contest_id,
                                  submission_id=submission_id)

                data = {
                    "id": submission_id,
                    "contest_id": contest_id,
                    "source_code": code.strip()
                }

                f.write(json.dumps(data))
                f.write("\n")


if __name__ == "__main__":
    main()