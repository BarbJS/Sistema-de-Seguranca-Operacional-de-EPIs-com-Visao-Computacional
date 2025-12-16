# ==============================================================================
# 0. BLOCO DE IMPORTAÇÃO E COMPATIBILIDADE
# ==============================================================================

import os # Importa o módulo 'os' para interagir com o sistema operacional (ex: criar pastas, definir variáveis de ambiente).
os.environ["TF_USE_LEGACY_KERAS"] = "1" # Define uma variável de ambiente para garantir a compatibilidade com modelos Keras mais antigos no TensorFlow.

import certifi # Importa 'certifi' para fornecer um pacote atualizado de certificados SSL, garantindo a validação segura da conexão de e-mail.
import cv2 # Importa a biblioteca OpenCV, usada para processamento de imagem e captura de vídeo da câmera.
import numpy as np # Importa a biblioteca NumPy, essencial para manipulação de arrays numéricos, especialmente para imagens.
import smtplib # Importa a biblioteca para enviar e-mails usando o protocolo SMTP.
import ssl # Importa a biblioteca para criar conexões seguras (SSL/TLS), usada no envio de e-mails.
import tensorflow.keras as keras # Importa o Keras do TensorFlow para carregar e usar o modelo de deep learning.
import time # Importa a biblioteca 'time' para funções relacionadas a tempo (ex: cooldown de alertas, pausas).

from datetime import datetime # Importa a classe 'datetime' para trabalhar com datas e horas (ex: para logs e timestamps).
from email.mime.multipart import MIMEMultipart # Importa a classe para criar mensagens de e-mail com múltiplas partes (ex: texto e anexos).
from email.mime.text import MIMEText # Importa a classe para criar o corpo de texto de um e-mail.
from PIL import Image, ImageOps # Importa componentes da biblioteca Pillow (PIL), embora não estejam sendo usados ativamente após a refatoração.

# ==============================================================================
# 1. CONFIGURAÇÕES GLOBAIS
# ==============================================================================

MODEL_PATH = "keras_model.h5" # Define o caminho para o arquivo do modelo treinado (.h5).
LABELS_PATH = "labels.txt" # Define o caminho para o arquivo de texto que contém os nomes das classes (labels).

EMAIL_SENDER = "seu_email@gmail.com" # Define o endereço de e-mail que enviará os alertas.
EMAIL_PASSWORD = "sua-senha-de-app" # Define a senha de aplicativo para o e-mail remetente (não a senha da conta).
EMAIL_RECEIVER = "email_destino_supervisor@gmail.com" # Define o endereço de e-mail que receberá os alertas.

LOG_DIR = "logs" # Define o nome do diretório onde os logs e as imagens de ocorrências serão salvos.
LOG_FILE = os.path.join(LOG_DIR, "log_ocorrencias.txt") # Cria o caminho completo para o arquivo de log de texto.
os.makedirs(LOG_DIR, exist_ok=True) # Cria o diretório de logs se ele ainda não existir. `exist_ok=True` evita erros se a pasta já existir.

LABEL_ALLOWED = "Com EPIs adequados (touca + mascara)" # Define o texto da label que representa a condição de acesso permitido.
LABEL_BACKGROUND = "Fundo" # Define o texto da label que representa o fundo ou uma cena vazia.
ALERT_COOLDOWN_SECONDS = 15 # Define o tempo de espera (em segundos) entre o envio de alertas de violação para evitar spam.
last_alert_time = 0 # Inicializa a variável que armazena o timestamp do último alerta enviado. Começa em 0.

# ==============================================================================
# 2. FUNÇÕES AUXILIARES (Alertas, Logs, Controle de Acesso)
# ==============================================================================

