import customtkinter as ctk
import threading
from tkinter import filedialog, messagebox
from youtube_music_splitter import YouTubeMusicSplitter, DependencyManager

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("YouTube Music Splitter v2.0")
        self.geometry("800x600")

        # self.splitter will be initialized after UI is ready


        # Layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1) # Log area expands

        # Header
        self.header_frame = ctk.CTkFrame(self)
        self.header_frame.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        
        self.label_title = ctk.CTkLabel(self.header_frame, text="YouTube Music Splitter", font=("Roboto", 24, "bold"))
        self.label_title.pack(pady=10)

        # Dependency Check moved to end of init


        # Tabs
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="ew")
        
        self.tab_tracklist = self.tabview.add("Tracklist (Álbum/Mix)")
        self.tab_playlist = self.tabview.add("Playlist (YouTube)")

        self.setup_tracklist_tab()
        self.setup_playlist_tab()

        # Log Area
        self.log_frame = ctk.CTkFrame(self)
        self.log_frame.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="nsew")
        self.log_frame.grid_columnconfigure(0, weight=1)
        self.log_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(self.log_frame, text="Log de Progresso:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        
        self.log_box = ctk.CTkTextbox(self.log_frame, state="disabled")
        self.log_box.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")

        # Initialize backend logic here (now that UI is ready for logs)
        self.splitter = YouTubeMusicSplitter(progress_callback=self.log_message)

        # Run dependency check after UI is ready
        self.after(200, self.check_deps)
        
        # Credits
        self.credits_label = ctk.CTkLabel(self, text="Desenvolvido por Augusto Severo - @guteco e Gemini - We accept Pizza 🍕", font=("Arial", 10), text_color="gray")
        self.credits_label.grid(row=3, column=0, pady=(0, 10))

    def log_message(self, message):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", str(message) + "\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def check_deps(self):
        if not DependencyManager.get_ffmpeg_path():
            msg = "FFmpeg não encontrado! Deseja baixar automaticamente? (Isso pode levar alguns minutos)"
            if messagebox.askyesno("Dependência Faltando", msg):
                threading.Thread(target=self.download_ffmpeg_thread, daemon=True).start()
            else:
                self.log_message("AVISO: FFmpeg não encontrado. Algumas funções podem falhar.")
        else:
            self.log_message("FFmpeg detectado com sucesso.")

    def download_ffmpeg_thread(self):
        self.log_message("Iniciando download do FFmpeg...")
        success = DependencyManager.download_ffmpeg(progress_callback=self.log_message)
        if success:
             self.log_message("FFmpeg pronto para uso!")

    def setup_tracklist_tab(self):
        tab = self.tab_tracklist
        
        ctk.CTkLabel(tab, text="URL do Vídeo:").pack(pady=5)
        self.url_entry = ctk.CTkEntry(tab, width=500, placeholder_text="https://www.youtube.com/watch?v=...")
        self.url_entry.pack(pady=5)

        self.auto_chapters_var = ctk.BooleanVar(value=True)
        self.chk_chapters = ctk.CTkCheckBox(tab, text="Detectar Capítulos Automaticamente", variable=self.auto_chapters_var, command=self.toggle_manual_timestamps)
        self.chk_chapters.pack(pady=10)

        self.manual_frame = ctk.CTkFrame(tab) # Container for manual input
        # Initially hidden if Auto is True
        
        ctk.CTkLabel(self.manual_frame, text="Cole timestamps manualmete se a detecção falhar:").pack()
        self.timestamps_input = ctk.CTkTextbox(self.manual_frame, height=100, width=500)
        self.timestamps_input.pack(pady=5)

        ctk.CTkButton(tab, text="Iniciar Processamento", command=self.start_tracklist_thread).pack(pady=20)

    def toggle_manual_timestamps(self):
        if not self.auto_chapters_var.get():
            self.manual_frame.pack(pady=5)
        else:
            self.manual_frame.pack_forget()

    def setup_playlist_tab(self):
        tab = self.tab_playlist
        
        ctk.CTkLabel(tab, text="URL da Playlist:").pack(pady=5)
        self.playlist_url_entry = ctk.CTkEntry(tab, width=500, placeholder_text="https://www.youtube.com/playlist?list=...")
        self.playlist_url_entry.pack(pady=5)

        ctk.CTkButton(tab, text="Baixar Playlist Inteira", command=self.start_playlist_thread).pack(pady=20)

    def start_tracklist_thread(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Erro", "Insira uma URL válida.")
            return
        
        threading.Thread(target=self.run_tracklist_process, args=(url,), daemon=True).start()

    def run_tracklist_process(self, url):
        self.log_message(f"Iniciando: {url}")
        
        if self.auto_chapters_var.get():
            success = self.splitter.process_with_chapters(url)
            if not success:
                self.log_message("Falha na detecção automática. Tente inserir timestamps manualmente.")
                self.chk_chapters.deselect()
                self.toggle_manual_timestamps()
        else:
            timestamps = self.timestamps_input.get("1.0", "end")
            self.splitter.process_manual(url, timestamps)

    def start_playlist_thread(self):
        url = self.playlist_url_entry.get().strip()
        if not url: return
        threading.Thread(target=self.run_playlist_process, args=(url,), daemon=True).start()

    def run_playlist_process(self, url):
        self.splitter.process_playlist(url)

if __name__ == "__main__":
    app = App()
    app.mainloop()
