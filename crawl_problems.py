import time
import requests
import os
import json


def main():
    # directory to save crawled data
    output_root = "../datasets/"

    # codeforces api
    url = "https://codeforces.com/api/problemset.problems"

    response = requests.get(url)
    if response.status_code != 200:
        raise ValueError(f"Request status error, status code: {response.status_code}. "
              f"Request URL: {url}.")
    data = response.json()

    if data["status"] != "OK":
        raise ValueError(f"Response status error, status: {data['status']}, "
              f"comment: {data['comment']}. Request URL: {url}.")

    # https://codeforces.com/apiHelp/methods#problemset.problems
    problems = data["result"]["problems"]

    # save problem information
    output_path = os.path.join(output_root, "problems.jsonl")
    with open(output_path, mode="w", encoding="utf-8") as f:
        for problem in problems:
            f.write(json.dumps(problem))
            f.write("\n")

    print(f"Problems saved")


if __name__ == "__main__":
    main()
