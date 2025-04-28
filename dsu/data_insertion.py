from typing import Dict, Tuple
import pandas as pd


def format_profit(amount: int) -> int:
    """
    Выделяет цифры прибыли из числа вида '202424 937 596 0000₽' → int(9375960000).
    """
    text = str(amount)
    clean = text.replace("\xa0", "").replace("₽", "")
    if len(clean) <= 4:
        return np.nan
    elif clean[4:] == '—' or clean[4:] == '-':
        return np.nan
    return int(clean[4:])


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
