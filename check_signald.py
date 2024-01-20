import subprocess
import time

# Lancer ce script en arrière plan avec 'nohup python3 script.py &'
# il vérifiera toutes les minutes que signald n'a pas été arrêté (par une micro coupue réseau par exemple) et
# le redémarrera si nécessaire.


def check_for_errors():
    result = subprocess.run(["docker", "logs", "signald"], capture_output=True, text=True)
    return "SocketException" in result.stdout or "UnknownHostException" in result.stdout

def restart_signald():
    subprocess.run(["docker", "restart", "signald"])

while True:
    if check_for_errors():
        restart_signald()
    time.sleep(60)  # Vérifie toutes les 5 minutes
