#!/bin/bash

# Função para verificar se um comando foi bem sucedido
check_error() {
    if [ $? -ne 0 ]; then
        echo "❌ Erro: $1"
        exit 1
    fi
}

echo "🔍 Verificando versão do Python..."
python3 --version | grep "Python 3" > /dev/null
check_error "Python 3 não encontrado. Por favor, instale o Python 3."

echo "🔍 Verificando se o Homebrew está instalado..."
if ! command -v brew &> /dev/null; then
    echo "⚙️ Instalando Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    check_error "Falha ao instalar o Homebrew"
else
    echo "✅ Homebrew já está instalado"
fi

echo "⚙️ Instalando/Atualizando dependências do sistema..."
brew install portaudio ffmpeg
check_error "Falha ao instalar dependências via Homebrew"

echo "🐍 Criando ambiente virtual Python..."
python3 -m venv venv
check_error "Falha ao criar ambiente virtual"

echo "🔄 Ativando ambiente virtual..."
source venv/bin/activate
check_error "Falha ao ativar ambiente virtual"

echo "⬆️ Atualizando pip..."
pip install --upgrade pip
check_error "Falha ao atualizar pip"

echo "📦 Instalando dependências Python (exceto PyAudio)..."
# Primeiro instalamos todas as dependências exceto PyAudio
grep -v "pyaudio" requirements.txt | xargs pip install
check_error "Falha ao instalar dependências Python principais"

echo "📦 Tentando instalar PyAudio..."
# Agora tentamos instalar o PyAudio
if ! pip install pyaudio; then
    echo "⚠️ Tentando instalar PyAudio via Homebrew..."
    brew install portaudio
    export LDFLAGS="-L/opt/homebrew/lib"
    export CPPFLAGS="-I/opt/homebrew/include"
    pip install --global-option="build_ext" --global-option="-I/opt/homebrew/include" --global-option="-L/opt/homebrew/lib" pyaudio
    check_error "Falha ao instalar PyAudio. Por favor, verifique se portaudio está instalado corretamente"
fi

echo "✨ Instalação concluída!"
echo "Para executar o programa, use:"
echo "source venv/bin/activate && python main.py"
