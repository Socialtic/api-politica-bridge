def make_banner(title):
    print()
    print("\t"*5, title)
    print("\t"*5, "-"*len(title))
    print()

# TODO: Pasar header para buscar la columna y no hardcodear indices
def get_professions(row):
    professions = row[16].split(",")
    for profession in row[17:22]:
        professions.append(profession)
    return professions

def get_urls(row):
    return [url for url in row[22:28] if url != ""]

def get_dates(row, indexes):
    return [row[_] for _ in indexes]