def send_alert_email(label_name, image_path): # Define a função para enviar um e-mail de alerta.
    
    print(f"[AÇÃO] Enviando e-mail de alerta para {EMAIL_RECEIVER}...") # Imprime uma mensagem no console informando o início do envio.
    
    try: # Inicia um bloco try-except para capturar possíveis erros durante o envio do e-mail.
        msg = MIMEMultipart() # Cria um objeto de mensagem de e-mail que pode conter várias partes.
        msg['Subject'] = "VIOLAÇÃO DE EPI DETECTADA" # Define o assunto do e-mail.
        msg['From'] = EMAIL_SENDER # Define o remetente do e-mail.
        msg['To'] = EMAIL_RECEIVER # Define o destinatário do e-mail.
        
        # Cria o corpo de texto do e-mail usando uma f-string formatada.
        body = f""" 
        Uma violação de conformidade de EPI foi detectada.

        Data/Hora: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        Classificação: {label_name}
        
        Uma imagem da ocorrência foi salva no sistema.
        Caminho: {image_path}
        Esta é uma mensagem automática. Por favor, não responda.

        Sistema de Monitoramento de EPI - Sineris
        """
        msg.attach(MIMEText(body, 'plain', 'utf-8')) # Anexa o corpo de texto à mensagem de e-mail, especificando o formato e a codificação.
      
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465) # Cria uma conexão segura (SSL) com o servidor SMTP do Gmail na porta 465.
        server.login(EMAIL_SENDER, EMAIL_PASSWORD) # Faz login no servidor de e-mail com as credenciais fornecidas.
        server.sendmail(EMAIL_SENDER, [EMAIL_RECEIVER], msg.as_string()) # Envia o e-mail. `msg.as_string()` converte o objeto de mensagem em uma string.
        server.quit() # Fecha a conexão com o servidor SMTP.
                  
        print("[AÇÃO] E-mail de alerta enviado com sucesso.") # Informa que o e-mail foi enviado.
        
    except smtplib.SMTPAuthenticationError: # Captura especificamente erros de autenticação.
        print("[ERRO DE E-MAIL] Falha na autenticacao. Verifique seu EMAIL_PASSWORD (Senha de App).") # Informa sobre falha de login.
    except Exception as e: # Captura qualquer outra exceção que possa ocorrer.
        print(f"[ERRO DE E-MAIL] Falha ao enviar: {e}") # Imprime a mensagem de erro genérica.

def log_violation(frame, label_name): # Define a função para registrar uma violação.
    
    print(f"[AÇÃO] VIOLAÇÃO DETECTADA: {label_name}. Registrando log...") # Imprime uma mensagem indicando que uma violação está sendo registrada.
    
    now = datetime.now() # Obtém a data e hora atuais.
    timestamp_file = now.strftime("%Y-%m-%d_%H-%M-%S") # Formata a data/hora para ser usada em nomes de arquivos (sem caracteres inválidos).
    timestamp_log = now.strftime("%Y-%m-%d %H:%M:%S") # Formata a data/hora para ser usada no texto do log.
    
    img_filename = f"imagem_ocorrencia_{timestamp_file}.jpg" # Cria o nome do arquivo de imagem com o timestamp.
    img_path = os.path.join(LOG_DIR, img_filename) # Monta o caminho completo para salvar a imagem no diretório de logs.
    
    cv2.imwrite(img_path, frame) # Salva o frame (imagem) da câmera no caminho especificado.
    
    log_entry = f"[{timestamp_log}] - Ocorrencia: {label_name} - Arquivo: {img_path}\n" # Cria a linha de texto que será adicionada ao arquivo de log.
    
    with open(LOG_FILE, "a", encoding="utf-8") as f: # Abre o arquivo de log em modo 'append' (adicionar ao final).
        f.write(log_entry) # Escreve a nova entrada de log no arquivo.
        
    return img_path # Retorna o caminho onde a imagem foi salva, para ser usado no e-mail.

def unlock_door(): # Define a função que simula o destravamento de uma porta.
   
    print("---------------------------------") # Imprime uma linha separadora.
    print(">>> PORTA DESTRAVADA <<<") # Imprime a mensagem de porta destravada.
    print("Acesso permitido.") # Imprime a mensagem de acesso permitido.
    print("---------------------------------") # Imprime outra linha separadora.
    time.sleep(5) # Pausa a execução do script por 5 segundos para simular o tempo que a porta fica aberta.

