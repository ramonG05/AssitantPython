import sys
import speech_recognition as sr
import subprocess
import webbrowser
import os
import re
import platform
import requests
import traceback
from bs4 import BeautifulSoup
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QLabel, 
                            QVBoxLayout, QWidget, QTextEdit, QHBoxLayout, QSystemTrayIcon, QMenu, QAction, QStyle)
from PyQt5.QtGui import QFont, QIcon, QPalette, QColor
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer

# Importamos keyboard para detectar la tecla F1 globalmente
try:
    import keyboard
    KEYBOARD_AVAILABLE = True
except ImportError:
    KEYBOARD_AVAILABLE = False
    print("La biblioteca 'keyboard' no está disponible. La funcionalidad de tecla F1 estará desactivada.")

class EscuchaThread(QThread):
    """Hilo separado para escuchar comandos de voz sin bloquear la interfaz"""
    comando_detectado = pyqtSignal(str)
    estado_actualizado = pyqtSignal(str)
    finalizado = pyqtSignal()
    
    def __init__(self, asistente):
        super().__init__()
        self.asistente = asistente
        self.is_running = True
        
    def run(self):
        try:
            self.estado_actualizado.emit("Escuchando...")
            comando = self.asistente.escuchar()
            if comando:
                self.comando_detectado.emit(comando)
                try:
                    respuesta = self.asistente.procesar_comando(comando)
                    self.estado_actualizado.emit(respuesta)
                    if not self.asistente.escuchando or respuesta == "salir":
                        self.estado_actualizado.emit("Acción completada. Presiona F1 o el botón 'Escuchar' para un nuevo comando.")
                except Exception as e:
                    self.estado_actualizado.emit(f"Error al procesar el comando: {str(e)}")
            else:
                self.estado_actualizado.emit("No se detectó ningún comando. Intenta de nuevo.")
        except Exception as e:
            self.estado_actualizado.emit(f"Error en el hilo de escucha: {str(e)}")
        finally:
            self.is_running = False
            self.finalizado.emit()

