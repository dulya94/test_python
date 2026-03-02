import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

class Config:
    """Класс для управления конфигурацией"""
    
    # API настройки
    BASE_URL = os.getenv('API_BASE_URL', 'https://portal.dev.symphony.moek.itfb.tech')
    AUTH_USERNAME = os.getenv('API_USERNAME', 'admin')
    AUTH_PASSWORD = os.getenv('API_PASSWORD', 'rYZ(@2Fu!3Rfh,FFgS')
    
    # Таймауты
    REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', 20))
    
    # URL сервисов
    TOKEN_URL = f"{BASE_URL}/api/auth-service/auth/token"
    
    @classmethod
    def validate(cls):
        """Проверка наличия обязательных переменных"""
        required_vars = ['BASE_URL', 'AUTH_USERNAME', 'AUTH_PASSWORD']
        missing = [var for var in required_vars if not getattr(cls, var)]
        
        if missing:
            raise ValueError(f"Отсутствуют обязательные переменные: {', '.join(missing)}")