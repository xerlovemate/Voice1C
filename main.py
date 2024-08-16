import json
import time
import keyboard
import pyaudio
import pyautogui
from plyer import notification
from vosk import Model, KaldiRecognizer


model = Model('model')
rec = KaldiRecognizer(model, 16000)
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
stream.start_stream()

voice_control_enabled = False


def notification_on(title_my, message_my):
    notification.notify(title=title_my, message=message_my, app_icon = 'open.ico', timeout = 2 )

def notification_off(title_my, message_my):
    notification.notify(title=title_my, message=message_my, app_icon = 'close.ico', timeout = 2 )

def listen():
    while True:
        data = stream.read(4000, exception_on_overflow=False)
        if (rec.AcceptWaveform(data)) and (len(data) > 0):
            answer = json.loads(rec.Result())
            if answer['text']:
                yield answer['text']


def menu():
    print('1) Режим 1С')
    print('2) Обычный режим')
    print('3) Выход')


def copy():
    pyautogui.hotkey('ctrl', 'c')

def paste():
    pyautogui.hotkey('ctrl', 'v')

def cut():
    pyautogui.hotkey('ctrl', 'x')

def find():
    pyautogui.hotkey('ctrl', 'f')

def delete():
    keyboard.press('ctrl + shift + left')
    keyboard.press('delete')
    time.sleep(0.1)
    keyboard.release('ctrl + shift + left')
    keyboard.release('delete')

def tab():
    keyboard.press('Tab')

def enter():
    keyboard.press('Enter')


def oneCSpeech():
    print('Выбран режим 1С!')
    for text in listen():
        zbstxt = (text.title().replace(' ', '').replace('Пробел', " ").replace("ВосклицательныйЗнак", "!")
                  .replace("Собака","@").replace('ДвойнаяКавычках','"').replace("Кавычках","'")
                  .replace('Решётка', "#").replace('Доллар','$').replace('ТочкаСЗапятой', ";")
                  .replace('Процент',"%").replace('Двоеточие',":")
                  .replace("АмперСант", "&").replace("АмперСанд", "&").replace("АмперСанкт", "&")
                  .replace("АмберСанд", "&").replace("АмберСаунд", "&").replace("АмберСанкт", "&")
                  .replace("АмпирСанд", "&").replace("АмберСант", "&").replace('ВопросительныйЗнак', "?")
                  .replace('ЗнакВопроса',"?").replace("Звездочка", "*").replace('КвадратнаяСкобкаОткрывается', "[")
                  .replace('КвадратнаяСкобкаЗакрывается', "]").replace('ФигурнаяСкобкаОткрывается', "{")
                  .replace('ФигурнаяСкобкаЗакрывается', "}").replace('СкобкаОткрывается', "(")
                  .replace('СкобкаЗакрывается', ")").replace("Тире", "-").replace('Минус', '-').replace('Плюс', "+")
                  .replace('Равно',"=").replace("Слэш","/").replace("Один", "1").replace("Два", "2").replace("Три", "3")
                  .replace("Четыре","4").replace("Пять", "5").replace("Шесть", "6").replace("Семь", "7")
                  .replace("Восемь","8").replace("Девять","9").replace("Ноль", "0").replace('Точка', ".")
                  .replace('Запятая',",").replace('НижнееПодчёркивание', "_")
                  .replace('Больше', ">").replace("Меньше", "<").replace('Андерсон', '&')
                  .replace("ё", "е").replace("Ё", "Е"))

        if text == 'старт':
            voice_control_enabled = True
            notification_on("Vocie1C", "Программа запущена!")
        elif text == 'стоп':
            voice_control_enabled = False
            notification_off("Voice1C", "Программа остановлена!")
        elif text == 'выйди':
            break
        elif voice_control_enabled:
            if text == "эндер" or text == "интер":
                enter()
            elif text == "тап" or text == "табы":
                tab()
            elif text == "удали" or text == 'вдали' or text == 'дали':
                delete()
            elif text == 'копье':
                copy()
            elif text == 'паста':
                paste()
            elif text == 'вырезать':
                cut()
            elif text == 'поиск':
                find()
            else:
                keyboard.write(zbstxt)
                #print(zbstext)    #logs


def defoultSpeech():
    print('Выбран обычный режим!')
    for text in listen():
        zbstxt = (text.replace("восклицательный знак", "!")
                  .replace("собака", "@").replace('двойная кавычках', '"').replace("кавычках", "'")
                  .replace('решётка', "#").replace('доллар', '$').replace('точка с запятой', ";")
                  .replace('процент', "%").replace('двоеточие', ":")
                  .replace("ампер сант", "&").replace("ампер санд", "&").replace("ампер санкт", "&")
                  .replace("амбер санд", "&").replace("амбер саунд", "&").replace("амбер санкт", "&")
                  .replace("ампир санд", "&").replace("амбер сант", "&").replace('вопросительный знак', "?")
                  .replace('знак вопроса', "?").replace("звездочка", "*").replace('квадратная скобка открывается', "[")
                  .replace('квадратная скобка закрывается', "]").replace('фигурная скобка открывается', "{")
                  .replace('фигурная скобка закрывается', "}").replace('скобка открывается', "(")
                  .replace('скобка закрывается', ")").replace("тире", "-").replace('минус', '-').replace('плюс', "+")
                  .replace('равно', "=").replace("слэш", "/").replace("один", "1").replace("два", "2").replace("три", "3")
                  .replace("четыре", "4").replace("пять", "5").replace("шесть", "6").replace("семь", "7")
                  .replace("восемь", "8").replace("девять", "9").replace("ноль", "0").replace('точка', ".")
                  .replace('запятая', ",").replace('нижнее подчёркивание', "_")
                  .replace('больше', ">").replace("меньше", "<").replace('андерсон', '&')
                  .replace("ё", "е").replace('пробел', ' ').capitalize())
        if text == 'старт':
            voice_control_enabled = True
            notification_on("Vocie1C", "Программа запущена!")
        elif text == 'стоп':
            voice_control_enabled = False
            notification_off("Voice1C", "Программа остановлена!")
        elif text == 'выйди':
            break
        elif voice_control_enabled:
            if text == "эндер" or text == "интер":
                enter()
            elif text == "тап" or text == "табы":
                tab()
            elif text == "удали" or text == 'вдали' or text == 'дали':
                delete()
            elif text == 'копье':
                copy()
            elif text == 'паста':
                paste()
            elif text == 'вырезать':
                cut()
            elif text == 'поиск':
                find()
            else:
                keyboard.write(zbstxt)


print('Программа запущена!')

while True:
    menu()
    choice = input('Выберите режим: ')

    if choice == '1':
        oneCSpeech()
        input('Нажмите Enter, чтобы вернуться в меню...')
    elif choice == '2':
        defoultSpeech()
        input('Нажмите Enter, чтобы вернуться в меню...')
    elif choice == '3':
        print('До свидания!')
        break
    else:
        print('Ошибка: Введите корректную опцию (1, 2 или 3)')

input()