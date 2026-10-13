"""Deterministic query normalization for hybrid product search.

This module is dependency-light so the alias/parser layer can be unit-tested
without loading the encoder or opening a database connection.
"""
from __future__ import annotations

import re


_CATEGORY_ALIASES: tuple[tuple[str, str], ...] = (
    ("casual shoes", "Casual Shoes"),
    ("giày thường ngày", "Casual Shoes"),
    ("giày đi chơi", "Casual Shoes"),
    ("sports shoes", "Sports Shoes"),
    ("running shoes", "Sports Shoes"),
    ("giày chạy bộ", "Sports Shoes"),
    ("giày thể thao", "Sports Shoes"),
    ("dép xăng đan", "Sandals"),
    ("sandals", "Sandals"),
    ("sandal", "Sandals"),
    ("tee shirt", "T-Shirt"),
    ("t-shirt", "T-Shirt"),
    ("t shirt", "T-Shirt"),
    ("tshirt", "T-Shirt"),
    ("áo thun", "T-Shirt"),
    ("áo hoodie", "Sweatshirt"),
    ("sweatshirt", "Sweatshirt"),
    ("hoodie", "Sweatshirt"),
    ("áo nỉ", "Sweatshirt"),
    ("pullover", "Sweatshirt"),
    ("jacket", "Jacket"),
    ("áo khoác", "Jacket"),
    ("polo shirt", "Polo"),
    ("áo polo", "Polo"),
    ("polo", "Polo"),
)

# The patterns are used for matching aliases in the query; the second value is
# the canonical English term fed to the text encoder.
_COLOR_ALIASES: tuple[tuple[str, str], ...] = (
    ("off-white", "White"),
    ("off white", "White"),
    ("navy blue", "Blue"),
    ("light blue", "Blue"),
    ("dark blue", "Blue"),
    ("xanh dương", "Blue"),
    ("xanh biển", "Blue"),
    ("xanh lá cây", "Green"),
    ("xanh lá", "Green"),
    ("black", "Black"),
    ("đen", "Black"),
    ("white", "White"),
    ("trắng", "White"),
    ("blue", "Blue"),
    ("xám", "Grey"),
    ("grey", "Grey"),
    ("gray", "Grey"),
    ("brown", "Brown"),
    ("nâu", "Brown"),
    ("green", "Green"),
    ("red", "Red"),
    ("đỏ", "Red"),
    ("pink", "Pink"),
    ("hồng", "Pink"),
    ("yellow", "Yellow"),
    ("vàng", "Yellow"),
    ("orange", "Orange"),
    ("cam", "Orange"),
    ("purple", "Purple"),
    ("tím", "Purple"),
    ("navy", "Navy"),
    ("beige", "Beige"),
    ("kem", "Beige"),
)

# The dataset intentionally contains only these product types. If a user
# explicitly asks for one of these known unsupported types without also asking
# for a supported type, return no results instead of presenting unrelated items.
_UNSUPPORTED_TYPE_ALIASES: tuple[str, ...] = (
    "sunglasses", "handbag", "backpack", "trousers", "jeans", "shorts",
    "skirts", "skirt", "dresses", "dress", "watches", "watch", "bags", "bag",
    "quần jean", "quần jeans", "quần short", "quần shorts", "quần tây",
    "váy", "đầm", "túi xách", "ba lô", "balo", "kính râm", "đồng hồ",
    "mũ", "nón",
)

_COLOR_FILTER_PATTERNS: dict[str, tuple[str, ...]] = {
    "Black": ("black",),
    "White": ("white", "off-white", "off white"),
    "Blue": ("blue",),
    "Navy": ("navy",),
    "Grey": ("grey", "gray"),
    "Brown": ("brown",),
    "Green": ("green",),
    "Red": ("red",),
    "Pink": ("pink",),
    "Yellow": ("yellow",),
    "Orange": ("orange",),
    "Purple": ("purple",),
    "Beige": ("beige", "cream"),
}


def _alias_matches(
    query: str,
    aliases: tuple[tuple[str, str], ...],
    kind: str,
) -> list[tuple[int, int, str, str]]:
    """Select longest non-overlapping alias matches from the original query."""
    source = query.casefold()
    candidates: list[tuple[int, int, str, str]] = []
    for alias, canonical in sorted(aliases, key=lambda item: len(item[0]), reverse=True):
        pattern = re.compile(rf"(?<!\w){re.escape(alias.casefold())}(?!\w)")
        for match in pattern.finditer(source):
            candidates.append((match.start(), match.end(), canonical, kind))

    selected: list[tuple[int, int, str, str]] = []
    for candidate in sorted(candidates, key=lambda item: (-(item[1] - item[0]), item[0])):
        start, end, _, _ = candidate
        if any(start < chosen_end and end > chosen_start for chosen_start, chosen_end, _, _ in selected):
            continue
        selected.append(candidate)
    return sorted(selected, key=lambda item: item[0])


def _matched_unsupported_type(query: str) -> str | None:
    source = query.casefold()
    for alias in sorted(_UNSUPPORTED_TYPE_ALIASES, key=len, reverse=True):
        if re.search(rf"(?<!\w){re.escape(alias.casefold())}(?!\w)", source):
            return alias
    return None


def normalize_search_query(query: str) -> dict[str, str | None]:
    """Normalize common query aliases and infer precise taxonomy/color intent.

    Returns ``normalized_query``, ``category``, ``color`` and ``unsupported_type``.
    An intent is inferred only when exactly one distinct canonical value is found;
    ambiguous multi-category/color queries are left to semantic ranking instead
    of being over-filtered.
    """
    query = query.strip()
    matches = _alias_matches(query, _CATEGORY_ALIASES, "category")
    matches += _alias_matches(query, _COLOR_ALIASES, "color")
    matches.sort(key=lambda item: (item[0], item[1]))

    categories = {value for _, _, value, kind in matches if kind == "category"}
    colors = {value for _, _, value, kind in matches if kind == "color"}
    category = next(iter(categories)) if len(categories) == 1 else None
    color = next(iter(colors)) if len(colors) == 1 else None

    # Replace recognized words/phrases with canonical English labels before
    # embedding. Keep any unrecognized descriptive words in the query.
    parts: list[str] = []
    cursor = 0
    for start, end, canonical, _kind in matches:
        if start < cursor:
            continue
        parts.append(query[cursor:start])
        parts.append(canonical.lower())
        cursor = end
    parts.append(query[cursor:])
    normalized = "".join(parts)
    normalized = re.sub(r"(?<!\w)(?:màu|áo|đôi|giày|tìm kiếm|tìm|cho tôi|tôi muốn)(?!\w)", " ", normalized, flags=re.IGNORECASE)
    normalized = re.sub(r"\s+", " ", normalized).strip(" ,.;:!?\t\r\n")
    if not normalized:
        normalized = query

    # A known unsupported type is actionable only when the query does not also
    # clearly mention an in-scope type (e.g. “jacket to wear with jeans”).
    unsupported_type = None
    if category is None:
        unsupported_type = _matched_unsupported_type(query)

    return {
        "normalized_query": normalized,
        "category": category,
        "color": color,
        "unsupported_type": unsupported_type,
    }


