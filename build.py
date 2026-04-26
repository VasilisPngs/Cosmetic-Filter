import urllib.request
import re

SOURCES_BASE = [
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

PLATFORMS = {
    "adguard",
    "adguard_app_windows",
    "adguard_app_mac",
    "adguard_app_android",
    "adguard_app_ios",
    "adguard_app_cli",
    "adguard_ext_safari",
    "adguard_ext_chromium",
    "adguard_ext_chromium_mv3",
    "adguard_ext_firefox",
    "adguard_ext_edge",
    "adguard_ext_opera",
    "adguard_ext_android_cb",
    "cap_html_filtering",
}

def eval_condition(expr):
    expr = expr.strip()
    if expr.startswith("(") and expr.endswith(")"):
        expr = expr[1:-1].strip()
    if "||" in expr:
        return any(eval_condition(p) for p in expr.split("||"))
    if "&&" in expr:
        return all(eval_condition(p) for p in expr.split("&&"))
    if expr.startswith("!"):
        return not eval_condition(expr[1:])
    return expr.strip() in PLATFORMS

def fetch_data(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return response.read().decode("utf-8", errors="replace").splitlines()
    except Exception:
        return []

def parse_lines(lines):
    result = []
    active = [True]
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("!#if "):
            active.append(eval_condition(stripped[5:]))
        elif stripped.startswith("!#else"):
            if len(active) > 1:
                active[-1] = not active[-1]
        elif stripped.startswith("!#endif"):
            if len(active) > 1:
                active.pop()
        elif all(active):
            result.append(stripped)
    return result

rules = set()

for url in SOURCES_BASE:
    for line in parse_lines(fetch_data(url)):
        if not line or line.startswith("!"):
            continue
        if line.startswith("||"):
            continue
        rules.add(line)

with open("cosmetic.txt", "w", encoding="utf-8", newline="\n") as f:
    f.writelines(r + "\n" for r in sorted(rules))
