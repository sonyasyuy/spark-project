from graph_construction import CompanyUnionFind
from typing import Dict, Tuple
import pandas as pd



import numpy as np

def format_profit_correct(amount):
    """
    Выделяет цифры прибыли из числа вида '202424 937 596 0000₽' → int(249375960000).
    """
    if isinstance(amount, str):
        clean = amount.replace("\xa0", "").replace("₽", "").replace(" ", "").replace("-", "").replace("—", "")
        if len(clean) <= 4:
            return np.nan
        clean = clean[4:]  
        if clean == "" or clean == "-":
            return np.nan
        try:
            return int(clean)
        except ValueError:
            return np.nan
    return np.nan



def build_company_data(
    df: pd.DataFrame,
    uf: CompanyUnionFind
) -> Dict[str, Tuple[str, int]]:

    company_info: Dict[str, Tuple[str, int]] = {}

    for _, row in df.iterrows():
        main_name = row['Наименование основной компании']
        child_name = row['Дочерняя компания']

        uf.make_company(main_name)
        uf.add_subsidiary(main_name, child_name)

        # данные по «главной» компании
        main_id     = row['ИДО']
        main_profit = format_profit(row['Выручка от продажи'])
        company_info[main_name] = (main_id, main_profit)

        # данные по «дочке»
        child_id     = row['ИДО дочка']
        child_profit = format_profit(row['Выручка от продажи дочка'])
        company_info[child_name] = (child_id, child_profit)

    return company_info


if __name__ == "__main__":

    df = pd.read_excel("izdevatelstvo.xlsx")
    uf = CompanyUnionFind()
    data_company = build_company_data(df, uf)

    print("Иерархия корней:", uf.as_dict())
    print("Собранная информация по компаниям:")
    for comp, (cid, profit) in data_company.items():
        print(f"  {comp!r}: ИДО={cid!r}, Profit={profit}")
