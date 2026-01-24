# YouTube Music Splitter

Uma ferramenta simples e poderosa para baixar músicas do YouTube e separar faixas de álbuns/mixes automaticamente.

## ✨ Funcionalidades

*   **Detecção Automática de Capítulos:** Baixe um álbum completo (vídeo único) e o programa detecta e corta as músicas automaticamente.
*   **Download de Playlists:** Baixe todos os vídeos de uma playlist do YouTube de uma vez.
*   **Conversão MP3:** Todos os áudios são convertidos para MP3 com metadados básicos.
*   **Gerenciamento Automático de Dependências:** O programa baixa o FFmpeg (necessário para áudio) automaticamente se ele não estiver instalado.

## 🚀 Como Instalar

1.  Certifique-se de ter o **Python** instalado.
2.  Instale as dependências:
    ```bash
    pip install -r requirements.txt
    ```
3.  (Opcional) Se você já tiver o FFmpeg instalado, o programa o usará. Caso contrário, ele perguntará se você deseja baixar na primeira execução.

## 🖥️ Como Usar

Execute o arquivo da interface gráfica:
```bash
python gui.py
```

### Para Álbuns / Mixes (Tracklist)
1.  Cole o link do vídeo do YouTube.
2.  Marque "Detectar Capítulos Automaticamente".
3.  Clique em **Iniciar Processamento**.
4.  *Se a detecção falhar:* Desmarque a caixa e cole a lista de timestamps manualmente (formato `00:00 - Nome da Música`).

### Para Playlists
1.  Vá na aba "Playlist".
2.  Cole o link da playlist.
3.  Clique em **Baixar Playlist Inteira**.

## 📂 Onde estão meus arquivos?
Os arquivos baixados e cortados serão salvos na pasta `downloads/` dentro do diretório do projeto.

---
**Desenvolvido por Augusto Severo - @guteco e Gemini - We accept Pizza 🍕**
