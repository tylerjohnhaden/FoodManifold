import json
import os

from tinydb import TinyDB, Query

if __name__ == '__main__':
    recipes_db = TinyDB('allrecipes.db')
    recipes_table = recipes_db.table('recipes_table')

    Recipe = Query()
    brownie_ids = []

    for recipe_id in (r['id'] for r in recipes_table.all()):
        if os.path.exists(f'allrecipe_recipe_htmls/{recipe_id}_recipe.html'):
            with open(f'allrecipe_recipe_htmls/{recipe_id}_recipe.html', 'r') as f:
                if 'brownie' in f.read():
                    brownie_ids.append(recipe_id)

    print(json.dumps(brownie_ids, indent=4))

actual_brownie_ids = [
    "10549",
    "9599",
    "25037",
    "17643",
    "25112",
    "9861",
    "9827",
    "276275",
    "222037",
    "26460",
    "220414",
    "272457",
    "10177",
    "277919",
    "10281",
    "44699"
]
