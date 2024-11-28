import os

from src.config import config
from src.hh import HeadHunterAPI
from src.manager import DBManager


def main():
    # Загрузка параметров подключения к базе данных
    params = config(os.path.join("src/database.ini"), "postgresql")

    # Создание экземпляра DBManager и подключение к базе данных
    db_manager = DBManager(
        dbname="postgresaa",
        params=params
    )

    # Создание базы данных и таблиц
    db_manager.create_table_and_database()

    # Список ID компаний, от которых будем получать вакансии
    employer_ids = [9475737, 9498120, 9885760, 3821329, 2515303, 4292707, 1051379, 3116650, 10011655, 6591]

    # Получение вакансий от выбранных компаний
    hh_api = HeadHunterAPI()
    all_vacancies = []
    for employer_id in employer_ids:
        vacancies = hh_api.get_vacancies(employer_id)
        all_vacancies.extend(vacancies)

    print("Все вакансии:")
    total_vacancies = 0
    final_lst_vacancies = []
    for vacancy in all_vacancies:
        if total_vacancies == 10:
            break
        else:
            print(vacancy["name"])
            total_vacancies += 1
            final_lst_vacancies.append(vacancy)

    # for element in final_lst_vacancies:
    #     print(element['employer']['name'])

    # Вставка данных о вакансиях в базу данных
    db_manager.insert_vacancies(final_lst_vacancies)

    # Примеры использования методов DBManager
    avg_salary = db_manager.get_avg_salary()
    print(f"\nСредняя зарплата: {int(avg_salary)}")

    vacancies_with_higher_salary = db_manager.get_vacancies_with_higher_salary()
    print("\nВакансии с зарплатой выше средней:")
    for vacancy in vacancies_with_higher_salary:
        print(vacancy)

    vacancies_with_keyword = db_manager.get_vacancies_with_keyword("python")
    print("\nВакансии, содержащие слово 'python':")
    for vacancy in vacancies_with_keyword:
        print(vacancy)


if __name__ == "__main__":
    main()
