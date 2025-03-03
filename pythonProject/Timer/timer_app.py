from TimerSO import *
from tkcalendar import Calendar

class TimerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Таймер и Будильник от Омара")
        self.root.geometry("500x400")
        self.root.configure(bg="#DEB887")

        # Вкладки
        self.tab_control = ttk.Notebook(root)
        self.timer_tab = ttk.Frame(self.tab_control)
        self.alarm_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.timer_tab, text="Таймер")
        self.tab_control.add(self.alarm_tab, text="Будильник")
        self.tab_control.pack(expand=1, fill="both")

        # ====== Таймер ======
        self.timer_label = tk.Label(self.timer_tab, text="Оставшееся время: 00:00:00", font=("Courier", 14), fg="blue", bg="#F0FFFF")
        self.timer_label.grid(row=0, column=0, columnspan=2, pady=10)

        self.timer_entry = tk.Entry(self.timer_tab, font=("Courier", 12), width=10, justify="center")
        self.timer_entry.insert(0, "00:00:10")
        self.timer_entry.grid(row=1, column=0, columnspan=2, pady=5)

        self.start_timer_btn = tk.Button(self.timer_tab, text="Старт Таймера", command=self.start_timer, font=("Times-Roman", 12), fg="green", bg="#444", width=20, height=2)
        self.start_timer_btn.grid(row=2, column=0, padx=10, pady=5)

        self.stop_timer_btn = tk.Button(self.timer_tab, text="Остановить Таймер", command=self.stop_timer, font=("Times-Roman", 12), fg="green", bg="#444", width=20, height=2)
        self.stop_timer_btn.grid(row=2, column=1, padx=10, pady=5)

        self.timer_running = False

        # ====== Будильник ======
        self.alarm_label = tk.Label(self.alarm_tab, text="Будильник: Не установлен", font=("Courier", 14), fg="blue", bg="#F0FFFF")
        self.alarm_label.grid(row=0, column=0, columnspan=2, pady=10)

        self.calendar = Calendar(self.alarm_tab, selectmode='day', date_pattern='yyyy-mm-dd')
        self.calendar.grid(row=1, column=0, columnspan=2, pady=5)

        self.alarm_entry = tk.Entry(self.alarm_tab, font=("Arial", 12), width=10, justify="center")
        self.alarm_entry.insert(0, datetime.now().strftime("%H:%M:%S"))
        self.alarm_entry.grid(row=2, column=0, columnspan=2, pady=5)

        self.set_alarm_btn = tk.Button(self.alarm_tab, text="Установить Будильник", command=self.set_alarm, font=("Arial", 12), fg="white", bg="#444", width=20, height=2)
        self.set_alarm_btn.grid(row=3, column=0, columnspan=2, pady=5)

        self.alarm_running = False

    def set_alarm(self):
        if self.alarm_running:
            return

        date_str = self.calendar.get_date()
        time_str = self.alarm_entry.get()
        try:
            alarm_datetime = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
        except ValueError:
            messagebox.showerror("Ошибка", "Введите время в формате ЧЧ:ММ:СС")
            return

        self.alarm_running = True
        self.alarm_label.config(text=f"Будильник установлен на {alarm_datetime}")

        threading.Thread(target=self.check_alarm, args=(alarm_datetime,), daemon=True).start()

    def check_alarm(self, alarm_datetime):
        while self.alarm_running:
            if datetime.now() >= alarm_datetime:
                self.show_alarm_popup()
                break
            time.sleep(1)

    def show_alarm_popup(self):
        self.alarm_running = False
        self.alarm_label.config(text="Будильник: Не установлен")

        response = messagebox.askquestion("Будильник", "Будильник сработал!\nОтложить на 15 минут?")
        if response == "yes":
            new_time = datetime.now() + timedelta(minutes=15)
            self.alarm_entry.delete(0, tk.END)
            self.alarm_entry.insert(0, new_time.strftime("%H:%M:%S"))
            self.set_alarm()

    def start_timer(self):
        if self.timer_running:
            return

        self.timer_running = True
        try:
            time_parts = list(map(int, self.timer_entry.get().split(":")))
            if len(time_parts) == 3:
                total_seconds = time_parts[0] * 3600 + time_parts[1] * 60 + time_parts[2]
            else:
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "Введите время в формате ЧЧ:ММ:СС")
            return

        threading.Thread(target=self.run_timer, args=(total_seconds,), daemon=True).start()

    def run_timer(self, total_seconds):
        while total_seconds > 0 and self.timer_running:
            mins, secs = divmod(total_seconds, 60)
            hours, mins = divmod(mins, 60)
            self.timer_label.config(text=f"Оставшееся время: {hours:02}:{mins:02}:{secs:02}")
            time.sleep(1)
            total_seconds -= 1

        if self.timer_running:
            self.timer_label.config(text="Таймер завершён!")
            messagebox.showinfo("Таймер", "Время вышло!")

        self.timer_running = False

    def stop_timer(self):
        self.timer_running = False
        self.timer_label.config(text="Оставшееся время: 00:00:00")


if __name__ == "__main__":
    root = tk.Tk()
    app = TimerApp(root)
    root.mainloop()
