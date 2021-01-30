import json
import re

from bs4 import BeautifulSoup
import requests
from tinydb import TinyDB


def crawl_for_all_recipe_ids(urls):
    all_recipe_url_pattern = r'https?://www.allrecipes.com/recipe/(\d+)/[\w-]+/?'

    if type(urls) is str:
        urls = [urls]

    found_ids = set()

    for url in urls:
        r = requests.get(url)
        if r.status_code != 200:
            print('Failed to retrieve url:', url, r.status_code, r.text)
            continue

        found_ids.update(int(x.group(1)) for x in re.finditer(all_recipe_url_pattern, r.text))

    return sorted(list(found_ids))


class AllRecipes:
    def __init__(self, db_path='allrecipes.db'):
        db = TinyDB(db_path)
        self.recipes_table = db.table('recipes_table')
        self.unseen_urls = set()

    def parse_ld_json_recipe_page(self, html, verbose=True):
        recipe_soup = BeautifulSoup(html, 'html.parser')
        ld_json_element = recipe_soup.find('script', {'type': 'application/ld+json'})

        if ld_json_element is None:
            return None

        self.unseen_urls.update(
            [item['item']['@id'] for item in json.loads(ld_json_element.contents[0])[0]['itemListElement']])
        ld_json = json.loads(ld_json_element.contents[0])[1]

        recipe_data = {}

        # unexplored fields:
        # - recipeCategory
        # - ratingValue
        # - reviewCount

        recipe_data['name'] = ld_json['name']

        if verbose:
            recipe_data['description'] = ld_json['description'].strip()
            recipe_data['recipeInstructions'] = [instruction['text'].strip() for instruction in
                                                 ld_json['recipeInstructions']]

        # <<minutes>>, times come in the form 'P0DT0H0M'
        recipe_data['prepTimeMinutes'] = format_time(ld_json['prepTime'])
        recipe_data['cookTimeMinutes'] = format_time(ld_json['cookTime'])
        recipe_data['totalTimeMinutes'] = format_time(ld_json['totalTime'])

        # <<no units>>
        recipe_data['energyContentCalories'] = format_calories(ld_json['nutrition']['calories'])

        # <<grams>>
        recipe_data['fatContentGrams'] = format_content(ld_json['nutrition']['fatContent'])
        recipe_data['carbohydrateContentGrams'] = format_content(
            ld_json['nutrition']['carbohydrateContent'])
        recipe_data['proteinContentGrams'] = format_content(ld_json['nutrition']['proteinContent'])

        # <<milligrams>
        recipe_data['cholesterolContentMilligrams'] = format_content(
            ld_json['nutrition']['cholesterolContent'])
        recipe_data['sodiumContentMilligrams'] = format_content(ld_json['nutrition']['sodiumContent'])

        # mostly <<milliliters>> or <<egg>> or <<serving>>
        recipe_data['ingredients'] = []
        for value, food_product in map(format_universal_ingredient, ld_json['recipeIngredient']):
            recipe_data['ingredients'].append((value, food_product))

        return recipe_data


def format_time(s, source='ld_json'):
    time_conversion_patterns = {
        'html': (re.compile(r'((\d+) d)? ?((\d+) h)? ?((\d+) m)?'), 2, 4, 6),
        'ld_json': (re.compile(r'P(\d+)DT(\d+)H(\d+)M'), 1, 2, 3),
    }
    time_conversion_pattern, day_group, hour_group, minute_group = time_conversion_patterns[source]

    time_match = time_conversion_pattern.match(s)
    if time_match is None:
        print(f'format time failed for "{s}"')
        return -1

    day_hour_minute_groups = time_match.group(day_group, hour_group, minute_group)

    days = 0 if day_hour_minute_groups[0] is None else int(day_hour_minute_groups[0])
    hours = 0 if day_hour_minute_groups[1] is None else int(day_hour_minute_groups[1])
    minutes = 0 if day_hour_minute_groups[2] is None else int(day_hour_minute_groups[2])

    return (24 * 60 * days) + (60 * hours) + minutes


def format_content(s):
    content_conversion_pattern = re.compile(r'(\d+(.\d+)?)( m?g)?')
    return float(content_conversion_pattern.match(s).group(1))


def format_calories(s):
    pattern = re.compile(r'(\d+(.\d+)?)( calories)?')
    return float(pattern.match(s).group(1))


