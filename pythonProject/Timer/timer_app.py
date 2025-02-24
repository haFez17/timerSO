from TimerSO import *


class TimerThread(QThread):
    update_signal = pyqtSignal(int)
    finished_signal = pyqtSignal()

    def __init__(self, total_seconds):
        super().__init__()
        self.time_left = total_seconds
        self.running = True

    def run(self):
        while self.time_left > 0 and self.running:
            self.sleep(1)
            self.time_left -= 1
            self.update_signal.emit(self.time_left)

        if self.running:
            self.finished_signal.emit()

    def stop(self):
        self.running = False


class AlarmThread(QThread):
    alarm_signal = pyqtSignal()

    def __init__(self, alarm_time):
        super().__init__()
        self.alarm_time = alarm_time
        self.running = True

    def run(self):
        while self.running:
            if QDateTime.currentDateTime() >= self.alarm_time:
                self.alarm_signal.emit()
                break
            self.sleep(1)

    def stop(self):
        self.running = False


class TimerApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Таймер и Будильник")
        self.setGeometry(100, 100, 400, 300)
        self.setStyleSheet("background-color: #2E2E2E; color: white;")

        self.layout = QVBoxLayout()
        self.tabs = QTabWidget()

        # Таймер
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

        # Будильник
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

        # Вкладки
        self.tabs.addTab(self.timer_tab, "Таймер")
        self.tabs.addTab(self.alarm_tab, "Будильник")

        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

        # Логика таймера и будильника
        self.timer_thread = None
        self.alarm_thread = None

        # Подключаем кнопки
        self.timer_start_btn.clicked.connect(self.start_timer)
        self.timer_stop_btn.clicked.connect(self.stop_timer)
        self.alarm_set_btn.clicked.connect(self.set_alarm)

    def start_timer(self):
        if self.timer_thread and self.timer_thread.isRunning():
            return

        time = self.timer_input.time()
        total_seconds = time.hour() * 3600 + time.minute() * 60 + time.second()

        if total_seconds == 0:
            return

        self.timer_thread = TimerThread(total_seconds)
        self.timer_thread.update_signal.connect(self.update_timer_label)
        self.timer_thread.finished_signal.connect(self.show_timer_finished)
        self.timer_thread.start()

    def update_timer_label(self, time_left):
        self.timer_label.setText(f"Оставшееся время: {time_left} сек")

    def stop_timer(self):
        if self.timer_thread:
            self.timer_thread.stop()
            self.timer_thread = None
            self.timer_label.setText("Таймер остановлен")

    def set_alarm(self):
        if self.alarm_thread and self.alarm_thread.isRunning():
            return

        alarm_time = self.alarm_input.dateTime()
        self.alarm_label.setText(f"Будильник установлен на {alarm_time.toString()}")

        self.alarm_thread = AlarmThread(alarm_time)
        self.alarm_thread.alarm_signal.connect(self.show_alarm_popup)
        self.alarm_thread.start()

    def show_timer_finished(self):
        QMessageBox.information(self, "Таймер", "Таймер завершился!")

    def show_alarm_popup(self):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Будильник!")
        msg_box.setText("Будильник прозвенел!")
        stop_btn = msg_box.addButton("Остановить", QMessageBox.ButtonRole.AcceptRole)
        snooze_btn = msg_box.addButton("Попозже (+15 минут)", QMessageBox.ButtonRole.ActionRole)

        msg_box.exec()

        if msg_box.clickedButton() == snooze_btn:
            self.snooze_alarm()

    def snooze_alarm(self):
        if self.alarm_thread:
            self.alarm_thread.stop()

        new_time = QDateTime.currentDateTime().addSecs(900)
        self.alarm_input.setDateTime(new_time)
        self.set_alarm()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TimerApp()
    window.show()
    sys.exit(app.exec())
