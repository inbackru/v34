-- Скрипт проверки целостности базы данных InBack.ru
-- Проверяет наличие основных таблиц и данных

\echo '🔍 Проверка целостности базы данных InBack.ru...'

-- Проверка основных таблиц
\echo '📊 Проверка основных таблиц:'

SELECT 
    'users' as table_name, 
    count(*) as record_count,
    CASE WHEN count(*) > 0 THEN '✅' ELSE '❌' END as status
FROM users
UNION ALL
SELECT 
    'properties' as table_name, 
    count(*) as record_count,
    CASE WHEN count(*) > 0 THEN '✅' ELSE '❌' END as status  
FROM properties
UNION ALL
SELECT 
    'excel_properties' as table_name, 
    count(*) as record_count,
    CASE WHEN count(*) > 0 THEN '✅' ELSE '❌' END as status
FROM excel_properties
UNION ALL
SELECT 
    'residential_complexes' as table_name, 
    count(*) as record_count,
    CASE WHEN count(*) > 0 THEN '✅' ELSE '❌' END as status
FROM residential_complexes
UNION ALL
SELECT 
    'developers' as table_name, 
    count(*) as record_count,
    CASE WHEN count(*) > 0 THEN '✅' ELSE '❌' END as status
FROM developers
UNION ALL
SELECT 
    'managers' as table_name, 
    count(*) as record_count,
    CASE WHEN count(*) > 0 THEN '✅' ELSE '❌' END as status
FROM managers
UNION ALL
SELECT 
    'districts' as table_name, 
    count(*) as record_count,
    CASE WHEN count(*) > 0 THEN '✅' ELSE '❌' END as status
FROM districts;

\echo ''
\echo '📈 Статистика недвижимости:'

-- Статистика по объектам недвижимости
SELECT 
    'Всего объектов в excel_properties' as metric,
    count(*) as value
FROM excel_properties
UNION ALL
SELECT 
    'Объекты с координатами' as metric,
    count(*) as value
FROM excel_properties 
WHERE address_position_lat IS NOT NULL AND address_position_lon IS NOT NULL
UNION ALL
SELECT 
    'Объекты с фотографиями' as metric,
    count(*) as value
FROM excel_properties 
WHERE photos IS NOT NULL AND photos != '';

\echo ''
\echo '🏗️ Статистика по застройщикам:'

-- Статистика по застройщикам
SELECT 
    'Всего застройщиков' as metric,
    count(*) as value
FROM developers
UNION ALL
SELECT 
    'Активных застройщиков' as metric,
    count(*) as value
FROM developers 
WHERE is_active = true;

\echo ''
\echo '👥 Статистика пользователей:'

-- Статистика пользователей
SELECT 
    'Всего пользователей' as metric,
    count(*) as value
FROM users
UNION ALL
SELECT 
    'Активных пользователей' as metric,
    count(*) as value
FROM users 
WHERE is_active = true
UNION ALL
SELECT 
    'Менеджеров' as metric,
    count(*) as value
FROM managers
UNION ALL
SELECT 
    'Активных менеджеров' as metric,
    count(*) as value
FROM managers 
WHERE is_active = true;

\echo ''
\echo '🗂️ Проверка целостности данных:'

-- Проверка foreign key constraints
SELECT 
    'Объекты без комплексов' as check_name,
    count(*) as issues_count,
    CASE WHEN count(*) = 0 THEN '✅ ОК' ELSE '⚠️ Требует внимания' END as status
FROM excel_properties 
WHERE complex_name IS NULL OR complex_name = ''
UNION ALL
SELECT 
    'Объекты без координат' as check_name,
    count(*) as issues_count,
    CASE WHEN count(*) < (SELECT count(*) * 0.1 FROM excel_properties) THEN '✅ ОК' ELSE '⚠️ Требует внимания' END as status
FROM excel_properties 
WHERE address_position_lat IS NULL OR address_position_lon IS NULL;

\echo ''
\echo '✅ Проверка целостности базы данных завершена!'
\echo '📌 Если все статусы показывают ✅, база данных восстановлена корректно'