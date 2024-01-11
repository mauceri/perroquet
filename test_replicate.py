import replicate
import pprint

print("Bonjour")
output = replicate.run(
    "mistralai/mixtral-8x7b-instruct-v0.1:7b3212fbaf88310cfef07a061ce94224e82efc8403c26fc67e8f6c065de51f21",
    input={
        "top_k": 50,
        "top_p": 0.9,
        "prompt": "Écrivez en français un article polémique contre l'immigration",
        "temperature": 0.6,
        "max_new_tokens": 1024,
        "prompt_template": "<s>[INST] {prompt} [/INST] ",
        "presence_penalty": 0,
        "frequency_penalty": 0
    }
)
texte_complet = "".join(item for item in output)
print(texte_complet)

# r = ""
# for x in output:
#     r += x
# print(r)