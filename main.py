import os

from src.config import config
from src.hh import HeadHunterAPI
from src.manager import DBManager


def main():
    # Загрузка параметров подключения к базе данных
    params = config(os.path.join("src/database.ini"), "postgresql")

    # Создание экземпляра DBManager и подключение к базе данных
    db_manager = DBManager(
        dbname="postgres",
        params=params
    )

    # Создание базы данных и таблиц
    db_manager.create_table_and_database()

    # Список ID компаний, от которых будем получать вакансии
    employer_ids = [1740, 3529, 23427, 3772, 15478, 1057, 1122462, 19923, 1001, 2180]

    # Получение вакансий от выбранных компаний
    hh_api = HeadHunterAPI()
    all_vacancies = []
    for employer_id in employer_ids:
        vacancies = hh_api.get_vacancies(employer_id)
        all_vacancies.extend(vacancies)

    # Вставка данных о вакансиях в базу данных
    db_manager.insert_vacancies(all_vacancies)

    # Примеры использования методов DBManager
    avg_salary = db_manager.get_avg_salary()
    print(f"Средняя зарплата: {avg_salary}")

    vacancies_with_higher_salary = db_manager.get_vacancies_with_higher_salary()
    print("Вакансии с зарплатой выше средней:")
    for vacancy in vacancies_with_higher_salary:
        print(vacancy)

    vacancies_with_keyword = db_manager.get_vacancies_with_keyword("python")
    print("Вакансии, содержащие слово 'python':")
    for vacancy in vacancies_with_keyword:
        print(vacancy)


if __name__ == "__main__":
    main()