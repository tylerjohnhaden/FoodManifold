from library.all_recipes import crawl_for_all_recipe_ids


def main():
    with open('urls_with_all_recipe_ids.txt') as url_file:
        crawled_ids = crawl_for_all_recipe_ids(line.strip() for line in url_file.readlines())

    print(crawled_ids)


if __name__ == '__main__':
    main()
