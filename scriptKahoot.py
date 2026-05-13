# kahoot_bot.py

# --- Importação das Bibliotecas ---
import cv2
import numpy as np
import mss
import pytesseract
import time
import google.generativeai as genai
import pyautogui
from PIL import Image
import os # Biblioteca para acessar variáveis de ambiente

# ----------------------------------------------------------------------------------
# --- ÁREA DE CONFIGURAÇÃO - AJUSTE ESTES VALORES PARA O SEU AMBIENTE ---
# ----------------------------------------------------------------------------------

# 1. CAMINHO PARA O EXECUTÁVEL DO TESSERACT
# Verifique onde o Tesseract foi instalado no seu computador e cole o caminho aqui.
# Exemplos:
# Windows: r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# Linux (se não estiver no PATH): r'/usr/bin/tesseract'
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# 2. NÚMERO DO MONITOR ALVO
# Use o script 'verificar_monitores.py' para descobrir o número do monitor onde o jogo vai rodar.
# [1] = Monitor primário, [2] = Monitor secundário, etc.
MONITOR_ALVO_NUM = 2

# 3. COORDENADAS DAS ÁREAS DE INTERESSE (Relativas ao monitor alvo)
# Use o script 'descobrir_coordenadas.py' para encontrar estes valores na sua tela.
# Formato: (x_canto_superior_esquerdo, y_canto_superior_esquerdo, largura, altura)
AREAS_DE_INTERESSE = {
    "pergunta": (0, 0, 1840, 167),
    "imagem_pergunta": (0, 0, 1920, 1080), # Ajuste para a área onde a imagem da pergunta aparece
    "resposta_vermelha": (20, 715, 934, 165),
    "resposta_azul": (968, 718, 934, 165),
    "resposta_amarela": (22, 897, 934, 165),
    "resposta_verde": (967, 895, 934, 165),
}

# 4. COORDENADAS PARA CLIQUES PÓS-RESPOSTA (Coordenadas globais da tela)
# Após responder, o Kahoot mostra uma tela de resultado e depois um lobby.
# O bot clica para avançar para a próxima rodada mais rápido.
# Use 'descobrir_coordenadas.py' para achar o local do botão "Avançar" e "Jogar de novo".
COORD_BOTAO_AVANCAR = (1831, 303)
COORD_BOTAO_JOGAR_NOVAMENTE = (1798, 200)

# ----------------------------------------------------------------------------------
# --- FIM DA ÁREA DE CONFIGURAÇÃO ---
# ----------------------------------------------------------------------------------

# --- Configuração da API Gemini (lendo de uma variável de ambiente) ---
try:
    # O script vai procurar por uma variável de ambiente chamada GOOGLE_API_KEY
    API_KEY = os.getenv("GOOGLE_API_KEY")
    if not API_KEY:
        raise ValueError("A variável de ambiente GOOGLE_API_KEY não foi encontrada.")
    genai.configure(api_key=API_KEY)
except Exception as e:
    print(f"Erro ao configurar a API: {e}")
    exit()

# Intervalos de cor em HSV para detecção das caixas de resposta
HSV_RANGES = {
    'resposta_vermelha': ((160, 100, 100), (180, 255, 255)),
    'resposta_azul':     ((100, 100, 100), (130, 255, 255)),
    'resposta_amarela':  ((20, 100, 100), (40, 255, 255)),
    'resposta_verde':    ((40, 100, 50), (80, 255, 255))
}

def is_pergunta_valida(texto_pergunta, min_caracteres=15, min_palavras=3):
    """Verifica se o texto da pergunta parece ser válido para evitar processar 'lixo' de transições de tela."""
    if not texto_pergunta or len(texto_pergunta) < min_caracteres or len(texto_pergunta.split()) < min_palavras:
        return False
    return True

def extrair_texto_da_area(imagem, area, nome_area):
    """Recorta uma área da imagem, pré-processa e extrai o texto usando Tesseract."""
    x, y, w, h = area
    roi = imagem[y:y+h, x:x+w]
    
    if nome_area == 'pergunta':
        cinza = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        _, processada = cv2.threshold(cinza, 127, 255, cv2.THRESH_BINARY)
    else:
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        cor_min, cor_max = HSV_RANGES[nome_area]
        mascara_fundo = cv2.inRange(hsv, cor_min, cor_max)
        processada = cv2.bitwise_not(mascara_fundo)
        
    try:
        texto = pytesseract.image_to_string(processada, lang='por', config='--psm 6')
        return texto.strip().replace('\n', ' ')
    except:
        return ""

def obter_resposta_da_ia(pergunta, opcoes, imagem=None):
    """Monta o prompt, envia para a API Gemini (com imagem, se houver) e retorna a resposta."""
    opcoes_validas = [opt for opt in opcoes if opt]
    if not opcoes_validas:
        return "Nenhuma opção válida foi fornecida."
    opcoes_formatadas = "\n".join([f"- {opcao}" for opcao in opcoes_validas])

    texto_prompt = f"""
    Você é um bot assistente especialista em jogos de trivia como o Kahoot.
    Sua função é analisar a pergunta em texto, as opções de resposta e a IMAGEM fornecida para determinar a resposta correta.
    Retorne APENAS o texto exato da alternativa correta, sem nenhuma palavra ou pontuação adicional.
    Caso você verifique pela imagem que as alternativas são "Verdadeiro" e "Falso", e as opções enviadas forem inelegiveis, você pode analisar a pergunta e responder com "Verdadeiro" ou "Falso" nesse caso.

    Pergunta: "{pergunta}"

    Opções:
    {opcoes_formatadas}
    """
    
    prompt_parts = [texto_prompt]
    if imagem:
        print("[IA] Imagem detectada. Enviando junto com o prompt.")
        prompt_parts.append(imagem)
    
    print("\n[IA] Gerando resposta...")
    # Usando um modelo conhecido e estável. Pode ser trocado por outros como 'gemini-1.5-pro-latest'.
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    try:
        response = model.generate_content(prompt_parts)
        return response.text.strip()
    except Exception as e:
        return f"Erro na API: {e}"

