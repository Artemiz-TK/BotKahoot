import pyautogui
import time

print("Pressione Ctrl+C para parar.")

try:
    while True:
        # Pega e exibe as coordenadas atuais do mouse.
        x, y = pyautogui.position()
        posicaoStr = f"X: {str(x).rjust(4)} Y: {str(y).rjust(4)}"
        print(posicaoStr, end='')
        print('\b' * len(posicaoStr), end='', flush=True)
        time.sleep(0.1)
except KeyboardInterrupt:
    print("\nPronto.")