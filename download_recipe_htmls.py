import datetime
import os
import time

import requests
from tinydb import TinyDB


def download_html(url):
    r = requests.get(url)
    if r.status_code != 200:
        print(r.text)
        raise Exception(f'Failed to retrieve download_html url: {url}, status:{r.status_code}')

    return r.text


if __name__ == '__main__':
    if not os.path.exists('allrecipe_recipe_htmls'):
        os.makedirs('allrecipe_recipe_htmls')

    all_recipes_db = TinyDB('allrecipes.db')
    recipes_table = all_recipes_db.table('recipes_table')

    recipes = recipes_table.all()

    total = len(recipes)
    count = 0
    times = []

    for recipe_id in (r['id'] for r in recipes):
        start = time.time()
        existed = True

        if not os.path.exists(f'allrecipe_recipe_htmls/{recipe_id}_recipe.html'):
            existed = False
            html = download_html(f'https://www.allrecipes.com/recipe/{recipe_id}/')
            with open(f'allrecipe_recipe_htmls/{recipe_id}_recipe.html', 'w') as f:
                f.write(html)

        times.append(time.time() - start)
        avg_time = sum(times) / len(times)
        print(f'already existed {existed}, '
              f'{count}/{total}, '
              f'{count / total}%, '
              f'{recipe_id}, '
              f'avg {avg_time}ms, '
              f'{datetime.datetime.fromtimestamp(((total - count) * avg_time) + time.time())}')

        count += 1
