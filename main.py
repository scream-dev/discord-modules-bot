#26-1-1

import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import traceback
import logging
from datetime import datetime
import json

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

load_dotenv()

class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix='!', intents=intents)
        self.modules_file = "modules.txt"
        self.loaded_modules = []
        self.log_channel_id = int(os.getenv('LOG_CHANNEL_ID', 0))
        self.log_channel = None
        self.owner_id = int(os.getenv('BOT_OWNER_ID', 0))
        self.start_time = datetime.now()

    async def on_ready(self):
        logger.info(f'Бот {self.user} успешно подключился к Discord!')
        print(f'Бот {self.user} успешно подключился к Discord!')
        
        if self.log_channel_id:
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
                logger.info(f"Модуль {module} успешно загружен")
            except Exception as e:
                failed.append(f"{module}: {str(e)}")
                logger.error(f"Ошибка загрузки {module}: {str(e)}")
                logger.error(traceback.format_exc())

        message = f"**Отчёт о запуске бота**\n"
        message += f"🟢 Успешно загружено: {len(loaded)}\n"
        message += f"🔴 Ошибок загрузки: {len(failed)}\n"
        message += f"⏰ Время запуска: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        if loaded:
            message += "\n**Загруженные модули:**\n```\n" + "\n".join(loaded) + "\n```"
        
        if failed:
            message += "\n**Ошибки загрузки:**\n```\n" + "\n".join(failed) + "\n```"

        try:
            await self.log_channel.send(message)
        except Exception as e:
            logger.error(f"Не удалось отправить отчёт в лог-канал: {e}")

    async def load_initial_modules(self):
        """Загружает модули из файла modules.txt"""
        if not os.path.exists(self.modules_file):
            with open(self.modules_file, 'w') as f:
                f.write('# Добавьте пути к модулям, по одному на строку\n')
            return

        with open(self.modules_file, 'r') as f:
            modules = [line.strip() for line in f.readlines() 
                      if line.strip() and not line.startswith('#')]
            self.loaded_modules = modules
            logger.info(f"Загружено {len(modules)} модулей из файла")

    async def add_module(self, module_path: str):
        """Добавляет новый модуль"""
        if not module_path.endswith('.py'):
            module_path += '.py'
            
        if module_path in self.loaded_modules:
            logger.warning(f"Модуль {module_path} уже загружен")
            return False, "Модуль уже загружен"
            
        if not os.path.exists(module_path):
            logger.error(f"Файл {module_path} не найден")
            return False, "Файл не найден"
            
        try:
            module_name = module_path.replace('.py', '')
            await self.load_extension(module_name)
            self.loaded_modules.append(module_path)
            self.save_modules_list()
            logger.info(f"Модуль {module_path} успешно добавлен")
            return True, "Модуль успешно добавлен"
        except commands.ExtensionAlreadyLoaded:
            logger.error(f"Модуль {module_path} уже загружен")
            return False, "Модуль уже загружен"
        except commands.ExtensionNotFound:
            logger.error(f"Модуль {module_path} не найден")
            return False, "Модуль не найден"
        except commands.ExtensionFailed as e:
            error_msg = f"Ошибка загрузки модуля: {str(e.__cause__)}"
            logger.error(f"Ошибка в модуле {module_path}: {error_msg}")
            logger.error(traceback.format_exc())
            return False, error_msg
        except Exception as e:
            error_msg = f"Неизвестная ошибка: {str(e)}"
            logger.error(f"Ошибка загрузки {module_path}: {error_msg}")
            logger.error(traceback.format_exc())
            return False, error_msg

    async def remove_module(self, module_path: str):
        """Удаляет модуль"""
        if not module_path.endswith('.py'):
            module_path += '.py'
            
        if module_path not in self.loaded_modules:
            logger.warning(f"Модуль {module_path} не найден в списке загруженных")
            return False, "Модуль не найден в списке загруженных"
            
        try:
            module_name = module_path.replace('.py', '')
            await self.unload_extension(module_name)
            self.loaded_modules.remove(module_path)
            self.save_modules_list()
            logger.info(f"Модуль {module_path} успешно удалён")
            return True, "Модуль успешно удалён"
        except commands.ExtensionNotLoaded:
            logger.error(f"Модуль {module_path} не загружен")
            return False, "Модуль не загружен"
        except Exception as e:
            error_msg = f"Ошибка удаления: {str(e)}"
            logger.error(f"Ошибка удаления {module_path}: {error_msg}")
            logger.error(traceback.format_exc())
            return False, error_msg

    def save_modules_list(self):
        """Сохраняет список модулей в файл"""
        with open(self.modules_file, 'w') as f:
            f.write('# Список загруженных модулей\n')
            f.write('# Добавьте пути к модулям, по одному на строку\n\n')
            f.write('\n'.join(self.loaded_modules))

    async def reload_all_modules(self):
        """Перезагружает все модули"""
        success = True
        errors = []
        modules_to_reload = self.loaded_modules.copy()
        
        for module_path in modules_to_reload:
            try:
                module_name = module_path.replace('.py', '')
                await self.reload_extension(module_name)
                logger.info(f"Модуль {module_path} успешно перезагружен")
            except Exception as e:
                success = False
                error_msg = f"{module_path}: {str(e)}"
                errors.append(error_msg)
                logger.error(f"Ошибка перезагрузки {module_path}: {str(e)}")
                logger.error(traceback.format_exc())
        
        return success, errors

    async def get_bot_status(self):
        """Возвращает статус бота"""
        uptime = datetime.now() - self.start_time
        hours, remainder = divmod(int(uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        
        status = {
            "name": self.user.name,
            "id": self.user.id,
            "uptime": f"{hours:02d}:{minutes:02d}:{seconds:02d}",
            "modules_loaded": len(self.loaded_modules),
            "latency": f"{self.latency*1000:.2f}ms",
            "guilds": len(self.guilds)
        }
        return status

bot = Bot()

@bot.command()
@commands.is_owner()
async def update(ctx):
    """Перезагружает все модули (только для владельца)"""
    await ctx.send("🔄 Начинаю перезагрузку модулей...")
    success, errors = await bot.reload_all_modules()
    
    if success and not errors:
        await ctx.send("✅ Все модули успешно перезагружены!")
    elif errors:
        error_list = "\n".join(errors[:5])  # Показываем только первые 5 ошибок
        await ctx.send(f"⚠ Перезагрузка завершена с ошибками:\n```{error_list}```\n*Подробности в логах*")
    else:
        await ctx.send("⚠ Не удалось перезагрузить некоторые модули")

@bot.command()
@commands.is_owner()
async def add(ctx, module_path: str):
    """Добавляет новый модуль (только для владельца)"""
    await ctx.send(f"🔄 Пытаюсь добавить модуль `{module_path}`...")
    success, message = await bot.add_module(module_path)
    
    if success:
        await ctx.send(f"✅ {message}")
    else:
        await ctx.send(f"❌ {message}")

@bot.command()
@commands.is_owner()
async def remove(ctx, module_path: str):
    """Удаляет модуль (только для владельца)"""
    await ctx.send(f"🔄 Пытаюсь удалить модуль `{module_path}`...")
    success, message = await bot.remove_module(module_path)
    
    if success:
        await ctx.send(f"✅ {message}")
    else:
        await ctx.send(f"❌ {message}")

@bot.command()
@commands.is_owner()
async def modules(ctx):
    """Показывает список загруженных модулей (только для владельца)"""
    if not bot.loaded_modules:
        await ctx.send("📭 Нет загруженных модулей")
        return
    
    modules_list = "\n".join([f"• {module}" for module in bot.loaded_modules])
    embed = discord.Embed(
        title="📦 Загруженные модули",
        description=f"Всего: {len(bot.loaded_modules)}",
        color=discord.Color.blue()
    )
    embed.add_field(name="Список модулей", value=f"```{modules_list}```", inline=False)
    await ctx.send(embed=embed)

@bot.command()
@commands.is_owner()
async def status(ctx):
    """Показывает статус бота (только для владельца)"""
    status_info = await bot.get_bot_status()
    
    embed = discord.Embed(
        title="📊 Статус бота",
        color=discord.Color.green()
    )
    embed.add_field(name="Имя", value=status_info["name"], inline=True)
    embed.add_field(name="ID", value=status_info["id"], inline=True)
    embed.add_field(name="Аптайм", value=status_info["uptime"], inline=True)
    embed.add_field(name="Задержка", value=status_info["latency"], inline=True)
    embed.add_field(name="Серверы", value=status_info["guilds"], inline=True)
    embed.add_field(name="Модули", value=status_info["modules_loaded"], inline=True)
    
    await ctx.send(embed=embed)

@bot.command()
@commands.is_owner()
async def shutdown(ctx):
    """Выключает бота (только для владельца)"""
    await ctx.send("🛑 Выключаю бота...")
    logger.info("Бот выключается по команде")
    await bot.close()

if __name__ == "__main__":
    TOKEN = os.getenv('DISCORD_TOKEN')
    if not TOKEN:
        logger.error("Токен DISCORD_TOKEN не найден в .env файле")
        print("Ошибка: Токен DISCORD_TOKEN не найден в .env файле")
    else:
        try:
            bot.run(TOKEN)
        except Exception as e:
            logger.error(f"Ошибка запуска бота: {e}")
