# Импорт библиотек
import os 
import json
import math



def get_crafts_list() -> list:
    """Эта функция создает список, содержащий названия всех существующих крафтов оружий"""
    crafts_list = [] # Создаем список для названий крафтов оружий. Он нужен, чтобы быстро определить, есть ли у оружия крафт или нет.
    for root, dirs, files in os.walk(abs_path_to_weapon_recipes): # Получаем список всех крафтов в crafts_list. Данные имеют формат простого списка с названием файлов
        for file in files:
            crafts_list.append(file[:-5])
    if crafts_list:
        return crafts_list
    else:
        raise ValueError(f'Ошибка при создании списка крафтов: он получился пустой. Проверьте директорию крафтов {abs_path_to_weapon_recipes}')


def create_json_dict_visualization_file(weapons_dict_for_output: dict) -> None:
    """Создаем вспомогательный файл со всеми собранными данными output/data.json. По сути это просто визуализация словаря оружия для удобства."""
    with open('output/data.json', 'w') as json_result: 
        json.dump(weapons_dict_for_output, json_result, indent = 4)



def read_weapon_types_data(weapon_types_data_file: str) -> dict:
    """Считываем данные из существующего файла, в котором представлен словарь с типами оружия Аркса и некоторыми их характеристиками."""
    try:
        with open(weapon_types_data_file, "r", encoding="utf-8") as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        raise FileNotFoundError(f"Файл с данными о типах оружия не найден: {weapon_types_data_file}")
    except json.JSONDecodeError:
        raise ValueError(f"Ошибка при разборе JSON в файле: {weapon_types_data_file}")



def define_weapon_type(weapon: dict, weapons_dict: dict, weapon_file: str = None):
    """Функция определяет тип оружия. На вход получает словарь конкретного оружия, общий словарь оружия и название файла оружия"""
    weapon_type_is_unknown = True
    for weapon_type in weapon_types_dict:
        if f"tag:is_{weapon_type}" in weapon["minecraft:item"]["components"]:
            weapon_type_is_unknown = False
            weapons_dict[weapon['minecraft:item']['description']['identifier'][4:]]['type'] = weapon_type
            break
        
    if weapon_type_is_unknown: # Если нет совпадения ни с одним известным типом оружия
        weapons_dict[weapon['minecraft:item']['description']['identifier'][4:]]['type'] = 'unknown'
        print(f'Не получилось опознать тип оружия {weapon_file}')



def create_weapons_data_dict() -> dict:
    """Создаем словарь с данными оружия Аркса. Никакого сложного анализа, просто записываем всю полезную инфу"""

    weapons_dict: dict = {} # Словарь который мы получаем в return

    weapon_files_counter = 0 # Счетчик файлов оружия. Нужен, чтобы по факту выполнения кода сосчитать количество единиц оружия

    for root, dirs, files in os.walk(abs_path_to_weapons):
        for file in files: # Цикл для каждого отдельного json-файла оружия

            weapon_files_counter += 1 # Увеличиваем счетчик файлов оружия
            with open(os.path.join(root, file), 'r', encoding='utf-8') as json_file: 
                weapon = json.load(json_file) # Создаем словарь для каждого файла оружия

                # Везде далее мы используем срез строки, чтобы убрать пространство имен arx:, так как оно здесь не нужно
                weapons_dict[weapon['minecraft:item']['description']['identifier'][4:]] = {} # Создаем пустой подсловарь для каждого оружия (в общем словаре, который пойдет в return)

                # === Обработка типа оружия === #
                define_weapon_type(weapon, weapons_dict, file)

                # === Обработка рецепта === #
                if weapon['minecraft:item']['description']['identifier'][4:] not in crafts_list: 
                    weapons_dict[weapon['minecraft:item']['description']['identifier'][4:]]['has_recipe'] = False
                else:
                    for recipe_root, recipe_dirs, recipe_files in os.walk(abs_path_to_weapon_recipes): # Анализируем файл крафта
                        for recipe_file in recipe_files:
                            if file == recipe_file:
                                cost = analyse_recipe_cost(os.path.join(recipe_root, recipe_file))
                                weapons_dict[weapon['minecraft:item']['description']['identifier'][4:]]['has_recipe'] = True
                                weapons_dict[weapon['minecraft:item']['description']['identifier'][4:]]['raw_cost'] = cost  # Присваиваем значение напрямую
                                weapons_dict[weapon['minecraft:item']['description']['identifier'][4:]]['damage'] = round(math.log(cost, 2.5) * weapon_types_dict[weapons_dict[weapon['minecraft:item']['description']['identifier'][4:]]['type']]["damage_multiplier"]) # Умножаем логарифм из стоимости оружия на множитель урона этого типа оружия
                                weapons_dict[weapon['minecraft:item']['description']['identifier'][4:]]['durability'] = round(math.log(cost, 1.1))

    print(str(weapon_files_counter) + ' json файлов оружий проанализировано')

    return weapons_dict



