import os
import sys
import json
import subprocess
import shutil

VERSION_FILE = "version.json"
APP_NAME = "FedsfmHybrid"

def get_version():
    """Чтение текущей версии из файла"""
    if os.path.exists(VERSION_FILE):
        with open(VERSION_FILE, 'r', encoding='utf-8') as f:
            return json.load(f).get("version", "1.0.0")
    return "1.0.0"

def save_version(version):
    """Сохранение новой версии"""
    with open(VERSION_FILE, 'w', encoding='utf-8') as f:
        json.dump({"version": version}, f, indent=4)

def increment_version(current, choice):
    """Логика повышения версии"""
    parts = current.split('.')
    major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])
    
    if choice == '1': # Patch (Исправления)
        patch += 1
    elif choice == '2': # Minor (Новые функции)
        minor += 1
        patch = 0
    elif choice == '3': # Major (Глобальные изменения)
        major += 1
        minor = 0
        patch = 0
    else:
        print("⚠️ Неверный выбор. Версия не изменена.")
        return current
        
    return f"{major}.{minor}.{patch}"

def build_exe(version):
    """Запуск PyInstaller"""
    print(f"\n🚀 Начинаем сборку {APP_NAME} v{version}...")
    
    # Очистка старых артефактов сборки
    for folder in ["dist", "build"]:
        if os.path.exists(folder):
            try:
                shutil.rmtree(folder)
            except PermissionError:
                print(f"⚠️ Не удалось удалить папку {folder}. Убедитесь, что .exe не запущен.")
    
    if os.path.exists(f"{APP_NAME}.spec"):
        os.remove(f"{APP_NAME}.spec")

    # Формирование команды PyInstaller
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconsole",          # Скрываем черное окно консоли
        "--onefile",            # Упаковываем всё в один .exe
        "--name", APP_NAME,     # Имя выходного файла
        "--clean",              # Очистка кэша PyInstaller
        # Скрытые импорты, которые PyInstaller может не заметить
        "--hidden-import", "apscheduler",
        "--hidden-import", "apscheduler.schedulers.background",
        "--hidden-import", "apscheduler.triggers.cron",
        "--hidden-import", "requests",
        "main.py"               # Точка входа
    ]

    try:
        # Запуск процесса сборки
        subprocess.run(cmd, check=True)
        print(f"\n✅ Сборка успешна!")
        print(f"📦 Готовый файл: dist/{APP_NAME}.exe")
        print(f"🔢 Версия: {version}")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Ошибка сборки: {e}")
    except FileNotFoundError:
        print("\n❌ PyInstaller не найден. Установите его: pip install pyinstaller")

def main():
    print("="*40)
    print("   FEDSFM HYBRID BUILD SYSTEM")
    print("="*40)
    
    current_ver = get_version()
    print(f"📌 Текущая версия: {current_ver}")
    
    print("\nКакие изменения были внесены в этой сборке?")
    print("1. Исправление ошибок (Patch)   -> v1.0.1")
    print("2. Новые функции (Minor)       -> v1.1.0")
    print("3. Глобальные изменения (Major)-> v2.0.0")
    print("0. Пропустить обновление версии")
    
    choice = input("\nВаш выбор (0-3): ").strip()
    
    if choice in ['1', '2', '3']:
        new_ver = increment_version(current_ver, choice)
        save_version(new_ver)
        print(f" Версия обновлена до: {new_ver}")
        build_exe(new_ver)
    elif choice == '0':
        print("️ Сборка с текущей версией...")
        build_exe(current_ver)
    else:
        print("❌ Отмена сборки.")

if __name__ == "__main__":
    main()