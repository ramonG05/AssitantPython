"""
Gestor del sistema operativo y aplicaciones
"""
import subprocess
import platform
import webbrowser
import requests
import re
from bs4 import BeautifulSoup
from config.settings import APPLICATIONS, URLS
from utils import SystemManagerError


class SystemManager:
    """Clase encargada de interactuar con el sistema operativo"""
    
    def __init__(self):
        self.system = platform.system()
        self.apps = APPLICATIONS.get(self.system, {})
    
    def open_application(self, app_name):
        """
        Abre una aplicación según el sistema operativo
        
        Args:
            app_name (str): Nombre de la aplicación a abrir
            
        Returns:
            bool: True si la aplicación se abrió correctamente
            
        Raises:
            SystemManagerError: Si hay problemas al abrir la aplicación
        """
        try:
            app_name_lower = app_name.lower()
            
            if self.system == "Windows":
                return self._open_windows_app(app_name_lower)
            elif self.system == "Darwin":  # macOS
                return self._open_macos_app(app_name_lower)
            elif self.system == "Linux":
                return self._open_linux_app(app_name)
            else:
                raise SystemManagerError(f"Sistema operativo no soportado: {self.system}")
                
        except Exception as e:
            raise SystemManagerError(f"Error al abrir la aplicación {app_name}: {e}")
    
    def _open_windows_app(self, app_name):
        """Abre una aplicación en Windows"""
        if app_name in self.apps:
            app_path = self.apps[app_name]
            if isinstance(app_path, list):
                # Intentar múltiples rutas para la aplicación
                for path in app_path:
                    try:
                        subprocess.Popen(path)
                        return True
                    except FileNotFoundError:
                        continue
                return False
            else:
                subprocess.Popen(app_path)
                return True
        else:
            # Intenta ejecutar el nombre directamente
            subprocess.Popen(app_name)
            return True
    
    def _open_macos_app(self, app_name):
        """Abre una aplicación en macOS"""
        if app_name in self.apps:
            subprocess.Popen(["open", "-a", self.apps[app_name]])
            return True
        else:
            # Intenta abrir directamente
            subprocess.Popen(["open", "-a", app_name])
            return True
    
    def _open_linux_app(self, app_name):
        """Abre una aplicación en Linux"""
        subprocess.Popen([app_name])
        return True
    
    def play_music(self, song_query):
        """
        Reproduce música buscando en YouTube
        
        Args:
            song_query (str): Consulta de búsqueda para la canción
            
        Returns:
            bool: True si se pudo reproducir la música
        """
        try:
            # Buscar el video en YouTube
            video_url = self._search_youtube(song_query)
            
            if video_url:
                # Abrir el video directamente
                webbrowser.open(video_url)
                return True
            else:
                # Si no se encuentra video específico, abrir búsqueda general
                search_url = URLS['youtube_search'].format(song_query.replace(" ", "+"))
                webbrowser.open(search_url)
                return True
                
        except Exception as e:
            print(f"Error al reproducir música: {e}")
            # En caso de error, intentar abrir búsqueda básica
            try:
                search_url = URLS['youtube_search'].format(song_query.replace(" ", "+"))
                webbrowser.open(search_url)
                return True
            except:
                return False
    
    def _search_youtube(self, query):
        """
        Busca un video en YouTube y devuelve la URL del primero
        
        Args:
            query (str): Consulta de búsqueda
            
        Returns:
            str: URL del video o None si no se encuentra
        """
        try:
            search_url = URLS['youtube_search'].format(query.replace(" ", "+"))
            response = requests.get(search_url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Buscar el ID del primer video en los resultados
            scripts = soup.find_all('script')
            
            for script in scripts:
                if script.string and 'var ytInitialData' in script.string:
                    # Buscar el primer videoId en el script
                    match = re.search(r'videoId":"([^"]+)"', script.string)
                    if match:
                        video_id = match.group(1)
                        return URLS['youtube_watch'].format(video_id)
            
            return None
            
        except Exception as e:
            print(f"Error en búsqueda de YouTube: {e}")
            return None