def analyse_recipe_cost(current_recipe_dir: str) -> int:
    """Функция анализирует рецепт по указанному пути current_recipe_dir и возвращает значение стоимости крафта типом int"""
    with open(current_recipe_dir, 'r', encoding='utf-8') as recipe_analyse_file: # Открываем файл крафта

        result_cost = 0 # Стоимость рецепта

        recipe_data = json.load(recipe_analyse_file) # Загружаем весь файл крафта в виде словаря в переменную recipe_data

        # Анализируем, какие предметы предоставлены 
        recipe_items_dict = {k: v["item"] for k, v in recipe_data["minecraft:recipe_shaped"]["key"].items()}

        # Создаем строку из символов крафта craft_string
        craft_string = ''.join(recipe_data["minecraft:recipe_shaped"]["pattern"]).replace(' ', '')

        # print(craft_string)

        # Анализируем стоимость
        for i in range(len(craft_string)):

            # Болванки
            if   recipe_items_dict[craft_string[i]] == "arx:duraluminum_billet": result_cost += 360
            elif recipe_items_dict[craft_string[i]] == "arx:duraluminum_ingot": result_cost += 180

            elif recipe_items_dict[craft_string[i]] == "arx:aluminum_billet": result_cost += 50
            elif recipe_items_dict[craft_string[i]] == "arx:aluminum_ingot": result_cost += 25

            elif recipe_items_dict[craft_string[i]] == "arx:iron_billet": result_cost += 70
            elif recipe_items_dict[craft_string[i]] == "minecraft:iron_ingot": result_cost += 35

            elif recipe_items_dict[craft_string[i]] == "arx:tin_billet": result_cost += 80
            elif recipe_items_dict[craft_string[i]] == "arx:tin_ingot": result_cost += 40

            elif recipe_items_dict[craft_string[i]] == "arx:cast_iron_billet": result_cost += 140
            elif recipe_items_dict[craft_string[i]] == "arx:cast_iron_ingot": result_cost += 70

            elif recipe_items_dict[craft_string[i]] == "arx:steel_billet": result_cost += 510
            elif recipe_items_dict[craft_string[i]] == "arx:steel_ingot": result_cost += 255

            elif recipe_items_dict[craft_string[i]] == "arx:durasteel_block": result_cost += 6210
            elif recipe_items_dict[craft_string[i]] == "arx:durasteel_billet": result_cost += 1360
            elif recipe_items_dict[craft_string[i]] == "arx:durasteel_ingot": result_cost += 680

            elif recipe_items_dict[craft_string[i]] == "arx:gold_billet": result_cost += 120
            elif recipe_items_dict[craft_string[i]] == "minecraft:gold_ingot": result_cost += 60
            elif recipe_items_dict[craft_string[i]] == "minecraft:gold_nugget": result_cost += 7

            elif recipe_items_dict[craft_string[i]] == "arx:plumbum_billet": result_cost += 80
            elif recipe_items_dict[craft_string[i]] == "arx:plumbum_ingot": result_cost += 40

            elif recipe_items_dict[craft_string[i]] == "arx:bronze_billet": result_cost += 236
            elif recipe_items_dict[craft_string[i]] == "arx:bronze_ingot": result_cost += 118

            elif recipe_items_dict[craft_string[i]] == "arx:riolik_protective_plate": result_cost += 600
            elif recipe_items_dict[craft_string[i]] == "arx:riolik_billet": result_cost += 400
            elif recipe_items_dict[craft_string[i]] == "arx:riolik_ingot": result_cost += 200

            elif recipe_items_dict[craft_string[i]] == "arx:caryite_block": result_cost += 135000
            elif recipe_items_dict[craft_string[i]] == "arx:caryite_billet": result_cost += 30000
            elif recipe_items_dict[craft_string[i]] == "arx:caryite_ingot": result_cost += 15000

            elif recipe_items_dict[craft_string[i]] == "arx:sphere_of_power": result_cost += 52000
            elif recipe_items_dict[craft_string[i]] == "arx:forfactorite_billet": result_cost += 26000
            elif recipe_items_dict[craft_string[i]] == "arx:forfactorite_ingot": result_cost += 13000

            elif recipe_items_dict[craft_string[i]] == "arx:altaite_billet": result_cost += 32000
            elif recipe_items_dict[craft_string[i]] == "arx:altaite_ingot": result_cost += 16000

            elif recipe_items_dict[craft_string[i]] == "arx:dorionite_billet": result_cost += 30000
            elif recipe_items_dict[craft_string[i]] == "arx:dorionite_ingot": result_cost += 15000

            elif recipe_items_dict[craft_string[i]] == "arx:chloronite_billet": result_cost += 40000
            elif recipe_items_dict[craft_string[i]] == "arx:chloronite_ingot": result_cost += 20000

            elif recipe_items_dict[craft_string[i]] == "arx:naginitis_block": result_cost += 90000
            elif recipe_items_dict[craft_string[i]] == "arx:naginitis_billet": result_cost += 20000
            elif recipe_items_dict[craft_string[i]] == "arx:naginitis_ingot": result_cost += 10000

            elif recipe_items_dict[craft_string[i]] == "arx:netherite_billet": result_cost += 30000
            elif recipe_items_dict[craft_string[i]] == "minecraft:netherite_ingot": result_cost += 15000

            elif recipe_items_dict[craft_string[i]] == "arx:toliriite_billet": result_cost += 36000
            elif recipe_items_dict[craft_string[i]] == "arx:toliriite_ingot": result_cost += 18000

            elif recipe_items_dict[craft_string[i]] == "arx:malafiotironite_billet": result_cost += 36000
            elif recipe_items_dict[craft_string[i]] == "arx:malafiotironite_ingot": result_cost += 18000

            elif recipe_items_dict[craft_string[i]] == "arx:lamenite_billet": result_cost += 90000
            elif recipe_items_dict[craft_string[i]] == "arx:lamenite_ingot": result_cost += 45000

            elif recipe_items_dict[craft_string[i]] == "arx:draphorite_billet": result_cost += 90000
            elif recipe_items_dict[craft_string[i]] == "arx:draphorite_ingot": result_cost += 45000

            # Камни драг
            elif recipe_items_dict[craft_string[i]] in ("arx:aquamarine_gem", "arx:chrysolite_gem", "arx:cornelian_gem", "arx:ruby_gem", "arx:saphire_gem", "arx:topaz_gem"): result_cost += 200
            elif recipe_items_dict[craft_string[i]] == "minecraft:diamond": result_cost += 100
            elif recipe_items_dict[craft_string[i]] == "minecraft:amethyst_shard": result_cost += 80

            # Прочее
            elif recipe_items_dict[craft_string[i]] == "minecraft:copper_ingot": result_cost += 7
            elif recipe_items_dict[craft_string[i]] == "minecraft:copper_block": result_cost += 63

            elif recipe_items_dict[craft_string[i]] == "minecraft:stick": result_cost += 1
            elif recipe_items_dict[craft_string[i]] == "minecraft:crimson_planks": result_cost += 25
            elif recipe_items_dict[craft_string[i]] == "minecraft:cherry_planks": result_cost += 20
            elif recipe_items_dict[craft_string[i]] == "minecraft:feather": result_cost += 10
            elif recipe_items_dict[craft_string[i]] == "minecraft:planks": result_cost += 2
            elif recipe_items_dict[craft_string[i]] == "minecraft:planks:1": result_cost += 3
            elif recipe_items_dict[craft_string[i]] in ("minecraft:coal", "minecraft:charcoal"): result_cost += 10
            elif recipe_items_dict[craft_string[i]] == "arx:myterious_eye": result_cost += 400
            elif recipe_items_dict[craft_string[i]] == "minecraft:blaze_rod": result_cost += 800
            elif recipe_items_dict[craft_string[i]] == "arx:desert_essence": result_cost += 800
            elif recipe_items_dict[craft_string[i]] == "minecraft:string": result_cost += 5
            elif recipe_items_dict[craft_string[i]] == "minecraft:wood": result_cost += 8
            elif recipe_items_dict[craft_string[i]] == "minecraft:leaves": result_cost += 8
            elif recipe_items_dict[craft_string[i]] == "arx:gold_feather": result_cost += 100000
            elif recipe_items_dict[craft_string[i]] == "minecraft:leaves": result_cost += 8
            elif recipe_items_dict[craft_string[i]] == "minecraft:obsidian": result_cost += 150
            elif recipe_items_dict[craft_string[i]] == "minecraft:dye": result_cost += 25
            elif recipe_items_dict[craft_string[i]] == "arx:silk": result_cost += 100
            elif recipe_items_dict[craft_string[i]] == "arx:small_stone": result_cost += 1
            elif recipe_items_dict[craft_string[i]] == "minecraft:bone": result_cost += 2
            elif recipe_items_dict[craft_string[i]] == "arx:essence_of_vicious_demon": result_cost += 2000

            elif recipe_items_dict[craft_string[i]] == "arx:vicious_dagger": result_cost += 10000
            elif recipe_items_dict[craft_string[i]] == "arx:vicious_lance": result_cost += 10000
            elif recipe_items_dict[craft_string[i]] == "arx:vicious_staff": result_cost += 10000
            

            else: print(recipe_items_dict[craft_string[i]], "неопознаный ингредиент в рецепте!")

    return result_cost