def preprocess_image(frame): # Define a função para pré-processar a imagem da câmera antes de enviá-la ao modelo.
    
    # 1. Center-Crop (corte central)
    h, w, _ = frame.shape # Obtém a altura (h), largura (w) e canais de cor do frame.
    min_dim = min(h, w) # Encontra a menor dimensão (altura ou largura).
    
    start_x = (w - min_dim) // 2 # Calcula a coordenada x inicial para o corte, centralizando-o horizontalmente.
    start_y = (h - min_dim) // 2 # Calcula a coordenada y inicial para o corte, centralizando-o verticalmente.
    
    # Realiza o corte para criar uma imagem quadrada a partir do centro do frame original.
    cropped_frame = frame[start_y : start_y + min_dim, start_x : start_x + min_dim]

    # 2. Converte BGR (padrão do OpenCV) para RGB (padrão do modelo)
    image_rgb = cv2.cvtColor(cropped_frame, cv2.COLOR_BGR2RGB) # Converte o espaço de cores da imagem cortada.

    # 3. Redimensiona a imagem para 224x224 pixels, que é o tamanho de entrada esperado pelo modelo.
    resized_image = cv2.resize(image_rgb, (224, 224), interpolation=cv2.INTER_AREA) # `INTER_AREA` é bom para reduzir imagens.

    # 4. Normaliza os valores dos pixels para o intervalo [-1, 1].
    # O modelo foi treinado com imagens normalizadas desta forma.
    normalized_image = (resized_image.astype(np.float32) / 127.5) - 1 # Converte para float, divide por 127.5 e subtrai 1.
    
    return normalized_image # Retorna a imagem processada e pronta para a predição.

# ==============================================================================
# 3. FUNÇÃO PRINCIPAL (Execução do Monitoramento)
# ==============================================================================