def clicar_na_resposta(nome_da_area, offset_monitor):
    """Calcula o centro da área de resposta e clica usando coordenadas globais."""
    if nome_da_area not in AREAS_DE_INTERESSE:
        print(f"[ERRO] Área '{nome_da_area}' não encontrada para clicar.")
        return

    x_rel, y_rel, w, h = AREAS_DE_INTERESSE[nome_da_area]
    centro_x_rel = x_rel + w // 2
    centro_y_rel = y_rel + h // 2

    # Converte as coordenadas relativas ao monitor para coordenadas globais da tela
    x_global = offset_monitor['left'] + centro_x_rel
    y_global = offset_monitor['top'] + centro_y_rel

    print(f"🖱️ Clicando em '{nome_da_area}' nas coordenadas globais ({x_global}, {y_global})")
    pyautogui.click(x_global, y_global)

def realizar_cliques_pos_resposta():
    """Realiza os cliques para avançar para a próxima rodada."""
    print("[AÇÃO] Clicando para avançar...")
    time.sleep(5)
    pyautogui.click(COORD_BOTAO_AVANCAR)
    time.sleep(2)
    pyautogui.click(COORD_BOTAO_JOGAR_NOVAMENTE)
    time.sleep(3) # Pausa adicional antes de começar a ler a próxima pergunta

# --- Loop Principal do Bot ---
ultima_pergunta_processada = ""
print("🚀 Bot iniciado. Pressione Ctrl+C no terminal para parar.")

try:
    with mss.mss() as sct:
        while True:
            monitor_alvo = sct.monitors[MONITOR_ALVO_NUM-1]
            screenshot = sct.grab(monitor_alvo)
            
            img_np = np.array(screenshot)
            img_bgr = cv2.cvtColor(img_np, cv2.COLOR_BGRA2BGR)

            resultados = {}
            for nome_area, coords in AREAS_DE_INTERESSE.items():
                if nome_area == "imagem_pergunta":
                    continue
                texto_extraido = extrair_texto_da_area(img_bgr, coords, nome_area)
                resultados[nome_area] = texto_extraido

            pergunta_atual = resultados.get("pergunta", "")

            # Lógica principal: só age se a pergunta for nova e válida
            if pergunta_atual and pergunta_atual != ultima_pergunta_processada:
                if is_pergunta_valida(pergunta_atual):
                    print(f"\n[LÓGICA] Pergunta válida detectada: {pergunta_atual}")
                    ultima_pergunta_processada = pergunta_atual
                    
                    opcoes = {k: v for k, v in resultados.items() if k != 'pergunta'}

                    # Prepara e envia a imagem para a IA
                    x, y, w, h = AREAS_DE_INTERESSE["imagem_pergunta"]
                    imagem_pergunta_np = img_bgr[y:y+h, x:x+w]
                    imagem_rgb = cv2.cv2tColor(imagem_pergunta_np, cv2.COLOR_BGR2RGB)
                    imagem_pil = Image.fromarray(imagem_rgb)

                    resposta_ia = obter_resposta_da_ia(pergunta_atual, list(opcoes.values()), imagem=imagem_pil)
                    
                    print(f"\n========================================")
                    print(f"🤖 RESPOSTA DA IA: {resposta_ia}")
                    print(f"========================================")
                    
                    # Procura a resposta da IA nas opções lidas e clica
                    achou_resposta = False
                    resposta_lower = resposta_ia.lower()

                    # Lógica especial para Verdadeiro/Falso
                    if "verdadeiro" in resposta_lower:
                        clicar_na_resposta("resposta_amarela", monitor_alvo) # Assumindo que Amarelo é Verdadeiro
                        achou_resposta = True
                    elif "falso" in resposta_lower:
                        clicar_na_resposta("resposta_verde", monitor_alvo) # Assumindo que Verde é Falso
                        achou_resposta = True
                    else:
                        # Lógica geral de correspondência de texto
                        for nome_area, texto_opcao in opcoes.items():
                            if texto_opcao and resposta_lower in texto_opcao.lower():
                                print(f"[LÓGICA] Resposta encontrada! Correspondência: '{texto_opcao}'")
                                clicar_na_resposta(nome_area, monitor_alvo)
                                achou_resposta = True
                                break
                    
                    if achou_resposta:
                        realizar_cliques_pos_resposta()
                    else:
                        print("[AVISO] Não foi possível encontrar uma correspondência para a resposta da IA nas opções lidas.")
                        time.sleep(8) # Pausa longa se não encontrar
except KeyboardInterrupt:
    print("\n[INFO] Bot interrompido pelo usuário (Ctrl+C). Encerrando.")
finally:
    cv2.destroyAllWindows()