import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import logging
from sqlalchemy import text
from app.database import async_session, async_engine
from app.models.base_model import Base
from app.models.activity import Activity  # noqa: F401
from app.models.organization import Organization, OrganizationPhone  # noqa: F401
from app.models.building import Building  # noqa: F401

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def init_database():
    """Создание таблиц и заполнение тестовыми данными"""
    try:
        # Создаем таблицы - ОТДЕЛЬНОЙ транзакцией
        logger.info('Creating database tables...')
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        # Заполняем тестовыми данными в отдельной транзакции
        logger.info('Populating with test data...')
        await populate_test_data()

        logger.info('Database initialization completed successfully!')
    except Exception as e:
        logger.error(f'Error initializing database: {e}')
        raise


async def populate_test_data():
    """Заполнение базы тестовыми данными"""
    async with async_session() as session:
        try:
            # Вставляем виды деятельности (дерево до 3 уровней)
            logger.info('Inserting activities...')
            activities_sql = """
            INSERT INTO activity (id, name, parent_id) VALUES
            -- 1 уровень (корневые)
            (1, 'Еда', NULL),
            (2, 'Автомобили', NULL),
            (3, 'Одежда', NULL),
            (4, 'Электроника', NULL),

            -- 2 уровень (дочерние для Еда)
            (5, 'Мясная продукция', 1),
            (6, 'Молочная продукция', 1),
            (7, 'Хлебобулочные изделия', 1),
            (8, 'Напитки', 1),

            -- 3 уровень (дочерние для Мясная продукция)
            (9, 'Говядина', 5),
            (10, 'Свинина', 5),
            (11, 'Птица', 5),

            -- 2 уровень (дочерние для Автомобили)
            (12, 'Грузовые автомобили', 2),
            (13, 'Легковые автомобили', 2),
            (14, 'Мотоциклы', 2),

            -- 3 уровень (дочерние для Легковые автомобили)
            (15, 'Запчасти', 13),
            (16, 'Аксессуары', 13),
            (17, 'Шины и диски', 13),

            -- 2 уровень (дочерние для Одежда)
            (18, 'Мужская одежда', 3),
            (19, 'Женская одежда', 3),
            (20, 'Детская одежда', 3),

            -- 2 уровень (дочерние для Электроника)
            (21, 'Компьютеры', 4),
            (22, 'Телефоны', 4),
            (23, 'Бытовая техника', 4)
            ON CONFLICT (id) DO NOTHING;
            """
            await session.execute(text(activities_sql))

            # Вставляем здания
            logger.info('Inserting buildings...')
            buildings_sql = """
            INSERT INTO building (id, address, latitude, longitude) VALUES
            (1, 'г. Москва, ул. Ленина 1, офис 3', 55.7558, 37.6173),
            (2, 'г. Москва, ул. Тверская 15', 55.7600, 37.6000),
            (3, 'г. Санкт-Петербург, Невский проспект 25', 59.9343, 30.3351),
            (4, 'г. Казань, ул. Баумана 10', 55.7964, 49.1088),
            (5, 'г. Екатеринбург, ул. Мамина-Сибиряка 45', 56.8389, 60.6057),
            (6, 'г. Новосибирск, Красный проспект 50', 55.0084, 82.9357)
            ON CONFLICT (id) DO NOTHING;
            """
            await session.execute(text(buildings_sql))

            # Вставляем организации
            logger.info('Inserting organizations...')
            organizations_sql = """
            INSERT INTO organization (id, name, building_id) VALUES
            (1, 'ООО "Рога и Копыта"', 1),
            (2, 'ИП "Мясной двор"', 2),
            (3, 'АО "Молоко Сибири"', 3),
            (4, 'ООО "АвтоМир"', 4),
            (5, 'ЗАО "ТехноСити"', 5),
            (6, 'ИП "Модная одежда"', 6),
            (7, 'ООО "Пивной бар"', 1),
            (8, 'АО "Автозапчасти"', 2),
            (9, 'ИП "Фруктовый рай"', 3),
            (10, 'ООО "Электроника+"', 4)
            ON CONFLICT (id) DO NOTHING;
            """
            await session.execute(text(organizations_sql))

            # Вставляем телефоны организаций
            logger.info('Inserting phone numbers...')
            phones_sql = """
            INSERT INTO organizationphone (id, organization_id, phone_number) VALUES
            -- ООО "Рога и Копыта"
            (1, 1, '8-800-555-35-35'),
            (2, 1, '8-495-123-45-67'),
            (3, 1, '8-926-111-22-33'),

            -- ИП "Мясной двор"
            (4, 2, '8-800-200-10-10'),
            (5, 2, '8-495-222-33-44'),

            -- АО "Молоко Сибири"
            (6, 3, '8-383-123-45-67'),
            (7, 3, '8-913-456-78-90'),

            -- ООО "АвтоМир"
            (8, 4, '8-843-111-22-33'),
            (9, 4, '8-927-333-44-55'),

            -- ЗАО "ТехноСити"
            (10, 5, '8-343-222-33-44'),
            (11, 5, '8-912-777-88-99'),

            -- ИП "Модная одежда"
            (12, 6, '8-383-444-55-66'),

            -- ООО "Пивной бар"
            (13, 7, '8-800-777-88-99'),
            (14, 7, '8-495-555-66-77'),

            -- АО "Автозапчасти"
            (15, 8, '8-800-888-99-00'),
            (16, 8, '8-495-666-77-88'),

            -- ИП "Фруктовый рай"
            (17, 9, '8-913-999-00-11'),

            -- ООО "Электроника+"
            (18, 10, '8-800-123-45-67'),
            (19, 10, '8-927-222-33-44')
            ON CONFLICT (id) DO NOTHING;
            """
            await session.execute(text(phones_sql))

            # Вставляем связи организаций с видами деятельности
            logger.info('Inserting organization-activity relationships...')
            org_activity_sql = """
            INSERT INTO organization_activity (organization_id, activity_id) VALUES
            -- ООО "Рога и Копыта" - занимается разными видами
            (1, 1),  -- Еда
            (1, 5),  -- Мясная продукция
            (1, 6),  -- Молочная продукция
            (1, 9),  -- Говядина
            (1, 10), -- Свинина

            -- ИП "Мясной двор" - специализируется на мясе
            (2, 5),  -- Мясная продукция
            (2, 9),  -- Говядина
            (2, 10), -- Свинина
            (2, 11), -- Птица

            -- АО "Молоко Сибири" - молочная продукция
            (3, 6),  -- Молочная продукция
            (3, 1),  -- Еда

            -- ООО "АвтоМир" - автомобили
            (4, 2),  -- Автомобили
            (4, 13), -- Легковые автомобили
            (4, 15), -- Запчасти
            (4, 16), -- Аксессуары

            -- ЗАО "ТехноСити" - электроника
            (5, 4),  -- Электроника
            (5, 21), -- Компьютеры
            (5, 22), -- Телефоны

            -- ИП "Модная одежда" - одежда
            (6, 3),  -- Одежда
            (6, 18), -- Мужская одежда
            (6, 19), -- Женская одежда
            (6, 20), -- Детская одежда

            -- ООО "Пивной бар" - напитки
            (7, 1),  -- Еда
            (7, 8),  -- Напитки

            -- АО "Автозапчасти" - запчасти для автомобилей
            (8, 2),  -- Автомобили
            (8, 13), -- Легковые автомобили
            (8, 15), -- Запчасти
            (8, 17), -- Шины и диски

            -- ИП "Фруктовый рай" - еда
            (9, 1),  -- Еда
            (9, 7),  -- Хлебобулочные изделия

            -- ООО "Электроника+" - электроника
            (10, 4), -- Электроника
            (10, 22), -- Телефоны
            (10, 23) -- Бытовая техника
            ON CONFLICT (organization_id, activity_id) DO NOTHING;
            """
            await session.execute(text(org_activity_sql))

            # Сбрасываем последовательности для автоинкрементных полей
            logger.info('Resetting sequences...')
            await session.execute(text("SELECT setval('activity_id_seq', (SELECT COALESCE(MAX(id), 1) FROM activity))"))
            await session.execute(text("SELECT setval('building_id_seq', (SELECT COALESCE(MAX(id), 1) FROM building))"))
            await session.execute(
                text("SELECT setval('organization_id_seq', (SELECT COALESCE(MAX(id), 1) FROM organization))")
            )
            await session.execute(
                text("SELECT setval('organizationphone_id_seq', (SELECT COALESCE(MAX(id), 1) FROM organizationphone))")
            )

            await session.commit()
            logger.info('Test data populated successfully!')

        except Exception as e:
            await session.rollback()
            logger.error(f'Error populating test data: {e}')
            raise


if __name__ == '__main__':
    asyncio.run(init_database())
