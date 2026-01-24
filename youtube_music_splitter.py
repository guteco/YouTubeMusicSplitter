#!/usr/bin/env python3

import os
import sys
import re
import shutil
import zipfile
import requests
import subprocess
from pathlib import Path
import yt_dlp
from pydub import AudioSegment

class DependencyManager:
    FFMPEG_URL = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
    
    @staticmethod
    def get_ffmpeg_path():
        """Returns valid path to ffmpeg executable or None."""
        # 1. Check PATH
        path = shutil.which("ffmpeg")
        if path: return path
        
        # 2. Check local bin folder
        local_bin = Path("./bin/ffmpeg.exe").resolve()
        if local_bin.exists(): return str(local_bin)

        # 3. Check root folder
        local_root = Path("./ffmpeg.exe").resolve()
        if local_root.exists(): return str(local_root)
        
        return None

    @staticmethod
    def download_ffmpeg(progress_callback=None):
        """Downloads and extracts FFmpeg locally."""
        try:
            url = DependencyManager.FFMPEG_URL
            if progress_callback: progress_callback("Baixando FFmpeg (isso pode demorar)...")
            
            response = requests.get(url, stream=True)
            total_size = int(response.headers.get('content-length', 0))
            block_size = 1024 * 1024 # 1 Megabyte
            
            zip_path = Path("ffmpeg_temp.zip")
            
            with open(zip_path, 'wb') as file:
                downloaded = 0
                for data in response.iter_content(block_size):
                    file.write(data)
                    downloaded += len(data)
                    if progress_callback and total_size > 0:
                        percent = (downloaded / total_size) * 100
                        progress_callback(f"Baixando FFmpeg: {percent:.1f}%")

            if progress_callback: progress_callback("Extraindo FFmpeg...")
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # Find the bin folder inside the zip
                for file in zip_ref.namelist():
                    if file.endswith("ffmpeg.exe") or file.endswith("ffprobe.exe"):
                        source = zip_ref.open(file)
                        target_path = Path("./bin/") / Path(file).name
                        target_path.parent.mkdir(parents=True, exist_ok=True)
                        with open(target_path, "wb") as target:
                            shutil.copyfileobj(source, target)
                        source.close() # Explicitly close source
            
            # Retrieve zip_ref is closed here automatically
            
            try:
                zip_path.unlink() # Cleanup zip
            except Exception as e:
                # If we cannot delete the temp file, it's fine, just log warnings or ignore
                if progress_callback: progress_callback(f"Aviso: Não foi possível apagar temporário (sem problemas): {e}")

            # Set environment variable for the current session
            os.environ["PATH"] += os.pathsep + str(Path("./bin").resolve())
            
            if progress_callback: progress_callback("FFmpeg configurado com sucesso!")
            return True
        except Exception as e:
            if progress_callback: progress_callback(f"Erro no processo do FFmpeg: {e}")
            return False

