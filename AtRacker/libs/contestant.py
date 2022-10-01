# -*- coding: utf-8 -*-

import re
from bisect import bisect
from time import sleep
from collections import namedtuple

import requests
from bs4 import BeautifulSoup


class UnknownUserError(Exception):
    ...


class AlreadyExistsError(Exception):
    ...


class NotParticipatingError(Exception):
    ...


Result = namedtuple('Result',
                    ('name', 'OldRating', 'NewRating', 'Performance'))


COLOR_PALETTE = (
    'Gray',
    'Brown',
    'Green',
    's-Blue',
    'Blue',
    'Yellow',
    'Orange',
    'Red',
    'Silver',
    'Gold'
)
COLOR_BORDER = (400, 800, 1200, 1600, 2000, 2400, 2800, 3200, 3600)


class Contestant(object):

    member: dict[str:object] = {}
    # A different set of objects would be fine, but it would be tedious to iterate when
    # displaying a list of member names, so I used a dictionary whose keys are user names.
    latest_abc_holding_number = 0

    @classmethod
    def raise_for_existence(cls, name: str) -> None:
        '''Raises AlreadyExistsError if name is already exists.'''
        if name in cls.member:
            raise AlreadyExistsError(f'{name} is already exists')

    @staticmethod
    def raise_for_registration(name: str) -> None:
        sleep(.1)
        '''Raises UnknownUserError if name does not register.'''
        res = requests.get(f'https://atcoder.jp/users/{name}')
        if res.status_code != 200:
            raise UnknownUserError(f'{name} is an unregistered user')

    @staticmethod
    def identify_latest_abc_holding_number() -> None:
        sleep(.1)
        url = 'https://atcoder.jp/contests/archive?ratedType=1&category=0&keyword='
        bs = BeautifulSoup(requests.get(url).text, features="html.parser")
        return re.findall(r'AtCoder Beginner Contest [0-9]{3}',
                          bs.find_all('td')[1].find('a').text)[0][-3:]

    def __init__(self, name) -> None:
        Contestant.raise_for_existence(name)
        Contestant.raise_for_registration(name)
        self.name = name
        self.history = self.fetch_user_history()
        self.current_rating = self.extract_current_rating()
        self.highest_rating = self.extract_highest_rating()
        Contestant.member[name] = self

    def fetch_user_history(self) -> list[dict]:
        sleep(.1)
        return requests.get(f'https://atcoder.jp/users/{self.name}/history/json').json()

    def extract_highest_rating(self) -> int:
        return max(data['NewRating'] for data in self.history)

    def extract_current_rating(self) -> int:
        return self.history[-1]['NewRating']

    def extract_specific_contest_result(self, contest_name: str) -> dict:
        '''
        Extracts specific contest results. Arguments are automatically normalized.

        >>> extract_specific_contest_result('abc250')
        {'IsRated': True,
         'Place': 3377,
         'OldRating': 468,
         ...}
        '''
        if isinstance(contest_name, int) or contest_name.isnumeric():
            contest_name = f'abc{contest_name}'
        contest_name = contest_name.lower()

        for data in self.history:
            if data['ContestScreenName'].startswith(contest_name):
                return data
        raise NotParticipatingError(
            f'{self.name} did not participate in {contest_name}')

    @classmethod
    def update(cls) -> None:
        cls.latest_abc_holding_number = cls.identify_latest_abc_holding_number()
        for user in cls.member.values():
            user.history = user.fetch_user_history()
            user.current_rating = user.extract_current_rating()
            user.highest_rating = user.extract_highest_rating()

    @staticmethod
    def calculate_difference(data: dict) -> int:
        return data['NewRating'] - data['OldRating']

    @classmethod
    def rank_contestants_by_achive(cls, abc_holding_number: str = None) -> list[tuple]:
        ranking = []
        if abc_holding_number is None:
            abc_holding_number = cls.identify_latest_abc_holding_number()
        for name, obj in cls.member.items():
            try:
                result = obj.extract_specific_contest_result(
                    abc_holding_number)
                ranking.append((name, cls.calculate_difference(result)))
            except NotParticipatingError:
                continue
        return sorted(ranking, key=lambda x: -x[1])

    @classmethod
    def rank_contestants_by_highest_rating(cls) -> list[tuple]:
        return sorted(((name, obj.highest_rating) for name, obj in cls.member.items()),
                      key=lambda x: -x[1])

    @classmethod
    def rank_contestants_by_current_rating(cls) -> list[tuple]:
        return sorted(((name, obj.current_rating) for name, obj in cls.member.items()),
                      key=lambda x: -x[1])

    @staticmethod
    def extract_old_and_new_rating(data: dict) -> tuple[int]:
        return data['OldRating'], data['NewRating']

    @classmethod
    def generate_specific_contest_result(cls, contest_name: str) -> list[Result]:
        results = []
        for name, obj in cls.member.items():
            try:
                raw_data = obj.extract_specific_contest_result(contest_name)
                if raw_data['IsRated']:
                    results.append(Result(
                        name, raw_data['OldRating'], raw_data['NewRating'], raw_data['Performance']))
            except NotParticipatingError:
                continue
        return sorted(results, key=lambda x: x.OldRating - x.NewRating)

    @staticmethod
    def detect_color_change(results: list[Result]) -> list[str]:
        changed = []
        for result in results:
            if bisect(COLOR_BORDER, result.OldRating) < (new := bisect(COLOR_BORDER, result.NewRating)):
                changed.append((result.name, COLOR_PALETTE[new]))
        return changed

    @classmethod
    def del_contestant(cls, name) -> None:
        if not name in cls.member:
            raise ValueError(f'{name} does not exist.')
        del cls.member[name]

    def __repr__(self):
        return self.name
