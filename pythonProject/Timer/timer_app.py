from TimerSO import *

class TimerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Таймер и Будильник")
        self.root.geometry("1280x720")
        self.root.configure(bg="#DEB887")  # Цвет фона

        # Создаем вкладки
        self.tab_control = ttk.Notebook(root)

        self.timer_tab = ttk.Frame(self.tab_control)
        self.alarm_tab = ttk.Frame(self.tab_control)

        self.tab_control.add(self.timer_tab, text="Таймер")
        self.tab_control.add(self.alarm_tab, text="Будильник")

        self.tab_control.pack(expand=1, fill="both")

        # ====== Таймер ======
        self.timer_label = tk.Label(self.timer_tab, text="Оставшееся время: 00:00:00", font=("Courier", 14), fg="blue", bg="#F0FFFF")
        self.timer_label.pack(pady=10)

        self.timer_entry = tk.Entry(self.timer_tab, font=("Courier", 12), width=10, justify="center")
        self.timer_entry.insert(0, "00:00:10")
        self.timer_entry.pack(pady=5)

        self.start_timer_btn = tk.Button(self.timer_tab, text="Старт Таймера", command=self.start_timer, font=("Times-Roman", 12), fg="green", bg="#444", width=20, height=2)
        self.start_timer_btn.pack(pady=5)

        self.stop_timer_btn = tk.Button(self.timer_tab, text="Остановить Таймер", command=self.stop_timer, font=("Times-Roman", 12), fg="green", bg="#444", width=20, height=2)
        self.stop_timer_btn.pack(pady=5)

        self.timer_running = False

        # ====== Будильник ======
        self.alarm_label = tk.Label(self.alarm_tab, text="Будильник: Не установлен", font=("Courier", 14), fg="blue", bg="#F0FFFF")
        self.alarm_label.pack(pady=10)

        self.alarm_entry = tk.Entry(self.alarm_tab, font=("Arial", 12), width=20, justify="center")
        self.alarm_entry.insert(0, datetime.now().strftime("%H:%M:%S"))  # Текущее время
        self.alarm_entry.pack(pady=5)

        self.set_alarm_btn = tk.Button(self.alarm_tab, text="Установить Будильник", command=self.set_alarm, font=("Arial", 12), fg="white", bg="#444", width=20, height=2)
        self.set_alarm_btn.pack(pady=5)

        self.alarm_running = False

    # ===== Таймер =====
    def start_timer(self):
        if self.timer_running:
            return

        time_str = self.timer_entry.get()
        try:
            h, m, s = map(int, time_str.split(":"))
            total_seconds = h * 3600 + m * 60 + s
        except ValueError:
            messagebox.showerror("Ошибка", "Введите время в формате ЧЧ:ММ:СС")
            return

        if total_seconds <= 0:
            messagebox.showerror("Ошибка", "Введите положительное время")
            return

        self.timer_running = True
        self.update_timer(total_seconds)

    def update_timer(self, time_left):
        if time_left <= 0:
            self.timer_label.config(text="Таймер завершен!")
            messagebox.showinfo("Таймер", "Время истекло!")
            self.timer_running = False
            return

        h, m, s = time_left // 3600, (time_left % 3600) // 60, time_left % 60
        self.timer_label.config(text=f"Оставшееся время: {h:02}:{m:02}:{s:02}")

        self.timer_thread = threading.Timer(1, lambda: self.update_timer(time_left - 1))
        self.timer_thread.start()

    def stop_timer(self):
        self.timer_running = False
        self.timer_label.config(text="Таймер остановлен!")

    # ===== Будильник =====
    def set_alarm(self):
        if self.alarm_running:
            return

        time_str = self.alarm_entry.get()
        try:
            alarm_time = datetime.strptime(time_str, "%H:%M:%S").time()
        except ValueError:
            messagebox.showerror("Ошибка", "Введите время в формате ЧЧ:ММ:СС")
            return

        self.alarm_running = True
        self.alarm_label.config(text=f"Будильник установлен на {time_str}")

        threading.Thread(target=self.check_alarm, args=(alarm_time,), daemon=True).start()

    def check_alarm(self, alarm_time):
        while self.alarm_running:
            now = datetime.now().time()
            if now >= alarm_time:
                self.show_alarm_popup()
                break
            time.sleep(1)

    def show_alarm_popup(self):
        self.alarm_running = False
        self.alarm_label.config(text="Будильник: Не установлен")

        response = messagebox.askquestion("Будильник", "Будильник сработал!\nОтложить на 15 минут?")
        if response == "yes":
            new_time = (datetime.now() + timedelta(minutes=15)).time()
            self.alarm_entry.delete(0, tk.END)
            self.alarm_entry.insert(0, new_time.strftime("%H:%M:%S"))
            self.set_alarm()


if __name__ == "__main__":
    root = tk.Tk()
    app = TimerApp(root)
    root.mainloop()
