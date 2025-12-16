# 🛡️ Sistema de Monitoramento e Controle de EPI com Visão Computacional 😷

Este projeto consiste no desenvolvimento de um MVP para um Sistema Inteligente de Visão Computacional desenvolvido para monitorar o uso correto de Equipamentos de Proteção Individual (EPIs) em um ambiente fabril. O sistema controla o acesso a ambientes restritos, registra logs de ocorrências e envia alertas automáticos em caso de infrações.

## 📖 Sobre o Projeto

O sistema utiliza uma câmera em tempo real para analisar se um indivíduo está vestindo os EPIs obrigatórios e de forma correta antes de entrar no ambiente fabril. Para este projeto, a autora utilizou apenas os EPIs máscara e touca. Utilizando um modelo de Deep Learning treinado por mim através da plataforma Teachable Machine, exportado em modo tensorflow.keras, o modelo detecta e classifica a imagem capturada, permitindo que o script .py integrado seja capaz de tomar decisões autônomas:

- Conformidade: Se o usuário estiver com touca e máscara, o acesso é liberado pela catraca (simulação de destravamento de porta).

- Violação: Se houver falta de algum EPI ou o EPI estiver na posição incorreta, o acesso pela catraca é negado, a ocorrência é registrada em log (com dados e imagem correspondente) e um alerta por e-mail é enviado aos responsáveis.

- Stand-by: Identifica quando não há ninguém na frente da câmera (Fundo), para evitar processamento desnecessário.

## 🚀 Importância e Objetivos

1. Importância
 
Em indústrias farmacêuticas, cosméticas, alimentícias, hospitalares ou laboratórios químicos, a contaminação cruzada é um risco altamente crítico. Garantir que todos os colaboradores estejam paramentados corretamente antes de entrar em áreas controladas, é vital para garantir a qualidade dos produtos e a segurança dos colaboradores.

2. Objetivos
   
- Automatizar a fiscalização: Reduzir a necessidade de supervisão humana constante na entrada de setores críticos.

- Controle de Acesso Ativo: Impedir fisicamente (via simulação de trava) a entrada de pessoas não conformes.

- Registro e Auditoria: Criar um histórico visual e de dados sobre violações de segurança para ações corretivas.

- Agilidade: Processamento em tempo real das imagens (com técnica skip-frames e normalização de imagens aplicada) para feedback visual imediato na tela.

## 🛠️ Tecnologias Utilizadas

O projeto foi desenvolvido em Python utilizando as seguintes bibliotecas e tecnologias:

- TensorFlow/Keras: Para carregar e executar o modelo.h5 de Rede Neural (Deep Learning) responsável pela detecacção e classificação das imagens baseadas nos labels de treinamento.

- OpenCV (cv2): Para captura de vídeo em tempo real da webcam, manipulação de imagem e exibição da interface visual.

- NumPy: Para operações matemáticas e normalização de arrays de imagem.

- SMTP (smtplib): Protocolo padrão para envio automático de e-mails de alerta.

- Datetime: Para geração de logs temporais precisos.

## 📊 Dados e Treinamento

O modelo.h5 foi treinado utilizando a plataforma Teachable Machine do Google, baseada em Transfer Learning (Transferência de Aprendizado).

- Dataset: O conjunto de dados foi construído manualmente, totalizando 2.697 amostras de imagens, divididas entre as 6 classes (aprox. 450 imagens por classe).

- Coleta: As imagens foram capturadas via webcam da autora em um ambiente controlado.

- Configurações de Treinamento (Hiperparâmetros):

Épocas: 50

Tamanho do Lote (Batch Size): 16

Taxa de Aprendizado (Learning Rate): 0.001

Pré-processamento: As imagens foram normalizadas e redimensionadas para 224x224 pixels (padrão do modelo base MobileNet/EfficientNet usado pelo Teachable Machine).

## 📋 Classes do Modelo

O modelo foi treinado para reconhecer as seguintes classes (conforme labels.txt): 

Com EPIs adequados (touca + máscara de forma correta) ✅ (Acesso Liberado)

