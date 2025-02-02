from datetime import datetime
from tkinter import *
from tkinter import messagebox
from tkcalendar import Calendar

from calendar_services import get_events_today, create_event, delete_event

# główne okno aplikacji
def create_window():
    global main_window
    global events

    # funkcja do tworzenia gui nowych okien
    def window_gui():
        window = Toplevel()
        window.title('Calendar Manager')
        window.minsize(300,0)
        return window

    # Funkcja tworząca główne okno aplikacji
    def create_main_window():
        global main_window
        main_window = Tk()
        main_window.geometry('300x100')
        main_window.title('Calendar Manager')

        show_button = Button(main_window, text="Pokaż wydarzenia", command=show_events)
        show_button.grid(row=0, column=0, padx=10, pady=10)

        create_button = Button(main_window, text='Dodaj wydarzenie', command=new_event)
        create_button.grid(row=0, column=1, padx=10, pady=10)

        main_window.grid_rowconfigure(0, weight=1)
        main_window.grid_columnconfigure(0, weight=1)
        main_window.grid_columnconfigure(1, weight=1)

        # Center both buttons horizontally in the middle of the window
        main_window.grid_rowconfigure(0, weight=1)
        main_window.grid_columnconfigure(0, weight=1)
        main_window.grid_columnconfigure(1, weight=1)

        main_window.mainloop()

    # Funkcja wyświetlająca wydarzenia
    def show_events():
        def return_to_main_window():
            events_window.destroy()
            main_window.deiconify()

        # funkcja usuwająca elementy i wczytujaca na nowo po usunięciu
        def remove_event(event_id, events):
            ev = [event for event in events if event["id"] != event_id]
            delete_event(event_id)
            for widget in events_window.winfo_children():
                widget.destroy()
            display_events(ev)

        # Funkcja wyświetlająca listę wydarzeń w oknie
        def display_events(events: list):

            for index, ev in enumerate(events):
                # Debugowanie: Sprawdzamy zawartość wydarzenia
                print(f"DEBUG: wydarzenie {index + 1}: {ev}")

                # Sprawdzamy, czy daty są dostępne i odpowiednio je formatujemy
                start_time = ev.get('start_time', None)
                end_time = ev.get('end_time', None)

                if start_time and end_time:
                    # Formatowanie daty na bardziej czytelny format (np. 2025-01-27 12:00)
                    start_time_obj = datetime.fromisoformat(start_time)
                    end_time_obj = datetime.fromisoformat(end_time)

                    formatted_start_time = start_time_obj.strftime('%m-%d %H:%M')
                    formatted_end_time = end_time_obj.strftime('%m-%d %H:%M')

                    event_label = Label(events_window, text=f'{index + 1}. {ev["title"]} ({formatted_start_time} - {formatted_end_time})')
                else:
                    event_label = Label(events_window, text=f'{index + 1}. {ev["title"]} (Brak danych o czasie)')

                event_label.grid(row=index, column=0, sticky=W, padx=30, pady=5)

                delete_button = Button(events_window, text='Usuń',command=lambda event_id=ev['id']: remove_event(event_id, events))
                delete_button.grid(row=index, column=1, padx=10, pady=5)

            return_button = Button(events_window, text='Wróć', command=return_to_main_window)
            return_button.grid(row=len(events), column=0, sticky="sw", padx=10, pady=10)

        main_window.withdraw()
        events_window = window_gui()
        events_window.title('Dzisiejsze wydarzenia')
        events = get_events_today()
        print(f'EVENTS: {events}')
        display_events(events)


    # funkcja dodająca wydarzenie
    def new_event():
        def return_to_main_window():
            new_window.destroy()
            main_window.deiconify()


        def open_calendar(entry_field):
            calendar_window = Toplevel(new_window)
            calendar_window.title("Wybierz datę")

            # Tworzenie widżetu kalendarza
            cal = Calendar(calendar_window, selectmode="day", date_pattern="yyyy-mm-dd")
            cal.pack(pady=20)

            # Funkcja do zatwierdzania wybranej daty
            def select_date():
                selected_date = cal.get_date()
                entry_field.delete(0, 'end')  # Usunięcie starej zawartości pola tekstowego
                entry_field.insert(0, selected_date)  # Wstawienie wybranej daty
                calendar_window.destroy()  # Zamknięcie okna kalendarza

            Button(calendar_window, text="Zatwierdź", command=select_date).pack(pady=10)

        def add_event():
            title = title_entry.get().strip()
            description = desc_entry.get().strip()
            start_date = start_date_entry.get().strip()
            start_time = start_time_entry.get().strip()
            end_date = end_date_entry.get().strip()
            end_time = end_time_entry.get().strip()

            # Debugowanie: Wyświetlanie wartości
            print(
                f"DEBUG: title='{title}', description='{description}', start_date='{start_date}', start_time='{start_time}', end_date='{end_date}', end_time='{end_time}'")

            # Walidacja pól - czy są puste?
            if not title:
                messagebox.showerror("Błąd", "Tytuł wydarzenia nie może być pusty!")
                return 'stop'
            if not start_date:
                messagebox.showerror("Błąd", "Musisz podać datę rozpoczęcia!")
                return 'stop'
            if not end_date:
                end_date = start_date
                end_time = '23:59'
            if not start_time:
                start_time = '00:00'
            if not  end_time:
                end_time = '23:59'
            try:
                # Dodanie wydarzenia z walidacją danych wejściowych
                create_event(
                    title=title,
                    description=description,
                    start_date=start_date,
                    start_time=start_time,
                    end_date=end_date,
                    end_time=end_time
                )
            except ValueError as e:
                # Obsługa błędów formatu daty i godziny
                print(f"Błąd walidacji: {e}")
                messagebox.showerror("Błąd", f"Niepoprawne dane: {e}")
                return 'stop'
            except Exception as e:
                # Obsługa innych błędów
                print(f"Błąd: {e}")
                messagebox.showerror("Błąd", f"Nie udało się dodać wydarzenia: {e}")
                return 'stop'

        def add_and_return():
            if add_event() == 'stop':
                return
            return_to_main_window()
            messagebox.showinfo("Sukces", "Wydarzenie zostało dodane!")

        main_window.withdraw()
        new_window = window_gui()
        new_window.title('Szczegóły wydarzenia')

        Label(new_window, text="Tytuł:").grid(row=0, column=0, padx=10, pady=5, sticky='w')
        title_entry = Entry(new_window)
        title_entry.grid(row=0, column=1, padx=10, pady=5)

        Label(new_window, text="Opis:").grid(row=1, column=0, padx=10, pady=5, sticky='w')
        desc_entry = Entry(new_window)
        desc_entry.grid(row=1, column=1, padx=10, pady=5)

        Label(new_window, text="Data rozpoczęcia:").grid(row=2, column=0, padx=10, pady=5, sticky='w')
        start_date_entry = Entry(new_window)
        start_date_entry.grid(row=2, column=1, padx=10, pady=5)
        Button(new_window, text="Wybierz datę", command=lambda: open_calendar(start_date_entry)).grid(row=2, column=2,
                                                                                                      padx=10, pady=5)

        Label(new_window, text="Godzina rozpoczęcia:").grid(row=3, column=0, padx=10, pady=5, sticky='w')
        start_time_entry = Entry(new_window)
        start_time_entry.grid(row=3, column=1, padx=10, pady=5)

        Label(new_window, text="Data zakończenia:").grid(row=4, column=0, padx=10, pady=5, sticky='w')
        end_date_entry = Entry(new_window)
        end_date_entry.grid(row=4, column=1, padx=10, pady=5)
        Button(new_window, text="Wybierz datę", command=lambda: open_calendar(end_date_entry)).grid(row=4, column=2,
                                                                                                    padx=10, pady=5)

        Label(new_window, text="Godzina zakończenia:").grid(row=5, column=0, padx=10, pady=5,
                                                            sticky='w')  # Przesunięcie godziny zakończenia na nowy wiersz
        end_time_entry = Entry(new_window)
        end_time_entry.grid(row=5, column=1, padx=10, pady=5)

        Button(new_window, text="Dodaj wydarzenie", command=add_and_return).grid(row=6, column=0, columnspan=2, pady=10)

        Button(new_window, text='Wróć', command=return_to_main_window).grid(row=7, column=0, sticky="sw", padx=10, pady=10)

    create_main_window()

if __name__ == "__main__":
    create_window()
