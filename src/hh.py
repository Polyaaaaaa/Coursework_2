import json
import os

import requests


from typing import Dict, List

import requests


class HeadHunterAPI:
    """Класс для получения информации о компаниях и вакансиях с API hh.ru."""

    BASE_URL = "https://api.hh.ru"

    @staticmethod
    def get_company_info(employer_id: str) -> Dict:
        """Возвращает информацию о компании по её ID."""
        response = requests.get(f"{HeadHunterAPI.BASE_URL}/employers/{employer_id}")
        response.raise_for_status()
        return response.json()

    @staticmethod
    def get_vacancies(employer_id: str, page: int = 0, per_page: int = 100) -> List[Dict]:
        """Возвращает список вакансий для компании с возможностью пагинации."""
        params = {"employer_id": employer_id, "page": page, "per_page": per_page}
        response = requests.get(f"{HeadHunterAPI.BASE_URL}/vacancies", params=params)
        response.raise_for_status()
        return response.json()["items"]

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
#
#         # Запись полученных данных в файл
#         with open("vacancies.json", "w", encoding="utf-8") as file:
#             json.dump(self.vacancies, file, ensure_ascii=False, indent=4)
#
#         return self.vacancies
#
#     def __str__(self):
#         return f"{self.vacancies}"