Com EPIs inadequados (touca + máscara de forma incorreta) ❌

Com EPI touca ❌

Com EPI mascara ❌

Sem EPIs ❌

Fundo (Aguardando...)

## 📂 Estrutura e Explicação do Código

O script principal 'monitor_epi.py' é dividido em blocos lógicos para facilitar a manutenção:

0. Importação e Compatibilidade: 
Configura o ambiente para aceitar modelos Keras legados (atendendo às demandas de compatibilidade do modelo treinado + versões disponíveis das bibliotecas + versão instalada do interpretador do kernel) e importa as bibliotecas necessárias para visão computacional, manipulação de arquivos e imagens, lógica de decisões e envio de e-mails.

1. Configurações Globais: 
Define constantes essenciais, como Caminhos dos arquivos a serem integrados (keras_model.h5, labels.txt); Credenciais de e-mail (Remetente/Destinatário); Diretórios de Log; Parâmetros de controle (tempo de cooldown para alertas e nomes das classes esperadas pela classficação).

2. Funções Auxiliares: 
Funções modulares que executam tarefas específicas, como 'send_alert_email()' para montar e enviar o e-mail de alerta com a foto da infração anexada ao supervisor; 'log_violation()' para salvar a imagem da infração no disco e escreve os detalhes no arquivo logs/log_ocorrencias.txt; 'unlock_door()' para simular a ação física de liberar uma catraca ou porta eletrônica de acesso restrito; 'preprocess_image()' para preparar a imagem da webcam em tempo real para o modelo (corte central, redimensionamento para 224x224 e normalização de pixels), mantendo a qualidade das imagens detectadas e permitindo que a confiança de classificação do modelo para cada label fosse alta e precisa.

3. Função Principal (Main Loop): 
Carrega o modelo de IA e as labels > Inicia a webcam > Entra em um loop sequencial e infinito que lê cada frame, detecta, processa e classifica a imagem > Baseado na confiança da IA (devendo ser maior ou igual a 90%), o script decide se libera o acesso pela catraca ou gera um log de ocorrência + envio automático do alerta de violação > Exibe o resultado na tela com feedback colorido (Verde = Ok, Vermelho = Violação, Amarelo = Fundo neutro).

## ⚠️ Limitações, Vieses e Roteiro de Melhorias
Este projeto é um protótipo funcional (MVP) e possui limitações conhecidas, tanto no modelo de inteligência artificial quanto na lógica do script de automação. Abaixo, detalhamos esses pontos e como a comunidade pode contribuir para transformá-lo em uma solução de produção.

1. Limitações do Modelo de IA (Dados e Treinamento)
   
- Viés de Identidade e Diversidade de Dados:

O Problema: O dataset atual contém 2.697 imagens focadas em uma única pessoa (autora), resultando em baixo poder de generalização para diferentes etnias, gêneros e características faciais.

🔧 Solução: Expandir o dataset coletando amostras de diversos indivíduos para reduzir o viés algorítmico e evitar overfitting.

- Dependência de Iluminação e Ambiente (Overfitting):

O Problema: O modelo foi treinado em ambiente com iluminação controlada e fundo estático. Mudanças de luz (sombras fortes, contra-luz) ou fundos movimentados podem gerar falsos positivos/negativos. Além disso, devido à especificidade das imagens, o modelo "decorou" características irrelevantes (como a cor da roupa da autora), reduzindo a generalização e o aprendizado de padrões.

🔧 Solução Proposta: Aplicar técnicas de Data Augmentation (Aumento de Dados) antes do treinamento. Isso envolve criar variações automáticas das imagens originais (rotação, zoom, ruído, alteração de brilho) para forçar o modelo a focar apenas nas características essenciais dos EPIs.


2. Limitações do Sistema e Script (Engenharia)

- Simulação de Atuadores (Mock Hardware):

O Problema: Atualmente, a função 'unlock_door()' é apenas uma simulação de software que imprime uma mensagem no console e exibe "Acesso Liberado" na tela. Não há integração física real com uma tranca ou catraca.

