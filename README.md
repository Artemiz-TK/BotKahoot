# Kahoot Bot

Um bot em Python que joga Kahoot automaticamente usando Visão Computacional para ler a tela e a API do Google Gemini para encontrar as respostas corretas.

Este projeto foi criado como um desafio de programação e um estudo sobre automação, OCR e integração com APIs de IA.

### ⚠️ Aviso de Uso
Este bot foi desenvolvido para fins educacionais e de entretenimento. Use-o de forma responsável, preferencialmente em jogos privados com amigos que saibam da brincadeira. O uso em competições ou ambientes acadêmicos avaliados constitui trapaça e viola os termos de serviço da plataforma Kahoot.

---

### Funcionalidades
-   **Visão Computacional:** Usa `OpenCV` e `MSS` para capturar a tela em alta velocidade.
-   **OCR:** Utiliza o `Tesseract` para extrair o texto da pergunta e das opções de resposta.
-   **Processamento de Imagem:** Isola as caixas de resposta coloridas usando o espaço de cor HSV para garantir uma leitura de texto confiável.
-   **Inteligência Artificial:** Envia a pergunta, as opções e a imagem da pergunta (se houver) para a API do Google Gemini para obter a resposta mais provável.
-   **Automação:** Usa `PyAutoGUI` para clicar automaticamente na resposta correta.

---

### Pré-requisitos
Antes de começar, você precisará ter o seguinte instalado em seu sistema:

1.  **Python 3.8+**
2.  **Tesseract OCR Engine:**
    * Siga as instruções de instalação para o seu sistema operacional: [Guia de Instalação do Tesseract](https://github.com/tesseract-ocr/tessdoc/blob/main/Installation.md)
    * **Importante:** Durante a instalação no Windows, certifique-se de marcar a opção para instalar os pacotes de idioma, incluindo o de **Português**.
3.  **Uma Chave de API do Google Gemini:**
    * Você pode obter uma chave gratuita no [Google AI Studio](https://aistudio.google.com/).

---

### Instalação

1.  **Clone este repositório:**
    ```bash
    git clone [https://github.com/seu-usuario/seu-repositorio.git](https://github.com/seu-usuario/seu-repositorio.git)
    cd seu-repositorio
    ```

2.  **Instale as dependências Python:**
    Recomenda-se criar um ambiente virtual.
    ```bash
    python -m venv venv
    source venv/bin/activate  # No Windows: venv\Scripts\activate
    ```
    Em seguida, instale os pacotes a partir do arquivo `requirements.txt`:
    ```bash
    pip install -r requirements.txt
    ```

---

### Configuração Obrigatória

Antes de rodar o bot, você **PRECISA** configurar as variáveis no topo do arquivo `kahoot_bot.py`.

1.  **Chave de API do Google Gemini:**
    Este script carrega a chave de uma **variável de ambiente** para segurança. Você precisa configurá-la no seu sistema:
    * **Windows (Terminal):**
        ```cmd
        set GOOGLE_API_KEY="SUA_CHAVE_DE_API_AQUI"
        ```
    * **Linux/macOS (Terminal):**
        ```bash
        export GOOGLE_API_KEY="SUA_CHAVE_DE_API_AQUI"
        ```
    Para uma configuração permanente, pesquise como adicionar variáveis de ambiente no seu sistema operacional.

2.  **Caminho do Tesseract:**
    Ajuste a variável `pytesseract.pytesseract.tesseract_cmd` com o caminho exato para o arquivo `tesseract.exe` no seu computador.

3.  **Número do Monitor:**
    Rode o script `verificar_monitores.py` para listar os monitores detectados. Altere a variável `MONITOR_ALVO_NUM` para o número do monitor onde o Kahoot será exibido (ex: `2` para o monitor secundário).

4.  **Coordenadas da Tela:**
    Esta é a parte mais crítica. As coordenadas no script foram calculadas para uma resolução e layout específicos. Você **precisará encontrar as suas próprias coordenadas**.
    * Execute o script `descobrir_coordenadas.py`.
    * Mova o mouse sobre a tela do Kahoot para descobrir os valores de `x` e `y`.
    * Atualize o dicionário `AREAS_DE_INTERESSE` e as variáveis `COORD_BOTAO_AVANCAR` e `COORD_BOTAO_JOGAR_NOVAMENTE` no arquivo `kahoot_bot.py`.

---

### Executando o Bot

1.  Abra o jogo Kahoot no monitor que você configurou.
2.  Deixe o terminal visível para acompanhar o que o bot está fazendo.
3.  Execute o script principal:
    ```bash
    python kahoot_bot.py
    ```
4.  Para parar o bot a qualquer momento, volte para o terminal e pressione **Ctrl+C**.
