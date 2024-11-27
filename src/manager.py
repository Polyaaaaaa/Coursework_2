import psycopg2
from psycopg2 import sql


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


class DBManager:
    """класс DBManager, который будет подключаться к БД PostgreSQL"""

    def __init__(self, dbname, params):
        """инициализация"""
        # self.connection = psycopg2.connect(
        #     dbname=dbname,
        #     user=user,
        #     password=password,
        #     host=host,
        #     port=port,
        # )
        self.dbname = dbname
        self.params = params

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

            # Создание таблицы vacancies
            query = """
                CREATE TABLE IF NOT EXISTS vacancies (
                    id SERIAL PRIMARY KEY,
                    employer_name VARCHAR(255),
                    vacancy_name VARCHAR(255),
                    salary VARCHAR(255),
                    vacancy_url VARCHAR(255)
                )
            """
            cur.execute(query)

            # Создание таблицы employees
            query = """
                CREATE TABLE IF NOT EXISTS employees (
                    employer_id VARCHAR(255),
                    employer_name VARCHAR(255)
                )
            """
            cur.execute(query)

            # Создание таблицы vacancy
            query = """
                CREATE TABLE IF NOT EXISTS vacancy (
                    id SERIAL PRIMARY KEY,
                    employer_id VARCHAR(255),
                    employer_title VARCHAR(255),
                    vacancy_id VARCHAR(255),
                    vacancy_title VARCHAR(255)
                )
            """
            cur.execute(query)

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
                query = sql.SQL("""
                    INSERT INTO vacancies (employer_name, vacancy_name, salary, vacancy_url)
                    VALUES (%s, %s, %s, %s)
                """)
                cursor.execute(query, (
                    vacancy['employer']['name'],
                    vacancy['name'],
                    vacancy.get('salary', {}).get('from', 'Не указано') if vacancy.get('salary') else 'Не указано',
                    vacancy['alternate_url']
                ))

    def get_companies_and_vacancies_count(self):
        """получает список всех компаний и
        количество вакансий у каждой компании."""

        with self.connection.cursor() as cursor:
            query = sql.SQL("""
                SELECT employer_name, COUNT(*)
                FROM vacancies
                GROUP BY employer_name
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
                        SELECT employer_name, vacancy_name, salary, vacancy_url
                        FROM vacancies
                        WHERE CAST(salary AS INTEGER) > %s
                    """)
            cursor.execute(query, (avg_salary,))
            result = cursor.fetchall()
        return result

    def get_vacancies_with_keyword(self, keyword):
        """получает список всех вакансий, в названии которых
        содержатся переданные в метод слова, например python."""

        with self.connection.cursor() as cursor:
            query = sql.SQL("""
                SELECT employer_name, vacancy_name, salary, vacancy_url
                FROM vacancies
                WHERE vacancy_name ILIKE %s
            """)
            cursor.execute(query, (f"%{keyword}%",))
            result = cursor.fetchall()
        return result

# params = config()
# emp1 = DBManager('asasasas', params)
# emp1.create_table_and_database()