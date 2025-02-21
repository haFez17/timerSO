from TimerSO import *


class TimerFunction:
    def __init__(self, app):
        self.app = app
        self.running = False
        self.time_left = 10
        self.timer_thread = None

    def _run_timer(self):
        while self.running and self.time_left > 0:
            time.sleep(1)
            self.time_left -= 1
            self.app.timer_label.setText(f"Оставшееся время: {self.time_left} сек")

        if self.time_left == 0:
            self.app.show_timer_finished()

    def start_timer(self):
        if not self.running:
            self.running = True
            self.timer_thread = threading.Thread(target=self._run_timer)
            self.timer_thread.start()

    def stop_timer(self):
        self.running = False


class AlarmFunction:
    def __init__(self, app):
        self.app = app
        self.alarm_set = False
        self.alarm_time = 10

    def set_alarm(self):
        if not self.alarm_set:
            self.alarm_set = True
            self.app.alarm_label.setText(f"Будильник установлен через {self.alarm_time} сек")
            threading.Timer(self.alarm_time, self.trigger_alarm).start()

    def trigger_alarm(self):
        self.app.show_alarm_popup()
        self.alarm_set = False

    def snooze_alarm(self):
        self.alarm_set = True
        self.alarm_time = 15
        self.app.alarm_label.setText(f"Будильник отложен на 15 минут")
        threading.Timer(self.alarm_time, self.trigger_alarm).start()


class TimerApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Таймер и Будильник")
        self.setGeometry(100, 100, 400, 300)

        self.layout = QVBoxLayout()
        self.tabs = QTabWidget()

        # Вкладка Таймер
        self.timer_tab = QWidget()
        self.timer_layout = QVBoxLayout()
        self.timer_label = QLabel("Оставшееся время: 0 сек")
        self.timer_start_btn = QPushButton("Старт Таймера")
        self.timer_stop_btn = QPushButton("Остановить Таймер")

        self.timer_layout.addWidget(self.timer_label)
        self.timer_layout.addWidget(self.timer_start_btn)
        self.timer_layout.addWidget(self.timer_stop_btn)
        self.timer_tab.setLayout(self.timer_layout)

        # Вкладка Будильник
        self.alarm_tab = QWidget()
        self.alarm_layout = QVBoxLayout()
        self.alarm_label = QLabel("Будильник: Не установлен")
        self.alarm_set_btn = QPushButton("Установить Будильник на 10 сек")

        self.alarm_layout.addWidget(self.alarm_label)
        self.alarm_layout.addWidget(self.alarm_set_btn)
        self.alarm_tab.setLayout(self.alarm_layout)

        # Добавляем вкладки
        self.tabs.addTab(self.timer_tab, "Таймер")
        self.tabs.addTab(self.alarm_tab, "Будильник")

        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

        # Логика таймера и будильника
        self.timer_function = TimerFunction(self)
        self.alarm_function = AlarmFunction(self)

        # Подключаем кнопки к функциям
        self.timer_start_btn.clicked.connect(self.timer_function.start_timer)
        self.timer_stop_btn.clicked.connect(self.timer_function.stop_timer)
        self.alarm_set_btn.clicked.connect(self.alarm_function.set_alarm)

    def show_timer_finished(self):
        QMessageBox.information(self, "Таймер", "Таймер завершился!")

    def show_alarm_popup(self):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Будильник!")
        msg_box.setText("Будильник прозвенел!")
        msg_box.addButton("Остановить", QMessageBox.ButtonRole.AcceptRole)
        snooze_btn = msg_box.addButton("Попозже (+15 минут)", QMessageBox.ButtonRole.ActionRole)

        msg_box.exec()

        if msg_box.clickedButton() == snooze_btn:
            self.alarm_function.snooze_alarm()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TimerApp()
    window.show()
    sys.exit(app.exec())