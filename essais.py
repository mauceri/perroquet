class Essai:
    def __init__(self,a:str,b:int=3):
        self.a = a
        self.b = b
        print("Constructeur")
        
    def test(self):
        print(f"a = {self.a} b = {self.b}")

if __name__ == '__main__':
    e = Essai(a="a")
    e.test()
