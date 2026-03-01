import re
import requests

BASE_URL = "https://portal.dev.symphony.moek.itfb.tech"
TOKEN_URL = f"{BASE_URL}/api/auth-service/auth/token"

JWT_RE = re.compile(r"^[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+$")


def main():
    username = "admin"
    password = "rYZ(@2Fu!3Rfh,FFgS"

    print("Отправляем GET запрос на получение токена...\n")

    r = requests.get(
        TOKEN_URL,
        auth=(username, password),  # Basic Auth
        timeout=20,
    )

    print(f"HTTP статус: {r.status_code}")
    print("Ответ сервера:")
    print(r.text)
    print("\n-----------------------------\n")

    if r.status_code != 200:
        print("Ошибка получения токена")
        return

    body = r.json()
    token = body["data"]["token"]

    print(f"Извлечённый token:\n{token}\n")

    if JWT_RE.match(token):
        print("Токен корректный (формат JWT подтверждён)")
    else:
        print("Токен НЕ соответствует формату JWT")

    print("\nДополнительные данные:")
    print("Username:", body["data"].get("username"))
    print("IssuedAt:", body["data"].get("issuedAt"))
    print("ExpiresAt:", body["data"].get("expiresAt"))


if __name__ == "__main__":
    main()