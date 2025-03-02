# 🎙️ Transcritor de Áudio

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![PySide6](https://img.shields.io/badge/PySide6-6.4.0+-green.svg)](https://wiki.qt.io/Qt_for_Python)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/yourusername/transcriber/graphs/commit-activity)

<div align="center">

Uma aplicação desktop moderna e eficiente para gravação e transcrição de áudio, com suporte a múltiplos serviços de transcrição e uma interface intuitiva.

[Funcionalidades](#funcionalidades) •
[Requisitos](#requisitos) •
[Instalação](#instalação) •
[Uso](#uso) •
[Configuração](#configuração)

</div>

## ✨ Funcionalidades

🎤 **Gravação Avançada**
- Gravação de áudio em alta qualidade via microfone
- Medidor VU em tempo real para monitoramento de níveis
- Suporte a múltiplos dispositivos de entrada
- Upload de arquivos de áudio existentes

🤖 **Múltiplos Serviços de Transcrição**
- [Whisper Local](https://github.com/openai/whisper) - Transcrição offline
- [Google Speech-to-Text](https://cloud.google.com/speech-to-text) - Alta precisão online
- [OpenAI Whisper API](https://platform.openai.com/docs/guides/speech-to-text) - Modelo state-of-the-art

💻 **Interface Moderna**
- Design responsivo e intuitivo
- Tema escuro moderno
- Ícones bonitos e intuitivos
- Visualização da transcrição em tempo real

📄 **Exportação Flexível**
- Exportação para TXT
- Exportação para DOCX com formatação
- Histórico de transcrições

💰 **Controle de Custos**
- Acompanhamento de gastos com APIs
- Estimativas de custo antes da transcrição
- Histórico de economia

## 🚀 Requisitos

- Python 3.8 ou superior
- Sistema operacional: Windows, macOS ou Linux
- Microfone (para gravação)
- Dependências Python listadas em `requirements.txt`

## 📦 Instalação

1. **Clone o repositório**
```bash
git clone https://github.com/yourusername/transcriber.git
cd transcriber
```

2. **Configure o ambiente virtual (recomendado)**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate
```

3. **Instale as dependências**
```bash
pip install -r requirements.txt
```

## 🎯 Uso

### Gravação de Áudio

1. Selecione o dispositivo de entrada desejado
2. Ajuste o nível de entrada usando o medidor VU
3. Clique em "Iniciar Gravação" para começar
4. Monitore os níveis de áudio em tempo real
5. Clique em "Parar" quando terminar

### Transcrição

1. Escolha o serviço de transcrição:
   - **Whisper Local**: Processamento offline, gratuito
   - **Google Speech**: Melhor para áudio limpo
   - **OpenAI Whisper**: Melhor para casos complexos

2. Configure as opções de transcrição:
   - Idioma (automático ou específico)
   - Qualidade (velocidade vs precisão)
   - Formato de saída

3. Inicie a transcrição e acompanhe o progresso

### Exportação

- Use o botão "Exportar" para salvar em TXT ou DOCX
- Escolha o local e formato desejados
- Adicione metadados opcionais

## ⚙️ Configuração

### Configuração de APIs

1. Acesse a aba "Configurações"
2. Insira suas chaves de API:
   - Google Cloud (opcional)
   - OpenAI API (opcional)
3. Configure as preferências:
   - Idioma padrão
   - Formato de exportação
   - Tema da interface

### Configurações de Áudio

- Taxa de amostragem
- Canais (mono/estéreo)
- Formato de gravação
- Qualidade de compressão

## 📊 Monitoramento de Custos

- Acompanhe o uso de APIs
- Visualize economia por serviço
- Defina limites de gastos
- Receba alertas de uso

## 🤝 Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para:

- Reportar bugs
- Sugerir novas funcionalidades
- Enviar pull requests
- Melhorar a documentação

## 📝 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

---

<div align="center">
Desenvolvido com ❤️ usando Python e Qt

[⬆ Voltar ao topo](#-transcritor-de-áudio)
</div>
