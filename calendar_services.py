from datetime import datetime, timezone, timedelta
from googleapiclient.discovery import build
from auth import authenticate


def get_events_today():
    events_list = []
    creds = authenticate()
    service = build('calendar', 'v3', credentials=creds)

    # Pobierz bieżący czas i koniec dnia w formacie ISO
    now = datetime.now(timezone.utc).isoformat()
    end_of_day = (datetime.now(timezone.utc).replace(hour=23, minute=59, second=59, microsecond=0)).isoformat()

    events_result = service.events().list(
        calendarId='primary',  # Główny kalendarz
        timeMin=now,  # Od teraz
        timeMax=end_of_day,  # Do końca dnia
        singleEvents=True,  # Tylko pojedyncze wydarzenia
        orderBy='startTime'  # Posortowane według czasu rozpoczęcia
    ).execute()

    events = events_result.get('items', [])
    if not events:
        print("Brak wydarzeń na dzisiaj.")
        return events_list

    # Zbierz wydarzenia do listy
    for event in events:
        # Upewnij się, że "summary" istnieje w wydarzeniu (nie wszystkie wydarzenia muszą mieć tytuł)
        title = event.get('summary', 'Bez tytułu')

        # Sprawdzanie czasu rozpoczęcia i zakończenia
        start_time = event.get('start', {}).get('dateTime', None)  # Czas rozpoczęcia
        end_time = event.get('end', {}).get('dateTime', None)  # Czas zakończenia

        # Dodajemy dane o czasie do słownika
        events_list.append({
            'title': title,
            'id': event['id'],
            'start_time': start_time,
            'end_time': end_time
        })
    return events_list


def delete_event(event_id):
    creds = authenticate()
    service = build('calendar', 'v3', credentials=creds)

    try:
        service.events().delete(calendarId='primary', eventId=event_id).execute()
        print(f"Wydarzenie o ID {event_id} zostało usunięte.")
    except Exception as e:
        print(f"Błąd podczas usuwania wydarzenia: {e}")


def debug_log(**kwargs):
    """Funkcja pomocnicza do debugowania"""
    for key, value in kwargs.items():
        print(f"DEBUG: {key}='{value}'")


def parse_datetime(date_str, time_str):
    """Konwersja daty i czasu na obiekt datetime z obsługą wyjątków."""
    try:
        if len(time_str) == 2 and time_str.isdigit():
            time_str += ':00'
        elif len(time_str) == 1 and time_str.isdigit():
            time_str = f'0{time_str}:00'
        if time_str in ['24:00', '24']:
            time_str = '23:59'

        combined = f"{date_str} {time_str}"
        parsed = datetime.strptime(combined, "%Y-%m-%d %H:%M")
        return parsed
    except ValueError as e:
        raise ValueError(f"Błąd parsowania daty/czasu: {combined}. Szczegóły: {e}")


def create_event(title, description=None, start_date=None, start_time=None, end_date=None, end_time=None):
    debug_log(
        title=title,
        description=description,
        start_date=start_date,
        start_time=start_time,
        end_date=end_date,
        end_time=end_time,
    )

    # Sprawdzenie wymaganych parametrów
    if not start_date or not start_time:
        raise ValueError("Musisz podać datę i godzinę rozpoczęcia.")
    if not end_date or not end_time:
        raise ValueError("Musisz podać datę i godzinę zakończenia.")

    # Konwersja daty i czasu do obiektów datetime
    start = parse_datetime(start_date, start_time)
    end = parse_datetime(end_date, end_time)

    # Walidacja czasu zakończenia
    if end <= start:
        print(f'st: {start} end: {end}')
        raise ValueError("Czas zakończenia musi być po czasie rozpoczęcia.")

    # Konwersja do ISO 8601
    start_iso = start.isoformat()
    end_iso = end.isoformat()

    debug_log(start_iso=start_iso, end_iso=end_iso)

    # Autoryzacja do Google Calendar
    creds = authenticate()
    service = build('calendar', 'v3', credentials=creds)

    # Tworzenie wydarzenia
    event = {
        'summary': title,
        'description': description if description else "Brak opisu",
        'start': {
            'dateTime': start_iso,
            'timeZone': 'Europe/Warsaw',
        },
        'end': {
            'dateTime': end_iso,
            'timeZone': 'Europe/Warsaw',
        },
        'reminders': {
            'useDefault': True,
        },
    }

    # Wysłanie wydarzenia do Google Calendar
    try:
        event_result = service.events().insert(calendarId='primary', body=event).execute()
        print(f"Wydarzenie dodane: {event_result['summary']}")
        print(f"Czas rozpoczęcia: {event_result['start']['dateTime']}")
        print(f"Czas zakończenia: {event_result['end']['dateTime']}")
    except Exception as e:
        raise RuntimeError(f"Błąd podczas dodawania wydarzenia: {e}")
