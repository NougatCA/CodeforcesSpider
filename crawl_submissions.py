import time
import requests
import os
import json
from tqdm import tqdm


def main():
    # directory to save crawled data
    output_root = "../crawled-codeforces-contest/"
    if not os.path.exists(output_root):
        os.makedirs(output_root)

    # codeforces api
    url = "https://codeforces.com/api/contest.status"
    # fetch by contest id
    for contest_id in tqdm(range(10, 1845), ascii=True):
    # for contest_id in ["1837"]:

        # print(f"********** CONTEST {contest_id} **********")
        # print(f"Fetching submissions...")

        params = {
            "contestId": contest_id,
            # "from": 1,
            # "count": 100
        }

        response = requests.get(url, params=params)
        if response.status_code != 200:
            print(f"Request status error, status code: {response.status_code}. "
                  f"Request URL: {url}, parameters: {params}")
            continue
        data = response.json()

        if data["status"] != "OK":
            print(f"Response status error, status: {data['status']}, "
                  f"comment: {data['comment']}. Request URL: {url}, parameters: {params}")
            continue

        # result is a list of submission jsons
        # https://codeforces.com/apiHelp/objects#Submission
        submissions = data["result"]
        # only needs accepted submissions
        ok_submissions = [submission for submission in submissions if submission["verdict"] == "OK"]
        # print(f"Submissions fetched, accepted submissions: {len(ok_submissions)}")

        # save submission information
        output_dir = os.path.join(output_root, str(contest_id))
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        idx_to_submissions = {}
        for submission in ok_submissions:
            contest_idx = submission["problem"]["index"]
            if contest_idx in idx_to_submissions:
                idx_to_submissions[contest_idx].append(submission)
            else:
                idx_to_submissions[contest_idx] = [submission]
        # with open(os.path.join(output_dir, f"{contest_id}_submissions.jsonl"), mode="w", encoding="utf-8") as f:
        #     for submission in ok_submissions:
        #         line = json.dumps(submission)
        #         f.write(line)
        #         f.write("\n")
        #         contest_idx = submission["problem"]["index"]
        #         if contest_idx in idx_to_submissions:
        #             idx_to_submissions[contest_idx].append(submission)
        #         else:
        #             idx_to_submissions[contest_idx] = [submission]

        for contest_idx, submissions in idx_to_submissions.items():
            with open(os.path.join(output_dir, f"{contest_id}_{contest_idx}_submissions.jsonl"),
                      mode="w", encoding="utf-8") as f:
                for submission in submissions:
                    line = json.dumps(submission)
                    f.write(line)
                    f.write("\n")

        # print(f"Submissions saved")

        time.sleep(1.5)


if __name__ == "__main__":
    main()
