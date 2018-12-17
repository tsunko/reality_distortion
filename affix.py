import json
from enum import Enum, unique
from random import randint
from typing import List, Tuple
from numpy.random import choice
import numpy


@unique
class Element(Enum):
    FIRE = "Fire"
    LIGHTNING = "Lightning"
    ICE = "Ice"

    def __str__(self):
        return self.value


class Affix:
    def __init__(self, name, parent, tier: int, element: Element or None,
                 roll_range: tuple or Tuple[tuple, tuple]):
        self.name = name
        self.parent = parent
        self.tier = tier
        self.element = element
        self.roll_range = roll_range

    def has_dual_rolls(self) -> bool:
        return isinstance(self.roll_range[0], tuple)

    def get_display_string(self, data: tuple or Tuple[tuple, tuple]) -> str:
        if self.has_dual_rolls():
            if not hasattr(data, "__len__") or len(data) != 2:
                raise ValueError("roll range type != data type; data[0] was an int?")
            return "Adds %d to %d %s" % (data[0], data[1], self.parent.friendly_name)
        else:
            if self.parent.is_percent:
                return "%d%% %s" % (data, str(self.parent))
            else:
                return "+%d to %s" % (data, str(self.parent))

    def __repr__(self):
        return "(parent=%s, tier=%d, element=%s, roll_range=%s)" % \
               (self.parent.group_name, self.tier, self.element, self.roll_range)


class AffixGroup:
    def __init__(self, group_name: str, friendly_name: str, is_percent: bool, is_prefix: bool, weighting: float):
        self.group_name = group_name
        self.friendly_name = friendly_name
        self.is_percent = is_percent
        self.is_prefix = is_prefix
        self.weighting = weighting
        self.affixes = list()

    def __repr__(self):
        as_str = "%s, weighting=%d,\r\n" % (self.group_name, self.weighting)
        for affix in self.affixes:
            as_str += "\t%s\r\n" % affix
        return as_str

    def __str__(self):
        return self.friendly_name


class AffixDatabase:
    def __init__(self):
        self.prefixes = list()
        self.suffixes = list()

    def load_file(self, db_file: str):
        file = None
        try:
            file = open(db_file)
            obj = json.load(file)

            self.prefixes.clear()
            self.suffixes.clear()

            parse_section(obj, "prefixes", self.prefixes, True)
            parse_section(obj, "suffixes", self.suffixes, False)
        finally:
            if file is not None:
                file.close()

    def get_random_mods(self, is_prefixes: bool, count) -> List[Affix]:
        possible_mods = list(self.prefixes if is_prefixes else self.suffixes)
        mods = list()
        for i in range(count):
            group_probability = numpy.array([group.weighting for group in possible_mods])
            group_probability /= group_probability.sum()
            selected_group = choice(possible_mods, p=group_probability)

            tier_probability = numpy.array([selected_group.weighting * mod.tier for mod in selected_group.affixes])
            tier_probability /= tier_probability .sum()
            selected_tier = choice(selected_group.affixes, p=tier_probability)

            mods.append(selected_tier)
            possible_mods.remove(selected_group)
        return mods


def parse_section(obj: json, section: str, destination: list, is_prefix: bool):
    for affix in obj[section]:
        affix_obj = obj[section][affix]

        if "mods_elemental" in affix_obj:
            for element in affix_obj['mods_elemental']:
                element_enum = Element[element.upper()]
                group = AffixGroup("%s.%s" % (affix, element),
                                   affix_obj['friendly_name'].replace("{element}", element_enum.__str__()),
                                   bool(affix_obj['is_percent']), is_prefix, float(affix_obj['weighting']))
                parse_tiers(group, affix_obj['mods_elemental'][element], element_enum)
                destination.append(group)
        else:
            group = AffixGroup(affix, affix_obj['friendly_name'], bool(affix_obj['is_percent']),
                               is_prefix, float(affix_obj['weighting']))
            parse_tiers(group, affix_obj['mods'], None)
            destination.append(group)


def parse_tiers(group: AffixGroup, mods_json, element: Element or None):
    for tier in mods_json:
        roll_range = mods_json[tier]['range']
        name = mods_json[tier]['name']
        if isinstance(roll_range[0], list):
            group.affixes.append(Affix(name, group, int(tier), element, tuple(tuple(r) for r in roll_range)))
        else:
            group.affixes.append(Affix(name, group, int(tier), element, tuple(roll_range)))


def __print_affixes(affixes):
    for affix in affixes:
        if affix.has_dual_rolls():
            low_roll = randint(affix.roll_range[0][0], affix.roll_range[0][1])
            high_roll = randint(affix.roll_range[1][0], affix.roll_range[1][1])
            print("\t(%s) %s (Tier: %d)" % ("P" if affix.parent.is_prefix else "S",
                                            affix.get_display_string((low_roll, high_roll)), affix.tier))
        else:
            roll = randint(affix.roll_range[0], affix.roll_range[1])
            print("\t(%s) %s (Tier: %d)" % ("P" if affix.parent.is_prefix else "S",
                                            affix.get_display_string(roll), affix.tier))


if __name__ == "__main__":
    affix_db = AffixDatabase()
    affix_db.load_file("affix_database.json")
    prefixes = affix_db.get_random_mods(True, randint(1, 3))
    suffixes = affix_db.get_random_mods(False, randint(1, 3))
    print("%s Sword %s" % (prefixes[0].name, suffixes[0].name))
    __print_affixes(prefixes)
    __print_affixes(suffixes)
