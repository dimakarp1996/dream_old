import requests


def main():
    url = "http://0.0.0.0:8018/badlisted_words"

    request_data = {
        "sentences": ["any fucks in this sentence", "good one", "fucked one"],
    }

    result = requests.post(url, json=request_data).json()[0]
    gold_result = {
        "bad_words": [True, False, True],
    }

    assert result == gold_result, f"Got\n{result}\n, but expected:\n{gold_result}"
    print("Success")


if __name__ == "__main__":
    main()
