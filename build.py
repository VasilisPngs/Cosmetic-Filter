import urllib.request

GLOBAL_SOURCES = [
    "https://raw.githubusercontent.com/AdguardTeam/AdguardFilters/master/BaseFilter/sections/allowlist.txt",
    "https://raw.githubusercontent.com/AdguardTeam/AdguardFilters/master/BaseFilter/sections/allowlist_stealth.txt",
    "https://raw.githubusercontent.com/AdguardTeam/AdguardFilters/master/BaseFilter/sections/antiadblock.txt",
    "https://raw.githubusercontent.com/AdguardTeam/AdguardFilters/master/BaseFilter/sections/banner_sizes.txt",
    "https://raw.githubusercontent.com/AdguardTeam/AdguardFilters/master/BaseFilter/sections/general_elemhide.txt",
    "https://raw.githubusercontent.com/AdguardTeam/AdguardFilters/master/BaseFilter/sections/general_extensions.txt",
    "https://raw.githubusercontent.com/AdguardTeam/AdguardFilters/master/BaseFilter/sections/specific.txt"
]

LOCAL_SOURCES = [
    "https://www.void.gr/kargig/void-gr-filters.txt"
]

def fetch_data(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req) as response:
            return response.read().decode('utf-8').splitlines()
    except:
        return []

final_rules = set()

# 1. Global Sources: Keep strictly Cosmetic / DOM rules
for url in GLOBAL_SOURCES:
    for line in fetch_data(url):
        line = line.strip()
        if not line or line.startswith('!'):
            continue
        if '##' in line or '#?#' in line or '#@#' in line or '#%#' in line:
            final_rules.add(line)

# 2. Local Sources (Greek): Keep EVERYTHING (Network + Cosmetic)
for url in LOCAL_SOURCES:
    for line in fetch_data(url):
        line = line.strip()
        if not line or line.startswith('!'):
            continue
        final_rules.add(line)

final_list = sorted(list(final_rules))

with open("cosmetic.txt", "w", encoding="utf-8") as f:
    for r in final_list:
        f.write(f"{r}\n")
