# import threading
# import time
# from PyQt6.QtCore import QTimer
# from interface import TimerInterface
#
# class TimerFunction(TimerInterface):
#     def __init__(self, app):
#         self.app = app
#         self.running = False
#         self.time_left = 10
#         self.timer_thread = None
#
#     def _run_timer(self):
#         while self.running and self.time_left > 0:
#             time.sleep(1)
#             self.time_left -= 1
#             self.app.timer_label.setText(f"Оставшееся время: {self.time_left} сек")
#
#         if self.time_left == 0:
#             self.app.show_timer_finished()
#
#     def start_timer(self):
#         if not self.running:
#             self.running = True
#             self.timer_thread = threading.Thread(target=self._run_timer)
#             self.timer_thread.start()
#
#     def stop_timer(self):
#         self.running = False
#
#     def reset_timer(self):
#         self.running = False
#         self.time_left = 10
#         self.app.timer_label.setText("Оставшееся время: 10 сек")
#
#
# class AlarmFunction:
#     def __init__(self, app):
#         self.app = app
#         self.alarm_set = False
#         self.alarm_time = 10
#
#     def set_alarm(self):
#         if not self.alarm_set:
#             self.alarm_set = True
#             self.app.alarm_label.setText(f"Будильник установлен через {self.alarm_time} сек")
#             threading.Timer(self.alarm_time, self.trigger_alarm).start()
#
#     def trigger_alarm(self):
#         self.app.show_alarm_popup()
#         self.alarm_set = False
#
#     def snooze_alarm(self):
#         self.alarm_set = True
#         self.alarm_time = 15
#         self.app.alarm_label.setText(f"Будильник отложен на 15 минут")
#         threading.Timer(self.alarm_time, self.trigger_alarm).start()
