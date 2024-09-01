import json
import asyncio
import pyaudio
from vosk import Model, KaldiRecognizer
from PyQt5.QtCore import QThread, pyqtSignal
from rapidfuzz import process
from plyer import notification
import keyboard as kb
from pynput.keyboard import Key, Controller
from utils import is_russian_layout

keyboard = Controller()

class VoiceThread(QThread):
    update_status_signal = pyqtSignal(str)

    def __init__(self, model_path, mode='default'):
        super().__init__()
        self.model_path = model_path
        self.mode = mode
        self.running = True
        self.voice_control_enabled = False
        self.russian_layout = is_russian_layout()

    def fuzzy_match(self, text, commands, threshold=75):
        if len(text) <= 2:
            return None

        match, score, _ = process.extractOne(text, commands)
        if score >= threshold:
            return match
        return None

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
        self.update_status_signal.emit(f'Голосовое управление запущено в режиме: {"1С" if self.mode == "1c" else "Обычный"}')

        try:
            stream.start_stream()

            async for text in self.async_listen(stream, rec):
                if not self.running:
                    break

                zbstxt = self.process_text(text)

                if text in ['старт']:
                    self.voice_control_enabled = True
                    self.update_status_signal.emit('Голосовое управление включено!')
                    notification.notify(title="Voice1C", message="Программа запущена!", app_icon='open.ico', timeout=2)
                elif text in ['стоп', 'сто']:
                    self.voice_control_enabled = False
                    self.update_status_signal.emit('Голосовое управление остановлено!')
                    notification.notify(title="Voice1C", message="Программа остановлена!", app_icon='close.ico', timeout=2)
                elif self.voice_control_enabled:
                    await self.perform_action_async(text, zbstxt)

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
            text = text.replace(',', ', ')
            text = text.replace('Нал', "NULL")
            text = text.replace('Ну', "NULL")
        else:
            text = text.replace('пробел', ' ')

        return text

    async def perform_action_async(self, text, zbstxt):
        commands = {
            "интер": ["эндер", "интер"],
            "таб": ["тап", "так", "пап"],
            "удали": ["удали"],
            "лево": ['лево', 'слева'],
            "право": ['право', 'справа'],
            "копье": ["копье"],
            "паста": ["паста"],
            "вырезать": ["вырезать", 'вязать'],
            "поиск": ["поиск"]
        }

        for action, keywords in commands.items():
            match = self.fuzzy_match(text, keywords)
            if match:
                if action == "интер":
                    self.press_and_release(Key.enter)
                elif action == "таб":
                    self.press_and_release(Key.tab)
                elif action == "удали":
                    self.delete_word()
                elif action == "лево":
                    self.left()
                elif action == "право":
                    self.right()
                elif action == "копье":
                    self.copy_text()
                elif action == "паста":
                    self.paste_text()
                elif action == "вырезать":
                    self.cut_text()
                elif action == "поиск":
                    self.search_text()
                return

        self.write_text(zbstxt)

    def press_and_release(self, key):
        keyboard.press(key)
        keyboard.release(key)

    def left(self):
        self.press_and_release(Key.left)

    def right(self):
        self.press_and_release(Key.right)

    def delete_word(self):
        with keyboard.pressed(Key.ctrl):
            self.press_and_release(Key.backspace)

    def copy_text(self):
        with keyboard.pressed(Key.ctrl):
            self.press_and_release('с' if self.russian_layout else 'c')

    def paste_text(self):
        with keyboard.pressed(Key.ctrl):
            self.press_and_release('м' if self.russian_layout else 'v')

    def cut_text(self):
        with keyboard.pressed(Key.ctrl):
            self.press_and_release('ч' if self.russian_layout else 'x')

    def search_text(self):
        with keyboard.pressed(Key.ctrl):
            self.press_and_release('а' if self.russian_layout else 'f')

    def write_text(self, text):
        kb.write(text, delay=0.005)