def main(): # Define a função principal que executa o loop de monitoramento.
    global last_alert_time # Declara que a função usará a variável global `last_alert_time`.
    
    print("Carregando modelo de IA (Modo de compatibilidade Keras 2)...") # Informa o início do carregamento do modelo.
    np.set_printoptions(suppress=True) # Configura o NumPy para não usar notação científica ao imprimir números, melhorando a legibilidade das predições.
    
    try: # Inicia um bloco para tratar erros no carregamento do modelo.
        model = keras.models.load_model(MODEL_PATH) # Carrega o modelo de IA a partir do arquivo .h5.
    except Exception as e: # Captura qualquer erro que ocorra durante o carregamento.
        print(f"[ERRO FATAL] Nao foi possivel carregar o modelo '{MODEL_PATH}'.") # Imprime uma mensagem de erro fatal.
        print(f"Detalhe: {e}") # Imprime os detalhes do erro.
        return # Encerra a função `main` se o modelo não puder ser carregado.

    class_names = [] # Inicializa uma lista vazia para armazenar os nomes das classes.
    try: # Inicia um bloco para tratar erros na leitura do arquivo de labels.
        with open(LABELS_PATH, "r", encoding="utf-8") as f: # Abre o arquivo de labels em modo de leitura.
            # Lê cada linha, remove espaços em branco, divide no primeiro espaço e pega a segunda parte (o nome da classe).
            class_names = [line.strip().split(' ', 1)[1] for line in f.readlines()]
    except Exception as e: # Captura qualquer erro que ocorra.
        print(f"[ERRO FATAL] Nao foi possivel carregar as labels '{LABELS_PATH}'.") # Imprime uma mensagem de erro fatal.
        print(f"Detalhe: {e}") # Imprime os detalhes do erro.
        return # Encerra a função `main` se as labels não puderem ser carregadas.

    print("Modelo e labels carregados com sucesso.") # Confirma que o modelo e as labels foram carregados.

    # Cria um array NumPy com o formato esperado pelo modelo: 1 imagem, 224x224 pixels, 3 canais de cor (RGB).
    data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)

    cap = cv2.VideoCapture(0) # Inicializa a captura de vídeo da primeira câmera conectada (índice 0).
    if not cap.isOpened(): # Verifica se a câmera foi aberta com sucesso.
        print("[ERRO FATAL] Nao foi possivel abrir a camera.") # Imprime um erro se a câmera não puder ser acessada.
        return # Encerra a função.

    print("\nIniciando monitoramento... Pressione 'q' para sair.") # Informa o início do monitoramento.

    while True: # Inicia o loop infinito que processa os frames da câmera.
        ret, frame = cap.read() # Lê um frame da câmera. `ret` é um booleano (sucesso/falha), `frame` é a imagem.
        if not ret: # Se a leitura do frame falhar...
            print("[ERRO] Frame perdido. Tentando novamente...") # ...imprime um erro...
            continue # ...e pula para a próxima iteração do loop.

        # Pré-processa o frame capturado usando a função auxiliar.
        normalized_image = preprocess_image(frame)
        
        # Carrega a imagem normalizada no array `data` que será passado para o modelo.
        data[0] = normalized_image

        # Executa a inferência (predição) do modelo na imagem. `verbose=0` desativa os logs de predição.
        prediction = model.predict(data, verbose=0) 
        index = np.argmax(prediction) # Encontra o índice da classe com a maior probabilidade.
        class_name = class_names[index] # Obtém o nome da classe correspondente a esse índice.
        confidence_score = prediction[0][index] # Obtém a pontuação de confiança para a classe prevista.

        # Cria o texto que será exibido na tela, mostrando a classe e a confiança.
        display_text = f"Label: {class_name} ({confidence_score*100:.2f}%)"
        current_time = time.time() # Obtém o tempo atual em segundos para a lógica de cooldown.
        color = (255, 255, 255) # Define a cor padrão do texto como branco.

        # Verifica se a confiança da predição está acima de um limiar (90%).
        if confidence_score > 0.90: 
            
            if class_name == LABEL_ALLOWED: # Se a classe for a permitida...
                color = (0, 255, 0) # ...define a cor do texto como verde.
                display_text += " - Acesso Liberado" # Adiciona "Acesso Liberado" ao texto.
                cv2.putText(frame, display_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2) # Desenha o texto na imagem.
                cv2.imshow('Monitoramento EPIs', frame) # Mostra a imagem em uma janela.
                unlock_door() # Chama a função para destravar a porta.

            elif class_name == LABEL_BACKGROUND: # Se a classe for "Fundo"...
                color = (200, 200, 200) # ...define a cor como cinza claro.
                display_text += " - Aguardando..." # Adiciona "Aguardando..." ao texto.
            
            else: # Para qualquer outra classe (considerada uma violação)...
                color = (0, 0, 255) # ...define a cor como vermelho.
                display_text += " - ACESSO NEGADO" # Adiciona "ACESSO NEGADO" ao texto.

                # Verifica se o tempo desde o último alerta é maior que o cooldown definido.
                if (current_time - last_alert_time) > ALERT_COOLDOWN_SECONDS:
                    print("\n--- VIOLACAO DETECTADA ---") # Imprime um cabeçalho de violação.
                    last_alert_time = current_time # Atualiza o tempo do último alerta para o tempo atual.
                    
                    saved_img_path = log_violation(frame, class_name) # Salva a imagem e o log da violação.
                    
                    send_alert_email(class_name, saved_img_path) # Envia o e-mail de alerta.
                    print("--------------------------\n") # Imprime um rodapé.
                else: # Se ainda estiver no período de cooldown...
                    display_text += " (Alerta em cooldown)" # ...adiciona uma mensagem indicando o cooldown.

        else: # Se a confiança for baixa...
            display_text = "Analisando... (Baixa confianca)" # ...define o texto para "Analisando...".
            color = (0, 255, 255) # ...define a cor como amarelo.

        # Desenha o texto final sobre o frame original da câmera.
        cv2.putText(frame, display_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        # Exibe o frame com o texto na janela 'Monitoramento EPIs'.
        cv2.imshow('Monitoramento EPIs', frame)

        # Aguarda por 1 milissegundo por uma tecla. Se a tecla 'q' for pressionada, o loop é interrompido.
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break # Sai do loop `while`.

    cap.release() # Libera o recurso da câmera.
    cv2.destroyAllWindows() # Fecha todas as janelas abertas pelo OpenCV.
    print("Monitoramento encerrado.") # Imprime uma mensagem final.

# ==============================================================================
# INICIALIZAÇÃO DO SCRIPT
# ==============================================================================
if __name__ == "__main__": # Verifica se o script está sendo executado diretamente (e não importado como um módulo).
    main() # Chama a função principal para iniciar o programa.
