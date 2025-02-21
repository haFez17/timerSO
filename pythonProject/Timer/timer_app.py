from TimerSO import *


class TimerFunction:
    def __init__(self, app):
        self.app = app
        self.running = False
        self.time_left = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)

    def start_timer(self):
        if not self.running:
            self.running = True
            time = self.app.timer_input.time()
            self.time_left = time.hour() * 3600 + time.minute() * 60 + time.second()
            self.timer.start(1000)

    def update_timer(self):
        if self.time_left > 0:
            self.time_left -= 1
            self.app.timer_label.setText(f"Оставшееся время: {self.time_left} сек")
        else:
            self.timer.stop()
            self.running = False
            self.app.show_timer_finished()

    def stop_timer(self):
        self.running = False
        self.timer.stop()


class AlarmFunction:
    def __init__(self, app):
        self.app = app
        self.alarm_timer = QTimer()
        self.alarm_timer.timeout.connect(self.check_alarm)
        self.alarm_timer.start(1000)
        self.alarm_time = None

    def set_alarm(self):
        self.alarm_time = self.app.alarm_input.dateTime()
        self.app.alarm_label.setText(f"Будильник установлен на {self.alarm_time.toString()}")

    def check_alarm(self):
        if self.alarm_time and QDateTime.currentDateTime() >= self.alarm_time:
            self.trigger_alarm()
            self.alarm_time = None

    def trigger_alarm(self):
        self.app.show_alarm_popup()

    def snooze_alarm(self):
        self.alarm_time = QDateTime.currentDateTime().addSecs(900)
        self.app.alarm_label.setText(f"Будильник отложен на 15 минут")


class TimerApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Таймер и Будильник")
        self.setGeometry(100, 100, 400, 300)
        self.setStyleSheet("background-color: #2E2E2E; color: white;")  # Основной стиль

        self.layout = QVBoxLayout()
        self.tabs = QTabWidget()

        # Вкладка Таймер
        self.timer_tab = QWidget()
        self.timer_layout = QVBoxLayout()
        self.timer_label = QLabel("Оставшееся время: 0 сек")
        self.timer_label.setStyleSheet("font-size: 16px;")
        self.timer_input = QTimeEdit()
        self.timer_input.setDisplayFormat("hh:mm:ss")
        self.timer_start_btn = QPushButton("Старт Таймера")
        self.timer_stop_btn = QPushButton("Остановить Таймер")

        self.timer_layout.addWidget(self.timer_label)
        self.timer_layout.addWidget(self.timer_input)
        self.timer_layout.addWidget(self.timer_start_btn)
        self.timer_layout.addWidget(self.timer_stop_btn)
        self.timer_tab.setLayout(self.timer_layout)

        # Вкладка Будильник
        self.alarm_tab = QWidget()
        self.alarm_layout = QVBoxLayout()
        self.alarm_label = QLabel("Будильник: Не установлен")
        self.alarm_label.setStyleSheet("font-size: 16px;")
        self.alarm_input = QDateTimeEdit()
        self.alarm_input.setDisplayFormat("dd.MM.yyyy hh:mm:ss")
        self.alarm_set_btn = QPushButton("Установить Будильник")

        self.alarm_layout.addWidget(self.alarm_label)
        self.alarm_layout.addWidget(self.alarm_input)
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