def inbuild_new_weapon_values(weapons_dict: dict) -> None:
    """Эта функция полагается на составленный ранее словарь weapons_dict и изменяет файлы оружия в Арксе зависимо от его содержимого"""

    weapon_files_counter = 0
    for key in weapons_dict:
        for root, paths, files in os.walk(abs_path_to_weapons):
            for file in files:
                if file[:-5] == key:
                    try:
                        with open(os.path.join(root, file), "r", encoding="utf-8") as weapon_file_r: # Открываем файл оружия в режиме чтения, чтобы загрузить из него данные
                            weapon_files_counter += 1
                            data = json.load(weapon_file_r)

                            with open(os.path.join(root, file), "w", encoding="utf-8") as weapon_file_w: # Открываем файл оружия в режиме записи, чтобы привнести в него изменения
                                if 'damage' in weapons_dict[key]:
                                    data['minecraft:item']['components']['minecraft:damage'] = weapons_dict[key]['damage']
                                
                                json.dump(data, weapon_file_w, indent = 4)

                    except Exception as e:
                        print(f"[Перестройка файлов оружия] Ошибка при открытии файла оружия <{key}>: {e}")
    
    print(f'{weapon_files_counter} файлов оружий откорректировано')

    return None



# === # НАЧАЛО ПРОГРАММЫ # === #



