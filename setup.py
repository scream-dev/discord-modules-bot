import os
import requests
import subprocess
import sys

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def check_discord_token(token):
    try:
        headers = {'Authorization': f'Bot {token}'}
        response = requests.get('https://discord.com/api/v10/users/@me', headers=headers)
        return response.status_code == 200
    except:
        return False

def get_input(prompt, optional=False):
    while True:
        user_input = input(prompt).strip()
        if user_input or optional:
            return user_input if user_input else None
        print("❌Это поле обязательно для заполнения. Пожалуйста, введите значение.")

def yes_no_prompt(prompt):
    while True:
        answer = input(prompt).strip().lower()
        if answer in ('y', 'n'):
            return answer == 'y'
        print("❌Пожалуйста, введите 'y' или 'n'.")

def install_dependencies():
    print("\n🔄️Проверяю зависимости...")
    
    # Создаем requirements.txt если его нет
    if not os.path.exists('requirements.txt'):
        with open('requirements.txt', 'w', encoding='utf-8') as f:
            f.write('discord.py>=2.3.0\n')
            f.write('python-dotenv>=1.0.0\n')
            f.write('requests>=2.31.0\n')
    
    while True:
        print("\n🔄️Устанавливаю зависимости...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
            print("✔️Зависимости установлены")
            return True
        except subprocess.CalledProcessError as e:
            print(f"✖️При установке зависимостей произошла ошибка:\n{e}")
            if not yes_no_prompt("Повторить попытку? (y/n): "):
                return False

def check_requirements():
    """Проверяет наличие необходимых файлов"""
    required_files = ['main.py', 'requirements.txt']
    missing_files = []
    
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"⚠️Отсутствуют необходимые файлы: {', '.join(missing_files)}")
        return False
    return True

def install():
    clear_screen()
    
    # Проверка необходимых файлов
    if not check_requirements():
        print("❌Установка не может быть продолжена.")
        return
    
    # Шаг 1: Проверка .env файла
    if os.path.exists('.env'):
        print("⚠️Обнаружен .env, при установке он очистится и заполнится новыми данными!")
        if not yes_no_prompt("Хотите продолжить установку? (y/n): "):
            print("❌Установка отменена.")
            return
        os.remove('.env')
    
    # Создаем новый .env файл
    with open('.env', 'w', encoding='utf-8') as f:
        pass
    
    # Шаг 2: Подтверждение источника
    print("\n👍Установщик не собирает никаких введённых данных, но мы можем гарантировать безопасность, только если вы скачали его из официального репозитория.")
    print("Если вы установили его из другого источника, то воспользуйтесь: https://github.com/scream-dev/discord-modules-bot и попробуйте снова.")
    if not yes_no_prompt("Продолжить установку? (y/n): "):
        print("❌Установка отменена.")
        os.remove('.env')
        return
    
    # Шаг 3: Ввод токена бота
    discord_token = None
    last_token = None
    while True:
        token_input = get_input("\n🔑Введите токен бота: ")
        
        if last_token is not None and token_input == last_token:
            discord_token = token_input
            break
        
        if check_discord_token(token_input):
            discord_token = token_input
            break
        else:
            print("❌Ваш токен не прошёл проверку на подлинность. Если вы уверены, что токен верный, отправьте его ещё раз, но это не гарантирует то, что он будет работать:")
            last_token = token_input
    
    # Шаг 4: Ввод ID канала для логов (необязательно)
    log_channel_id = get_input("\n#️⃣Введите ID канала для логов (необязательно): ", optional=True)
    
    # Шаг 5: Ввод ID администратора
    bot_owner_id = get_input("\n👑Введите ID администратора: ")
    
    # Шаг 6: Создание необходимых файлов
    if not os.path.exists('modules.txt'):
        with open('modules.txt', 'w', encoding='utf-8') as f:
            f.write('# Список загруженных модулей\n')
            f.write('# Добавьте пути к модулям, по одному на строку\n')
            f.write('# Пример: example_module.py\n\n')
    
    # Запись всех данных в .env
    with open('.env', 'w', encoding='utf-8') as f:
        f.write(f"DISCORD_TOKEN={discord_token}\n")
        f.write(f"LOG_CHANNEL_ID={log_channel_id if log_channel_id else '0'}\n")
        f.write(f"BOT_OWNER_ID={bot_owner_id}\n")
        f.write("# Написано Scream [dev]\n")
    
    # Шаг 7: Установка зависимостей
    if not install_dependencies():
        print("❌Установка зависимостей не удалась. Некоторые функции бота могут не работать.")
        return
    
    # Шаг 8: Завершение установки
    print("\n" + "="*50)
    print("✅ Discord Modules Bot успешно установлен!")
    print("="*50)
    print("\n📁 Созданные файлы:")
    print("  • .env - настройки бота")
    print("  • modules.txt - список модулей")
    print("  • requirements.txt - зависимости")
    print("\n🚀 Для запуска бота выполните:")
    print("  python main.py")
    print("\n🛠️ Все введённые данные можно изменить в файле .env")
    print("\n💡 Создайте свой первый модуль в папке с ботом и добавьте его командой:")
    print("  !add ваш_модуль.py")

if __name__ == "__main__":
    install()
