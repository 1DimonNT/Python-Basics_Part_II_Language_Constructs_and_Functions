# email_system.py
from datetime import date
from typing import List, Tuple, Dict

# ==================== Часть A. Вспомогательные функции ====================

def normalize_addresses(value: str) -> str:
    """Приводит email к нижнему регистру и убирает пробелы по краям."""
    return value.lower().strip()

def add_short_body(email: dict) -> dict:
    """Добавляет в словарь письма короткую версию тела (первые 10 символов + '...')."""
    body = email.get('body', '')
    short_body = body[:10] + '...' if len(body) > 10 else body
    email['short_body'] = short_body
    return email

def clean_body_text(body: str) -> str:
    """Заменяет табуляции и переводы строк на пробелы."""
    return ' '.join(body.split())

def build_sent_text(email: dict) -> str:
    """Формирует итоговый текст письма из данных словаря."""
    return (f"Кому: {email.get('recipient', '')}, от {email.get('sender', '')}\n"
            f"Тема: {email.get('subject', '')}, дата {email.get('date', '')}\n"
            f"{email.get('short_body', '')}")

def check_empty_fields(subject: str, body: str) -> tuple[bool, bool]:
    """Проверяет, пустые ли тема и тело письма."""
    is_subject_empty = not bool(subject and subject.strip())
    is_body_empty = not bool(body and body.strip())
    return is_subject_empty, is_body_empty

def mask_sender_email(login: str, domain: str) -> str:
    """Создает маску email: первые 2 символа логина + '***@' + домен."""
    if len(login) >= 2:
        masked_login = login[:2] + "***"
    else:
        # Если логин короче 2 символов, маскируем все, что есть
        masked_login = login + "***" if login else "***"
    return f"{masked_login}@{domain}"

def get_correct_email(email_list: list[str]) -> list[str]:
    """Возвращает список email, прошедших валидацию: есть '@' и домен .com/.ru/.net."""
    valid_domains = ('.com', '.ru', '.net')
    correct_emails = []

    for email in email_list:
        cleaned_email = email.strip()
        if not cleaned_email:
            continue

        # Проверка наличия '@' и что он не первый и не последний символ
        if '@' not in cleaned_email or cleaned_email.startswith('@') or cleaned_email.endswith('@'):
            continue

        # Проверка окончания на допустимый домен (без учета регистра)
        domain_part = cleaned_email.split('@')[-1].lower()
        if not any(domain_part.endswith(domain) for domain in valid_domains):
            continue

        # Дополнительная проверка, что перед доменом есть точка и символы
        if '.' not in domain_part or domain_part.split('.')[-2] == '':
            continue

        correct_emails.append(cleaned_email)

    return correct_emails

def create_email(sender: str, recipient: str, subject: str, body: str) -> dict:
    """Создает базовый словарь письма."""
    return {
        'sender': sender,
        'recipient': recipient,
        'subject': subject,
        'body': body
    }

def add_send_date(email: dict) -> dict:
    """Добавляет в словарь письма текущую дату в формате YYYY-MM-DD."""
    email['date'] = date.today().isoformat()
    return email

def extract_login_domain(address: str) -> tuple[str, str]:
    """Разделяет email на логин и домен."""
    login, domain = address.split('@', 1)
    return login, domain

# ==================== Часть B. Основная функция ====================

def sender_email(recipient_list: list[str], subject: str, message: str, *, sender="default@study.com") -> list[dict]:
    """
    Основная функция отправки писем с полной обработкой данных.
    Возвращает список готовых словарей писем.
    """

    # 1. Проверить, что список получателей не пустой
    if not recipient_list:
        print("Ошибка: Список получателей пуст.")
        return []

    # 2. Проверить корректность email отправителя и получателей
    all_emails_to_check = [sender] + recipient_list
    correct_emails = get_correct_email(all_emails_to_check)

    # Если отправитель некорректен, прерываем работу
    if sender not in correct_emails:
        print(f"Ошибка: Email отправителя '{sender}' некорректен.")
        return []

    # Оставляем только корректных получателей, которые есть в списке правильных email
    valid_recipients = [email for email in recipient_list if email in correct_emails]

    # 3. Проверить пустоту темы и тела письма
    is_subject_empty, is_body_empty = check_empty_fields(subject, message)
    if is_subject_empty or is_body_empty:
        print("Ошибка: Тема или тело письма пустые.")
        return []

    # 4. Исключить отправку самому себе (создаем новый список)
    final_recipients = [rec for rec in valid_recipients if normalize_addresses(rec) != normalize_addresses(sender)]

    if not final_recipients:
        print("Нет получателей после исключения отправки самому себе.")
        return []

    # 5. Нормализовать данные
    normalized_sender = normalize_addresses(sender)
    normalized_subject = clean_body_text(subject)
    normalized_message = clean_body_text(message)
    normalized_recipients = [normalize_addresses(rec) for rec in final_recipients]

    # 6-10. Создать письмо для каждого получателя, обогатить данными и собрать результат
    result_emails = []
    for recipient in normalized_recipients:
        # 6. Создать письмо
        email_dict = create_email(normalized_sender, recipient, normalized_subject, normalized_message)

        # 7. Добавить дату отправки
        email_dict = add_send_date(email_dict)

        # 8. Замаскировать email отправителя
        login, domain = extract_login_domain(email_dict['sender'])
        email_dict['masked_sender'] = mask_sender_email(login, domain)

        # 9. Создать короткую версию тела письма
        email_dict = add_short_body(email_dict)

        # 10. Сформировать итоговый текст письма
        email_dict['sent_text'] = build_sent_text(email_dict)

        result_emails.append(email_dict)

    return result_emails

# ==================== Демонстрация работы ====================
if __name__ == "__main__":
    print("=" * 30, "Тест функции get_correct_email", "=" * 30)
    test_emails = [
        "user@gmail.com", "admin@company.ru", "test_123@service.net", "Example.User@domain.com",
        "default@study.com", " hello@corp.ru  ", "user@site.NET", "user@domain.coM",
        "user.name@domain.ru", "usergmail.com", "user@domain", "user@domain.org",
        "@mail.ru", "name@.com", "name@domain.comm", "", "   ",
    ]
    correct_list = get_correct_email(test_emails)
    print(f"Корректные email: {correct_list}")
    print(f"Всего корректных: {len(correct_list)} из {len(test_emails)}")
    print("\n")

    print("=" * 30, "Тест функции sender_email", "=" * 30)
    # Пример использования sender_email
    recipients = [
        "admin@company.ru",
        " FRIEND@study.COM  ",
        "invalid-email",
        "another@domain.net",
        "default@study.com"  # Сам себе
    ]
    subject = "Привет, коллега!"
    message = "Это тестовое сообщение.\nС новой строки и табуляцией."

    emails = sender_email(
        recipient_list=recipients,
        subject=subject,
        message=message,
        sender="default@study.com"
    )

    if emails:
        print(f"Успешно обработано писем: {len(emails)}")
        for i, email in enumerate(emails, 1):
            print(f"\n--- Письмо {i} ---")
            print(f"Кому (ориг): {email['recipient']}")
            print(f"Маска отправителя: {email['masked_sender']}")
            print(f"Дата: {email['date']}")
            print(f"Короткое тело: {email['short_body']}")
            print(f"Итоговый текст:\n{email['sent_text']}")
    else:
        print("Не удалось создать письма.")