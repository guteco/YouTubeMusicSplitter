# 🎵 YouTube Music Splitter

Uma ferramenta simples e poderosa para **baixar músicas do YouTube** e **separar faixas de álbuns/mixes automaticamente**, com interface gráfica.

---

## ✨ Funcionalidades

- 🎼 **Detecção automática de capítulos**  
  Baixe um álbum completo (vídeo único) e o programa detecta e corta as músicas automaticamente.

- 📂 **Download de playlists**  
  Baixe todos os vídeos de uma playlist do YouTube de uma vez.

- 🔊 **Conversão para MP3**  
  Todos os áudios são convertidos para MP3 com metadados básicos.

- ⚙️ **Gerenciamento automático de dependências**  
  O programa utiliza FFmpeg para processamento de áudio.

---

## ⚠️ Requisitos Importantes (LEIA ISSO)

Este projeto **NÃO é compatível com Python 3.13 ou superior (3.14+)**.

Motivo técnico:
- A biblioteca `pydub` depende do módulo `audioop`
- O módulo `audioop` foi **removido do Python a partir da versão 3.13**

### ✅ Versões compatíveis do Python

- ✔️ **Python 3.11 (recomendado)**
- ✔️ Python 3.12

### ❌ Versões incompatíveis

- ❌ Python 3.13
- ❌ Python 3.14+

---

## 🚀 Instalação (Windows)

### 1️⃣ Instale o Python 3.11

Baixe em:
https://www.python.org/downloads/release/python-3119/

Durante a instalação:
- Marque **Add Python to PATH**
- Marque **Install launcher for all users** (se disponível)

---

### 2️⃣ Crie um ambiente virtual

No diretório do projeto:

```bash
py -3.11 -m venv venv
venv\Scripts\activate
```

Confirme:
```bash
python --version
```
Saída esperada:
```text
Python 3.11.x
```

---

### 3️⃣ Instale as dependências

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 🎬 FFmpeg (Obrigatório)

O FFmpeg é essencial para o processamento de áudio.

### Opção recomendada (manual):

1. Baixe em:
   https://www.gyan.dev/ffmpeg/builds/
2. Escolha **release essentials**
3. Extraia e adicione a pasta `bin` ao **PATH do Windows**

Verifique:
```bash
ffmpeg -version
```

---

## 🖥️ Como Usar

Execute a interface gráfica:

```bash
python gui.py
```

### 🎧 Para Álbuns / Mixes (Tracklist)

1. Cole o link do vídeo do YouTube
2. Marque **Detectar Capítulos Automaticamente**
3. Clique em **Iniciar Processamento**
4. Se a detecção falhar:
   - Desmarque a opção
   - Cole os timestamps manualmente no formato:
     ```
     00:00 - Nome da Música
     ```

---

### 📜 Para Playlists

1. Vá na aba **Playlist**
2. Cole o link da playlist do YouTube
3. Clique em **Baixar Playlist Inteira**

---

## 📂 Onde ficam os arquivos?

Todos os arquivos baixados e processados são salvos na pasta:

```
/downloads
```

Dentro do diretório do projeto.

---

## 🧠 Observações Técnicas

- Evite usar versões muito novas do Python para projetos de áudio/vídeo
- Sempre utilize ambientes virtuais (`venv`)
- Python 3.11 é a versão mais estável para esse projeto

---

## 👨‍💻 Créditos

**Desenvolvido por Augusto Severo (@guteco)**  
com apoio do Gemini 🤖  

> *We accept Pizza 🍕*

