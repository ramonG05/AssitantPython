
# Configuración del reconocimiento de voz
VOICE_CONFIG = {
    'pause_threshold': 0.8,
    'energy_threshold': 300,
    'language': 'es-ES',
    'timeout': 5,
    'phrase_time_limit': 5,
    'ambient_noise_duration': 0.5,
}

# Configuración de la interfaz gráfica
GUI_CONFIG = {
    'window_title': 'Asistente de Voz (F1)',
    'window_geometry': (300, 300, 550, 400),
    'font_family': 'Arial',
    'title_font_size': 18,
    'default_font_size': 10,
    'button_font_size': 12,
    'button_height': 50,
    'text_area_min_height': 200,
}

# Configuración de teclas globales
KEYBOARD_CONFIG = {
    'hotkey': 'f1',
    'enable_timeout': 500,  # milisegundos
}

# Aplicaciones por sistema operativo
APPLICATIONS = {
    'Windows': {
        'brave': 'brave.exe',
        'navegador': 'brave.exe',
        'chrome': 'chrome.exe',
        'firefox': 'firefox.exe',
        'word': 'winword.exe',
        'excel': 'excel.exe',
        'bloc de notas': 'notepad.exe',
        'notepad': 'notepad.exe',
        'calculadora': 'calc.exe',
        'explorador de archivos': 'explorer.exe',
        'steam': [
            r"C:\Program Files (x86)\Steam\steam.exe",
            r"C:\Program Files\Steam\steam.exe",
            "steam.exe"
        ],
    },
    'Darwin': {  # macOS
        'brave': 'Brave Browser',
        'navegador': 'Brave Browser',
        'chrome': 'Google Chrome',
        'safari': 'Safari',
        'firefox': 'Firefox',
        'word': 'Microsoft Word',
        'excel': 'Microsoft Excel',
        'notas': 'Notes',
        'calculadora': 'Calculator',
        'finder': 'Finder',
    },
    'Linux': {
        # En Linux se usará el nombre del comando directamente
    }
}

# Mensajes del sistema
MESSAGES = {
    'welcome': [
        "¡Bienvenido al Asistente de Voz!",
        "Presiona F1 en cualquier momento para activar el asistente.",
        "Puedes pedirme que abra aplicaciones diciendo 'abrir [nombre]'",
        "O reproducir música diciendo 'reproducir [canción]'",
        "Di 'ayuda' para más información o 'salir' para terminar."
    ],
    'help': "Puedo abrir aplicaciones diciendo 'abrir [nombre]' y reproducir música diciendo 'reproducir [canción]'.",
    'exit': "salir",
    'unknown_command': "No entendí ese comando. Prueba decir 'ayuda' para ver lo que puedo hacer.",
    'listening': "Escuchando...",
    'ready': "Listo para escuchar",
    'completed': "Acción completada. Presiona F1 o el botón 'Escuchar' para un nuevo comando.",
    'no_command': "No se detectó ningún comando. Intenta de nuevo.",
    'tray_message': "El asistente sigue activo. Presiona F1 para activarlo o haz clic para abrir.",
}

# URLs y patrones
URLS = {
    'youtube_search': "https://www.youtube.com/results?search_query={}",
    'youtube_watch': "https://www.youtube.com/watch?v={}",
}

# Patrones de expresiones regulares para comandos
COMMAND_PATTERNS = {
    'open_app': r"(abrir|abre|ejecuta|ejecutar|inicia|iniciar)\s+(.+)",
    'play_music': r"(reproducir|reproduce|pon|poner|escuchar|tocar)\s+(.+)",
    'search_files': r"(buscar|busca|encuentra|encontrar)\s+archivo[s]?\s+(.+)",
    'help': r"(ayuda|ayúdame|qué puedes hacer|funciones)",
    'exit': r"(salir|terminar|finalizar|adiós)",
}