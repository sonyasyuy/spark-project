from dsu.data_insertion import uf
from ido_algo_realization import correct_ido
from dsu.data_insertion import data_company

alpha = 1.1
corrected_idos = correct_ido(data_company, uf, alpha)

for company, new_ido in corrected_idos.items():
    print(f"{company!r}: old={data_company[company][0]}, new={new_ido:.2f}")
