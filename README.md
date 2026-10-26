# 🎙️ Audio Transcriber

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![PySide6](https://img.shields.io/badge/PySide6-6.4.0+-green.svg)](https://wiki.qt.io/Qt_for_Python)
[![Whisper](https://img.shields.io/badge/OpenAI-Whisper-orange.svg)](https://github.com/openai/whisper)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

<div align="center">

**Uma aplicação desktop moderna e elegante para gravação e transcrição de áudio com IA**

✨ Waveform neon em tempo real • 🚀 Transcrição ultra-precisa • 🎨 Interface moderna • 🎯 Otimizado para português brasileiro

[🚀 Instalação Rápida](#-instalação-rápida) •
[✨ Funcionalidades](#-funcionalidades) •
[📖 Como Usar](#-como-usar) •
[⚙️ Configuração](#️-configuração)

![Screenshot](https://via.placeholder.com/800x500/1a1a1a/4a9eff?text=Audio+Transcriber+Interface)

</div>

## ✨ Funcionalidades

### 🎨 **Interface Moderna**
- **Tema escuro elegante** com design minimalista
- **Waveform neon dinâmica** com gradiente de cores em tempo real
- **Layout responsivo** com navegação por abas intuitiva
- **Toast notifications** para feedback visual imediato
- **Animações suaves** e transições modernas

### 🎤 **Gravação Profissional**
- **Gravação em alta qualidade** (16kHz, mono otimizado)
- **Waveform reativa** com 5 níveis de cores neon dinâmicas
- **Seleção de microfone** com detecção automática de dispositivos
- **Timer de gravação** com controle preciso de tempo
- **Feedback visual** de sucesso com toast notifications

### 🚀 **Transcrição Otimizada**
- **Whisper AI local** - 100% offline e privado
- **Processamento direto de áudio** sem arquivos temporários
- **Normalização automática** e reamostragem para 16kHz
- **Idioma português forçado** para máxima precisão
- **Configurações otimizadas** (beam_size=5, best_of=5)

### 💰 **Controle de Economia**
- **Cálculo automático** de economia vs serviços pagos
- **Histórico detalhado** de transcrições
- **Estatísticas em tempo real** de uso e economia
- **Comparação de custos** com OpenAI Whisper API

### 📁 **Gerenciamento Inteligente**
- **Histórico completo** de transcrições salvas
- **Busca e organização** de arquivos
- **Exportação de texto** com um clique
- **Backup automático** de dados

## 🚀 Instalação Rápida

### Pré-requisitos
- **Python 3.8+** instalado
- **Microfone** conectado (para gravação)
- **4GB RAM** mínimo recomendado

### Instalação em 3 passos

```bash
# 1. Clone o repositório
git clone https://github.com/yourusername/audio-transcriber.git
cd audio-transcriber

# 2. Instale as dependências
pip install -r requirements.txt

# 3. Execute a aplicação
python main.py
```

### 🐍 Ambiente Virtual (Recomendado)
```bash
# Crie o ambiente virtual
python -m venv venv

# Ative o ambiente
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Instale as dependências
pip install -r requirements.txt
```

## 📖 Como Usar

### 🎤 **Gravação Simples**
1. **Selecione seu microfone** no dropdown da interface
2. **Clique no botão de gravação** (ícone de microfone)
3. **Observe a waveform neon** reagindo ao seu áudio em tempo real
4. **Clique no botão stop** para finalizar
5. **Receba confirmação visual** com toast notification de sucesso

### 📁 **Gerenciar Arquivos**
1. **Clique em "My Files"** na barra superior
2. **Selecione qualquer arquivo** da lista
3. **Clique "Transcribe"** para processar
4. **Aguarde o progresso** na barra de carregamento

### ⚙️ **Configurações Avançadas**
1. **Acesse "Settings"** no menu superior
2. **Escolha o modelo Whisper** (Tiny para velocidade)
3. **Visualize suas economias** acumuladas
4. **Ajuste preferências** conforme necessário

### 💡 **Dicas de Uso**
- **Ambiente silencioso** = melhor qualidade de transcrição
- **Fale claramente** e em ritmo normal para máxima precisão
- **Observe a waveform** - cores mais vibrantes indicam melhor captação
- **Toast verde** confirma que a gravação foi salva com sucesso
- **Timer automático** mostra duração da gravação em tempo real

## ⚙️ Configuração

### 🔧 **Configurações do Sistema**
A aplicação funciona **100% offline** por padrão, sem necessidade de APIs externas:

- **Modelo Whisper**: Tiny (rápido) ou Small (preciso)
- **Idioma**: Português brasileiro otimizado
- **Qualidade de áudio**: 16kHz, mono (otimizado)
- **Formato de saída**: JSON com metadados completos

### 📊 **Estrutura de Arquivos**
```
transcriber/
├── audio/           # Gravações temporárias
├── transcriptions/  # Histórico de transcrições
├── config/          # Configurações e economia
├── src/            # Código fonte
└── main.py         # Executável principal
```

### 🎛️ **Configurações Avançadas**
- **GPU**: Detecção automática para aceleração
- **Memória**: Otimizado para sistemas com 4GB+
- **Threads**: Processamento paralelo inteligente
- **Cache**: Modelos baixados automaticamente

## 📊 Sistema de Economia

### 💰 **Cálculo Automático**
- **OpenAI Whisper API**: $0.006/minuto
- **Whisper Local**: $0.00/minuto
- **Economia total**: Calculada em tempo real

### 📈 **Estatísticas Detalhadas**
- Tempo total transcrito
- Valor economizado acumulado
- Histórico de uso por arquivo
- Comparativo de custos

## 🚀 Performance

### ⚡ **Otimizações Implementadas**
- **Processamento direto**: Áudio passado diretamente ao Whisper (sem I/O de arquivos)
- **Normalização automática**: Previne clipping e melhora qualidade
- **Reamostragem inteligente**: Converte automaticamente para 16kHz
- **Configuração otimizada**: beam_size=5, best_of=5, temperature=0.0
- **Idioma forçado**: Português brasileiro para evitar detecção incorreta

### 📱 **Requisitos Mínimos**
- **RAM**: 4GB (8GB recomendado)
- **CPU**: Dual-core 2GHz+
- **GPU**: Opcional (CUDA/OpenCL)
- **Espaço**: 2GB para modelos

## 🤝 Contribuindo

Quer melhorar o Audio Transcriber? 

### 🐛 **Reportar Bugs**
- Abra uma [issue](https://github.com/yourusername/audio-transcriber/issues)
- Descreva o problema detalhadamente
- Inclua logs e screenshots

### ✨ **Sugerir Funcionalidades**
- Compartilhe suas ideias
- Vote em funcionalidades existentes
- Participe das discussões

### 🔧 **Desenvolver**
```bash
# Fork o projeto
git fork https://github.com/yourusername/audio-transcriber

# Crie uma branch
git checkout -b minha-funcionalidade

# Faça suas alterações
git commit -m "Adiciona nova funcionalidade"

# Envie um PR
git push origin minha-funcionalidade
```

## 📝 Licença

**MIT License** - Use, modifique e distribua livremente!

---

<div align="center">

**🎙️ Desenvolvido com ❤️ usando Python, PySide6 e OpenAI Whisper**

*Transformando áudio em texto com elegância e velocidade*

[![⭐ Star no GitHub](https://img.shields.io/badge/⭐-Star%20no%20GitHub-yellow.svg)](https://github.com/yourusername/audio-transcriber)
[![🐛 Reportar Bug](https://img.shields.io/badge/🐛-Reportar%20Bug-red.svg)](https://github.com/yourusername/audio-transcriber/issues)
[![💡 Sugerir Funcionalidade](https://img.shields.io/badge/💡-Sugerir%20Funcionalidade-blue.svg)](https://github.com/yourusername/audio-transcriber/issues)

[⬆ Voltar ao topo](#-audio-transcriber)

</div>

Feito por [Douglas Siqueira](https://dsiqueira.com/sobre) · [dsiqueira.com](https://dsiqueira.com)
