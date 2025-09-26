#!/bin/bash

# Скрипт настройки окружения для InBack.ru
# Автор: InBack.ru Team
# Дата: $(date)

set -e  # Выход при любой ошибке

echo "🚀 Настройка окружения для InBack.ru..."

# Проверка что мы находимся в Replit
if [ -z "$REPL_ID" ]; then
    echo "⚠️  ВНИМАНИЕ: Переменная REPL_ID не найдена. Убедитесь, что вы запускаете это в Replit."
fi

# 1. Установка Python модуля
echo "📦 Установка Python 3.11..."
# В Replit это обычно уже установлено, но на всякий случай
python3 --version || {
    echo "❌ Python 3 не найден. Установите Python 3.11 через Replit Modules."
    exit 1
}

# 2. Установка PostgreSQL модуля
echo "🗄️  Проверка PostgreSQL..."
if ! command -v psql &> /dev/null; then
    echo "⚠️  PostgreSQL не найден. Установите PostgreSQL через Replit Modules или создайте базу данных."
fi

# 3. Установка Python зависимостей
echo "📋 Установка Python зависимостей..."
if [ -f "../PROJECT_FILES/requirements.txt" ]; then
    pip install -r ../PROJECT_FILES/requirements.txt
    echo "✅ Python зависимости установлены"
else
    echo "❌ Файл requirements.txt не найден в PROJECT_FILES/"
    exit 1
fi

# 4. Создание переменных окружения
echo "🔧 Настройка переменных окружения..."
if [ ! -f ".env" ]; then
    echo "📝 Создание файла .env с примерами переменных..."
    cat > .env << 'EOF'
# ОБЯЗАТЕЛЬНЫЕ ПЕРЕМЕННЫЕ - УСТАНОВИТЕ РЕАЛЬНЫЕ ЗНАЧЕНИЯ!

# Session secret (генерируйте случайную строку)
SESSION_SECRET=your-super-secret-session-key-here-change-this

# Database URL (создайте PostgreSQL базу в Replit)
DATABASE_URL=postgresql://username:password@host:port/database

# Email настройки (для уведомлений)
SENDGRID_API_KEY=your-sendgrid-api-key
EMAIL_FROM=noreply@inback.ru

# Telegram Bot (для уведомлений менеджерам)
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
TELEGRAM_CHAT_ID=your-telegram-chat-id

# OpenAI API (для ИИ функций)
OPENAI_API_KEY=your-openai-api-key

# ДОПОЛНИТЕЛЬНЫЕ ПЕРЕМЕННЫЕ
FLASK_ENV=development
FLASK_DEBUG=True
EOF
    
    echo "⚠️  ВАЖНО: Настройте переменные окружения в файле .env или в Replit Secrets!"
    echo "   Основные переменные: SESSION_SECRET, DATABASE_URL"
else
    echo "✅ Файл .env уже существует"
fi

# 5. Создание папок
echo "📁 Создание необходимых папок..."
mkdir -p static/uploads
mkdir -p instance/uploads
mkdir -p logs
echo "✅ Папки созданы"

# 6. Настройка прав доступа
echo "🔐 Настройка прав доступа..."
chmod +x *.sh 2>/dev/null || true
chmod 755 static/uploads instance/uploads logs
echo "✅ Права доступа настроены"

echo ""
echo "🎉 Настройка окружения завершена!"
echo ""
echo "📋 СЛЕДУЮЩИЕ ШАГИ:"
echo "1. ✅ Создайте PostgreSQL базу данных в Replit"
echo "2. ✅ Настройте переменные окружения (DATABASE_URL, SESSION_SECRET)"
echo "3. ✅ Запустите скрипт восстановления базы данных: ../DATABASE_BACKUP/restore_database.sh"
echo "4. ✅ Запустите скрипт проверки: verify_installation.py"
echo "5. ✅ Настройте workflow: gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app"
echo ""
echo "💡 Подробные инструкции смотрите в FULL_RESTORE_INSTRUCTIONS.md"