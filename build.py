import re
import urllib.request
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import lru_cache

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
    "https://raw.githubusercontent.com/kargig/greek-adblockplus-filter/master/void-gr-filters.txt",
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

TOKEN_RE = re.compile(r"&&|\|\||!|\(|\)|[A-Za-z_][A-Za-z0-9_]*")


def eval_condition(expr):
    expr = re.sub(r"\s+", "", expr)
    tokens = TOKEN_RE.findall(expr)

    def parse_or(pos):
        value, pos = parse_and(pos)
        while pos < len(tokens) and tokens[pos] == "||":
            rhs, pos = parse_and(pos + 1)
            value = value or rhs
        return value, pos

    def parse_and(pos):
        value, pos = parse_unary(pos)
        while pos < len(tokens) and tokens[pos] == "&&":
            rhs, pos = parse_unary(pos + 1)
            value = value and rhs
        return value, pos

    def parse_unary(pos):
        if pos < len(tokens) and tokens[pos] == "!":
            value, pos = parse_unary(pos + 1)
            return not value, pos
        return parse_primary(pos)

    def parse_primary(pos):
        if pos >= len(tokens):
            return False, pos
        token = tokens[pos]
        if token == "(":
            value, pos = parse_or(pos + 1)
            if pos < len(tokens) and tokens[pos] == ")":
                return value, pos + 1
            return False, pos
        if token in PLATFORMS:
            return True, pos + 1
        return False, pos + 1

    try:
        value, pos = parse_or(0)
        return value and pos == len(tokens)
    except Exception:
        return False


@lru_cache(maxsize=None)
def _fetch_data(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as response:
        return tuple(response.read().decode("utf-8", errors="replace").splitlines())

def fetch_data(url):
    try:
        return _fetch_data(url)
    except Exception:
        return tuple()


def process_source(url, rules, visited):
    if url in visited:
        return
    visited.add(url)

    active = [True]
    condition_stack = []

    for raw_line in fetch_data(url):
        stripped = raw_line.strip()
        if not stripped:
            continue
        if stripped.startswith("!#if"):
            condition = stripped[4:].strip()
            condition_value = eval_condition(condition)
            condition_stack.append(condition_value)
            active.append(active[-1] and condition_value)
            continue
        if stripped.startswith("!#else"):
            if len(active) > 1 and condition_stack:
                active[-1] = active[-2] and (not condition_stack[-1])
            continue
        if stripped.startswith("!#endif"):
            if len(active) > 1:
                active.pop()
            if condition_stack:
                condition_stack.pop()
            continue
        if stripped.startswith("!#include"):
            if active[-1]:
                include_target = stripped[len("!#include"):].strip()
                if include_target:
                    include_url = urljoin(url, include_target)
                    process_source(include_url, rules, visited)
            continue
        if stripped.startswith("!"):
            continue
        if not active[-1]:
            continue
        if stripped.startswith("||") or stripped.startswith("@@||"):
            continue
        rules.add(stripped)


def process_source_safe(url):
    local_rules = set()
    process_source(url, local_rules, set())
    return local_rules


rules = set()

with ThreadPoolExecutor(max_workers=8) as executor:
    futures = {executor.submit(process_source_safe, url): url for url in SOURCES}
    for future in as_completed(futures):
        rules.update(future.result())

with open("cosmetic.txt", "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(sorted(rules)) + "\n")
