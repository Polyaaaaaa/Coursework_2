import requests
import json


class HeadHunterAPI:
    def __init__(self):
        self.url = "https://api.hh.ru/vacancies"
        self.headers = {"User-Agent": "HH-User-Agent"}
        self.params = {"text": "", "page": 0, "per_page": 100}
        self.vacancies = []

    def get_vacancies(self, employer_id):
        self.params["employer_id"] = employer_id
        self.params["page"] = 0
        while self.params["page"] < 20:
            response = requests.get(self.url, headers=self.headers, params=self.params)

            if response.status_code != 200:
                print(f"Ошибка при запросе: {response.status_code}")
                return []  # Возвращаем пустой список в случае ошибки

            vacancies = response.json().get("items", [])
            if not vacancies:
                break
            self.vacancies.extend(vacancies)
            self.params["page"] += 1

        # Запись полученных данных в файл
        with open("vacancies.json", "w", encoding="utf-8") as file:
            json.dump(self.vacancies, file, ensure_ascii=False, indent=4)
        return self.vacancies


# # Создаем экземпляр класса HeadHunterAPI
# hh_api = HeadHunterAPI()
#
# # Вызываем метод get_vacancies на экземпляре класса
# print(hh_api.get_vacancies("9498120"))
