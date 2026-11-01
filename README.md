# __The project will be completely redesigned to meet modern realities in the near future. It is outdated in terms of its architecture__
# 🚀 DMB - Discord Modules Bot  
## Позволяет вам быстро загружать модули для вашего Discord бота

---

## 📥 Установка

### Способ 1: Клонирование репозитория
```bash
git clone https://github.com/scream-dev/discord-modules-bot.git
cd discord-modules-bot
```

### Способ 2: Прямая загрузка
[📦 Скачать ZIP-архив](https://github.com/scream-dev/discord-modules-bot/archive/refs/heads/main.zip)

### Настройка бота
1. **Запустите установщик:**
```python
python setup.py
```

2. **Введите данные, которые запросит установщик:**
- Токен бота
- Канал для логов (необязательно)
- ID администратора бота

### Альтернативная настройка
Вы также можете вручную создать файл `.env` со следующим содержимым:
```env
DISCORD_TOKEN=ваш_токен_бота
LOG_CHANNEL_ID=0
BOT_OWNER_ID=ваш_id_администратора
```
*Примечание: использование `setup.py` проще для новичков.*

3. **Для запуска бота используйте:**
```python
python main.py
```

---

## 🛠 Команды владельца
| Команда | Описание | Пример |
|---------|----------|--------|
| `!add [файл]` | Добавить новый модуль | `!add my_module.py` |
| `!remove [файл]` | Удалить модуль | `!remove old_module.py` |
| `!update` | Перезагрузить все модули | `!update` |
| `!modules` | Показать список модулей | `!modules` |
| `!status` | Показать статус бота | `!status` |
| `!shutdown` | Выключить бота | `!shutdown` |

---

## 📁 Базовая структура модуля
Каждый модуль должен быть классом, унаследованным от `commands.Cog` и содержать:
- `__init__` – инициализация (настройки, переменные)
- `setup` – функция для загрузки модуля (обязательная)
- Команды (`@commands.command()`)
- Обработчики событий (`@commands.Cog.listener()`)

**Пример минимального модуля:**
```python
import discord
from discord.ext import commands

class MyCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot  # Передаем бота в модуль
    
    @commands.command(name="test")
    async def test_command(self, ctx):
        await ctx.send("Тестовая команда работает!")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        print(f"Получено сообщение: {message.content}")

async def setup(bot):
    await bot.add_cog(MyCog(bot))  # Обязательная функция для загрузки
```

---

## 🔧 Обязательные элементы
### **(1) Класс модуля**
- Должен наследоваться от `commands.Cog`.
- В `__init__` обязательно передавать `bot` и сохранять его в `self.bot`.

### **(2) Функция `setup(bot)`**
- **Обязательная** для загрузки модуля.
- Должна быть асинхронной (`async def`).
- Должна содержать `await bot.add_cog(MyCog(bot))`.

### **(3) Обработка ошибок**
- Все команды и события должны иметь `try-except` с логированием.
- Пример:
```python
@commands.command(name="ping")
async def ping(self, ctx):
    try:
        await ctx.send("Pong!")
    except Exception as e:
        print(f"Ошибка в команде ping: {e}")
```

---

## 📋 Особенности и правила
### **(1) Импорты**
- Все необходимые библиотеки (`discord`, `asyncio` и др.) должны быть в начале файла.
- Если модуль использует `.env`, добавьте:
```python
from dotenv import load_dotenv
load_dotenv()
```

### **(2) Конфигурация**
- Если модуль требует настройки (ID каналов, токены), выносите их в **верхние переменные**:
```python
class MyCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ADMIN_ID = 123456789  # Пример ID админа
        self.LOG_CHANNEL_ID = 987654321  # Пример ID канала для логов
```

### **(3) Команды (`@commands.command`)**
- Все команды должны быть методами класса.
- Используйте `name="название"`, если хотите изменить имя команды.
- Пример:
```python
@commands.command(name="hello")
async def hello(self, ctx):
    await ctx.send(f"Привет, {ctx.author.mention}!")
```

### **(4) События (`@commands.Cog.listener`)**
- Если модуль должен реагировать на сообщения/ивенты, используйте:
```python
@commands.Cog.listener()
async def on_message(self, message):
    if message.author.bot:
        return
    print(f"Новое сообщение: {message.content}")
```

### **(5) Асинхронная инициализация**
- Если модулю нужно загрузить данные при старте (БД, конфиги), используйте:
```python
async def cog_load(self):
    """Вызывается при загрузке модуля"""
    print("Модуль загружен!")
    self.data = await self.load_data()  # Пример асинхронной загрузки
```

---

## ❌ Что нельзя делать
❌ **Не создавайте глобальных переменных бота**  
Вместо:
```python
bot = commands.Bot(...)  # ❌ Неправильно
```
Используйте:
```python
class MyCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot  # ✅ Правильно
```

❌ **Не используйте `on_message` без `@commands.Cog.listener()`**  
Неправильно:
```python
async def on_message(message):  # ❌ Не сработает
```
Правильно:
```python
@commands.Cog.listener()
async def on_message(self, message):  # ✅ Работает
```

❌ **Не забывайте про `await` в асинхронных функциях**  
Неправильно:
```python
@commands.command()
def test(ctx):  # ❌ Без async/await
    ctx.send("Test")  # ❌ Без await
```
Правильно:
```python
@commands.command()
async def test(self, ctx):  # ✅
    await ctx.send("Test")  # ✅
```

---

## 📝 Пример готового модуля (шаблон)
```python
import discord
from discord.ext import commands
import asyncio

class ExampleCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.settings = {
            "PREFIX": "!",
            "ADMIN_ROLE": "Admin"
        }
    
    async def cog_load(self):
        print(f"Модуль {self.__class__.__name__} загружен!")
    
    @commands.command(name="greet")
    async def greet_user(self, ctx, user: discord.Member):
        try:
            await ctx.send(f"Привет, {user.mention}!")
        except Exception as e:
            print(f"Ошибка: {e}")
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        print(f"{member.name} зашел на сервер!")

async def setup(bot):
    await bot.add_cog(ExampleCog(bot))
```

---

## 📊 Логирование
Бот использует систему логирования Python. Все логи сохраняются в файл `bot.log` и выводятся в консоль.
Формат логов:
```
2024-01-01 12:00:00 - bot - INFO - Бот успешно подключился к Discord!
2024-01-01 12:00:01 - bot - INFO - Модуль example.py успешно загружен
```

---

## 🎯 Итог
1. **Структура**: Класс + `setup(bot)`.
2. **Команды**: `@commands.command()`.
3. **События**: `@commands.Cog.listener()`.
4. **Ошибки**: Всегда `try-except`.
5. **Асинхронность**: Все команды с `async/await`.
6. **Конфиги**: Выносите настройки в `__init__`.
