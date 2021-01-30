from collections import defaultdict
import json
import os
import time

import numpy as np
from tinydb import TinyDB, Query
from tinydb.operations import set

from library.all_recipes import AllRecipes

random_order = True
verbose = True
brownie = False

all_recipes_thing = AllRecipes()

if __name__ == '__main__':
    start = time.time()

    recipes_db = TinyDB('allrecipes.db')
    recipes_table = recipes_db.table('recipes_table')

    Recipe = Query()
    count = 0
    ahh_count = 0
    food_product_list = defaultdict(list)
    recipe_datas = []

    if brownie:
        id_list = [
            "10549",
            "9599",
            "25037",
            "25112",
            "9861",
            "9827",
            "10177",
            "277919",
            "10281",
        ]
    else:
        id_list = list(r['id'] for r in recipes_table.all())

    if random_order:
        id_list = np.random.permutation(id_list)

    for recipe_id in id_list:
        if os.path.exists(f'allrecipe_recipe_htmls/{recipe_id}_recipe.html'):
            with open(f'allrecipe_recipe_htmls/{recipe_id}_recipe.html', 'r') as recipe_file:

                text = recipe_file

                recipe_data = all_recipes_thing.parse_ld_json_recipe_page(recipe_file.read())
                recipe_datas.append(recipe_data)

                for ingredient in recipe_data['ingredients']:
                    food_product_list[ingredient[1]].append(ingredient[0])

        count += 1
        if count >= 100:
            break
        elif count % 100 == 0:
            print(
                f'processed {count} recipes and {len(food_product_list)} ingredients in {round(time.time() - start, 2)} seconds')

    sorted_products = {k: v for k, v in
                       sorted(food_product_list.items(), key=(lambda item: len(item[1])), reverse=True)}
    print(
        f'processed {count} recipes and {len(food_product_list)} ingredients in {round(time.time() - start, 2)} seconds')

    if brownie:
        data_dir = 'brownie_data'
    else:
        data_dir = 'all_data_sample_100'

    os.makedirs(data_dir)
    json.dump(recipe_datas, open(f'{data_dir}/recipes.json', 'w'), indent=2)
    json.dump(food_product_list, open(f'{data_dir}/ingredients.json', 'w'), indent=2)
