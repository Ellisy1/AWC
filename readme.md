## AWC - Arx Weapons Corrector

Задача этого кода - автоматически расставлять прочность и урон (и некоторые другие параметры) оружия в Арксе, опираясь на его рецепт, или при его остуствии на свой собственный словарь

# Последовательность действий:
1. Формируем словарь оружия, основываясь на файлах оружий в Арксе
2. Дополняем этот словарь ценностью оружия из рецептов или из файла оружия
3. Дополняем словарь кодом
    3.1. Устанавливаем урон зависимо от сырой стоимости и типа оружия
    3.2. Устанавливаем прочность зависимо от сырой стоимости
    3.3. В случае, если оружие AOE-дамагное, рассчитываем AOE урон через сырую стоимость
4. Проверяем, нет ли конфликтов или проблем в полученном словаре
5. Вносим в файлы оружия изменения из словаря