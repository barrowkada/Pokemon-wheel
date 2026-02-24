#!/usr/bin/env python3
"""
Generate pokemon-data.js from PokéAPI CSV data.
Downloads CSV files from the PokéAPI GitHub repository and processes them
into a JavaScript data file for the Pokémon Slot Machine app.
"""

import csv
import io
import json
import urllib.request
import sys
from collections import defaultdict

BASE_URL = "https://raw.githubusercontent.com/PokeAPI/pokeapi/master/data/v2/csv"

CSV_FILES = [
    "pokemon.csv",
    "pokemon_species.csv",
    "pokemon_stats.csv",
    "pokemon_types.csv",
    "pokemon_abilities.csv",
    "pokemon_forms.csv",
    "pokemon_colors.csv",
    "types.csv",
    "abilities.csv",
    "ability_names.csv",
    "type_names.csv",
    "pokemon_form_names.csv",
    "pokemon_species_names.csv",
    "pokemon_species_flavor_text.csv",
    "growth_rates.csv",
    "growth_rate_prose.csv",
]

# Gen 9 max species ID (through Pecharunt #1025)
MAX_SPECIES_ID = 1025

# Stat ID mapping from PokéAPI
STAT_ORDER = {1: "hp", 2: "atk", 3: "def", 4: "spa", 5: "spd", 6: "spe"}

# English language ID in PokéAPI
ENGLISH_LANG_ID = "9"


def download_csv(filename):
    """Download a CSV file from PokéAPI GitHub and return parsed rows."""
    url = f"{BASE_URL}/{filename}"
    print(f"  Downloading {filename}...", end=" ", flush=True)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "PokemonWheelGenerator/1.0"})
        with urllib.request.urlopen(req, timeout=30) as response:
            content = response.read().decode("utf-8")
        reader = csv.DictReader(io.StringIO(content))
        rows = list(reader)
        print(f"({len(rows)} rows)")
        return rows
    except Exception as e:
        print(f"FAILED: {e}")
        return []


def title_case_pokemon(name):
    """Convert pokemon identifier to display name."""
    # Handle special cases
    special = {
        "nidoran-f": "Nidoran♀",
        "nidoran-m": "Nidoran♂",
        "mr-mime": "Mr. Mime",
        "mr-rime": "Mr. Rime",
        "mime-jr": "Mime Jr.",
        "type-null": "Type: Null",
        "jangmo-o": "Jangmo-o",
        "hakamo-o": "Hakamo-o",
        "kommo-o": "Kommo-o",
        "tapu-koko": "Tapu Koko",
        "tapu-lele": "Tapu Lele",
        "tapu-bulu": "Tapu Bulu",
        "tapu-fini": "Tapu Fini",
        "ho-oh": "Ho-Oh",
        "porygon-z": "Porygon-Z",
        "flabebe": "Flabébé",
        "chi-yu": "Chi-Yu",
        "chien-pao": "Chien-Pao",
        "ting-lu": "Ting-Lu",
        "wo-chien": "Wo-Chien",
        "great-tusk": "Great Tusk",
        "scream-tail": "Scream Tail",
        "brute-bonnet": "Brute Bonnet",
        "flutter-mane": "Flutter Mane",
        "slither-wing": "Slither Wing",
        "sandy-shocks": "Sandy Shocks",
        "iron-treads": "Iron Treads",
        "iron-bundle": "Iron Bundle",
        "iron-hands": "Iron Hands",
        "iron-jugulis": "Iron Jugulis",
        "iron-moth": "Iron Moth",
        "iron-thorns": "Iron Thorns",
        "roaring-moon": "Roaring Moon",
        "iron-valiant": "Iron Valiant",
        "walking-wake": "Walking Wake",
        "iron-leaves": "Iron Leaves",
        "gouging-fire": "Gouging Fire",
        "raging-bolt": "Raging Bolt",
        "iron-boulder": "Iron Boulder",
        "iron-crown": "Iron Crown",
    }
    if name in special:
        return special[name]
    # Default: capitalize each word
    return " ".join(w.capitalize() for w in name.split("-"))


