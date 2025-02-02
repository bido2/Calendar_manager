import tkinter as tk
from tkinter import messagebox
from tkcalendar import Calendar

def open_calendar():
    # Tworzenie nowego okna z kalendarzem
    calendar_window = tk.Toplevel(root)
    calendar_window.title("Wybierz datę")

    # Kalendarz
    cal = Calendar(calendar_window, selectmode="day", date_pattern="dd.mm.yyyy")
    cal.pack(pady=20)

    # Przycisk do zatwierdzania daty
    def select_date():
        selected_date = cal.get_date()
        messagebox.showinfo("Wybrana data", f"Wybrałeś datę: {selected_date}")
        calendar_window.destroy()

    tk.Button(calendar_window, text="Zatwierdź", command=select_date).pack(pady=10)

# Główne okno aplikacji
root = tk.Tk()
root.title("Wybór daty")

# Przycisk do otwarcia kalendarza
tk.Button(root, text="Wybierz datę", command=open_calendar).pack(pady=20)

# Uruchomienie pętli aplikacji
root.mainloop()
