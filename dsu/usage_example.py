if __name__ == "__main__":
    uf = CompanyUnionFind()
    uf.make_company("Группа-А")
    uf.add_subsidiary("Группа-А", "Дочка-1")
    uf.add_subsidiary("Группа-А", "Дочка-2")
    uf.union("Группа-Б", "Группа-А", prefer="second")

    print("Главная для 'Дочка-1':", uf.find_main("Дочка-1"))
    print("Главная для 'Группа-Б':", uf.find_main("Группа-Б"))
    print("Все связи:", uf.as_dict())