def format_form_name(form_identifier, pokemon_name, form_names_map, form_id):
    """Generate a display-friendly form name."""
    # Check if we have a proper display name from form_names
    if form_id in form_names_map:
        return form_names_map[form_id]

    if not form_identifier:
        return ""

    # Common form patterns
    form_lower = form_identifier.lower()

    form_map = {
        "mega": "Mega",
        "mega-x": "Mega X",
        "mega-y": "Mega Y",
        "alola": "Alolan",
        "galar": "Galarian",
        "hisui": "Hisuian",
        "paldea": "Paldean",
        "gmax": "Gigantamax",
        "primal": "Primal",
        "origin": "Origin Forme",
        "sky": "Sky Forme",
        "land": "Land Forme",
        "altered": "Altered Forme",
        "attack": "Attack Forme",
        "defense": "Defense Forme",
        "speed": "Speed Forme",
        "normal": "Normal Forme",
        "heat": "Heat",
        "wash": "Wash",
        "frost": "Frost",
        "fan": "Fan",
        "mow": "Mow",
        "sandy": "Sandy Cloak",
        "trash": "Trash Cloak",
        "plant": "Plant Cloak",
        "sunshine": "Sunshine Form",
        "overcast": "Overcast Form",
        "east": "East Sea",
        "west": "West Sea",
        "spring": "Spring Form",
        "summer": "Summer Form",
        "autumn": "Autumn Form",
        "winter": "Winter Form",
        "incarnate": "Incarnate Forme",
        "therian": "Therian Forme",
        "black": "Black Kyurem",
        "white": "White Kyurem",
        "resolute": "Resolute Form",
        "aria": "Aria Forme",
        "pirouette": "Pirouette Forme",
        "confined": "Confined",
        "unbound": "Unbound",
        "10": "10% Forme",
        "50": "50% Forme",
        "complete": "Complete Forme",
        "baile": "Baile Style",
        "pom-pom": "Pom-Pom Style",
        "pau": "Pa'u Style",
        "sensu": "Sensu Style",
        "midday": "Midday Form",
        "midnight": "Midnight Form",
        "dusk": "Dusk Form",
        "solo": "Solo Form",
        "school": "School Form",
        "dawn-wings": "Dawn Wings",
        "dusk-mane": "Dusk Mane",
        "ultra": "Ultra",
        "single-strike": "Single Strike Style",
        "rapid-strike": "Rapid Strike Style",
        "ice": "Ice Rider",
        "shadow": "Shadow Rider",
        "bloodmoon": "Blood Moon",
        "cornerstone": "Cornerstone Mask",
        "hearthflame": "Hearthflame Mask",
        "wellspring": "Wellspring Mask",
        "teal": "Teal Mask",
        "stellar": "Stellar Form",
        "terastal": "Terastal Form",
        "low-key": "Low Key Form",
        "amped": "Amped Form",
        "gulping": "Gulping Form",
        "gorging": "Gorging Form",
        "noice": "Noice Face",
        "ice-face": "Ice Face",
        "hangry": "Hangry Mode",
        "crowned": "Crowned",
        "eternamax": "Eternamax",
        "hero": "Hero of Many Battles",
        "blue-striped": "Blue-Striped Form",
        "red-striped": "Red-Striped Form",
        "white-striped": "White-Striped Form",
        "female": "Female",
        "male": "Male",
        "curly": "Curly Form",
        "droopy": "Droopy Form",
        "stretchy": "Stretchy Form",
        "three-segment": "Three-Segment Form",
        "two-segment": "Two-Segment Form",
        "family-of-three": "Family of Three",
        "family-of-four": "Family of Four",
        "roaming": "Roaming Form",
        "zero": "Zero Form",
    }

    if form_lower in form_map:
        return form_map[form_lower]

    # Default: title case the form identifier
    return " ".join(w.capitalize() for w in form_identifier.split("-"))


