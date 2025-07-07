"""
Motor de reconocimiento de voz
"""
import speech_recognition as sr
from config.settings import VOICE_CONFIG
from utils import VoiceRecognitionError


class VoiceEngine:
    """Clase encargada del reconocimiento de voz"""
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self._configure_recognizer()
    
    def _configure_recognizer(self):
        """Configura el reconocedor con los parámetros predefinidos"""
        self.recognizer.pause_threshold = VOICE_CONFIG['pause_threshold']
        self.recognizer.energy_threshold = VOICE_CONFIG['energy_threshold']
    
    def listen(self):
        """
        Escucha el micrófono y devuelve el texto reconocido
        
        Returns:
            str: Texto reconocido en minúsculas, o cadena vacía si no se reconoce nada
            
        Raises:
            VoiceRecognitionError: Si hay problemas con el micrófono o reconocimiento
        """
        try:
            with sr.Microphone() as source:
                # Ajustar para ruido ambiental
                self.recognizer.adjust_for_ambient_noise(
                    source, 
                    duration=VOICE_CONFIG['ambient_noise_duration']
                )
                
                print("Escuchando... Hable ahora")
                
                audio = self.recognizer.listen(
                    source, 
                    timeout=VOICE_CONFIG['timeout'],
                    phrase_time_limit=VOICE_CONFIG['phrase_time_limit']
                )
                
            # Reconocer el audio
            return self._recognize_audio(audio)
            
        except sr.WaitTimeoutError:
            print("Tiempo de espera agotado")
            return ""
        except Exception as e:
            raise VoiceRecognitionError(f"Error al acceder al micrófono: {e}")
    
    def _recognize_audio(self, audio):
        """
        Reconoce el audio usando Google Speech Recognition
        
        Args:
            audio: Objeto de audio capturado
            
        Returns:
            str: Texto reconocido en minúsculas
        """
        try:
            texto = self.recognizer.recognize_google(
                audio, 
                language=VOICE_CONFIG['language']
            )
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