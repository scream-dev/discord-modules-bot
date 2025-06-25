import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import traceback

load_dotenv()

class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix='!', intents=intents)
        self.modules_file = "modules.txt"
        self.loaded_modules = []
        self.log_channel_id = int(os.getenv('LOG_CHANNEL_ID'))
        self.log_channel = None
        self.owner_id = int(os.getenv('BOT_OWNER_ID'))

    async def on_ready(self):
        print(f'Бот {self.user} успешно подключился к Discord!')
        self.log_channel = self.get_channel(self.log_channel_id)
        await self.load_initial_modules()
        await self.send_startup_report()

    async def send_startup_report(self):
        """Отправляет отчёт о загруженных модулях"""
        if not self.log_channel:
            return

        loaded = []
        failed = []
        
        for module in self.loaded_modules:
            try:
                await self.load_extension(module.replace('.py', ''))
                loaded.append(module)
            except Exception as e:
                failed.append(f"{module}: {str(e)}")
                print(f"Ошибка загрузки {module}: {str(e)}")
                traceback.print_exc()

        message = "**Отчёт о запуске бота**\n\n"
        message += f"🟢 Успешно загружено модулей: {len(loaded)}\n"
        
        if loaded:
            message += "```\n" + "\n".join(loaded) + "\n```\n"
        
        if failed:
            message += f"🔴 Ошибки загрузки ({len(failed)}):\n"
            message += "```\n" + "\n".join(failed) + "\n```"
        else:
            message += "🔴 Ошибок загрузки нет"

        await self.log_channel.send(message)

    async def load_initial_modules(self):
        """Загружает модули из файла modules.txt"""
        if not os.path.exists(self.modules_file):
            return

        with open(self.modules_file, 'r') as f:
            modules = [line.strip() for line in f.readlines() if line.strip()]
            self.loaded_modules = modules

    async def add_module(self, module_path: str):
        """Добавляет новый модуль"""
        if module_path in self.loaded_modules:
            return False
            
        try:
            await self.load_extension(module_path.replace('.py', ''))
            self.loaded_modules.append(module_path)
            self.save_modules_list()
            return True
        except Exception as e:
            error_msg = f"Ошибка загрузки модуля {module_path}: {str(e)}"
            print(error_msg)
            traceback.print_exc()
            await self.log_channel.send(f"❌ {error_msg}")
            return False

    def save_modules_list(self):
        """Сохраняет список модулей в файл"""
        with open(self.modules_file, 'w') as f:
            f.write('\n'.join(self.loaded_modules))

    async def reload_all_modules(self):
        """Перезагружает все модули"""
        success = True
        modules_to_reload = self.loaded_modules.copy()
        
        for module_path in modules_to_reload:
            try:
                await self.reload_extension(module_path.replace('.py', ''))
                await self.log_channel.send(f"🔄 Модуль {module_path} успешно перезагружен")
            except Exception as e:
                success = False
                error_msg = f"Ошибка перезагрузки {module_path}: {str(e)}"
                print(error_msg)
                traceback.print_exc()
                await self.log_channel.send(f"❌ {error_msg}")
        
        return success

bot = Bot()

@bot.command()
@commands.is_owner()
async def update(ctx):
    """Перезагружает все модули (только для владельца)"""
    await ctx.send("Начинаю перезагрузку модулей...")
    if await bot.reload_all_modules():
        await ctx.send("✅ Все модули успешно перезагружены!")
    else:
        await ctx.send("⚠ Перезагрузка завершена с ошибками (см. логи)")

@bot.command()
@commands.is_owner()
async def add(ctx, module_path: str):
    """Добавляет новый модуль (только для владельца)"""
    if not os.path.exists(module_path):
        await ctx.send(f"❌ Файл {module_path} не найден!")
        return
        
    if await bot.add_module(module_path):
        await ctx.send(f"✅ Модуль {module_path} успешно добавлен!")
    else:
        await ctx.send(f"❌ Не удалось загрузить модуль {module_path} (см. логи)")

if __name__ == "__main__":
    TOKEN = os.getenv('DISCORD_TOKEN')
    if not TOKEN:
        print("Ошибка: Токен DISCORD_TOKEN не найден в .env файле")
    else:
        bot.run(TOKEN)