class AsistenteVoz:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.sistema = platform.system()  # Detecta el sistema operativo
        self.escuchando = True
        # Configuración más tolerante para el reconocimiento
        self.recognizer.pause_threshold = 0.8  # Tiempo de pausa entre frases
        self.recognizer.energy_threshold = 300  # Umbral de energía para considerar un sonido como habla
        
    def escuchar(self):
        """Escucha el micrófono y devuelve el texto reconocido"""
        try:
            with sr.Microphone() as source:
                # Ajustar para ruido ambiental
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                print("Escuchando... Hable ahora")
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
                
            try:
                texto = self.recognizer.recognize_google(audio, language="es-ES")
                print(f"Se reconoció: {texto}")
                return texto.lower()
            except sr.UnknownValueError:
                print("No se pudo reconocer el audio")
                return ""
            except sr.RequestError as e:
                print(f"Error en la solicitud a Google Speech Recognition; {e}")
                return ""
            except Exception as e:
                print(f"Error desconocido en reconocimiento: {e}")
                return ""
        except Exception as e:
            print(f"Error al acceder al micrófono: {e}")
            return ""
    
    def abrir_aplicacion(self, nombre_app):
        """Abre una aplicación según el sistema operativo"""
        try:
            if self.sistema == "Windows":
                # Lista de aplicaciones comunes y sus rutas/comandos en Windows
                apps = {
                    "brave": "brave.exe",
                    "navegador": "brave.exe",
                    "chrome": "chrome.exe",
                    "firefox": "firefox.exe",
                    "word": "winword.exe",
                    "excel": "excel.exe",
                    "bloc de notas": "notepad.exe",
                    "notepad": "notepad.exe",
                    "calculadora": "calc.exe",
                    "explorador de archivos": "explorer.exe",
                    "marvel rivals": "MarvelRivals_Launcher.exe",
                }
                
                if nombre_app.lower() in apps:
                    subprocess.Popen(apps[nombre_app.lower()])
                    self.escuchando = False  # Detiene el ciclo de escucha después de abrir la aplicación
                    return True
                else:
                    # Intenta ejecutar el nombre directamente
                    subprocess.Popen(nombre_app)
                    self.escuchando = False  # Detiene el ciclo de escucha después de abrir la aplicación
                    return True
                    
            elif self.sistema == "Darwin":  # macOS
                apps = {
                    "brave": "Brave Browser",
                    "navegador": "Brave Browser",
                    "chrome": "Google Chrome",
                    "safari": "Safari",
                    "firefox": "Firefox",
                    "word": "Microsoft Word",
                    "excel": "Microsoft Excel",
                    "notas": "Notes",
                    "calculadora": "Calculator",
                    "finder": "Finder",
                }
                
                if nombre_app.lower() in apps:
                    subprocess.Popen(["open", "-a", apps[nombre_app.lower()]])
                    self.escuchando = False  # Detiene el ciclo de escucha después de abrir la aplicación
                    return True
                else:
                    # Intenta abrir directamente
                    subprocess.Popen(["open", "-a", nombre_app])
                    self.escuchando = False  # Detiene el ciclo de escucha después de abrir la aplicación
                    return True
                    
            elif self.sistema == "Linux":
                # En Linux, simplemente intenta ejecutar el comando
                subprocess.Popen([nombre_app])
                self.escuchando = False  # Detiene el ciclo de escucha después de abrir la aplicación
                return True
                
            return False
        except Exception as e:
            return False
    
    def reproducir_musica(self, cancion):
        """Abre Brave y reproduce la primera canción encontrada en YouTube"""
        query = cancion.replace(" ", "+")
        search_url = f"https://www.youtube.com/results?search_query={query}"
        
        try:
            # Obtenemos la página de resultados
            response = requests.get(search_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Buscamos el ID del primer video en los resultados
            scripts = soup.find_all('script')
            video_id = None
            
            for script in scripts:
                if script.string and 'var ytInitialData' in script.string:
                    # Buscamos el primer videoId en el script
                    match = re.search(r'videoId":"([^"]+)"', script.string)
                    if match:
                        video_id = match.group(1)
                        break
            
            if video_id:
                # Formamos la URL directa del video
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                
                # Abrimos Brave
                self.abrir_aplicacion("brave")
                
                # Abrimos el video directamente
                webbrowser.open(video_url)
                self.escuchando = False  # Detiene el ciclo de escucha después de reproducir música
                return True
            else:
                # Si no encontramos video_id, caemos al método anterior
                self.abrir_aplicacion("brave")
                webbrowser.open(search_url)
                self.escuchando = False  # Detiene el ciclo de escucha después de abrir la búsqueda
                return True
                
        except Exception as e:
            # En caso de error, abrimos la búsqueda general
            self.abrir_aplicacion("brave")
            webbrowser.open(search_url)
            self.escuchando = False  # Detiene el ciclo de escucha incluso si hay un error
            return True
    
    def reiniciar_escucha(self):
        """Reinicia el estado de escucha para que el asistente vuelva a escuchar comandos"""
        self.escuchando = True
    
    def procesar_comando(self, comando):
        """Procesa el comando de voz y ejecuta la acción correspondiente"""
        # Comando para abrir aplicaciones
        if re.search(r"(abrir|abre|ejecuta|ejecutar|inicia|iniciar)\s+(\w+)", comando):
            match = re.search(r"(abrir|abre|ejecuta|ejecutar|inicia|iniciar)\s+(.+)", comando)
            if match:
                app_name = match.group(2).strip()
                self.abrir_aplicacion(app_name)
                return f"Abriendo {app_name}"
        
        # Comando para reproducir música
        elif re.search(r"(reproducir|reproduce|pon|poner|escuchar|tocar)\s+(.+)", comando):
            match = re.search(r"(reproducir|reproduce|pon|poner|escuchar|tocar)\s+(.+)", comando)
            if match:
                cancion = match.group(2).strip()
                self.reproducir_musica(cancion)
                return f"Reproduciendo {cancion}"
                
        # Comando para buscar archivos (básico, se puede mejorar después)
        elif re.search(r"(buscar|busca|encuentra|encontrar)\s+archivo[s]?\s+(.+)", comando):
            match = re.search(r"(buscar|busca|encuentra|encontrar)\s+archivo[s]?\s+(.+)", comando)
            if match:
                archivo = match.group(2).strip()
                return f"La búsqueda de archivos se implementará en una versión futura."
        
        # Comando de ayuda
        elif re.search(r"(ayuda|ayúdame|qué puedes hacer|funciones)", comando):
            return "Puedo abrir aplicaciones diciendo 'abrir [nombre]' y reproducir música diciendo 'reproducir [canción]'."
        
        # Comando para salir
        elif re.search(r"(salir|terminar|finalizar|adiós)", comando):
            self.escuchando = False  # Detiene el ciclo de escucha al salir
            return "salir"
        
        else:
            return "No entendí ese comando. Prueba decir 'ayuda' para ver lo que puedo hacer."

class AsistenteGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.asistente = AsistenteVoz()
        self.initUI()
        
        # Bandera para rastrear si la ventana está visible
        self.esta_visible = True
        
        # Variable para controlar si la tecla F1 está habilitada
        self.tecla_f1_habilitada = True
        
        # Tiempo de espera entre activaciones de F1 (en milisegundos)
        self.tiempo_espera_f1 = 500
        
        # Variable para controlar si hay un proceso de escucha activo
        self.escucha_activa = False
        
        try:
            if KEYBOARD_AVAILABLE:
                # Configurar detector para cuando se presiona F1
                keyboard.on_press_key('f1', self.on_f1_press)
                # No usamos el detector tradicional de hotkey para evitar activaciones múltiples
        except Exception as e:
            print(f"Error al configurar la tecla F1: {e}")
            self.resultado_text.append(f"\nNo se pudo configurar la tecla F1: {str(e)}")
            self.tecla_f1_habilitada = False
        
    def on_f1_press(self, event):
        """Maneja el evento cuando se presiona F1"""
        if self.tecla_f1_habilitada and not self.escucha_activa:
            # Deshabilitar temporalmente la tecla F1
            self.tecla_f1_habilitada = False
            
            # Iniciar la escucha
            self.iniciar_escucha()
            
            # Configurar un temporizador para rehabilitar la tecla después de un tiempo
            QTimer.singleShot(self.tiempo_espera_f1, self.rehabilitar_f1)
            
    def rehabilitar_f1(self):
        """Rehabilita la tecla F1 después del tiempo de espera"""
        self.tecla_f1_habilitada = True
        
    def initUI(self):
        # Configuración de la ventana principal
        self.setWindowTitle('Asistente de Voz (F1)')
        self.setGeometry(300, 300, 550, 400)
        self.setWindowIcon(QIcon('mic.png'))  # Puedes añadir un icono si lo tienes
        
        # Configurar el tema oscuro
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2D2D30;
            }
            QWidget {
                background-color: #2D2D30;
                color: #FFFFFF;
            }
            QPushButton {
                background-color: #007ACC;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0098FF;
            }
            QPushButton:pressed {
                background-color: #005A9C;
            }
            QPushButton:disabled {
                background-color: #555555;
            }
            QTextEdit {
                background-color: #1E1E1E;
                color: #D4D4D4;
                border: 1px solid #3F3F46;
                border-radius: 5px;
                padding: 5px;
            }
            QLabel {
                color: #FFFFFF;
            }
        """)
        
        # Widget central y layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Título
        title_label = QLabel('Asistente de Voz')
        title_label.setFont(QFont('Arial', 18, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Instrucciones
        instrucciones = QLabel('Presiona F1 o el botón "Escuchar" para activar el asistente')
        instrucciones.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(instrucciones)
        
        # Área de texto para mostrar resultado
        self.resultado_text = QTextEdit()
        self.resultado_text.setReadOnly(True)
        self.resultado_text.setFont(QFont('Arial', 10))
        self.resultado_text.setMinimumHeight(200)
        main_layout.addWidget(self.resultado_text)
        
        # Área para mostrar el estado actual
        self.estado_label = QLabel('Listo para escuchar')
        self.estado_label.setAlignment(Qt.AlignCenter)
        self.estado_label.setFont(QFont('Arial', 11))
        main_layout.addWidget(self.estado_label)
        
        # Botones
        button_layout = QHBoxLayout()
        
        # Botón para escuchar
        self.escuchar_btn = QPushButton('Escuchar')
        self.escuchar_btn.setFont(QFont('Arial', 12))
        self.escuchar_btn.setMinimumHeight(50)
        self.escuchar_btn.clicked.connect(self.iniciar_escucha)
        button_layout.addWidget(self.escuchar_btn)
        
        # Botón para limpiar
        self.limpiar_btn = QPushButton('Limpiar')
        self.limpiar_btn.setFont(QFont('Arial', 12))
        self.limpiar_btn.setMinimumHeight(50)
        self.limpiar_btn.clicked.connect(self.limpiar_resultado)
        button_layout.addWidget(self.limpiar_btn)
        
        # Botón para minimizar a la bandeja del sistema
        self.minimizar_btn = QPushButton('Minimizar a bandeja')
        self.minimizar_btn.setFont(QFont('Arial', 12))
        self.minimizar_btn.setMinimumHeight(50)
        self.minimizar_btn.clicked.connect(self.minimizar_a_bandeja)
        button_layout.addWidget(self.minimizar_btn)
        
        main_layout.addLayout(button_layout)
        
        # Configurar el icono de la bandeja del sistema
        self.setup_tray_icon()
        
        # Inicializar el hilo de escucha
        self.escucha_thread = None
        
        # Mensaje inicial
        self.resultado_text.append("¡Bienvenido al Asistente de Voz!")
        self.resultado_text.append("Presiona F1 en cualquier momento para activar el asistente.")
        self.resultado_text.append("Puedes pedirme que abra aplicaciones diciendo 'abrir [nombre]'")
        self.resultado_text.append("O reproducir música diciendo 'reproducir [canción]'")
        self.resultado_text.append("Di 'ayuda' para más información o 'salir' para terminar.")
    
    def setup_tray_icon(self):
        """Configura el icono de la bandeja del sistema"""
        self.tray_icon = QSystemTrayIcon(self)
        
        # Usar un icono por defecto si no se encuentra el personalizado
        try:
            self.tray_icon.setIcon(QIcon('mic.png'))
        except:
            # Usar un icono del sistema si no hay uno personalizado
            self.tray_icon.setIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))
        
        # Crear menú contextual para el icono de la bandeja
        tray_menu = QMenu()
        
        # Acción para mostrar la ventana
        show_action = QAction("Mostrar", self)
        show_action.triggered.connect(self.show_from_tray)
        tray_menu.addAction(show_action)
        
        # Acción para escuchar (equivalente a presionar F1)
        listen_action = QAction("Escuchar (F1)", self)
        listen_action.triggered.connect(self.iniciar_escucha)
        tray_menu.addAction(listen_action)
        
        # Acción para salir
        quit_action = QAction("Salir", self)
        quit_action.triggered.connect(self.quit_app)
        tray_menu.addAction(quit_action)
        
        # Asignar el menú al icono de la bandeja
        self.tray_icon.setContextMenu(tray_menu)
        
        # Permitir que al hacer doble clic en el icono se muestre la ventana
        self.tray_icon.activated.connect(self.tray_icon_activated)
        
        # Mostrar el icono en la bandeja
        self.tray_icon.show()
    
    def tray_icon_activated(self, reason):
        """Maneja los clics en el icono de la bandeja"""
        if reason == QSystemTrayIcon.DoubleClick:
            self.show_from_tray()
    
    def show_from_tray(self):
        """Muestra la ventana desde la bandeja del sistema"""
        self.esta_visible = True
        self.showNormal()  # Restaura la ventana
        self.activateWindow()  # Activa la ventana
    
    def minimizar_a_bandeja(self):
        """Minimiza la aplicación a la bandeja del sistema"""
        self.esta_visible = False
        self.hide()  # Oculta la ventana
        # Muestra un mensaje en la bandeja
        self.tray_icon.showMessage("Asistente de Voz", 
                                   "El asistente sigue activo. Presiona F1 para activarlo o haz clic para abrir.",
                                   QSystemTrayIcon.Information, 3000)
    
    def quit_app(self):
        """Cierra completamente la aplicación"""
        # Liberar el atajo de teclado F1
        if KEYBOARD_AVAILABLE:
            keyboard.unhook_all()
        QApplication.quit()
    
    def closeEvent(self, event):
        """Sobrescribe el evento de cierre para minimizar a la bandeja en lugar de cerrar"""
        if self.esta_visible:
            self.minimizar_a_bandeja()
            event.ignore()  # Evita que la ventana se cierre
        else:
            self.quit_app()
            event.accept()
    
    def iniciar_escucha(self):
        """Inicia el proceso de escucha en un hilo separado"""
        try:
            # Si la ventana está minimizada, mostrarla
            if not self.esta_visible:
                self.show_from_tray()
            
            # Verificar si ya hay un proceso de escucha activo
            if self.escucha_thread and self.escucha_thread.isRunning():
                self.resultado_text.append("\nYa hay un proceso de escucha activo.")
                return
            
            # Marcar que hay un proceso de escucha activo
            self.escucha_activa = True
            
            # Desactivar el botón mientras escucha
            self.escuchar_btn.setEnabled(False)
            
            # Reiniciar el estado de escucha del asistente
            self.asistente.reiniciar_escucha()
            
            # Crear y configurar el hilo de escucha
            self.escucha_thread = EscuchaThread(self.asistente)
            self.escucha_thread.comando_detectado.connect(self.mostrar_comando)
            self.escucha_thread.estado_actualizado.connect(self.actualizar_estado)
            self.escucha_thread.finalizado.connect(self.escucha_finalizada)
            
            # Iniciar el hilo
            self.escucha_thread.start()
        except Exception as e:
            self.resultado_text.append(f"\nError al iniciar la escucha: {str(e)}")
            self.escuchar_btn.setEnabled(True)
            self.escucha_activa = False
    
    def mostrar_comando(self, comando):
        """Muestra el comando detectado en el área de texto"""
        self.resultado_text.append(f"\nComando detectado: {comando}")
    
    def actualizar_estado(self, estado):
        """Actualiza la etiqueta de estado"""
        self.estado_label.setText(estado)
        if estado != "Escuchando...":
            self.resultado_text.append(f"\n> {estado}")
    
    def escucha_finalizada(self):
        """Se llama cuando el hilo de escucha ha terminado"""
        self.escuchar_btn.setEnabled(True)
        self.escucha_activa = False
        
        # Asegurarse de que F1 esté habilitado
        self.tecla_f1_habilitada = True
    
    def limpiar_resultado(self):
        """Limpia el área de texto de resultados"""
        self.resultado_text.clear()
        self.estado_label.setText('Listo para escuchar')

def main():
    app = QApplication(sys.argv)
    
    # Evitar que la aplicación se cierre cuando se cierra la ventana principal
    app.setQuitOnLastWindowClosed(False)
    
    try:
        ventana = AsistenteGUI()
        ventana.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(f"Error fatal en la aplicación: {e}")
        # Crear una ventana de error básica
        from PyQt5.QtWidgets import QMessageBox
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText(f"Error al iniciar la aplicación: {str(e)}")
        msg.setWindowTitle("Error")
        msg.exec_()
        sys.exit(1)

if __name__ == "__main__":
    main()