def main():
    print("=== Pokémon Data Generator ===\n")
    print("Downloading CSV data from PokéAPI GitHub...\n")

    # Download all CSVs
    data = {}
    for f in CSV_FILES:
        data[f] = download_csv(f)
        if not data[f]:
            print(f"WARNING: Failed to download {f}, continuing...")

    print("\nProcessing data...\n")

    # Build lookup tables
    # Species: id -> {generation_id, color_id, identifier, capture_rate, base_happiness, growth_rate_id}
    species_map = {}
    for row in data["pokemon_species.csv"]:
        sid = int(row["id"])
        if sid <= MAX_SPECIES_ID:
            species_map[sid] = {
                "gen": int(row["generation_id"]),
                "color_id": int(row["color_id"]),
                "name": row["identifier"],
                "capture_rate": int(row.get("capture_rate", 0)),
                "base_happiness": int(row.get("base_happiness", 0) or 0),
                "growth_rate_id": int(row.get("growth_rate_id", 1)),
            }

    # Colors: id -> name
    color_map = {}
    for row in data["pokemon_colors.csv"]:
        color_map[int(row["id"])] = row["identifier"]

    # Types: id -> name
    type_map = {}
    for row in data["types.csv"]:
        type_map[int(row["id"])] = row["identifier"]

    # Type display names (English)
    type_display = {}
    for row in data["type_names.csv"]:
        if row["local_language_id"] == ENGLISH_LANG_ID:
            type_display[int(row["type_id"])] = row["name"]

    # Abilities: id -> identifier
    ability_id_map = {}
    for row in data["abilities.csv"]:
        ability_id_map[int(row["id"])] = row["identifier"]

    # Ability display names (English)
    ability_display = {}
    for row in data["ability_names.csv"]:
        if row["local_language_id"] == ENGLISH_LANG_ID:
            ability_display[int(row["ability_id"])] = row["name"]

    # Pokemon: id -> {species_id, height, weight, identifier, is_default, base_experience}
    pokemon_map = {}
    for row in data["pokemon.csv"]:
        pid = int(row["id"])
        species_id = int(row["species_id"])
        if species_id <= MAX_SPECIES_ID:
            pokemon_map[pid] = {
                "species_id": species_id,
                "height": int(row["height"]),
                "weight": int(row["weight"]),
                "identifier": row["identifier"],
                "is_default": row["is_default"] == "1",
                "base_experience": int(row.get("base_experience", 0) or 0),
            }

    # Stats: pokemon_id -> {hp, atk, def, spa, spd, spe}
    stats_map = defaultdict(dict)
    for row in data["pokemon_stats.csv"]:
        pid = int(row["pokemon_id"])
        stat_id = int(row["stat_id"])
        if pid in pokemon_map and stat_id in STAT_ORDER:
            stats_map[pid][STAT_ORDER[stat_id]] = int(row["base_stat"])

    # Types: pokemon_id -> [type1, type2]
    types_map = defaultdict(list)
    for row in data["pokemon_types.csv"]:
        pid = int(row["pokemon_id"])
        if pid in pokemon_map:
            type_id = int(row["type_id"])
            slot = int(row["slot"])
            type_name = type_display.get(type_id, type_map.get(type_id, "Unknown"))
            types_map[pid].append((slot, type_name))
    # Sort by slot
    for pid in types_map:
        types_map[pid].sort(key=lambda x: x[0])
        types_map[pid] = [t[1] for t in types_map[pid]]

    # Abilities: pokemon_id -> [ability_names]
    abilities_map = defaultdict(list)
    for row in data["pokemon_abilities.csv"]:
        pid = int(row["pokemon_id"])
        if pid in pokemon_map:
            aid = int(row["ability_id"])
            is_hidden = row["is_hidden"] == "1"
            slot = int(row["slot"])
            name = ability_display.get(aid, ability_id_map.get(aid, "Unknown"))
            abilities_map[pid].append((slot, name, is_hidden))
    for pid in abilities_map:
        abilities_map[pid].sort(key=lambda x: x[0])
        abilities_map[pid] = [a[1] for a in abilities_map[pid]]

    # Forms: pokemon_id -> {form_identifier, form_name, is_battle_only, is_mega}
    forms_map = {}
    for row in data["pokemon_forms.csv"]:
        pid = int(row["pokemon_id"])
        if pid in pokemon_map:
            form_id = int(row["id"])
            forms_map[pid] = {
                "form_id": form_id,
                "form_identifier": row.get("form_identifier", ""),
                "is_battle_only": row.get("is_battle_only", "0") == "1",
                "is_mega": row.get("is_mega", "0") == "1",
            }

    # Form display names (English)
    form_names_map = {}
    for row in data["pokemon_form_names.csv"]:
        if row["local_language_id"] == ENGLISH_LANG_ID:
            fid = int(row["pokemon_form_id"])
            name = row.get("pokemon_name", "") or row.get("form_name", "")
            if name:
                form_names_map[fid] = name

    # Genus (category): species_id -> English genus (e.g. "Seed Pokémon")
    genus_map = {}
    for row in data["pokemon_species_names.csv"]:
        if row["local_language_id"] == ENGLISH_LANG_ID:
            sid = int(row["pokemon_species_id"])
            genus = row.get("genus", "")
            if genus and sid <= MAX_SPECIES_ID:
                genus_map[sid] = genus

    # Flavor text: species_id -> English flavor text (latest version)
    # We pick the entry with the highest version_id for each species
    flavor_text_raw = defaultdict(list)
    for row in data["pokemon_species_flavor_text.csv"]:
        if row["language_id"] == ENGLISH_LANG_ID:
            sid = int(row["species_id"])
            if sid <= MAX_SPECIES_ID:
                version_id = int(row["version_id"])
                text = row.get("flavor_text", "")
                if text:
                    flavor_text_raw[sid].append((version_id, text))
    flavor_text_map = {}
    for sid, entries in flavor_text_raw.items():
        # Pick the latest version's text and clean it up
        entries.sort(key=lambda x: x[0], reverse=True)
        text = entries[0][1]
        # PokéAPI flavor text has form feeds and newlines embedded
        text = text.replace("\f", " ").replace("\n", " ").replace("\r", " ")
        # Collapse multiple spaces
        text = " ".join(text.split())
        flavor_text_map[sid] = text

    # Growth rates: growth_rate_id -> English name
    growth_rate_map = {}
    for row in data["growth_rate_prose.csv"]:
        if row["local_language_id"] == ENGLISH_LANG_ID:
            gid = int(row["growth_rate_id"])
            growth_rate_map[gid] = row["name"]
    # Fallback from growth_rates.csv identifiers
    if not growth_rate_map:
        for row in data["growth_rates.csv"]:
            gid = int(row["id"])
            name = " ".join(w.capitalize() for w in row["identifier"].split("-"))
            growth_rate_map[gid] = name

    # Build the final Pokémon list
    print("Building Pokémon entries...\n")

    pokemon_list = []
    skipped_battle_only = 0
    skipped_no_stats = 0

    # Forms/variants to exclude (cosmetic only, battle-only transforms, or totem)
    # We keep most forms but exclude purely battle-only transformations
    # that don't have distinct visual identities worth showcasing
    EXCLUDE_FORM_PATTERNS = [
        "totem",  # Totem Pokémon (just bigger versions)
        "starter",  # Starter Pikachu
        "busted",  # Mimikyu busted (in-battle only)
        "power-construct",  # Zygarde power construct
    ]

    for pid in sorted(pokemon_map.keys()):
        pdata = pokemon_map[pid]
        species_id = pdata["species_id"]

        if species_id not in species_map:
            continue

        sdata = species_map[species_id]

        # Get form info
        form_info = forms_map.get(pid, {})
        form_identifier = form_info.get("form_identifier", "")
        is_battle_only = form_info.get("is_battle_only", False)
        form_id = form_info.get("form_id", pid)

        # Skip battle-only forms (in-battle transformations)
        if is_battle_only:
            skipped_battle_only += 1
            continue

        # Skip excluded form patterns
        skip = False
        for pattern in EXCLUDE_FORM_PATTERNS:
            if pattern in form_identifier.lower():
                skip = True
                break
        if skip:
            continue

        # Get stats
        stats = stats_map.get(pid, {})
        if not stats or len(stats) < 6:
            skipped_no_stats += 1
            continue

        # Get types
        types = types_map.get(pid, ["Normal"])

        # Get abilities
        abilities = abilities_map.get(pid, [])

        # Get form display name
        form_display = format_form_name(
            form_identifier, sdata["name"], form_names_map, form_id
        )

        # Get species display name
        species_name = title_case_pokemon(sdata["name"])

        # Color
        color = color_map.get(sdata["color_id"], "white")

        entry = {
            "id": pid,
            "name": species_name,
            "form": form_display,
            "dex": species_id,
            "gen": sdata["gen"],
            "types": types,
            "stats": [
                stats.get("hp", 0),
                stats.get("atk", 0),
                stats.get("def", 0),
                stats.get("spa", 0),
                stats.get("spd", 0),
                stats.get("spe", 0),
            ],
            "abilities": abilities,
            "height": pdata["height"],
            "weight": pdata["weight"],
            "color": color,
            "category": genus_map.get(species_id, ""),
            "description": flavor_text_map.get(species_id, ""),
            "catchRate": sdata["capture_rate"],
            "baseHappiness": sdata["base_happiness"],
            "baseExp": pdata["base_experience"],
            "growthRate": growth_rate_map.get(sdata["growth_rate_id"], ""),
        }

        pokemon_list.append(entry)

    print(f"Total Pokémon entries: {len(pokemon_list)}")
    print(f"Skipped (battle-only): {skipped_battle_only}")
    print(f"Skipped (no stats): {skipped_no_stats}")

    # Count by generation
    gen_counts = defaultdict(int)
    for p in pokemon_list:
        gen_counts[p["gen"]] += 1
    for g in sorted(gen_counts.keys()):
        print(f"  Gen {g}: {gen_counts[g]}")

    # Write the JS file
    output_path = "/home/user/Pokemon-wheel/js/pokemon-data.js"
    print(f"\nWriting to {output_path}...")

    js_content = "// Auto-generated Pokémon data - DO NOT EDIT MANUALLY\n"
    js_content += f"// Generated from PokéAPI CSV data\n"
    js_content += f"// Total entries: {len(pokemon_list)}\n\n"
    js_content += "const POKEMON_DATA = "
    js_content += json.dumps(pokemon_list, separators=(",", ":"))
    js_content += ";\n"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(js_content)

    file_size = len(js_content) / 1024
    print(f"File size: {file_size:.1f} KB")
    print("\nDone!")


if __name__ == "__main__":
    main()
