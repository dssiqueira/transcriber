#!/bin/bash

echo "🔍 Verificando se o Homebrew está instalado..."
if ! command -v brew &> /dev/null; then
    echo "⚙️ Instalando Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
else
    echo "✅ Homebrew já está instalado"
fi

echo "⚙️ Instalando dependências do sistema..."
brew install portaudio ffmpeg

echo "🐍 Criando ambiente virtual Python..."
python3 -m venv venv
source venv/bin/activate

echo "⬆️ Atualizando pip..."
pip install --upgrade pip

echo "📦 Instalando dependências Python..."
pip install -r requirements.txt

echo "✨ Instalação concluída!"
echo "Para executar o programa, use:"
echo "source venv/bin/activate && python main.py"
