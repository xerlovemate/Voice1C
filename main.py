import sys
import json
import asyncio
import time
import keyboard
import pyaudio
import pyautogui
from plyer import notification
from vosk import Model, KaldiRecognizer
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget
from PyQt5.QtGui import QIcon
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)


class VoiceThread(QThread):
    update_status_signal = pyqtSignal(str)

    def __init__(self, model_path, mode='default'):
        super().__init__()
        self.model_path = model_path
        self.mode = mode
        self.running = True
        self.voice_control_enabled = False

    def run(self):
        asyncio.run(self.async_run())

    async def async_run(self):
        try:
            model = Model(self.model_path)
        except Exception as e:
            self.update_status_signal.emit(f'Ошибка загрузки модели: {str(e)}')
            return

        rec = KaldiRecognizer(model, 16000)
        p = pyaudio.PyAudio()

        stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=1024)

        self.update_status_signal.emit(
            f'Голосовое управление запущено в режиме: {"1С" if self.mode == "1c" else "Обычный"}')

        try:
            stream.start_stream()

            async for text in self.async_listen(stream, rec):
                if not self.running:
                    break

                zbstxt = self.process_text(text)

                if text == 'старт':
                    self.voice_control_enabled = True
                    self.update_status_signal.emit('Голосовое управление включено!')
                    notification.notify(title="Voice1C", message="Программа запущена!", app_icon='open.ico', timeout=2)
                elif text == 'стоп':
                    self.voice_control_enabled = False
                    self.update_status_signal.emit('Голосовое управление остановлено!')
                    notification.notify(title="Voice1C", message="Программа остановлена!", app_icon='close.ico',
                                        timeout=2)
                elif self.voice_control_enabled:
                    asyncio.create_task(self.perform_action_async(text, zbstxt))

        except Exception as e:
            self.update_status_signal.emit(f'Ошибка при работе с аудиопотоком: {str(e)}')
        finally:
            stream.stop_stream()
            stream.close()
            p.terminate()

    async def async_listen(self, stream, rec):
        while self.running:
            data = await asyncio.to_thread(stream.read, 1024, exception_on_overflow=False)
            if rec.AcceptWaveform(data):
                answer = json.loads(rec.Result())
                if answer.get('text'):
                    yield answer['text']
            await asyncio.sleep(0.05)

    def process_text(self, text):
        replacements = {
            "восклицательный знак": "!", "собака": "@", "двойная кавычках": '""',
            "двойные кавычки": '""', "кавычках": "''", "кавычки": "''",
            "решётка": "#", "доллар": "$", "точка с запятой": ";", "процент": "%", "двоеточие": ":",
            "ампер сант": "&", "ампер санд": "&", "ампер санкт": "&", "амбер санд": "&", "амбер саунд": "&",
            "амбер санкт": "&", "ампир санд": "&", "амбер сант": "&", "вопросительный знак": "?",
            "знак вопроса": "?", "звёздочка": "*",
            "квадратные скобки": "[]", "фигурные скобки": "{}", "скобки": "()",
            "квадратная скобка": "[]", "фигурная скобка": "{}", "скобка": "()",
            "тире": "-", "минус": "-", "плюс": "+", "равно": "=", "слэш": "/",
            "один": "1", "два": "2", "три": "3", "четыре": "4", "пять": "5", "шесть": "6", "восемь": "8",
            "семь": "7", "девять": "9", "ноль": "0", "точка": ".", "запятая": ", ", "нижнее подчёркивание": "_",
            "больше": ">", "меньше": "<", "андерсон": "&", "ё": "е"
        }

        for key, value in replacements.items():
            text = text.replace(key, value)

        if self.mode == '1c':
            text = text.title().replace(' ', '')
            text = text.replace('Пробел', ' ')
            text = text.replace('=', ' = ')
            text = text.replace(',',', ')
        else:
            text = text.replace('пробел', ' ').capitalize()

        return text

    async def perform_action_async(self, text, zbstxt):
        if text in ["эндер", "интер", "эмбер", "центр"]:
            await asyncio.to_thread(keyboard.press_and_release, 'Enter')
        elif text in ["тап", "табы", "тапа", "бы"]:
            await asyncio.to_thread(keyboard.press_and_release, 'Tab')
        elif text in ["удали", "вдали", "дали"]:
            await asyncio.to_thread(self.delete_word)
        elif text in ["точка с запятой"]:
            await asyncio.to_thread(keyboard.write, ';')
            await asyncio.to_thread(pyautogui.hotkey, 'enter')
        elif text in ['лево', 'лева', 'влево', 'слева']:
            await asyncio.to_thread(self.left)
        elif text in ['право', 'права', 'вправо', 'правы', 'справа', 'в праву']:
            await asyncio.to_thread(self.right)
        elif text == "копье":
            await asyncio.to_thread(pyautogui.hotkey, 'ctrl', 'c')
            time.sleep(1)
        elif text == "паста":
            await asyncio.to_thread(pyautogui.hotkey, 'ctrl', 'v')
        elif text == "вырезать":
            await asyncio.to_thread(pyautogui.hotkey, 'ctrl', 'x')
        elif text == "поиск":
            await asyncio.to_thread(pyautogui.hotkey, 'ctrl', 'f')
        else:
            await asyncio.to_thread(keyboard.write, zbstxt)

    def left(self):
        keyboard.press_and_release('left')

    def right(self):
        keyboard.press_and_release('right')

    def delete_word(self):
        keyboard.press('ctrl')
        keyboard.press('backspace')

        time.sleep(0.05)

        keyboard.release('backspace')
        keyboard.release('ctrl')

class VoiceControlApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Voice 1C')
        self.setGeometry(100, 100, 600, 300)
        self.setWindowIcon(QIcon('icon.ico'))
        self.setFixedSize(600, 300)

        self.status_label = QLabel('Выберите режим', self)
        self.mode_selection_widget = QWidget(self)
        self.mode_selection_layout = QVBoxLayout(self.mode_selection_widget)

        self.mode_1c_button = QPushButton('Режим 1С', self)
        self.default_mode_button = QPushButton('Обычный режим', self)
        self.return_to_menu_button = QPushButton('Вернуться в меню', self)
        self.return_to_menu_button.setVisible(False)

        self.mode_selection_layout.addWidget(self.mode_1c_button)
        self.mode_selection_layout.addWidget(self.default_mode_button)
        self.mode_selection_widget.setLayout(self.mode_selection_layout)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.status_label, alignment=Qt.AlignCenter)
        main_layout.addWidget(self.mode_selection_widget, alignment=Qt.AlignCenter)
        main_layout.addWidget(self.return_to_menu_button, alignment=Qt.AlignCenter)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        self.load_stylesheet('styles.css')

        self.mode_1c_button.clicked.connect(self.start_mode_1c)
        self.default_mode_button.clicked.connect(self.start_default_mode)
        self.return_to_menu_button.clicked.connect(self.return_to_menu)

    def load_stylesheet(self, filename):
        with open(filename, 'r') as f:
            stylesheet = f.read()
        self.setStyleSheet(stylesheet)

    def start_mode_1c(self):
        self.start_voice_thread('1c')

    def start_default_mode(self):
        self.start_voice_thread('default')

    def start_voice_thread(self, mode):
        self.status_label.setText(f'Запуск голосового управления ({mode})...')
        self.mode_selection_widget.setVisible(False)
        self.return_to_menu_button.setVisible(True)
        try:
            self.voice_thread = VoiceThread(model_path="model", mode=mode)
            self.voice_thread.update_status_signal.connect(self.update_status)
            self.voice_thread.start()
        except Exception as e:
            self.status_label.setText(f'Ошибка при запуске потока: {str(e)}')

    def update_status(self, status):
        self.status_label.setText(status)

    def return_to_menu(self):
        if hasattr(self, 'voice_thread') and self.voice_thread.isRunning():
            self.voice_thread.running = False
            self.voice_thread.wait()
        self.status_label.setText('Выберите режим')
        self.mode_selection_widget.setVisible(True)
        self.return_to_menu_button.setVisible(False)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VoiceControlApp()
    window.show()
    sys.exit(app.exec_())