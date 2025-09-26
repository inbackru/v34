#!/usr/bin/env python3
"""
Скрипт проверки корректности установки InBack.ru
Автор: InBack.ru Team
"""

import os
import sys
import logging
import requests
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import importlib.util

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class InstallationVerifier:
    def __init__(self):
        """Инициализация верификатора"""
        self.errors = []
        self.warnings = []
        self.success_count = 0
        self.total_checks = 0
    
    def check_result(self, name, condition, error_msg="", warning_msg=""):
        """Регистрация результата проверки"""
        self.total_checks += 1
        print(f"🔍 Проверка: {name}", end=" ... ")
        
        if condition:
            print("✅ ОК")
            self.success_count += 1
        else:
            if error_msg:
                print(f"❌ ОШИБКА: {error_msg}")
                self.errors.append(f"{name}: {error_msg}")
            elif warning_msg:
                print(f"⚠️ ПРЕДУПРЕЖДЕНИЕ: {warning_msg}")
                self.warnings.append(f"{name}: {warning_msg}")
            else:
                print("❌ НЕУДАЧА")
                self.errors.append(name)
    
    def check_environment_variables(self):
        """Проверка переменных окружения"""
        logger.info("🔧 Проверка переменных окружения...")
        
        required_vars = {
            'DATABASE_URL': 'Обязательная переменная для подключения к базе данных',
            'SESSION_SECRET': 'Обязательная переменная для безопасности сессий'
        }
        
        optional_vars = {
            'SENDGRID_API_KEY': 'Для отправки email уведомлений',
            'TELEGRAM_BOT_TOKEN': 'Для Telegram уведомлений',
            'OPENAI_API_KEY': 'Для ИИ функций'
        }
        
        for var, description in required_vars.items():
            value = os.environ.get(var)
            self.check_result(
                f"Переменная {var}",
                value is not None and value.strip() != "",
                f"Обязательная переменная не установлена. {description}"
            )
        
        for var, description in optional_vars.items():
            value = os.environ.get(var)
            self.check_result(
                f"Переменная {var} (опционально)",
                True,  # Всегда успех для опциональных
                warning_msg="" if value else f"Опциональная переменная не установлена. {description}"
            )
    
    def check_database_connection(self):
        """Проверка подключения к базе данных"""
        logger.info("🗄️ Проверка подключения к базе данных...")
        
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            self.check_result(
                "Подключение к базе данных",
                False,
                "DATABASE_URL не установлен"
            )
            return
        
        try:
            engine = create_engine(database_url)
            Session = sessionmaker(bind=engine)
            session = Session()
            
            # Тестовый запрос
            result = session.execute(text("SELECT 1"))
            session.close()
            
            self.check_result("Подключение к базе данных", True)
            
        except Exception as e:
            self.check_result(
                "Подключение к базе данных",
                False,
                f"Ошибка подключения: {str(e)}"
            )
    
    def check_database_tables(self):
        """Проверка наличия таблиц в базе данных"""
        logger.info("📊 Проверка структуры базы данных...")
        
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            return
        
        required_tables = [
            'users', 'properties', 'excel_properties', 'developers',
            'residential_complexes', 'managers', 'districts'
        ]
        
        try:
            engine = create_engine(database_url)
            Session = sessionmaker(bind=engine)
            session = Session()
            
            for table in required_tables:
                try:
                    result = session.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = result.scalar()
                    self.check_result(
                        f"Таблица {table}",
                        True,
                        warning_msg="" if count > 0 else f"Таблица пуста (0 записей)"
                    )
                except Exception as e:
                    self.check_result(
                        f"Таблица {table}",
                        False,
                        f"Таблица не найдена или недоступна: {str(e)}"
                    )
            
            session.close()
            
        except Exception as e:
            self.check_result(
                "Проверка структуры БД",
                False,
                f"Ошибка доступа к базе данных: {str(e)}"
            )
    
    def check_python_dependencies(self):
        """Проверка Python зависимостей"""
        logger.info("📦 Проверка Python зависимостей...")
        
        required_packages = [
            'flask', 'sqlalchemy', 'psycopg2', 'pandas', 
            'openpyxl', 'requests', 'gunicorn'
        ]
        
        for package in required_packages:
            try:
                __import__(package)
                self.check_result(f"Пакет {package}", True)
            except ImportError:
                self.check_result(
                    f"Пакет {package}",
                    False,
                    f"Пакет не установлен. Выполните: pip install {package}"
                )
    
    def check_project_files(self):
        """Проверка наличия файлов проекта"""
        logger.info("📁 Проверка файлов проекта...")
        
        required_files = [
            '../PROJECT_FILES/app.py',
            '../PROJECT_FILES/models.py', 
            '../PROJECT_FILES/main.py',
            '../PROJECT_FILES/requirements.txt'
        ]
        
        required_dirs = [
            '../PROJECT_FILES/templates',
            '../PROJECT_FILES/static',
            '../PROJECT_FILES/attached_assets'
        ]
        
        for file_path in required_files:
            self.check_result(
                f"Файл {os.path.basename(file_path)}",
                os.path.isfile(file_path),
                f"Файл не найден: {file_path}"
            )
        
        for dir_path in required_dirs:
            self.check_result(
                f"Папка {os.path.basename(dir_path)}",
                os.path.isdir(dir_path),
                f"Папка не найдена: {dir_path}"
            )
    
    def check_flask_app(self):
        """Проверка запуска Flask приложения"""
        logger.info("🌐 Проверка Flask приложения...")
        
        # Проверяем возможность импорта app
        sys.path.insert(0, '../PROJECT_FILES')
        try:
            import app
            self.check_result("Импорт Flask приложения", True)
            
            # Проверяем конфигурацию
            flask_app = app.app
            self.check_result(
                "Конфигурация Flask",
                flask_app.config.get('SQLALCHEMY_DATABASE_URI') is not None
            )
            
        except Exception as e:
            self.check_result(
                "Импорт Flask приложения",
                False,
                f"Ошибка импорта: {str(e)}"
            )
    
    def check_permissions(self):
        """Проверка прав доступа"""
        logger.info("🔐 Проверка прав доступа...")
        
        # Проверяем возможность записи в папки
        write_dirs = [
            '../PROJECT_FILES/static/uploads',
            '../PROJECT_FILES/instance',
            '.'
        ]
        
        for dir_path in write_dirs:
            if os.path.exists(dir_path):
                try:
                    test_file = os.path.join(dir_path, 'test_write.tmp')
                    with open(test_file, 'w') as f:
                        f.write('test')
                    os.remove(test_file)
                    self.check_result(f"Запись в {dir_path}", True)
                except Exception as e:
                    self.check_result(
                        f"Запись в {dir_path}",
                        False,
                        f"Нет прав на запись: {str(e)}"
                    )
    
    def run_all_checks(self):
        """Запуск всех проверок"""
        print("🚀 Начинаем проверку установки InBack.ru...")
        print("=" * 60)
        
        self.check_environment_variables()
        print()
        
        self.check_python_dependencies()
        print()
        
        self.check_project_files()
        print()
        
        self.check_permissions()
        print()
        
        self.check_database_connection()
        print()
        
        self.check_database_tables()
        print()
        
        self.check_flask_app()
        print()
        
        # Итоговый отчет
        print("=" * 60)
        print("📊 ИТОГОВЫЙ ОТЧЕТ:")
        print(f"✅ Успешных проверок: {self.success_count}/{self.total_checks}")
        
        if self.errors:
            print(f"❌ Критических ошибок: {len(self.errors)}")
            for error in self.errors:
                print(f"   • {error}")
        
        if self.warnings:
            print(f"⚠️ Предупреждений: {len(self.warnings)}")
            for warning in self.warnings:
                print(f"   • {warning}")
        
        print("=" * 60)
        
        if not self.errors:
            print("🎉 ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ УСПЕШНО!")
            print("   Приложение готово к запуску!")
            print("")
            print("🚀 Для запуска выполните:")
            print("   cd ../PROJECT_FILES")
            print("   gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app")
            return True
        else:
            print("❌ ОБНАРУЖЕНЫ КРИТИЧЕСКИЕ ОШИБКИ!")
            print("   Исправьте ошибки перед запуском приложения.")
            print("   Подробные инструкции см. в FULL_RESTORE_INSTRUCTIONS.md")
            return False

def main():
    """Главная функция"""
    verifier = InstallationVerifier()
    success = verifier.run_all_checks()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()