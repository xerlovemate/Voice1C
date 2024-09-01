import ctypes

def get_keyboard_layout():
    user32 = ctypes.windll.user32
    hwnd = user32.GetForegroundWindow()
    thread_id = user32.GetWindowThreadProcessId(hwnd, None)
    layout_id = user32.GetKeyboardLayout(thread_id)

    lid = layout_id & (2**16 - 1)
    return lid

def is_russian_layout():
    rus_layout_ids = [0x419]
    return get_keyboard_layout() in rus_layout_ids