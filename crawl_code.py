import json
import time
import os

import requests
import re
import html
from tqdm import tqdm


CODE_START_PATTERN = r"<pre id=\"program-source-text\" class=\"prettyprint.+?program-source\" style=\"padding: 0\.5em;\">"


def fetch_code(contest_id, submission_id) -> str:
    url = f"https://codeforces.com/contest/{contest_id}/submission/{submission_id}"
    response = requests.get(url=url)
    if response.status_code != 200:
        raise ValueError(f"Request status error, status code: {response.status_code}. "
                         f"Request URL: {url}.")
    content = response.text

    match = re.search(CODE_START_PATTERN, content)
    if match is None:
        raise ValueError(f"Source code not found. url: {url}")
    start_pos = match.end()
    end_pos = content.find("</pre>", start_pos)
    result = content[start_pos: end_pos]
    code = html.unescape(result)

    return code


def main():

    langs = ["C++", "Java", "Python", "Rust"]

    save_code_dir = "./saved/"
    os.makedirs(save_code_dir, exist_ok=True)

    for lang in langs:

        # load all submissions
        all_submissions = []
        with open(f"{lang}_required.jsonl", mode="r", encoding="utf-8") as f:
            for line in f.readlines():
                data = json.loads(line)
                all_submissions.append(data)

        # crawl code from website
        with open(os.path.join(save_code_dir, f"{lang}_code.jsonl"), mode="w", encoding="utf-8") as f:
            for submission in all_submissions:
                submission_id = submission["id"]
                contest_id = submission["contest_id"]

                code = fetch_code(contest_id=contest_id, submission_id=submission_id)

                data = {
                    "id": submission_id,
                    "contest_id": contest_id,
                    "source_code": code.strip()
                }

                f.write(json.dumps(data))
                f.write("\n")


if __name__ == "__main__":
    main()
