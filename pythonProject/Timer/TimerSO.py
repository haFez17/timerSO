from abc import ABC, abstractmethod
import tkinter as tk
from Function import TimerFunction

class TimerInterface(ABC):
    @abstractmethod
    def start_timer(self):
        pass

    @abstractmethod
    def stop_timer(self):
        pass

    @abstractmethod
    def reset_timer(self):
        pass

class TimerApp(tk.Tk):
    def __init__(self, timer_function: TimerInterface):
        super().__init__()
        self.timer_function = timer_function
        self.title("Timer App")
        self.geometry("300x200")

        self.start_button = tk.Button(self, text="Start", command=self.timer_function.start_timer)
        self.start_button.pack()

        self.stop_button = tk.Button(self, text="Stop", command=self.timer_function.stop_timer)
        self.stop_button.pack()

        self.reset_button = tk.Button(self, text="Reset", command=self.timer_function.reset_timer)
        self.reset_button.pack()

if __name__ == "__main__":
    timer_function = TimerFunction()
    app = TimerApp(timer_function)
    app.mainloop()