def convert_to_decimal_from_fraction(s):
    conversions = {
        '⅛': 0.125,
        '⅙': 0.1667,
        '⅕': 0.2,
        '¼': 0.25,
        '1/4': 0.25,
        '⅓': 0.3333,
        '1/3': 0.3333,
        '⅜': 0.375,
        '⅖': 0.4,
        '½': 0.5,
        '1/2': 0.5,
        '⅗': 0.6,
        '⅝': 0.625,
        '⅔': 0.6667,
        '¾': 0.75,
        '⅘': 0.8,
        '⅚': 0.8333,
        '⅞': 0.875,
    }

    values = s.replace('\u2009', ' ').split(' ')

    cumulative = 0

    if values[0] in conversions.keys():
        cumulative += conversions[values[0]]
    else:
        cumulative += float(values[0])

    if len(values) == 2:
        if values[1] in conversions.keys():
            cumulative += conversions[values[1]]
        else:
            cumulative += float(values[1])

    if len(values) > 2:
        raise Exception(f'Found fraction with >2 components: "{s}"')

    return cumulative


def format_universal_ingredient(s):
    egg_pattern = re.compile(
        r'^([\d½¼⅓⅔⅛¾/]+(( | )[\d½¼⅓⅔⅛¾/]+)?) (egg| large eggs egg|egg yolk|egg, beaten| large eggs eggs, beaten| large egg whites egg white)s?$'
    )
    main_pattern = re.compile(
        r'^([\d½¼⅓⅔⅛¾/]+(( | )[\d½¼⅓⅔⅛¾/]+)?) (cup|teaspoon|tablespoon| serving|pound|quart|pinch)s? (.+)$'
    )
    unitless_pattern = re.compile(r'^([\d½¼⅓⅔⅛¾/]+(( | )[\d½¼⅓⅔⅛¾/]+)?) (.+)$')

    s = s.lower()

    for a, b in [
        (', or more to taste', ''),
        (', or more as needed', ''),
        (', or as needed', ''),
        (', or to taste', ''),
        (' to taste', ''),
        (' - divided', ''),
        (', divided', ''),
        (' and divided', ''),
        (' (divided)', ''),
        (' for decoration', ''),
        ('white sugar', 'sugar'),
        ('confectioners\' sugar', 'powdered sugar'),
        ('sifted ', ''),
        (', sifted', ''),
        ('packed brown sugar', 'brown sugar'),
        ('firmly packed brown sugar', 'brown sugar'),
        ('brown sugar, firmly packed', 'brown sugar'),
        ('packed light brown sugar', 'light brown sugar'),
        ('firmly packed dark brown sugar', 'dark brown sugar'),
        ('unsweetened cocoa powder', 'cocoa powder'),
        ('distilled white vinegar', 'white vinegar'),
    ]:
        s = s.replace(a, b)

    egg_match = egg_pattern.match(s)
    main_match = main_pattern.match(s)
    unitless_match = unitless_pattern.match(s)

    if main_match is not None:
        _value, _unit, _food_product = main_match.group(1, 4, 5)

    elif egg_match is not None:
        _value, _food_product = egg_match.group(1, 4)
        _unit = 'unit'
        _food_product = _food_product.replace(' large eggs egg', 'egg').replace(' large egg whites egg white',
                                                                                'egg white').replace(
            ' large eggs eggs, beaten',
            'eggs, beaten')

    elif unitless_match is not None:
        _value, _food_product = unitless_match.group(1, 4)
        _unit = 'unit'

    else:
        _value = '1'
        _unit = 'unit'
        _food_product = s

    _value = convert_to_decimal_from_fraction(_value)

    # todo: figure out all the salt, pepper, and salt and pepper

    if _unit in ['cup', 'teaspoon', 'tablespoon', 'quart', 'pinch']:
        if _unit == 'cup':
            _value *= 236.5
        elif _unit == 'teaspoon':
            _value *= 5
        elif _unit == 'tablespoon':
            _value *= 15
        elif _unit == 'quart':
            _value *= 946
        elif _unit == 'pinch':
            _value *= 0.31

        return round(_value, 4), f'{_food_product} (mL)'

    if _unit in ['pound']:
        _value *= 453.5
        return round(_value, 0), f'{_food_product} (g)'

    if _unit in ['serving', ' serving']:
        return _value, f'{_food_product} (serving)'

    if _unit in ['unit']:
        return _value, f'{_food_product} (unit)'

    raise Exception(f'universal ingredient formatter failed for "{s}", ({_value}, {_unit}, {_food_product})')
