from datetime import date


# ==================== Часть A. Вспомогательные функции ====================

def normalize_addresses(value: str) -> str:
    """
    Возвращает значение, в котором адрес приведен к нижнему регистру и очищен от пробелов по краям.
    """
    return value.lower().strip()


def add_short_body(email: dict) -> dict:
    """
    Возвращает email с новым ключом email["short_body"] —
    первые 10 символов тела письма + "...".
    """
    body = email.get("body", "")
    email["short_body"] = body[:10] + "..." if len(body) > 10 else body
    return email


def clean_body_text(body: str) -> str:
    """
    Заменяет табы и переводы строк на пробелы.
    """
    return " ".join(body.split())


def build_sent_text(email: dict) -> str:
    """
    Формирует текст письма в формате:
    Кому: {to}, от {from}
    Тема: {subject}, дата {date}
    {clean_body}
    """
    return (
        f"Кому: {email.get('recipient', '')}, от {email.get('sender', '')}\n"
        f"Тема: {email.get('subject', '')}, дата {email.get('date', '')}\n"
        f"{email.get('short_body', '')}"
    )


def check_empty_fields(subject: str, body: str) -> tuple[bool, bool]:
    """
    Возвращает кортеж (is_subject_empty, is_body_empty).
    True, если поле пустое.
    """
    return not subject.strip(), not body.strip()


def mask_sender_email(login: str, domain: str) -> str:
    """
    Возвращает маску email: первые 2 символа логина + "***@" + домен.
    """
    return f"{login[:2]}***@{domain}" if login else "***@unknown"


def get_correct_email(email_list: list[str]) -> list[str]:
    """
    Возвращает список корректных email.
    Адрес считается корректным, если:
    - содержит символ @
    - оканчивается на один из доменов: .com, .ru, .net
    """
    valid_domains = (".com", ".ru", ".net")
    seen_emails = set()
    correct_emails = []

    for email in email_list:
        cleaned_email = email.strip()
        if not cleaned_email or cleaned_email in seen_emails:
            continue

        # Проверка наличия '@' и что он не первый и не последний символ
        if (
            "@" not in cleaned_email
            or cleaned_email.startswith("@")
            or cleaned_email.endswith("@")
        ):
            continue

        # Проверка окончания на допустимый домен
        domain_part = cleaned_email.split("@")[-1].lower()
        if not any(domain_part.endswith(domain) for domain in valid_domains):
            continue

        # Проверка, что перед доменом есть точка и символы
        if "." not in domain_part or not domain_part.split(".")[-2]:
            continue

        seen_emails.add(cleaned_email)
        correct_emails.append(cleaned_email)

    return correct_emails


def create_email(sender: str, recipient: str, subject: str, body: str) -> dict:
    """
    Создает словарь email с базовыми полями:
    'sender', 'recipient', 'subject', 'body'
    """
    return {
        "sender": sender,
        "recipient": recipient,
        "subject": subject,
        "body": body,
    }


def add_send_date(email: dict) -> dict:
    """
    Возвращает email с добавленным ключом email["date"] — текущая дата в формате YYYY-MM-DD.
    """
    email["date"] = date.today().isoformat()
    return email


def extract_login_domain(address: str) -> tuple[str, str]:
    """
    Возвращает логин и домен отправителя.
    Пример: "user@mail.ru" -> ("user", "mail.ru")
    """
    return address.split("@", 1)


# ==================== Часть B. Основная функция отправки ====================

