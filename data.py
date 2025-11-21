import json


def get_data(
    file_path: str = "data.json", film_id: int | None = None
) -> list[dict] | dict:
    with open(file_path, "r") as fp:
        films = json.load(fp)
        if film_id != None and film_id < len(films):
            return films[film_id]
        return films


def add_data(film: dict, file_path: str = "data.json"):
    films = get_data(file_path=file_path, film_id=None)
    if films:
        films.append(film)
        with open(file_path, "w") as fp:
            json.dump(films, fp, indent=4, ensure_ascii=False)


def get_film_name(name: str, file_path: str = "data.json"):
    films = get_data(file_path=file_path)
    for category in films:
        for x, items in category.items():
            if x == name:
                return items


if __name__ == "__main__":
    print(get_data(film_id=1))

