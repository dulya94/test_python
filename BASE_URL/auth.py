"""
Модуль авторизации для работы с API
"""

import re
import requests
import os
from typing import Optional, Dict, Any

# Простая конфигурация
class Config:
    """Конфигурация для авторизации"""
    
    # Получаем значения из переменных окружения или используем значения по умолчанию
    BASE_URL = os.getenv('API_BASE_URL', 'https://portal.dev.symphony.moek.itfb.tech')
    USERNAME = os.getenv('API_USERNAME', 'admin')
    PASSWORD = os.getenv('API_PASSWORD', 'rYZ(@2Fu!3Rfh,FFgS')
    TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', '20'))
    
    @classmethod
    def get_token_url(cls):
        """Получить URL для получения токена"""
        return f"{cls.BASE_URL}/api/auth-service/auth/token"


class AuthClient:
    """
    Клиент для авторизации и работы с токенами
    """
    
    # Регулярное выражение для проверки JWT токена
    JWT_RE = re.compile(r"^[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+$")
    
    def __init__(self, base_url: str = None, username: str = None, password: str = None):
        """
        Инициализация клиента авторизации
        
        Args:
            base_url: Базовый URL API
            username: Имя пользователя
            password: Пароль
        """
        self.base_url = base_url or Config.BASE_URL
        self.username = username or Config.USERNAME
        self.password = password or Config.PASSWORD
        self.timeout = Config.TIMEOUT
        self.token_url = f"{self.base_url}/api/auth-service/auth/token"
        self._token: Optional[str] = None
        self._token_data: Optional[Dict[str, Any]] = None
        
        print(f"🔧 Инициализация AuthClient")
        print(f"   URL: {self.base_url}")
        print(f"   Username: {self.username}")
    
    def get_token(self, force_refresh: bool = False) -> Optional[str]:
        """
        Получение токена авторизации
        
        Args:
            force_refresh: Принудительно обновить токен
            
        Returns:
            Токен или None в случае ошибки
        """
        if self._token and not force_refresh:
            print("🔄 Используем существующий токен")
            return self._token
        
        print("🔐 Запрашиваем новый токен...")
        
        try:
            response = requests.get(
                self.token_url,
                auth=(self.username, self.password),
                timeout=self.timeout
            )
            
            print(f"📡 HTTP статус: {response.status_code}")
            
            if response.status_code != 200:
                print(f"❌ Ошибка получения токена: HTTP {response.status_code}")
                print(f"Ответ сервера: {response.text}")
                return None
            
            # Парсим ответ
            data = response.json()
            
            # Проверяем структуру ответа
            if "data" in data and "token" in data["data"]:
                self._token_data = data.get("data", {})
                self._token = self._token_data.get("token")
                print("✅ Токен успешно получен")
            else:
                print("❌ Неожиданная структура ответа")
                print(f"Ответ: {data}")
                return None
            
            return self._token
            
        except requests.exceptions.ConnectionError:
            print("❌ Ошибка подключения к серверу")
            return None
        except requests.exceptions.Timeout:
            print("❌ Превышен таймаут запроса")
            return None
        except Exception as e:
            print(f"❌ Непредвиденная ошибка: {e}")
            return None
    
    def validate_token(self, token: str = None) -> bool:
        """
        Проверка корректности формата токена
        
        Args:
            token: Токен для проверки (если не указан, используется текущий)
            
        Returns:
            True если токен корректен
        """
        token_to_check = token or self._token
        
        if not token_to_check:
            print("❌ Токен не найден")
            return False
            
        is_valid = bool(self.JWT_RE.match(token_to_check))
        
        if is_valid:
            print("✅ Токен корректен (формат JWT)")
        else:
            print("❌ Токен НЕ соответствует формату JWT")
            
        return is_valid
    
    def get_token_info(self) -> Dict[str, Any]:
        """
        Получение информации о токене
        
        Returns:
            Словарь с информацией о токене
        """
        if not self._token_data:
            return {
                "username": None,
                "issued_at": None,
                "expires_at": None,
                "has_token": False
            }
            
        return {
            "username": self._token_data.get("username"),
            "issued_at": self._token_data.get("issuedAt"),
            "expires_at": self._token_data.get("expiresAt"),
            "has_token": self._token is not None
        }
    
    def get_auth_header(self) -> Dict[str, str]:
        """
        Получение заголовка авторизации для использования в запросах
        
        Returns:
            Словарь с заголовком Authorization
        """
        if not self._token:
            self.get_token()
            
        if self._token:
            return {"Authorization": f"Bearer {self._token}"}
        return {}
    
    def print_token_info(self):
        """Вывод информации о токене"""
        print("\n" + "="*50)
        print("🔐 ИНФОРМАЦИЯ О ТОКЕНЕ")
        print("="*50)
        
        if self._token:
            # Показываем первые 50 символов токена
            token_preview = self._token[:50] + "..." if len(self._token) > 50 else self._token
            print(f"Токен: {token_preview}")
        else:
            print("Токен: не получен")
        
        info = self.get_token_info()
        print(f"Username: {info['username']}")
        print(f"Issued At: {info['issued_at']}")
        print(f"Expires At: {info['expires_at']}")
        print(f"Статус: {'✅ Активен' if info['has_token'] else '❌ Не активен'}")
        
        self.validate_token()
        print("="*50)


# Создаем глобальный экземпляр для удобства
_default_client = None

def get_auth_client() -> AuthClient:
    """Получить глобальный экземпляр клиента авторизации"""
    global _default_client
    if _default_client is None:
        _default_client = AuthClient()
    return _default_client


def authenticate() -> Optional[str]:
    """
    Упрощенная функция для быстрой авторизации
    
    Returns:
        Токен или None
    """
    client = get_auth_client()
    return client.get_token()


# Для обратной совместимости с вашим оригинальным кодом
def main():
    """Основная функция для тестирования модуля"""
    
    print("\n" + "="*60)
    print("🚀 ТЕСТИРОВАНИЕ МОДУЛЯ АВТОРИЗАЦИИ")
    print("="*60)
    
    # Создаем клиент
    client = AuthClient()
    
    # Получаем токен
    print("\n📡 Получение токена...")
    token = client.get_token()
    
    if token:
        print("\n✅ Токен успешно получен!")
        
        # Проверяем токен
        client.validate_token()
        
        # Показываем информацию
        client.print_token_info()
        
        # Показываем заголовок для использования в запросах
        print("\n🔑 Заголовок авторизации:")
        print(client.get_auth_header())
        
    else:
        print("\n❌ Не удалось получить токен")
        print("\nВозможные причины:")
        print("1. Сервер недоступен")
        print("2. Неправильный логин или пароль")
        print("3. Проблемы с сетью или прокси")
        print("4. Неверный BASE_URL")


if __name__ == "__main__":
    main()