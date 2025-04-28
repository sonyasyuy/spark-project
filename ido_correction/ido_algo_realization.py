import numpy as np
from typing import Dict, Tuple

def correct_ido(
    data_company: Dict[str, Tuple[float, float]],
    uf: CompanyUnionFind,
    alpha: float
) -> Dict[str, float]:
    """
    Для каждой дочерней компании в data_company (ключ — название компании,
    значение — tuple(ido, profit)) вычисляет скорректированный ИДО по алгоритму:

    Шаг 1. Получить ido_kernel, ido_child, profit_kernel, profit_child.
    Шаг 2. Если ido_kernel > ido_child → cor_ido = ido_child и пропустить остальные шаги.
    Шаг 3. Иначе, если невозможно вычислить w (nan или деление на ноль) → cor_ido = ido_child.
            Иначе w = 1 + log_alpha(profit_kernel / profit_child).
    Шаг 4. w* = max(1, w).
    Шаг 5. cor_ido = (w* * ido_kernel + ido_child) / (w* + 1).
    """
    corrected: Dict[str, float] = {}

    for comp_name, (ido_child, profit_child) in data_company.items():
        root = uf.find_main(comp_name)

        if root == comp_name:
            continue

        ido_kernel, profit_kernel = data_company[root]
        print('went', ido_kernel, ido_child)
        if ido_kernel == '-' or ido_child == '-':
            continue

        if ido_kernel > ido_child:
            cor_ido = ido_child
        else:
            if (
                profit_kernel is None
                or profit_child is None
                or np.isnan(profit_kernel)
                or np.isnan(profit_child)
                or profit_child == 0
            ):
                cor_ido = ido_child
            else:
                w = 1 + np.log(profit_kernel / profit_child) / np.log(alpha)

                w_star = max(1.0, w)
                print(max(1.0, w), w_star, w)
                print(ido_kernel, ido_child)
                cor_ido = (w_star * ido_kernel + ido_child) / (w_star + 1.0)

        corrected[comp_name] = cor_ido

    return corrected
