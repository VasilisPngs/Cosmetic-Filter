import urllib.request

SOURCES = [
    "https://raw.githubusercontent.com/AdguardTeam/AdguardFilters/master/BaseFilter/sections/adservers.txt",
    "https://raw.githubusercontent.com/AdguardTeam/AdguardFilters/master/BaseFilter/sections/adservers_firstparty.txt",
    "https://raw.githubusercontent.com/AdguardTeam/AdguardFilters/master/BaseFilter/sections/allowlist.txt",
    "https://raw.githubusercontent.com/AdguardTeam/AdguardFilters/master/BaseFilter/sections/allowlist_stealth.txt",
    "https://raw.githubusercontent.com/AdguardTeam/AdguardFilters/master/BaseFilter/sections/antiadblock.txt",
    "https://raw.githubusercontent.com/AdguardTeam/AdguardFilters/master/BaseFilter/sections/banner_sizes.txt",
    "https://raw.githubusercontent.com/AdguardTeam/AdguardFilters/master/BaseFilter/sections/content_blocker.txt",
    "https://raw.githubusercontent.com/AdguardTeam/AdguardFilters/master/BaseFilter/sections/cryptominers.txt",
    "https://raw.githubusercontent.com/AdguardTeam/AdguardFilters/master/BaseFilter/sections/foreign.txt",
    "https://raw.githubusercontent.com/AdguardTeam/AdguardFilters/master/BaseFilter/sections/general_elemhide.txt",
    "https://raw.githubusercontent.com/AdguardTeam/AdguardFilters/master/BaseFilter/sections/general_extensions.txt",
    "https://raw.githubusercontent.com/AdguardTeam/AdguardFilters/master/BaseFilter/sections/general_url.txt",
    "https://raw.githubusercontent.com/AdguardTeam/AdguardFilters/master/BaseFilter/sections/replace.txt",
    "https://raw.githubusercontent.com/AdguardTeam/AdguardFilters/master/BaseFilter/sections/specific.txt",
    "https://raw.githubusercontent.com/kargig/greek-adblockplus-filter/master/void-gr-filters.txt"
]

def fetch_data(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return response.read().decode("utf-8", errors="replace").splitlines()
    except Exception:
        return []

rules = set()

for url in SOURCES:
    for line in fetch_data(url):
        line = line.strip()
        if not line or line.startswith("!"):
            continue
        if line.startswith("||"):
            continue
        rules.add(line)

with open("cosmetic.txt", "w", encoding="utf-8", newline="\n") as f:
    f.writelines(r + "\n" for r in sorted(rules))
