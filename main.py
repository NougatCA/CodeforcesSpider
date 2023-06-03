
import requests


def main():
    url = "https://codeforces.com/api/contest.status"
    params = {
        "contestId": 566,
        "from": 1,
        "count": 10
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
    else:
        raise ValueError(f"Request status error, status code: {response.status_code}. "
                         f"Request URL: {url}, parameters: {params}")

    if data["status"] != "OK":
        raise ValueError(f"Response status error, status: {data['status']}, "
                         f"comment: {data['comment']}. Request URL: {url}, parameters: {params}")

    submissions = data["result"]
    


if __name__ == "__main__":
    main()
