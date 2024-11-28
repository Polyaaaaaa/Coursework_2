import psycopg2
from psycopg2 import sql

from src.config import config
from src.hh import HeadHunterAPI


class DBManager:
    """класс DBManager, который будет подключаться к БД PostgreSQL"""

    def __init__(self, dbname, params):
        """инициализация"""
        self.dbname = dbname
        self.params = params
        self.connection = None

    def create_table_and_database(self):
        """Создание базы данных и таблиц."""

        try:
            # Подключение к базе данных 'postgres' для создания новой базы данных
            conn = psycopg2.connect(dbname='postgres', **self.params, client_encoding='utf8')
            conn.autocommit = True
            cur = conn.cursor()

            # Удаление базы данных, если она существует
            cur.execute(sql.SQL("DROP DATABASE IF EXISTS {}").format(sql.Identifier(self.dbname)))
            # Создание новой базы данных
            cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(self.dbname)))

            cur.close()
            conn.close()

            # Подключение к новой базе данных
            conn = psycopg2.connect(dbname=self.dbname, **self.params, client_encoding='utf8')
            conn.autocommit = True
            cur = conn.cursor()
            query = """
                CREATE TABLE IF NOT EXISTS employees (
                    employees_id SERIAL PRIMARY KEY,
                    employer_name VARCHAR(255)
                )
            """
            cur.execute(query)

            # Создание таблицы vacancies
            query = """
                CREATE TABLE IF NOT EXISTS vacancies (
                    id SERIAL PRIMARY KEY,
                    vacancy_name VARCHAR(255),
                    salary VARCHAR(255),
                    vacancy_url VARCHAR(255),
                    employees_id INT REFERENCES employees(employees_id)
                )
            """
            cur.execute(query)

            # query = """
            #     WITH ranked_vacancies AS (
            #         SELECT
            #             e.employer_name,
            #             v.vacancy_name,
            #             v.salary,
            #             v.vacancy_url,
            #             ROW_NUMBER() OVER (PARTITION BY e.employer_name ORDER BY v.vacancy_name) AS rn
            #         FROM
            #             vacancies v
            #         JOIN
            #             employees e ON v.employees_id = e.employees_id
            #     )
            #     SELECT
            #         employer_name,
            #         vacancy_name,
            #         salary,
            #         vacancy_url
            #     FROM
            #         ranked_vacancies
            #     WHERE
            #         rn = 1
            #             """
            # cur.execute(query)

            # Закрытие курсора и соединения
            cur.close()
            conn.close()

        except Exception as e:
            print(f"Ошибка при создании базы данных или таблиц: {e}")

        self.connection = psycopg2.connect(
            dbname=self.dbname,
            user=self.params['user'],
            password=self.params['password'],
            host=self.params['host'],
            port=self.params['port'],
        )
        self.connection.autocommit = True

    def insert_vacancies(self, vacancies):
        with self.connection.cursor() as cursor:
            for vacancy in vacancies:
                employer_name = vacancy['employer']['name']

                # Проверка, существует ли работодатель в таблице employees
                cursor.execute("SELECT employees_id FROM employees WHERE employer_name = %s", (employer_name,))
                result = cursor.fetchone()

                if result:
                    employees_id = result[0]
                else:
                    # Вставка нового работодателя и получение его employees_id
                    cursor.execute("INSERT INTO employees (employer_name) VALUES (%s) RETURNING employees_id",
                                   (employer_name,))
                    employees_id = cursor.fetchone()[0]

                # Вставка вакансии
                cursor.execute("""
                    INSERT INTO vacancies (employees_id, vacancy_name, salary, vacancy_url)
                    VALUES (%s, %s, %s, %s)
                """, (
                    employees_id,
                    vacancy['name'],
                    vacancy.get('salary', {}).get('from', 'Не указано') if vacancy.get('salary') else 'Не указано',
                    vacancy['alternate_url']
                ))

    def get_companies_and_vacancies_count(self):
        """получает список всех компаний и
        количество вакансий у каждой компании."""

        with self.connection.cursor() as cursor:
            query = sql.SQL("""
                SELECT e.employer_name, COUNT(*)
                FROM vacancies v
                JOIN employees e ON v.employees_id = e.employees_id
                GROUP BY e.employer_name
            """)
            cursor.execute(query)
            result = cursor.fetchall()
        return result

    def get_all_vacancies(self):
        """получает список всех вакансий с указанием названия компании,
        названия вакансии и зарплаты и ссылки на вакансию."""

        with self.connection.cursor() as cursor:
            query = sql.SQL("""
                       SELECT employer_name, vacancy_name, salary, vacancy_url
                       FROM vacancies
                   """)
            cursor.execute(query)
            result = cursor.fetchall()
        return result

    def get_avg_salary(self):
        """получает среднюю зарплату по вакансиям."""

        with self.connection.cursor() as cursor:
            query = sql.SQL("""
                SELECT AVG(CAST(salary AS INTEGER))
                FROM vacancies
                WHERE salary <> 'Не указано'
            """)
            cursor.execute(query)
            result = cursor.fetchone()
        return result[0] if result[0] else 0

    def get_vacancies_with_higher_salary(self):
        """получает список всех вакансий, у которых
        зарплата выше средней по всем вакансиям."""

        avg_salary = self.get_avg_salary()
        with self.connection.cursor() as cursor:
            query = sql.SQL("""
            SELECT vacancy_name, salary, vacancy_url
            FROM vacancies
            WHERE salary <> 'Не указано'
              AND CAST(salary AS INTEGER) > (
                SELECT AVG(CAST(salary AS INTEGER))
                FROM vacancies
                WHERE salary <> 'Не указано'
              )
                    """)
            cursor.execute(query)
            result = cursor.fetchall()
        return result

    def get_vacancies_with_keyword(self, keyword):
        """получает список всех вакансий, в названии которых
        содержатся переданные в метод слова, например python."""

        with self.connection.cursor() as cursor:
            query = """
                SELECT vacancy_name, salary, vacancy_url
                FROM vacancies
                WHERE vacancy_name ILIKE %s
            """
            cursor.execute(query, (f"%{keyword}%",))
            result = cursor.fetchall()
        return result

# # Пример использования
# hh_api = HeadHunterAPI()
# vacancies = hh_api.get_vacancies([1740, 3529, 23427, 3772, 15478, 1057, 1122462, 19923, 1001, 2180])
# params = config()
# db_manager = DBManager('asardgdfgdfgdsasas', params)
#
# # Убедитесь, что база данных и таблицы созданы перед выполнением других операций
# db_manager.create_table_and_database()
# #
# # Вставка вакансий в базу данных
# print(db_manager.insert_vacancies(vacancies))

# # Получение вакансий с зарплатой выше средней
# db_manager.get_vacancies_with_higher_salary()
#
# # список всех вакансий, в названии которых содержатся переданные в метод слова
# db_manager.get_vacancies_with_keyword("python")
