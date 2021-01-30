from datetime import datetime
import json
import random
import re

import requests
from tinydb import TinyDB, Query


def print_recipe_info(r):
    print('CURRENT RECIPES TABLE INFO:')
    print('length:', len(r), ', size:', len(str(r)) / 1000, ' MB')
    print('example:', json.dumps(random.choice(r) if len(r) > 0 else {}, indent=2))


def find_recipe_indexes(url):
    r = requests.get(url)
    if r.status_code != 200:
        print('Failed to retrieve find_recipe_indexes url:', r.status_code, r.text)
        return

    recipe_url_pattern = r'https?://www.allrecipes.com/recipe/(\d+)/([\w-]+)/?'

    return {x.group(1): x.group(2) for x in re.finditer(recipe_url_pattern, r.text)}


if __name__ == '__main__':
    recipes_db = TinyDB('allrecipes.db')
    recipes_table = recipes_db.table('recipes_table')

    print_recipe_info(recipes_table.all())

    Recipe = Query()

    recipes_urls = [
        # 'https://www.allrecipes.com/recipes/',
        # 'https://www.allrecipes.com/recipes/79/desserts/',
        # 'https://www.allrecipes.com/recipes/76/appetizers-and-snacks/',
        # 'https://www.allrecipes.com/recipes/156/bread/',
        # 'https://www.allrecipes.com/recipes/77/drinks/',
        # 'https://www.allrecipes.com/recipes/80/main-dish/',
        # 'https://www.allrecipes.com/recipes/96/salad/',
        # 'https://www.allrecipes.com/recipes/81/side-dish/',
        # 'https://www.allrecipes.com/recipes/94/soups-stews-and-chili/',
        # 'https://www.allrecipes.com/recipes/15453/main-dish/casseroles/beef/ground-beef/',
        # 'https://www.allrecipes.com/recipes/78/breakfast-and-brunch/',
        # 'https://www.allrecipes.com/recipes/22959/healthy-recipes/keto-diet/',
        # 'https://www.allrecipes.com/recipes/86/world-cuisine/',
        # 'https://www.allrecipes.com/gallery/best-new-recipes-of-2019/',
        # 'https://www.allrecipes.com/recipes/17562/dinner/',
        # 'https://www.allrecipes.com/gallery/recipes-that-start-with-frozen-vegetables/',
        # 'https://www.allrecipes.com/recipes/16942/soups-stews-and-chili/soup/taco-soup/',
        # 'https://www.allrecipes.com/recipes/138/drinks/smoothies/',
        # 'https://www.allrecipes.com/recipes/17561/lunch/',
        # 'https://www.allrecipes.com/recipes/16376/healthy-recipes/lunches/',
        # 'https://www.allrecipes.com/recipes/17881/main-dish/bowls/',
        # 'https://www.allrecipes.com/recipes/251/main-dish/sandwiches/',
        # 'https://www.allrecipes.com/recipes/17557/main-dish/sandwiches/wraps-and-roll-ups/',
        # 'https://www.allrecipes.com/recipes/16369/soups-stews-and-chili/soup/',
        # 'https://www.allrecipes.com/recipes/96/salad/',
        # 'https://www.allrecipes.com/recipes/12154/everyday-cooking/family-friendly/back-to-school/lunch-box/',
        # 'https://www.allrecipes.com/recipes/18036/everyday-cooking/family-friendly/back-to-school/lunch-box/healthy/',
        # 'https://www.allrecipes.com/recipes/22882/everyday-cooking/instant-pot/',
        # 'https://www.allrecipes.com/recipes/362/desserts/cookies/',
        # 'https://www.allrecipes.com/recipes/15436/everyday-cooking/one-pot-meals/',
        # 'https://www.allrecipes.com/recipes/363/desserts/custards-and-puddings/',
        # 'https://www.allrecipes.com/recipes/272/us-recipes/cajun-and-creole/',
        # 'https://www.allrecipes.com/recipes/695/world-cuisine/asian/chinese/',
        # 'https://www.allrecipes.com/recipes/227/world-cuisine/asian/',
        # 'https://www.allrecipes.com/recipes/699/world-cuisine/asian/japanese/',
        # 'https://www.allrecipes.com/recipes/700/world-cuisine/asian/korean/',
        # 'https://www.allrecipes.com/recipes/233/world-cuisine/asian/indian/',
    ]

    for recipes_url in recipes_urls:
        for recipe_index, recipe_label in find_recipe_indexes(recipes_url).items():
            if not recipes_table.search(Recipe.id == recipe_index):
                recipes_table.insert({
                    'id': recipe_index,
                    'label': recipe_label,
                    'retrieval_date': datetime.now().isoformat(),
                })

    print_recipe_info(recipes_table.all())