def sender_email(
    recipient_list: list[str], subject: str, message: str, *, sender="default@study.com"
) -> list[dict]:
    """
    Функция отправки письма с валидацией и обработкой.
    Принимает список получателей, тему, сообщение и отправителя.
    Возвращает список готовых словарей писем.
    """
    # 1. Проверить, что список получателей не пустой
    if not recipient_list:
        print("Ошибка: Список получателей пуст.")
        return []

    # 2. Проверить корректность email отправителя
    if sender not in get_correct_email([sender]):
        print(f"Ошибка: Email отправителя '{sender}' некорректен.")
        return []

    # 3. Получить список корректных получателей (уникальных)
    correct_recipients = get_correct_email(recipient_list)

    # 4. Проверить пустоту темы и тела письма
    is_subject_empty, is_body_empty = check_empty_fields(subject, message)
    if is_subject_empty or is_body_empty:
        print("Ошибка: Тема или тело письма пустые.")
        return []

    # 5. Исключить отправку самому себе
    normalized_sender = normalize_addresses(sender)
    final_recipients = [
        rec
        for rec in correct_recipients
        if normalize_addresses(rec) != normalized_sender
    ]

    if not final_recipients:
        print("Нет получателей после исключения отправки самому себе.")
        return []

    # 6. Нормализовать данные
    normalized_subject = clean_body_text(subject)
    normalized_message = clean_body_text(message)
    normalized_recipients = [normalize_addresses(rec) for rec in final_recipients]

    # 7-12. Создать письмо для каждого получателя
    result_emails = []
    for recipient in normalized_recipients:
        # 7. Создать письмо
        email_dict = create_email(
            normalized_sender, recipient, normalized_subject, normalized_message
        )

        # 8. Добавить дату отправки
        email_dict = add_send_date(email_dict)

        # 9. Замаскировать email отправителя
        login, domain = extract_login_domain(email_dict["sender"])
        email_dict["masked_sender"] = mask_sender_email(login, domain)

        # 10. Создать короткую версию тела письма
        email_dict = add_short_body(email_dict)

        # 11. Сформировать итоговый текст письма
        email_dict["sent_text"] = build_sent_text(email_dict)

        result_emails.append(email_dict)

    return result_emails


# ==================== Демонстрация работы ====================
if __name__ == "__main__":
    # Тестовые данные для проверки get_correct_email
    test_emails = [
        # Корректные адреса
        "user@gmail.com",
        "admin@company.ru",
        "test_123@service.net",
        "Example.User@domain.com",
        "default@study.com",
        " hello@corp.ru  ",
        "user@site.NET",
        "user@domain.coM",
        "user.name@domain.ru",
        # Некорректные адреса
        "usergmail.com",  # нет @
        "user@domain",  # нет домена
        "user@domain.org",  # неподдерживаемый домен
        "@mail.ru",  # @ в начале
        "name@.com",  # пустой логин
        "name@domain.comm",  # неподдерживаемый домен
        "",  # пустая строка
        "   ",  # пробелы
        "admin@company.ru",  # дубликат
    ]

    print("=" * 60)
    print("ТЕСТ 1: Проверка функции get_correct_email")
    print("=" * 60)
    correct_list = get_correct_email(test_emails)
    print(f"Корректные email: {correct_list}")
    print(f"Всего корректных: {len(correct_list)} из 9 (уникальных корректных)")
    print()

    print("=" * 60)
    print("ТЕСТ 2: Проверка функции sender_email")
    print("=" * 60)

    # Тестовые данные для отправки
    recipients = [
        "admin@company.ru",
        " FRIEND@study.COM  ",
        "invalid-email",
        "another@domain.net",
        "default@study.com",  # Сам себе
        "admin@company.ru",  # Дубликат
        "colleague@work.com",
    ]

    subject = "Важное совещание"
    message = "Привет, коллега!\nНапоминаю о совещании завтра в 10:00.\nС уважением, команда."

    emails = sender_email(
        recipient_list=recipients,
        subject=subject,
        message=message,
        sender="default@study.com",
    )

    if emails:
        print(f"Успешно обработано писем: {len(emails)}")
        print(
            f"Получатели после фильтрации: {[email['recipient'] for email in emails]}"
        )
        print()

        for i, email in enumerate(emails, 1):
            print(f"--- Письмо {i} ---")
            print(f"Кому: {email['recipient']}")
            print(f"Отправитель (ориг): {email['sender']}")
            print(f"Маска отправителя: {email['masked_sender']}")
            print(f"Тема: {email['subject']}")
            print(f"Дата: {email['date']}")
            print(f"Короткое тело: {email['short_body']}")
            print(f"Итоговый текст:\n{email['sent_text']}")
            print()
    else:
        print("Не удалось создать письма.")