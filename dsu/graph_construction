from __future__ import annotations
from typing import Dict


class CompanyUnionFind:
    """
    Union‑Find для компаний без ранговой эвристики:
    хранит иерархию через parent и использует сжатие пути.
    """

    def __init__(self) -> None:
        self._parent: Dict[str, str] = {}

    def make_company(self, name: str) -> None:
        """
        Регистрирует новую компанию в системе.
        Если уже есть — ничего не делает.
        """
        if name not in self._parent:
            self._parent[name] = name

    def _find_root(self, name: str) -> str:
        """
        Внутренняя реализация функции find с сжатием пути.
        Возвращает корень для name.
        """
        parent = self._parent.setdefault(name, name)
        if parent != name:
            self._parent[name] = self._find_root(parent)
        return self._parent[name]

    def find_main(self, name: str) -> str:
        """
        Публичный метод: находит главную (корневую) компанию для name.
        """
        if name not in self._parent:
            raise KeyError(f"Компания {name!r} не зарегистрирована.")
        return self._find_root(name)

    def union(self, a: str, b: str, prefer: str = "first") -> None:
        """
        Объединяет группы компаний A и B:
        просто делает корень B дочерним по отношению к корню A
        (или наоборот, если prefer == "second").
        """
        self.make_company(a)
        self.make_company(b)

        if prefer.lower() == "second":
            a, b = b, a

        root_a = self._find_root(a)
        root_b = self._find_root(b)
        if root_a != root_b:
            self._parent[root_b] = root_a

    def add_subsidiary(self, parent: str, child: str) -> None:
        self.union(parent, child, prefer="first")

    def as_dict(self) -> Dict[str, str]:
        """
        Текущее отображение компании → её корень.
        """
        return {name: self.find_main(name) for name in self._parent}
