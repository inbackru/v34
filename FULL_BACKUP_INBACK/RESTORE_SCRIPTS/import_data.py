#!/usr/bin/env python3
"""
Скрипт импорта данных из Excel файлов для InBack.ru
Автор: InBack.ru Team
"""

import os
import sys
import pandas as pd
import json
from datetime import datetime
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DataImporter:
    def __init__(self, database_url=None):
        """Инициализация импортера данных"""
        self.database_url = database_url or os.environ.get('DATABASE_URL')
        if not self.database_url:
            raise ValueError("DATABASE_URL не установлен")
        
        self.engine = create_engine(self.database_url)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        
    def import_excel_properties(self, excel_file_path):
        """Импорт недвижимости из Excel файла"""
        logger.info(f"🏠 Импорт недвижимости из {excel_file_path}")
        
        try:
            # Читаем Excel файл
            df = pd.read_excel(excel_file_path)
            logger.info(f"📊 Найдено {len(df)} записей в Excel файле")
            
            imported_count = 0
            for index, row in df.iterrows():
                try:
                    # Подготавливаем данные для вставки
                    property_data = {
                        'inner_id': row.get('id', f'import_{index}'),
                        'complex_name': row.get('complex_name', ''),
                        'developer_name': row.get('developer_name', ''),
                        'object_rooms': int(row.get('rooms', 0)) if pd.notna(row.get('rooms')) else 0,
                        'object_area': float(row.get('area', 0)) if pd.notna(row.get('area')) else 0,
                        'price': int(row.get('price', 0)) if pd.notna(row.get('price')) else 0,
                        'object_min_floor': int(row.get('floor', 1)) if pd.notna(row.get('floor')) else 1,
                        'object_max_floor': int(row.get('floor', 1)) if pd.notna(row.get('floor')) else 1,
                        'address_display_name': row.get('address', ''),
                        'address_position_lat': float(row.get('latitude')) if pd.notna(row.get('latitude')) else None,
                        'address_position_lon': float(row.get('longitude')) if pd.notna(row.get('longitude')) else None,
                        'photos': json.dumps([]) if pd.isna(row.get('photos')) else str(row.get('photos', '[]')),
                        'created_at': datetime.utcnow(),
                        'updated_at': datetime.utcnow()
                    }
                    
                    # Вставляем в базу данных
                    self.session.execute(text('''
                        INSERT INTO excel_properties (
                            inner_id, complex_name, developer_name, object_rooms, 
                            object_area, price, object_min_floor, object_max_floor,
                            address_display_name, address_position_lat, address_position_lon,
                            photos, created_at, updated_at
                        ) VALUES (
                            :inner_id, :complex_name, :developer_name, :object_rooms,
                            :object_area, :price, :object_min_floor, :object_max_floor,
                            :address_display_name, :address_position_lat, :address_position_lon,
                            :photos, :created_at, :updated_at
                        ) ON CONFLICT (inner_id) DO UPDATE SET
                            complex_name = EXCLUDED.complex_name,
                            developer_name = EXCLUDED.developer_name,
                            updated_at = EXCLUDED.updated_at
                    '''), property_data)
                    
                    imported_count += 1
                    
                    # Коммитим каждые 100 записей
                    if imported_count % 100 == 0:
                        self.session.commit()
                        logger.info(f"✅ Импортировано {imported_count} объектов...")
                        
                except Exception as e:
                    logger.error(f"❌ Ошибка импорта записи {index}: {e}")
                    continue
            
            # Финальный коммит
            self.session.commit()
            logger.info(f"🎉 Импорт завершен! Обработано {imported_count} объектов")
            return imported_count
            
        except Exception as e:
            logger.error(f"❌ Ошибка импорта Excel файла: {e}")
            self.session.rollback()
            return 0
    
    def import_developers(self, excel_file_path):
        """Импорт застройщиков из Excel файла"""
        logger.info(f"🏗️ Импорт застройщиков из {excel_file_path}")
        
        try:
            df = pd.read_excel(excel_file_path)
            imported_count = 0
            
            for index, row in df.iterrows():
                try:
                    developer_data = {
                        'name': row.get('name', f'Застройщик {index}'),
                        'slug': self.create_slug(row.get('name', f'zastroishik-{index}')),
                        'full_name': row.get('full_name', ''),
                        'description': row.get('description', ''),
                        'phone': row.get('phone', ''),
                        'email': row.get('email', ''),
                        'website': row.get('website', ''),
                        'is_active': True,
                        'created_at': datetime.utcnow(),
                        'updated_at': datetime.utcnow()
                    }
                    
                    self.session.execute(text('''
                        INSERT INTO developers (
                            name, slug, full_name, description, phone, email, website,
                            is_active, created_at, updated_at
                        ) VALUES (
                            :name, :slug, :full_name, :description, :phone, :email, :website,
                            :is_active, :created_at, :updated_at
                        ) ON CONFLICT (name) DO UPDATE SET
                            full_name = EXCLUDED.full_name,
                            updated_at = EXCLUDED.updated_at
                    '''), developer_data)
                    
                    imported_count += 1
                    
                except Exception as e:
                    logger.error(f"❌ Ошибка импорта застройщика {index}: {e}")
                    continue
            
            self.session.commit()
            logger.info(f"🎉 Импорт застройщиков завершен! Обработано {imported_count} записей")
            return imported_count
            
        except Exception as e:
            logger.error(f"❌ Ошибка импорта застройщиков: {e}")
            self.session.rollback()
            return 0
    
    def create_slug(self, name):
        """Создание slug из названия"""
        import re
        import unicodedata
        
        # Транслитерация
        translit_map = {
            'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
            'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
            'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
            'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
            'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya'
        }
        
        slug = str(name).lower()
        for cyrillic, latin in translit_map.items():
            slug = slug.replace(cyrillic, latin)
        
        slug = re.sub(r'[^\w\s-]', '', slug)
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug.strip('-')
    
    def auto_import_excel_files(self, attachments_dir="../PROJECT_FILES/attached_assets"):
        """Автоматический импорт всех Excel файлов из папки"""
        logger.info(f"📁 Поиск Excel файлов в {attachments_dir}")
        
        if not os.path.exists(attachments_dir):
            logger.error(f"❌ Папка {attachments_dir} не найдена")
            return
        
        excel_files = []
        for file in os.listdir(attachments_dir):
            if file.endswith(('.xlsx', '.xls')) and not file.startswith('~'):
                excel_files.append(os.path.join(attachments_dir, file))
        
        logger.info(f"📊 Найдено {len(excel_files)} Excel файлов")
        
        total_imported = 0
        for excel_file in excel_files[:5]:  # Импортируем первые 5 файлов
            logger.info(f"📂 Обрабатываем {os.path.basename(excel_file)}")
            
            if 'properties' in excel_file.lower() or 'excel_properties' in excel_file.lower():
                count = self.import_excel_properties(excel_file)
            elif 'developers' in excel_file.lower():
                count = self.import_developers(excel_file)
            else:
                # Пробуем как properties по умолчанию
                count = self.import_excel_properties(excel_file)
            
            total_imported += count
        
        logger.info(f"🎉 Автоимпорт завершен! Всего импортировано {total_imported} записей")
    
    def close(self):
        """Закрытие соединения"""
        self.session.close()

def main():
    """Главная функция"""
    print("🚀 Запуск импорта данных InBack.ru...")
    
    try:
        # Создаем импортер
        importer = DataImporter()
        
        # Автоматический импорт Excel файлов
        importer.auto_import_excel_files()
        
        print("✅ Импорт данных завершен успешно!")
        
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
        sys.exit(1)
    finally:
        if 'importer' in locals():
            importer.close()

if __name__ == "__main__":
    main()