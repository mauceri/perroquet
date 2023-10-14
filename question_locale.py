import requests
import sys

def test_server(questions):
    #url = "https://mauceri--llama-cpp-python-nu-fastapi-app-dev.modal.run"
    url = "http://127.0.0.1:8000"

    for question in questions:
        print(f"Question: {question}")
        response = requests.post(f"{url}/question", json={"prompt": question})
        print(f'Response: {response.json()["choices"][0]["text"]}')

if __name__ == "__main__":
    questions = [line.strip() for line in sys.stdin]
    test_server(questions)
