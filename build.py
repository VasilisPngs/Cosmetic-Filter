import urllib.request

SOURCES = [
    "https://raw.githubusercontent.com/AdguardTeam/AdguardFilters/master/BaseFilter/sections/general_elemhide.txt",
    "https://raw.githubusercontent.com/AdguardTeam/AdguardFilters/master/BaseFilter/sections/specific.txt",
    "https://raw.githubusercontent.com/AdguardTeam/AdguardFilters/master/BaseFilter/sections/banner_sizes.txt",
    "https://raw.githubusercontent.com/AdguardTeam/AdguardFilters/master/BaseFilter/sections/antiadblock.txt",
    "https://raw.githubusercontent.com/AdguardTeam/AdguardFilters/master/BaseFilter/sections/general_extensions.txt",
    "https://www.void.gr/kargig/void-gr-filters.txt"
]

def fetch_data(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as response:
        return response.read().decode('utf-8').splitlines()

cosmetic_rules = set()

for url in SOURCES:
    try:
        for line in fetch_data(url):
            line = line.strip()
            if not line or line.startswith('!'):
                continue
            if '##' in line or '#?#' in line or '#@#' in line or '#%#' in line:
                cosmetic_rules.add(line)
    except:
        pass

final_list = sorted(list(cosmetic_rules))

with open("cosmetic.txt", "w", encoding="utf-8") as f:
    for r in final_list:
        f.write(f"{r}\n")
