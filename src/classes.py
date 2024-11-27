# from abc import ABC, abstractmethod
# import psycopg2
# import requests
# from psycopg2 import sql
#
#
# class AbsManager(ABC):
#     @abstractmethod
#     def get_companies_and_vacancies_count(self):
#         pass
#
#     @abstractmethod
#     def get_all_vacancies(self):
#         pass
#
#     @abstractmethod
#     def get_avg_salary(self):
#         pass
#
#     @abstractmethod
#     def get_vacancies_with_higher_salary(self):
#         pass
#
#     @abstractmethod
#     def get_vacancies_with_keyword(self):
#         pass
#
# class HeadHunterAPI:
#     def __init__(self):
#         self.url = "https://api.hh.ru/vacancies"
#         self.headers = {"User-Agent": "HH-User-Agent"}
#         self.params = {"text": "", "page": 0, "per_page": 100}
#         self.vacancies = []
#
#     def get_vacancies(self, employer_id):
#         self.params["employer_id"] = employer_id
#         self.params["page"] = 0
#         while self.params["page"] < 20:
#             response = requests.get(self.url, headers=self.headers, params=self.params)
#             if response.status_code != 200:
#                 print(f"Ошибка при запросе: {response.status_code}")
#                 return []  # Возвращаем пустой список в случае ошибки
#
#             vacancies = response.json().get("items", [])
#             if not vacancies:
#                 break
#             self.vacancies.extend(vacancies)
#             self.params["page"] += 1
#         return self.vacancies
#
# class DBManager:
#     """класс DBManager, который будет подключаться к БД PostgreSQL"""
#
#     def __init__(self, dbname, user, password, host, port):
#         """инициализация"""
#         self.connection = psycopg2.connect(
#             dbname=dbname,
#             user=user,
#             password=password,
#             host=host,
#             port=port,
#         )
#         self.connection.autocommit = True
#
#     def create_table_and_database(self, database_name: str, params: dict):
#         """Создание базы данных и таблиц."""
#
#         # Подключение к базе данных 'postgres' для создания новой базы данных
#         conn = psycopg2.connect(dbname='postgres', **params, client_encoding='utf8')
#         conn.autocommit = True
#         cur = conn.cursor()
#
#         # Удаление базы данных, если она существует
#         cur.execute(sql.SQL("DROP DATABASE IF EXISTS {}").format(sql.Identifier(database_name)))
#         # Создание новой базы данных
#         cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(database_name)))
#
#         cur.close()
#         conn.close()
#
#         # Подключение к новой базе данных
#         conn = psycopg2.connect(dbname=database_name, **params, client_encoding='utf8')
#         cur = conn.cursor()
#
#         # Создание таблицы vacancies
#         query = sql.SQL("""
#             CREATE TABLE IF NOT EXISTS vacancies (
#                 id SERIAL PRIMARY KEY,
#                 employer_name VARCHAR(255),
#                 vacancy_name VARCHAR(255),
#                 salary VARCHAR(255),
#                 vacancy_url VARCHAR(255)
#             )
#         """)
#         cur.execute(query)
#
#         # Закрытие курсора и соединения
#         cur.close()
#         conn.close()
#
#     def insert_vacancies(self, vacancies):
#         with self.connection.cursor() as cursor:
#             for vacancy in vacancies:
#                 query = sql.SQL("""
#                     INSERT INTO vacancies (employer_name, vacancy_name, salary, vacancy_url)
#                     VALUES (%s, %s, %s, %s)
#                 """)
#                 cursor.execute(query, (
#                     vacancy['employer']['name'],
#                     vacancy['name'],
#                     vacancy.get('salary', {}).get('from', 'Не указано') if vacancy.get('salary') else 'Не указано',
#                     vacancy['alternate_url']
#                 ))
#
#     def get_companies_and_vacancies_count(self):
#         """получает список всех компаний и
#         количество вакансий у каждой компании."""
#
#         with self.connection.cursor() as cursor:
#             query = sql.SQL("""
#                 SELECT employer_name, COUNT(*)
#                 FROM vacancies
#                 GROUP BY employer_name
#             """)
#             cursor.execute(query)
#             result = cursor.fetchall()
#         return result
#
#     def get_all_vacancies(self):
#         """получает список всех вакансий с указанием названия компании,
#         названия вакансии и зарплаты и ссылки на вакансию."""
#
#         with self.connection.cursor() as cursor:
#             query = sql.SQL("""
#                        SELECT employer_name, vacancy_name, salary, vacancy_url
#                        FROM vacancies
#                    """)
#             cursor.execute(query)
#             result = cursor.fetchall()
#         return result
#
#     def get_avg_salary(self):
#         """получает среднюю зарплату по вакансиям."""
#
#         with self.connection.cursor() as cursor:
#             query = sql.SQL("""
#                 SELECT AVG(CAST(salary AS INTEGER))
#                 FROM vacancies
#                 WHERE salary <> 'Не указано'
#             """)
#             cursor.execute(query)
#             result = cursor.fetchone()
#         return result[0] if result[0] else 0
#
#     def get_vacancies_with_higher_salary(self):
#         """получает список всех вакансий, у которых
#         зарплата выше средней по всем вакансиям."""
#
#         avg_salary = self.get_avg_salary()
#         with self.connection.cursor() as cursor:
#             query = sql.SQL("""
#                         SELECT employer_name, vacancy_name, salary, vacancy_url
#                         FROM vacancies
#                         WHERE CAST(salary AS INTEGER) > %s
#                     """)
#             cursor.execute(query, (avg_salary,))
#             result = cursor.fetchall()
#         return result
#
#     def get_vacancies_with_keyword(self, keyword):
#         """получает список всех вакансий, в названии которых
#         содержатся переданные в метод слова, например python."""
#
#         with self.connection.cursor() as cursor:
#             query = sql.SQL("""
#                 SELECT employer_name, vacancy_name, salary, vacancy_url
#                 FROM vacancies
#                 WHERE vacancy_name ILIKE %s
#             """)
#             cursor.execute(query, (f"%{keyword}%",))
#             result = cursor.fetchall()
#         return result

# # Пример использования
# db_manager = DBManager(
#     dbname="postgres",
#     host="localhost",
#     user="postgres",
#     password="12345",
#     port="5432"
# )
#
# # Список ID компаний, от которых будем получать вакансии
# employer_ids = [1740, 3529, 23427, 3772, 15478, 1057, 1122462, 19923, 1001, 2180]
#
# # Получение вакансий от выбранных компаний
# hh_api = HeadHunterAPI()
# all_vacancies = []
#
#
#
# # Убедитесь, что путь к файлу указан правильно
# config_file_path = os.path.join("database.ini")
# params = config(config_file_path, "postgresql")
#
# # Создание базы данных и таблиц
# db_manager.create_table_and_database("your_dbname", params)
#
# # Вставка данных о вакансиях в базу данных
# db_manager.insert_vacancies(all_vacancies)
#
# # Примеры использования методов DBManager
# avg_salary = db_manager.get_avg_salary()
# print(f"Средняя зарплата: {avg_salary}")
#
# vacancies_with_higher_salary = db_manager.get_vacancies_with_higher_salary()
# print("Вакансии с зарплатой выше средней:")
# for vacancy in vacancies_with_higher_salary:
#     print(vacancy)
#
# vacancies_with_keyword = db_manager.get_vacancies_with_keyword("python")
# print("Вакансии, содержащие слово 'python':")
# for vacancy in vacancies_with_keyword:
#     print(vacancy)