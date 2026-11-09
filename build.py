"""
Скрипт автоматической сборки фоторедактора в исполняемый файл
(вариант 1: базовая сборка, PyInstaller, режим --onefile).

Запуск из активированного виртуального окружения:
    python build.py
"""

import os
import subprocess
import sys

APP_NAME = "PhotoEditor"
ENTRY_POINT = "photo_editor.py"
ICON_FILE = "icon.ico"  # необязательно: если файла нет, иконка не добавляется


def get_build_command():
    """Сформировать команду PyInstaller (список аргументов, не строка)."""
    # python -m PyInstaller работает и из виртуального окружения
    command = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",          # один исполняемый файл
        "--windowed",         # без консольного окна (GUI-приложение)
        "--noconfirm",        # перезаписывать прошлую сборку без вопросов
        "--clean",            # очистить кэш PyInstaller
        "--name", APP_NAME,   # имя результата: dist/PhotoEditor.exe
        "--hidden-import", "cv2",
    ]
    if os.path.exists(ICON_FILE):
        command += ["--icon", ICON_FILE]
    command.append(ENTRY_POINT)
    return command


def run_build():
    """Запустить процесс сборки. Вернуть True при успехе."""
    if not os.path.exists(ENTRY_POINT):
        print(f"Ошибка: не найден файл {ENTRY_POINT}")
        return False

    command = get_build_command()
    print("Команда сборки:")
    print(" ".join(command))

    try:
        subprocess.run(command, check=True)
    except FileNotFoundError:
        print("Ошибка: Python или PyInstaller не найден.")
        return False
    except subprocess.CalledProcessError as e:
        print(f"Ошибка сборки, код возврата: {e.returncode}")
        print("Подсказка: установите PyInstaller командой "
              "pip install pyinstaller")
        return False
    return True


def test_executable():
    """Проверить собранный файл и вывести информацию о дистрибутиве."""
    exe_name = APP_NAME + (".exe" if sys.platform.startswith("win") else "")
    exe_path = os.path.join("dist", exe_name)

    if not os.path.exists(exe_path):
        print(f"Ошибка: файл {exe_path} не найден")
        return False

    size_mb = os.path.getsize(exe_path) / (1024 * 1024)
    print("Дистрибутив:")
    print(f"  Файл:   {os.path.abspath(exe_path)}")
    print(f"  Размер: {size_mb:.1f} МБ")
    return True


if __name__ == "__main__":
    print("Начинаю сборку...")
    if run_build() and test_executable():
        print("Сборка завершена!")
    else:
        print("Сборка не удалась.")
        sys.exit(1)
