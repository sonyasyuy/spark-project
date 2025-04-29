from __future__ import annotations
from typing import Dict, List, Set, Tuple
import pandas as pd
import numpy as np

def build_company_data_and_children(
    df: pd.DataFrame,
    uf: CompanyUnionFind
) -> Tuple[Dict[str, Tuple[str, int]], Dict[str, List[str]]]:
    company_info: Dict[str, Tuple[str, int]] = {}
    children_map: Dict[str, List[str]] = {}
    for _, row in df.iterrows():
        main = row['Наименование основной компании']
        child = row['Дочерняя компания']
        uf.make_company(main); uf.add_subsidiary(main, child)
        company_info[main]  = (row['ИДО'], format_profit(row['Выручка от продажи']))
        company_info[child] = (row['ИДО дочка'], format_profit(row['Выручка от продажи дочка']))
        children_map.setdefault(main, []).append(child)
        children_map.setdefault(child, [])
    return company_info, children_map

def get_all_descendants(name: str, children_map: Dict[str, List[str]]) -> Set[str]:
    seen: Set[str] = set()
    def dfs(n: str):
        for ch in children_map.get(n, []):
            if ch not in seen:
                seen.add(ch)
                dfs(ch)
    dfs(name)
    return seen

def print_recursive_descendants(name: str, children_map: Dict[str, List[str]]):
    descendants = get_all_descendants(name, children_map)
    print(f"Все дочерние компании для {name!r}:")
    for d in sorted(descendants):
        print("  ", d)
    for child in children_map.get(name, []):
        print_recursive_descendants(child, children_map)

if __name__ == "__main__":
    df = pd.read_excel("izdevatelstvo.xlsx")
    uf = CompanyUnionFind()
    data_company, children_map = build_company_data_and_children(df, uf)

    target = "ПАО \"ТАТНЕФТЬ\" ИМ. В.Д. ШАШИНА"
    print_recursive_descendants(target, children_map)