os.chdir(os.path.dirname(os.path.abspath(__file__))) # Устанавливаем путь выполнения кода

# Определяем пути
# Общий путь
path_to_bps = "C:/Users/arsen/AppData/Local/Packages/Microsoft.MinecraftUWP_8wekyb3d8bbwe/LocalState/games/com.mojang/development_behavior_packs" # Путь до папки бех-паков

# Локальные пути
loc_path_to_weapons = "ARX NAP BP/items/weapons"
loc_path_to_weapon_recipes = "ARX NAP BP/recipes/weapons"

# Абсолютные пути
if os.path.exists(os.path.join(path_to_bps, loc_path_to_weapons)): abs_path_to_weapons = os.path.join(path_to_bps, loc_path_to_weapons)
else: print(f'Ошибка при инициализации абсолютного пути для {loc_path_to_weapons}')
if os.path.exists(os.path.join(path_to_bps, loc_path_to_weapon_recipes)): abs_path_to_weapon_recipes = os.path.join(path_to_bps, loc_path_to_weapon_recipes)
else: print(f'Ошибка при инициализации абсолютного пути для {loc_path_to_weapon_recipes}')

# Получаем список названий существующих крафтов оружия
crafts_list = get_crafts_list()

# Читаем данные о типах оружия
weapon_types_dict = read_weapon_types_data("assets/weapon_types.json")

# Создаем словарь со всем существующем оружием
weapons_dict = create_weapons_data_dict() 

# Модифицируем файлы оружия в системе
inbuild_new_weapon_values(weapons_dict) 

# Создаем визуализацию словаря
create_json_dict_visualization_file(weapons_dict)

print('Работа AWC успешно завершена.')