🔧 Solução: Implementar comunicação serial (biblioteca pyserial) ou GPIO para enviar sinais elétricos a um microcontrolador (Arduino/ESP32) do hardware, permitindo o acionamento físico de eletroímãs ou catracas.

- Execução Bloqueante (Time Sleep):

O Problema: O script utiliza time.sleep(5) para simular o tempo de porta aberta. Isso "congela" o feed de vídeo e o processamento durante 5 segundos, criando um ponto cego na segurança.

🔧 Solução: Refatorar o código para utilizar Threads ou processamento assíncrono. O controle do tempo da porta deve ocorrer em uma thread separada, permitindo que a câmera continue monitorando e gravando logs sem interrupções.

- Segurança Anti-Spoofing (Liveness Detection):

O Problema: O modelo atual classifica apenas a presença visual dos EPIs. Ele é suscetível a fraudes simples, como apresentar uma foto de uma pessoa usando máscara para a câmera.

🔧 Solução: Integrar um algoritmo de "Liveness Detection" (detecção de vivacidade), que exige que o usuário pisque ou mova a cabeça, ou utilizar sensores de profundidade para garantir que há uma pessoa real tridimensional à frente da câmera.

- *Cenários de falha comuns incluem:* Oclusão parcial do rosto por mãos ou objetos não treinados; Uso de máscaras ou toucas de cores/formatos muito diferentes dos usados no treino; Distância excessiva da câmera (o rosto fica muito pequeno para detecção).


##  🎯 Métricas de Performance

Durante a fase de validação:

- Acurácia Global: O modelo atingiu 100% de acurácia no conjunto de teste específico (acurácia total e acurácia por label) utilizado pela plataforma (o que reforça o alerta de overfitting ao ambiente controlado, conforme já mencionado).

- Perda por épocas (Loss): A curva de perda convergiu para próximo de 0, indicando que o modelo aprendeu perfeitamente a distinguir as classes/labels (dentro do universo do conjunto de dados apresentado).


## 💻 Como Executar o Projeto

Para rodar este projeto em sua máquina local, siga os passos abaixo.

0. Pré-requisitos:

- Python 3.11 ou superior instalado.

- Uma Webcam conectada.

- Arquivo do modelo treinado e labels.txt (keras_model.h5) na raiz do projeto.

1. Clonar o Repositório: Bash 'git clone [https://github.com/BarbJS/Sistema-de-Seguranca-Operacional-de-EPIs-com-Visao-Computacional]' -> 'cd 'Sistema-de-Seguranca-Operacional-de-EPIs-com-Visao-Computacional''
   
2. Criar e Ativar um Ambiente Virtual

É altamente recomendado usar um ambiente virtual para isolar as dependências. Para isso, siga os passos abaixo.

- No Windows: Bash 'python -m venv venv' -> '.\venv\Scripts\activate'
- No Linux/Mac: Bash 'python3 -m venv venv' -> 'source venv/bin/activate'
  
3. Instalar Dependências:
   
Instale as bibliotecas necessárias listadas no código: Bash 'pip install tensorflow keras opencv-python numpy certifi pillow'

4. Configurar Credenciais

Abra o arquivo 'monitor_epi.py' e edite as variáveis de e-mail com suas credenciais (recomenda-se criae e usar Senha de App do Google para sua segurança - NÃO É SUA SENHA USUAL): 

'EMAIL_SENDER = "seu_email@gmail.com"
EMAIL_PASSWORD = "sua_senha_de_app"
EMAIL_RECEIVER = "email_destino_supervisor@gmail.com"'

5. Executar

Com tudo configurado, execute o script: Bash 'python monitor_epi.py'. Uma janela se abrirá mostrando a captura da câmera. O sistema começará a classificar sua imagem imediatamente. Pressione a tecla 'q' para encerrar o programa.

*Este projeto de MVP foi desenvolvido pela autora (Bárbara Jaeger Specian) durante o aprendizado da disicplina AI Factory do curso Tecnólogo em Inteligência Artificial: Sistemas de Dados Inteligentes da PUCPR (2025).*