class YouTubeMusicSplitter:
    def __init__(self, output_dir="./downloads", progress_callback=None):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.temp_dir = self.output_dir / "temp"
        self.temp_dir.mkdir(exist_ok=True)
        self.progress_callback = progress_callback
        
        # Ensure AudioSegment finds ffmpeg
        ffmpeg_path = DependencyManager.get_ffmpeg_path()
        if ffmpeg_path:
            # Force absolute path for pydub
            AudioSegment.converter = ffmpeg_path
            AudioSegment.ffmpeg = ffmpeg_path
            AudioSegment.ffprobe = ffmpeg_path.replace("ffmpeg.exe", "ffprobe.exe")
            
            directory = os.path.dirname(ffmpeg_path)
            if directory not in os.environ["PATH"]:
                 os.environ["PATH"] += os.pathsep + directory

    def log(self, message):
        if self.progress_callback:
            self.progress_callback(message)
        else:
            print(message)

    def get_video_info(self, youtube_url):
        """Retrieves video metadata including chapters."""
        ydl_opts = {'quiet': True}
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(youtube_url, download=False)
                return info
        except Exception as e:
            self.log(f"Erro ao obter info: {e}")
            return None

    def sanitize_filename(self, filename):
        sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
        return sanitized.strip()

    def cleanup_temp(self):
        try:
            for file in self.temp_dir.glob('*'):
                file.unlink()
            self.temp_dir.rmdir()
        except Exception:
            pass

    def convert_webm_to_mp3(self, src_dir, dst_dir):
        dst_dir.mkdir(exist_ok=True)
        if hasattr(AudioSegment.converter, 'which'): # Verify pydub/ffmpeg
            AudioSegment.converter = DependencyManager.get_ffmpeg_path() or "ffmpeg"

        files = list(src_dir.glob('*'))
        total_files = len(files)
        
        for idx, file in enumerate(files):
            self.log(f"Convertendo {idx+1}/{total_files}: {file.name}")
            if file.suffix.lower() in ['.webm', '.m4a', '.opus', '.mp4']:
                try:
                    audio = AudioSegment.from_file(str(file))
                    target_path = dst_dir / (file.stem + ".mp3")
                    audio.export(target_path, format="mp3")
                except Exception as e:
                    self.log(f"Erro na conversão de {file.name}: {e}")
            elif file.suffix.lower() == '.mp3':
                target_path = dst_dir / file.name
                file.rename(target_path)

    def download_audio(self, youtube_url, is_playlist=False):
        self.log("Iniciando download...")
        
        def ydl_progress_hook(d):
            if d['status'] == 'downloading':
                p = d.get('_percent_str', '0%')
                self.log(f"Baixando: {p}")

        ydl_opts = {
            'format': 'bestaudio/best',
            'extractaudio': True,
            'audioformat': 'mp3',
            'outtmpl': str(self.temp_dir / '%(id)s.%(ext)s'),
            'quiet': False,
            'yesplaylist': is_playlist,
            'nopart': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=True)
            video_title = info.get('title', 'Unknown')
            
            if is_playlist:
                return None, video_title
            
            # For header photo (thumbnail) - simple approach is to just get audio first
            # Advanced metadata would require downloading thumbnail separately and attaching
            
            # Find the downloaded file
            files_found = list(self.temp_dir.glob('*'))
            for file in files_found:
                if file.is_file() and file.suffix in ['.webm', '.m4a', '.mp3', '.opus', '.mp4']:
                    return file, video_title
            
            self.log(f"ERRO CRÍTICO: Download parecia ok, mas arquivo sumiu.")
            self.log(f"Conteúdo da pasta temp: {[f.name for f in files_found]}")
            raise FileNotFoundError("Arquivo de áudio não encontrado na pasta temporária.")

    def get_duration(self, file_path):
        """Get duration in seconds using ffprobe."""
        try:
            cmd = [
                str(Path(DependencyManager.get_ffmpeg_path()).parent / "ffprobe.exe"),
                "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                str(file_path)
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return float(result.stdout.strip())
        except Exception as e:
            self.log(f"Erro ao ler duração com ffprobe: {e}")
            return None

    def split_audio(self, audio_file, timestamps, album_name):
        self.log("Processando divisão de faixas (FFmpeg nativo)...")
        
        ffmpeg_exe = DependencyManager.get_ffmpeg_path()
        if not ffmpeg_exe:
            self.log("ERRO: FFmpeg não encontrado para divisão.")
            return [], None

        total_duration = self.get_duration(audio_file)
        if total_duration is None: return [], None

        output_folder = self.output_dir / self.sanitize_filename(album_name)
        output_folder.mkdir(exist_ok=True)
        tracks_created = []

        for i, (start_time, title) in enumerate(timestamps):
            start_time = float(start_time)
            # Calculate duration or end time
            end_time = timestamps[i + 1][0] if i + 1 < len(timestamps) else total_duration
            
            # Formatting track number
            track_number = f"{i+1:02d}"
            filename = f"{track_number} - {self.sanitize_filename(title)}.mp3"
            output_path = output_folder / filename
            
            # FFmpeg splitting command
            # -i input -ss start -to end -map 0:a -c:a libmp3lame -q:a 2 -metadata ... output.mp3
            cmd = [
                ffmpeg_exe,
                "-y", # Overwrite
                "-i", str(audio_file),
                "-ss", str(start_time),
                "-to", str(end_time),
                "-map", "0:a", # Map audio only
                "-c:a", "libmp3lame", # Enforce MP3
                "-q:a", "2", # High quality (VBR)
                "-metadata", f"artist=YouTube Splitter",
                "-metadata", f"album={album_name}",
                "-metadata", f"title={title}",
                "-metadata", f"track={i+1}/{len(timestamps)}",
                str(output_path)
            ]
            
            # Remove -to for last track to ensure we get everything? 
            # Actually -to works fine if duration is correct.
            
            try:
                # self.log(f"Convertendo: {title}...")
                subprocess.run(cmd, check=True, capture_output=True)
                self.log(f"✅ Faixa {track_number}: {title}")
                tracks_created.append(str(output_path))
            except subprocess.CalledProcessError as e:
                self.log(f"❌ Erro ao converter '{title}': {e}")
            
        return tracks_created, str(output_folder)

    def process_with_chapters(self, youtube_url):
        info = self.get_video_info(youtube_url)
        if not info: return
        
        chapters = info.get('chapters')
        if not chapters:
            self.log("Nenhum capítulo detectado automaticamente.")
            return False
            
        timestamps = []
        for chapter in chapters:
            timestamps.append((chapter['start_time'], chapter['title']))
            
        self.log(f"Detectados {len(timestamps)} capítulos.")
        audio_file, title = self.download_audio(youtube_url, is_playlist=False)
        self.split_audio(audio_file, timestamps, title)
        self.cleanup_temp()
        self.log("Concluído com sucesso!")
        return True

    def process_manual(self, youtube_url, timestamps_text):
        timestamps = []
        for line in timestamps_text.strip().split('\n'):
            if not line.strip(): continue
            parts = re.match(r'(?:\d+\.\s*)?(\d{1,2}:\d{2}(?::\d{2})?)\s*[-–—]\s*(.+)', line.strip())
            if parts:
                t_str, t_title = parts.groups()
                # Parse time
                time_parts = list(map(int, t_str.split(':')))
                seconds = 0
                if len(time_parts) == 2: seconds = time_parts[0]*60 + time_parts[1]
                else: seconds = time_parts[0]*3600 + time_parts[1]*60 + time_parts[2]
                timestamps.append((seconds, t_title.strip()))
        
        if not timestamps:
            self.log("Nenhum timestamp válido identificado.")
            return

        audio_file, title = self.download_audio(youtube_url)
        self.split_audio(audio_file, timestamps, title)
        self.cleanup_temp()
        self.log("Concluído com sucesso!")

    def process_playlist(self, youtube_url):
        self.log("Baixando playlist...")
        dummy, title = self.download_audio(youtube_url, is_playlist=True)
        final_dir = self.output_dir / self.sanitize_filename(title)
        self.convert_webm_to_mp3(self.temp_dir, final_dir)
        self.cleanup_temp()
        self.log(f"Playlist salva em {final_dir}")
