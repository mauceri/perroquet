from typing import List
import sys
from transformers import AutoTokenizer



class TestFormat:   
    def __init__(self):
        self.contextel = []
        self.contextel.append({"role":"system","content":"Vous êtes un robot de discussion générale. Vos réponses sont concises."})
        self.contextel.append({"role":"user","content":"Qui était Henri IV de France"})
        self.contextel.append({"role":"assistant","content":"Un roi de France"})
        self.contextel.append({"role":"user","content":"Qui était Charles Baudelaire"})
        self.contextel.append({"role":"assistant","content":"Un poète Français"})
        self.tokenizer = AutoTokenizer.from_pretrained("bofenghuang/vigostral-7b-chat")
        self.contexte = self.tokenizer.apply_chat_template(self.contextel, tokenize=False, add_generation_prompt=True)
        #print(f"Historique = {self.contexte}")
        

    def vazy(self,questions:List[str]):
        for question in questions:
            self.contextel.append({"role":"user","content":question})
            print(f"{self.tokenizer.apply_chat_template(self.contextel, tokenize=False, add_generation_prompt=True)}")
            self.contextel.append({"role":"assistant","content":"je ne sais pas"})
            
        

if __name__ == "__main__":
    questions = [line.strip() for line in sys.stdin]
    TestFormat().vazy(questions)

 