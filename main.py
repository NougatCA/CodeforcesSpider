
import requests
import re
import os
import json
from tqdm import tqdm
import html


CODE_START_PATTERN = r'<pre id="program-source-text" class="prettyprint .*?program-source" style="padding: 0\.5em;">'
SYMBOL_REPLACEMENT = {
    "&quot;": "\"",
    "&gt;": ">",
    "&lt;": "<",
    "&amp;": "&",
    "&apos;": "'",
    "&#39;": "'"
}


def fetch_code(contest_id, submission_id) -> str:
    url = f"https://codeforces.com/contest/{contest_id}/submission/{submission_id}"
    response = requests.get(url=url)
    if response.status_code != 200:
        raise ValueError(f"Request status error, status code: {response.status_code}. "
                         f"Request URL: {url}.")
    content = response.text

    start_pos = re.search(CODE_START_PATTERN, content).end()
    end_pos = content.find("</pre>", start_pos)
    result = content[start_pos: end_pos]
    # for key, value in SYMBOL_REPLACEMENT.items():
    #     result = result.replace(key, value)
    code = html.unescape(result)

    return code


def main():
    # directory to save crawled data
    output_root = "../codeforces-contest/"
    if not os.path.exists(output_root):
        os.makedirs(output_root)

    # codeforces api
    url = "https://codeforces.com/api/contest.status"
    # fetch by contest id
    for contest_id in ["566"]:

        print(f"********** CONTEST {contest_id} **********")
        print(f"Fetching submissions...")

        params = {
            "contestId": contest_id,
            # "from": 1,
            # "count": 100
        }

        response = requests.get(url, params=params)
        if response.status_code != 200:
            raise ValueError(f"Request status error, status code: {response.status_code}. "
                             f"Request URL: {url}, parameters: {params}")
        data = response.json()

        if data["status"] != "OK":
            raise ValueError(f"Response status error, status: {data['status']}, "
                             f"comment: {data['comment']}. Request URL: {url}, parameters: {params}")

        # result is a list of submission jsons
        # https://codeforces.com/apiHelp/objects#Submission
        submissions = data["result"]
        # only needs accepted submissions
        ok_submissions = [submission for submission in submissions if submission["verdict"] == "OK"]
        print(f"Submissions fetched, accepted submissions: {len(ok_submissions)}")

        # save submission information
        output_dir = os.path.join(output_root, contest_id)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        submission_path = os.path.join(output_dir, f"{contest_id}_submissions.jsonl")
        with open(submission_path, mode="w", encoding="utf-8") as f:
            for submission in ok_submissions:
                line = json.dumps(submission)
                f.write(line)
                f.write("\n")
        print(f"Submissions saved to {submission_path}")

        # fetch source code
        # code_dir = os.path.join(output_dir, "code")
        # if not os.path.exists(code_dir):
        #     os.makedirs(code_dir)
        # for submission in tqdm(ok_submissions, desc="Downloading code", ascii=True):
        #     submission_id = submission["id"]
        #     code = fetch_code(contest_id=contest_id, submission_id=submission_id)
        #     with open(os.path.join(code_dir, f"{submission_id}.txt"), mode="w", encoding="utf-8") as f:
        #         f.write(code)
        #
        # print(f"Code saved")


if __name__ == "__main__":
    main()
