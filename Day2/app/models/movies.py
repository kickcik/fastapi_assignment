# app/models/movies.py

import random


class MovieModel:
    _data = []  # 데이터를 저장할 리스트
    _id_counter = 1  # ID 자동 증가

    def __init__(self, title, playtime, genre):
        self.id = MovieModel._id_counter
        self.title: str = title
        self.playtime: int = playtime
        self.genre: list[str] = genre

        # 데이터를 리스트에 추가
        MovieModel._data.append(self)
        MovieModel._id_counter += 1

    @classmethod
    def create(cls, title, playtime, genre):
        """새로운 영화 추가"""
        return cls(title, playtime, genre)

    @classmethod
    def get(cls, **kwargs):
        """조건에 맞는 단일 영화 반환 (없으면 None)"""
        for movie in cls._data:
            if all(getattr(movie, key) == value for key, value in kwargs.items()):
                return movie
        return None

    @classmethod
    def filter(cls, **kwargs):
        """조건에 맞는 모든 영화 리스트 반환"""
        result = [
            movie
            for movie in cls._data
            if all(getattr(movie, key) == value or value in getattr(movie, key) for key, value in kwargs.items())
        ]

        return result

    def update(self, **kwargs):
        """영화 정보 업데이트"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                if value is not None:
                    setattr(self, key, value)

    def delete(self):
        """현재 인스턴스를 _data 리스트에서 삭제"""
        if self in MovieModel._data:
            MovieModel._data.remove(self)

    @classmethod
    def all(cls):
        """전체 영화 리스트 반환"""
        return cls._data

    @classmethod
    def create_dummy(cls):
        for i in range(1, 11):
            cls.create(
                title=f"dummy_movie {i}",
                playtime=random.randint(100, 300),
                genre=random.sample(
                    [
                        "SF",
                        "Romantic",
                        "Adventure",
                        "Action",
                        "Comedy",
                        "Horror",
                        "Drama",
                        "Thriller",
                        "Mystery",
                        "Crime",
                        "Musical",
                        "War",
                        "Western",
                        "Historical",
                        "Documentary",
                        "Animation",
                        "Fantasy",
                        "Biopic",
                        "Superhero",
                        "Noir",
                        "Disaster",
                        "Sports",
                        "Family",
                    ],
                    k=3,
                ),
            )

    def __repr__(self):
        return f"MovieModel(id={self.id}, title='{self.title}', playtime={self.playtime}, genre='{self.genre}')"

    def __str__(self):
        return self.title
