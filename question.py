from collections import deque
import requests
import sys

class ChatHistory:
    def __init__(self, msg_limit):
        self.stack = deque(maxlen=msg_limit)

    def append(self, msg):
        return self.stack.append(msg)

    def get_as_list(self):
        return list(self.stack)

    def get_as_string(self):
        res = ""
        for e in self.get_as_list():
            res +=  e + "\n"
        return res

h = ChatHistory(5)

def test_server(questions):
    #url = "https://mauceri--llama-cpp-python-nu-fastapi-app-dev.modal.run"
    url = "https://mauceri--llama-cpp-python-nu-fastapi-app.modal.run"
    for question in questions:
        print(f"Longueur historique : {len(h.get_as_string())}")
        print(f"Question: {question}, historique: {h.get_as_string()}")
        response = requests.post(f"{url}/question", json={"prompt": question,"context":h.get_as_string()})
        print(f'Response: {response.json()["choices"][0]["text"]}')
        h.append(f"<|user|>: {question}")
        h.append(f'<|system|>: {response.json()["choices"][0]["text"]}')

if __name__ == "__main__":
    questions = [line.strip() for line in sys.stdin]
    test_server(questions)
