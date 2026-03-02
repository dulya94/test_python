"""
Пример использования модуля auth для создания документа
Исправлена ошибка 415 - отправка как multipart/form-data с файлом
"""

from auth import AuthClient, get_auth_client, authenticate
import requests
import json
from datetime import datetime
import io

class DocumentCreator:
    """Класс для создания документов"""
    
    def __init__(self, auth_client=None):
        """
        Инициализация создателя документов
        
        Args:
            auth_client: Клиент авторизации (если не указан, создается новый)
        """
        self.auth = auth_client or AuthClient()
        self.base_url = self.auth.base_url
    
    def create_test_document(self):
        """Создание тестового документа через multipart/form-data"""
        
        print("\n📄 СОЗДАНИЕ ДОКУМЕНТА (multipart/form-data)")
        print("="*50)
        
        # Получаем токен
        token = self.auth.get_token()
        if not token:
            print("❌ Не удалось получить токен авторизации")
            return None
        
        # Получаем заголовок авторизации
        auth_header = self.auth.get_auth_header()
        
        # Формируем данные документа
        document_data = {
            "attributes": {
                "signatory": [
                    {
                        "login": "admin",
                        "fullName": "Петух Вячеслав Сергеевич",
                        "departmentId": "1",
                        "department": "Департамент качества",
                        "organizationId": "001",
                        "organization": "ITFB GROUP"
                    }
                ],
                "counterparty": {
                    "inn": "72737472347273",
                    "kpp": "12312312312313",
                    "guid": "b4eeead5-e135-4a9e-a1fc-d442726e7fa4",
                    "name": "Тест",
                    "displayTitle": "ИНН:72737472347273"
                }
            },
            "attachments": [],
            "relations": [],
            "title": f"Тест АПИ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "summary": "",
            "type": "TEST2",
            "docNumber": "",
            "description": "",
            "roles": [],
            "users": [],
            "personalData": False,
            "registrationDate": None,
            "documentNumber": "",
            "externalNumber": "",
            "externalDate": None,
            "containerTemplates": [],
            "draft": False,
            "majorVersion": False
        }
        
        # Преобразуем данные в JSON строку
        json_string = json.dumps(document_data, ensure_ascii=False)
        print(f"📦 JSON данные: {json_string[:200]}...")
        
        # Создаем файлоподобный объект из JSON строки
        json_file = io.BytesIO(json_string.encode('utf-8'))
        
        # Формируем multipart/form-data
        # Важно: имя поля должно быть "document", а filename="blob" как в примере
        files = {
            'document': ('blob', json_file, 'application/json')
        }
        
        # Заголовки - только авторизация, Content-Type установится автоматически для multipart
        headers = {}
        if auth_header:
            headers.update(auth_header)
        
        print(f"\n📋 Заголовки запроса:")
        for key, value in headers.items():
            if key == "Authorization":
                print(f"   {key}: Bearer {value[10:30]}...")
            else:
                print(f"   {key}: {value}")
        
        print(f"\n📁 Multipart/form-data:")
        print(f"   Поле: document")
        print(f"   Имя файла: blob")
        print(f"   Content-Type: application/json")
        print(f"   Размер: {len(json_string)} байт")
        
        # Отправляем запрос
        url = f"{self.base_url}/api/documents"
        
        try:
            print(f"\n📡 Отправка POST запроса на {url}")
            
            response = requests.post(
                url,
                headers=headers,
                files=files,
                timeout=self.auth.timeout
            )
            
            print(f"📡 HTTP статус: {response.status_code}")
            
            if response.status_code in [200, 201]:
                print("✅ Документ успешно создан!")
                result = response.json()
                
                if 'id' in result:
                    print(f"🆔 ID документа: {result['id']}")
                
                print(f"\n📊 Ответ сервера:")
                print(json.dumps(result, indent=2, ensure_ascii=False))
                
                return result
            else:
                print(f"❌ Ошибка создания документа: {response.status_code}")
                print(f"Ответ: {response.text}")
                
                # Диагностика
                print(f"\n🔍 Диагностика:")
                print(f"   Использован multipart/form-data")
                print(f"   Поле: document, файл: blob")
                
                return None
                
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return None
        finally:
            json_file.close()
    
    def create_document_from_file(self, json_file_path=None):
        """
        Создание документа из JSON файла через multipart/form-data
        
        Args:
            json_file_path: Путь к JSON файлу (если None, создает временный)
        """
        print("\n📄 СОЗДАНИЕ ДОКУМЕНТА ИЗ ФАЙЛА")
        print("="*50)
        
        # Получаем токен
        token = self.auth.get_token()
        if not token:
            print("❌ Не удалось получить токен авторизации")
            return None
        
        auth_header = self.auth.get_auth_header()
        
        # Если передан путь к файлу, используем его
        if json_file_path:
            try:
                with open(json_file_path, 'rb') as f:
                    file_content = f.read()
                print(f"📁 Загружен файл: {json_file_path}")
                filename = os.path.basename(json_file_path)
            except Exception as e:
                print(f"❌ Ошибка чтения файла: {e}")
                return None
        else:
            # Используем данные по умолчанию
            document_data = {
                "attributes": {
                    "signatory": [
                        {
                            "login": "admin",
                            "fullName": "Петух Вячеслав Сергеевич",
                            "departmentId": "1",
                            "department": "Департамент качества",
                            "organizationId": "001",
                            "organization": "ITFB GROUP"
                        }
                    ],
                    "counterparty": {
                        "inn": "72737472347273",
                        "kpp": "12312312312313",
                        "guid": "b4eeead5-e135-4a9e-a1fc-d442726e7fa4",
                        "name": "Тест",
                        "displayTitle": "ИНН:72737472347273"
                    }
                },
                "attachments": [],
                "relations": [],
                "title": f"Тест АПИ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                "summary": "",
                "type": "TEST2",
                "docNumber": "",
                "description": "",
                "roles": [],
                "users": [],
                "personalData": False,
                "registrationDate": None,
                "documentNumber": "",
                "externalNumber": "",
                "externalDate": None,
                "containerTemplates": [],
                "draft": False,
                "majorVersion": False
            }
            json_string = json.dumps(document_data, ensure_ascii=False)
            file_content = json_string.encode('utf-8')
            filename = "blob"
            print(f"📁 Создан временный файл: {filename}")
        
        # Создаем файлоподобный объект
        json_file = io.BytesIO(file_content)
        
        # Формируем multipart/form-data
        files = {
            'document': (filename, json_file, 'application/json')
        }
        
        # Заголовки
        headers = {}
        if auth_header:
            headers.update(auth_header)
        
        print(f"\n📋 Заголовки запроса:")
        for key, value in headers.items():
            if key == "Authorization":
                print(f"   {key}: Bearer {value[10:30]}...")
        
        print(f"\n📁 Multipart/form-data:")
        print(f"   Поле: document")
        print(f"   Имя файла: {filename}")
        print(f"   Content-Type: application/json")
        print(f"   Размер: {len(file_content)} байт")
        
        url = f"{self.base_url}/api/documents"
        
        try:
            print(f"\n📡 Отправка POST запроса на {url}")
            
            response = requests.post(
                url,
                headers=headers,
                files=files,
                timeout=self.auth.timeout
            )
            
            print(f"📡 HTTP статус: {response.status_code}")
            
            if response.status_code in [200, 201]:
                print("✅ Документ успешно создан!")
                result = response.json()
                
                if 'id' in result:
                    print(f"🆔 ID документа: {result['id']}")
                
                return result
            else:
                print(f"❌ Ошибка: {response.status_code}")
                print(f"Ответ: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return None
        finally:
            json_file.close()


def simple_example():
    """Простой пример использования"""
    
    print("\n🚀 ЗАПУСК ТЕСТИРОВАНИЯ")
    print("="*50)
    
    # Создаем клиент
    client = get_auth_client()
    
    # Получаем токен
    token = client.get_token()
    if token:
        print(f"✅ Токен получен: {token[:20]}...")
        
        # Создаем документ через multipart/form-data
        creator = DocumentCreator(client)
        doc = creator.create_test_document()
        
        if doc:
            print("\n🎉 Документ создан успешно!")
        else:
            print("\n❌ Не удалось создать документ")
    else:
        print("❌ Не удалось получить токен")


def test_with_file(json_file_path):
    """Тест с конкретным JSON файлом"""
    
    print("\n🚀 ТЕСТ С JSON ФАЙЛОМ")
    print("="*50)
    
    client = get_auth_client()
    token = client.get_token()
    
    if token:
        creator = DocumentCreator(client)
        doc = creator.create_document_from_file(json_file_path)
        
        if doc:
            print("\n🎉 Документ создан успешно!")
        else:
            print("\n❌ Не удалось создать документ")
    else:
        print("❌ Не удалось получить токен")


if __name__ == "__main__":
    import sys
    import os
    
    if len(sys.argv) > 1:
        # Если передан путь к файлу как аргумент
        test_with_file(sys.argv[1])
    else:
        # Запускаем простой пример
        simple_example()