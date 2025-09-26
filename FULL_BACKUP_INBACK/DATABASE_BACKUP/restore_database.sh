#!/bin/bash

# Скрипт восстановления базы данных PostgreSQL для InBack.ru
# Автор: InBack.ru Team
# Дата: $(date)

set -e  # Выход при любой ошибке

echo "🚀 Начинаем восстановление базы данных PostgreSQL..."

# Проверяем наличие переменной DATABASE_URL
if [ -z "$DATABASE_URL" ]; then
    echo "❌ ОШИБКА: Переменная окружения DATABASE_URL не установлена"
    echo "   Установите переменную DATABASE_URL в формате:"
    echo "   postgresql://username:password@host:port/database"
    exit 1
fi

# Проверяем наличие файла дампа
DUMP_FILE="database_dump.sql"
if [ ! -f "$DUMP_FILE" ]; then
    echo "❌ ОШИБКА: Файл дампа $DUMP_FILE не найден"
    echo "   Убедитесь, что файл database_dump.sql находится в той же папке"
    exit 1
fi

echo "📁 Найден файл дампа: $DUMP_FILE"
echo "🔗 Подключение к базе данных: $DATABASE_URL"

# Восстанавливаем базу данных
echo "🔄 Восстанавливаем базу данных из дампа..."
psql "$DATABASE_URL" -f "$DUMP_FILE" -v ON_ERROR_STOP=1

if [ $? -eq 0 ]; then
    echo "✅ База данных успешно восстановлена!"
    echo ""
    echo "🔍 Проверяем целостность восстановленной базы..."
    
    # Запускаем проверку целостности если есть файл
    if [ -f "verify_database.sql" ]; then
        psql "$DATABASE_URL" -f "verify_database.sql"
        echo "✅ Проверка целостности завершена"
    else
        echo "⚠️  Файл verify_database.sql не найден, пропускаем проверку целостности"
    fi
    
    echo ""
    echo "🎉 Восстановление базы данных завершено успешно!"
    echo "   Теперь можно запускать приложение"
else
    echo "❌ Ошибка при восстановлении базы данных"
    exit 1
fi