# Transcritor de Áudio

Aplicação desktop para gravação e transcrição de áudio com suporte a múltiplos serviços de transcrição.

## Funcionalidades

- Gravação de áudio via microfone
- Upload de arquivos de áudio existentes
- Suporte a múltiplos serviços de transcrição:
  - Whisper Local
  - Google Speech-to-Text
  - OpenAI Whisper API
- Interface desktop moderna e intuitiva
- Visualização da transcrição em tempo real
- Exportação em múltiplos formatos (TXT, DOCX)
- Gerenciamento de chaves de API

## Requisitos

- Python 3.8+
- PyQt6
- Dependências listadas em requirements.txt

## Instalação

1. Clone o repositório
2. Crie um ambiente virtual (recomendado):
```bash
python -m venv venv
venv\Scripts\activate
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

## Executando a aplicação

```bash
python main.py
```

## Configuração

1. Na aba "Configurações", configure suas chaves de API para os serviços que deseja utilizar
2. As configurações são salvas automaticamente no arquivo `config/api_settings.json`

## Uso

1. Na aba "Gravação":
   - Use o botão "Iniciar Gravação" para gravar áudio do microfone
   - Use "Carregar Arquivo de Áudio" para importar arquivos existentes

2. Na aba "Transcrição":
   - Selecione o serviço de transcrição desejado
   - Visualize a transcrição
   - Exporte para TXT ou DOCX conforme necessário
