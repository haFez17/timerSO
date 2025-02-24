from TimerSO import *


class TimerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Супер Таймер")
        self.root.geometry("500x400")
        self.root.configure(bg="#2E3B4E")

        # Переменные для таймера
        self.hours = tk.StringVar(value="00")
        self.minutes = tk.StringVar(value="00")
        self.seconds = tk.StringVar(value="00")
        self.is_running = False
        self.is_paused = False # булево
        self.pause_event = threading.Event() # для потоков
        self.stop_event = threading.Event()
        self.timer_thread = None
        self.remaining_time = timedelta(seconds=0)

        self.title_text = tk.StringVar(value="СУПЕР ТАЙМЕР")

        self.timer_history = []

        self.presets = {
            "Помодоро": {"hours": "00", "minutes": "25", "seconds": "00"},
            "Короткий перерыв": {"hours": "00", "minutes": "05", "seconds": "00"},
            "Длинный перерыв": {"hours": "00", "minutes": "15", "seconds": "00"},
            "Яйцо вкрутую": {"hours": "00", "minutes": "10", "seconds": "00"}
        }

        self.create_widgets()

        # Настройка фоновой задачи для сохранения истории
        self.history_saver = threading.Thread(target=self.save_history_daemon, daemon=True)
        self.history_saver.start()

    def create_widgets(self):
        # Создание основного фрейма
        main_frame = tk.Frame(self.root, bg="#2E3B4E", padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        self.title_label = tk.Label(main_frame, textvariable=self.title_text, font=("Helvetica", 20, "bold"),
                                    bg="#2E3B4E", fg="#FFFFFF")
        self.title_label.pack(pady=10)

        # Фрейм для ввода времени
        time_frame = tk.Frame(main_frame, bg="#2E3B4E")
        time_frame.pack(pady=15)

        # Стиль для спинбоксов
        style = ttk.Style()
        style.configure("TSpinbox", fieldbackground="#3E4B5E", foreground="#FFFFFF",
                        background="#2E3B4E", font=("Helvetica", 18))

        # Часы, минуты, секунды
        hours_spinbox = ttk.Spinbox(time_frame, from_=0, to=23, wrap=True, width=3,
                                    textvariable=self.hours, justify="center",
                                    format="%02.0f", style="TSpinbox")
        hours_spinbox.pack(side=tk.LEFT, padx=5)

        tk.Label(time_frame, text=":", font=("Helvetica", 18), bg="#2E3B4E", fg="#FFFFFF").pack(side=tk.LEFT)

        minutes_spinbox = ttk.Spinbox(time_frame, from_=0, to=59, wrap=True, width=3,
                                      textvariable=self.minutes, justify="center",
                                      format="%02.0f", style="TSpinbox")
        minutes_spinbox.pack(side=tk.LEFT, padx=5)

        tk.Label(time_frame, text=":", font=("Helvetica", 18), bg="#2E3B4E", fg="#FFFFFF").pack(side=tk.LEFT)

        seconds_spinbox = ttk.Spinbox(time_frame, from_=0, to=59, wrap=True, width=3,
                                      textvariable=self.seconds, justify="center",
                                      format="%02.0f", style="TSpinbox")
        seconds_spinbox.pack(side=tk.LEFT, padx=5)

        # Фрейм для отображения счетчика
        counter_frame = tk.Frame(main_frame, bg="#2E3B4E")
        counter_frame.pack(pady=10)

        self.time_display = tk.Label(counter_frame, text="00:00:00",
                                     font=("Helvetica", 36, "bold"), bg="#2E3B4E", fg="#FF9500")
        self.time_display.pack()

        # Фрейм для кнопок управления
        buttons_frame = tk.Frame(main_frame, bg="#2E3B4E")
        buttons_frame.pack(pady=10)

        # Стиль для кнопок
        button_style = {"font": ("Helvetica", 12), "width": 10, "border": 0,
                        "borderwidth": 0, "highlightthickness": 0, "pady": 5}

        self.start_button = tk.Button(buttons_frame, text="Старт", bg="#4CAF50", fg="white",
                                      command=self.start_timer, **button_style)
        self.start_button.pack(side=tk.LEFT, padx=5)

        self.pause_button = tk.Button(buttons_frame, text="Пауза", bg="#FFC107", fg="white",
                                      command=self.pause_timer, state=tk.DISABLED, **button_style)
        self.pause_button.pack(side=tk.LEFT, padx=5)

        self.stop_button = tk.Button(buttons_frame, text="Стоп", bg="#F44336", fg="white",
                                     command=self.stop_timer, state=tk.DISABLED, **button_style)
        self.stop_button.pack(side=tk.LEFT, padx=5)

        # Фрейм для пресетов
        presets_frame = tk.Frame(main_frame, bg="#2E3B4E")
        presets_frame.pack(pady=10, fill=tk.X)

        tk.Label(presets_frame, text="Пресеты:", bg="#2E3B4E", fg="#FFFFFF",
                 font=("Helvetica", 12)).pack(anchor=tk.W)

        presets_buttons_frame = tk.Frame(presets_frame, bg="#2E3B4E")
        presets_buttons_frame.pack(fill=tk.X, pady=5)

        preset_button_style = {"font": ("Helvetica", 10), "border": 0,
                               "borderwidth": 0, "highlightthickness": 0, "pady": 3}

        for i, (name, values) in enumerate(self.presets.items()):
            preset_name = name  # Сохраняем имя в локальной переменной
            btn = tk.Button(presets_buttons_frame, text=preset_name, bg="#3E4B5E", fg="white",
                            command=lambda preset=values.copy(), name=preset_name: self.apply_preset(preset, name),
                            **preset_button_style)

            btn.grid(row=i // 2, column=i % 2, padx=5, pady=3, sticky=tk.W + tk.E)

        presets_buttons_frame.grid_columnconfigure(0, weight=1)
        presets_buttons_frame.grid_columnconfigure(1, weight=1)

        # Прогресс-бар
        self.progress = ttk.Progressbar(main_frame, orient="horizontal", length=400, mode="determinate")
        self.progress.pack(pady=10, fill=tk.X)

        # Метка для отображения информации
        self.info_label = tk.Label(main_frame, text="Готов к запуску", bg="#2E3B4E", fg="#AAAAAA")
        self.info_label.pack(pady=5)

    def apply_preset(self, preset, name):
        """Загружает и запускает предустановленные значения времени"""
        # Сначала останавливаем текущий таймер, если он запущен
        if self.is_running:
            self.stop_timer()

        # Устанавливаем название пресета в заголовок
        self.title_text.set(name)

        # Загружаем значения времени
        self.hours.set(preset["hours"])
        self.minutes.set(preset["minutes"])
        self.seconds.set(preset["seconds"])

        # Обновляем информационную метку
        hours_str = preset["hours"]
        minutes_str = preset["minutes"]
        seconds_str = preset["seconds"]
        self.info_label.config(text=f"Пресет загружен: {hours_str}:{minutes_str}:{seconds_str}")

        # Автоматически запускаем таймер
        self.start_timer()

    def load_preset(self, preset):
        """Загружает предустановленные значения времени без запуска"""
        self.hours.set(preset["hours"])
        self.minutes.set(preset["minutes"])
        self.seconds.set(preset["seconds"])

        # Обновляем информационную метку
        hours_str = preset["hours"]
        minutes_str = preset["minutes"]
        seconds_str = preset["seconds"]
        self.info_label.config(text=f"Пресет загружен: {hours_str}:{minutes_str}:{seconds_str}")

    def start_timer(self):
        if self.is_paused:
            self.is_paused = False
            self.pause_event.set()
            self.start_button.config(state=tk.DISABLED)
            self.pause_button.config(state=tk.NORMAL)
            return

        if self.is_running:
            return

        # Получаем время из спинбоксов
        try:
            h = int(self.hours.get())
            m = int(self.minutes.get())
            s = int(self.seconds.get())

            if h == 0 and m == 0 and s == 0:
                messagebox.showwarning("Ошибка", "Установите время больше нуля!")
                return

            self.total_seconds = h * 3600 + m * 60 + s
            self.remaining_time = timedelta(seconds=self.total_seconds)

            # Запуск таймера в отдельном потоке
            self.stop_event.clear()
            self.pause_event.set()
            self.is_running = True
            self.timer_thread = threading.Thread(target=self.run_timer, daemon=True)
            self.timer_thread.start()

            # Запись в историю
            self.timer_history.append({
                "start_time": datetime.now(),
                "duration": self.total_seconds,
                "status": "started"
            })

            # Обновление интерфейса
            self.start_button.config(state=tk.DISABLED)
            self.pause_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.NORMAL)
            self.info_label.config(text="Таймер запущен")

        except ValueError:
            messagebox.showerror("Ошибка", "Пожалуйста, введите корректные значения!")

    def pause_timer(self):
        if not self.is_running:
            return

        if self.is_paused:
            self.is_paused = False
            self.pause_event.set()
            self.pause_button.config(text="Пауза")
            self.start_button.config(state=tk.DISABLED)
            self.info_label.config(text="Таймер продолжен")
        else:
            self.is_paused = True
            self.pause_event.clear()
            self.pause_button.config(text="Продолжить")
            self.start_button.config(state=tk.NORMAL)
            self.info_label.config(text="Таймер на паузе")

        # Запись в историю
        status = "paused" if self.is_paused else "resumed"
        self.timer_history.append({
            "time": datetime.now(),
            "status": status
        })

    def stop_timer(self):
        if not self.is_running:
            return

        self.stop_event.set()
        self.pause_event.set()  # Освобождаем поток от ожидания, если он на паузе

        # Запись в историю
        self.timer_history.append({
            "time": datetime.now(),
            "status": "stopped"
        })

        # Сбрасываем состояние
        self.is_running = False
        self.is_paused = False

        # Обновление интерфейса
        self.pause_button.config(text="Пауза")
        self.start_button.config(state=tk.NORMAL)
        self.pause_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.DISABLED)
        self.progress.config(value=0)
        self.time_display.config(text="00:00:00")
        self.info_label.config(text="Таймер остановлен")

        # Возвращаем стандартный заголовок
        self.title_text.set("СУПЕР ТАЙМЕР")

    def run_timer(self):
        start_time = datetime.now()
        total_seconds = self.total_seconds

        while self.remaining_time.total_seconds() > 0 and not self.stop_event.is_set():
            # Проверка на паузу
            self.pause_event.wait()
            if self.stop_event.is_set():
                break

            # Форматирование времени
            hours, remainder = divmod(int(self.remaining_time.total_seconds()), 3600)
            minutes, seconds = divmod(remainder, 60)
            time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            progress_value = 100 - self.remaining_time.total_seconds() / total_seconds * 100

            # Обновление интерфейса в основном потоке
            self.root.after(0, self.update_display, time_str, progress_value)

            # Пауза потока
            time.sleep(1)

            # Обновление оставшегося времени ПОСЛЕ паузы
            self.remaining_time -= timedelta(seconds=1)

        # Если таймер не остановлен принудительно, значит он завершился естественным путем
        if not self.stop_event.is_set():
            self.root.after(0, self.timer_completed)

    def update_display(self, time_str, progress_value):
        self.time_display.config(text=time_str)
        self.progress.config(value=progress_value)

    def timer_completed(self):
        self.is_running = False
        self.progress.config(value=100)
        self.time_display.config(text="00:00:00")
        self.info_label.config(text="Таймер завершен!")
        self.start_button.config(state=tk.NORMAL)
        self.pause_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.DISABLED)

        # Возвращаем стандартный заголовок
        self.title_text.set("СУПЕР ТАЙМЕР")

        # Запись в историю
        self.timer_history.append({
            "time": datetime.now(),
            "status": "completed"
        })

        # Показываем уведомление
        messagebox.showinfo("Таймер завершен", "Время истекло!")

    def save_history_daemon(self):
        """Демон-поток для периодического сохранения истории таймеров"""
        while True:
            # Проверка, есть ли что сохранять
            if self.timer_history:
                try:
                    with open("timer_history.txt", "a", encoding="utf-8") as f:
                        for entry in self.timer_history:
                            f.write(f"{datetime.now()} - {entry}\n")
                    self.timer_history = []  # Очищаем после сохранения
                except Exception as e:
                    print(f"Ошибка при сохранении истории: {e}")

            # Пауза перед следующей проверкой
            time.sleep(30)  # Сохраняем каждые 30 секунд

    def on_closing(self):
        """Обработчик закрытия приложения"""
        if self.is_running:
            if messagebox.askyesno("Выход", "Таймер активен. Вы уверены, что хотите выйти?"):
                self.stop_timer()
                self.root.destroy()
        else:
            self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = TimerApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()