import os # Импорт библиотек
import json
import math



def read_weapon_types_data(weapon_types_data_file: str) -> dict:
    """Считываем данные из существующего файла, в котором представлен словарь с типами оружия и некоторыми их характеристиками"""
    if os.path.exists(weapon_types_data_file):
        with open(weapon_types_data_file, "r", encoding="utf-8") as file:
            return json.load(file)
    else: 
        print(f'Файла {weapon_types_data_file} не существует!')
        exit()



def create_weapons_data_dict() -> dict:
    """Создаем словарь с данными оружия Аркса. Никакого сложного анализа, просто записываем всю полезную инфу"""

    weapons_dict: dict = {} # Словарь который мы получаем в return

    crafts_list = []
    
    for root, dirs, files in os.walk(abs_path_to_weapon_recipes): # Получаем список всех крафтов
        for file in files:
            crafts_list.append(file[:-5])

    weapon_files_counter = 0 # Счетчик файлов оружия

    for root, dirs, files in os.walk(abs_path_to_weapons): # Вносим ID из названий файлов
        for file in files: # Цикл для каждого отдельного json-файла оружия

            weapon_files_counter += 1
            file_path = os.path.join(root, file) 
            with open(file_path, 'r', encoding='utf-8') as json_file: 
                data = json.load(json_file) # Создаем словарь для каждого файла оружия

                # Везде далее мы используем срез строки, чтобы убрать пространство имен arx:, так как оно здесь не нужно
                weapons_dict[data['minecraft:item']['description']['identifier'][4:]] = {} # Создаем пустой подсловарь для каждого файла в указаной выше директории


                try: # Тип
                    if   any('is_dagger' in block for block in data['minecraft:item']['events']['hurt']['run_command']['command']): weapons_dict[data['minecraft:item']['description']['identifier'][4:]]['type'] = 'dagger' # Кинжал
                    elif any('is_default' in block for block in data['minecraft:item']['events']['hurt']['run_command']['command']): weapons_dict[data['minecraft:item']['description']['identifier'][4:]]['type'] = 'default_sword' # Обычный меч
                    elif any('is_heavy' in block for block in data['minecraft:item']['events']['hurt']['run_command']['command']): weapons_dict[data['minecraft:item']['description']['identifier'][4:]]['type'] = 'heavy_sword' # Тяжёлый меч
                    elif any('is_lance' in block for block in data['minecraft:item']['events']['hurt']['run_command']['command']): weapons_dict[data['minecraft:item']['description']['identifier'][4:]]['type'] = 'lance' # Древка
                    elif any('is_long' in block for block in data['minecraft:item']['events']['hurt']['run_command']['command']): weapons_dict[data['minecraft:item']['description']['identifier'][4:]]['type'] = 'light_longsword' # Легкий двуруч  
                    elif any('is_scythe' in block for block in data['minecraft:item']['events']['hurt']['run_command']['command']): weapons_dict[data['minecraft:item']['description']['identifier'][4:]]['type'] = 'scythe' # Коса
                    elif any('is_staff' in block for block in data['minecraft:item']['events']['hurt']['run_command']['command']): weapons_dict[data['minecraft:item']['description']['identifier'][4:]]['type'] = 'staff' # Посох             
                    elif any('is_very_heavy' in block for block in data['minecraft:item']['events']['hurt']['run_command']['command']): weapons_dict[data['minecraft:item']['description']['identifier'][4:]]['type'] = 'very_heavy_sword' # Сверхтяж
                    elif any('is_wand' in block for block in data['minecraft:item']['events']['hurt']['run_command']['command']): weapons_dict[data['minecraft:item']['description']['identifier'][4:]]['type'] = 'wand' # Волшебная палочка
                    else: weapons_dict[data['minecraft:item']['description']['identifier'][4:]]['type'] = 'unknown'

                except Exception:
                    print(f"Не удалось определить тип оружия для {file}")


                if data['minecraft:item']['description']['identifier'][4:] not in crafts_list:
                    weapons_dict[data['minecraft:item']['description']['identifier'][4:]]['has_recipe'] = False
                else:
                    for recipe_root, recipe_dirs, recipe_files in os.walk(abs_path_to_weapon_recipes): # Анализируем файл крафта
                        for recipe_file in recipe_files:
                            if file == recipe_file:
                                cost = analyse_recipe_cost(os.path.join(recipe_root, recipe_file))
                                weapons_dict[data['minecraft:item']['description']['identifier'][4:]]['has_recipe'] = True

                                weapons_dict[data['minecraft:item']['description']['identifier'][4:]]['raw_cost'] = cost  # Присваиваем значение напрямую

                                weapons_dict[data['minecraft:item']['description']['identifier'][4:]]['damage'] = math.ceil(math.log(cost, 2.5))
                                

                    

    print(str(weapon_files_counter) + ' json файлов оружий всего')

    # Создаем вспомогательный файл со всеми собранными данными data.json. По сути это просто визуализация словаря для удобства
    with open('output/data.json', 'w') as json_result: 
        json.dump(weapons_dict, json_result, indent = 4)

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
    for key in weapons_dict:
        for root, paths, files in os.walk(abs_path_to_weapons):
            for file in files:
                if file[:4] == key:
                    print(file, key)
                    try:
                        with open(os.path.join(abs_path_to_weapons, ""), "r", encoding="utf-8") as weapon_file:
                            pass
                    except Exception as e:
                        print(f"Ошибка при открытии файла оружия <{key}>: {e}")
        
    return None


# === # Начало программы # === #


os.chdir(os.path.dirname(os.path.abspath(__file__))) # Устанавливаем путь выполнения кода
print('=====')

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

# Читаем данные о типах оружия
weapon_types_data = read_weapon_types_data("assets/weapon_types.json")

# Создаем словарь со всем существующем оружием
weapons_dict = create_weapons_data_dict() 

# Модифицируем файлы оружия в системе
inbuild_new_weapon_values(weapons_dict) 


print('Работа AWC успешно завершена.')