from __future__ import annotations

import json
from typing import Any


class NBT(dict[str, Any]):
    def __str__(self) -> str:
        return json.dumps(self)

    def get_or_create_nbt(self, value: str) -> NBT:
        if value not in self:
            self[value] = NBT()
        return self[value]

    def get_or_create_list(self, value: str) -> list[NBT | str]:
        if value not in self:
            self[value] = []
        return self[value]

    def set_unbreakable(self) -> None:
        self["Unbreakable"] = 1

    def set_name(self, text: str, italics: bool = True) -> None:
        itstr = str(bool(italics)).lower()
        self.get_or_create_nbt("display")["Name"] = f'[{{"text": "{text}", "italic": {itstr}}}]'

    def add_lore(self, text: str) -> None:
        self.get_or_create_nbt("display").get_or_create_list("Lore").append(f'"{text}"')

    def add_can_place_on(self, block: str) -> None:
        self.get_or_create_list("CanPlaceOn").append(block)

    def add_can_destroy(self, block: str) -> None:
        self.get_or_create_list("CanDestroy").append(block)

    def add_enchantment(self, enchantment: str, level: int = 1) -> None:
        tag = NBT({"id": enchantment, "lvl": level})
        self.get_or_create_list("Enchantments").append(tag)

    def add_aqua_affinity(self, level: int = 1) -> None:
        self.add_enchantment("aqua_affinity", level)

    def add_bane_of_arthropods(self, level: int = 1) -> None:
        self.add_enchantment("bane_of_arthropods", level)

    def add_blast_protection(self, level: int = 1) -> None:
        self.add_enchantment("blast_protection", level)

    def add_channeling(self, level: int = 1) -> None:
        self.add_enchantment("channeling", level)

    def add_binding_curse(self, level: int = 1) -> None:
        self.add_enchantment("binding_curse", level)

    def add_vanishing_curse(self, level: int = 1) -> None:
        self.add_enchantment("vanishing_curse", level)

    def add_depth_strider(self, level: int = 1) -> None:
        self.add_enchantment("depth_strider", level)

    def add_efficiency(self, level: int = 1) -> None:
        self.add_enchantment("efficiency", level)

    def add_feather_falling(self, level: int = 1) -> None:
        self.add_enchantment("feather_falling", level)

    def add_fire_aspect(self, level: int = 1) -> None:
        self.add_enchantment("fire_aspect", level)

    def add_fire_protection(self, level: int = 1) -> None:
        self.add_enchantment("fire_protection", level)

    def add_flame(self, level: int = 1) -> None:
        self.add_enchantment("flame", level)

    def add_fortune(self, level: int = 1) -> None:
        self.add_enchantment("fortune", level)

    def add_frost_walker(self, level: int = 1) -> None:
        self.add_enchantment("frost_walker", level)

    def add_impaling(self, level: int = 1) -> None:
        self.add_enchantment("impaling", level)

    def add_infinity(self, level: int = 1) -> None:
        self.add_enchantment("infinity", level)

    def add_knockback(self, level: int = 1) -> None:
        self.add_enchantment("knockback", level)

    def add_looting(self, level: int = 1) -> None:
        self.add_enchantment("looting", level)

    def add_loyalty(self, level: int = 1) -> None:
        self.add_enchantment("loyalty", level)

    def add_luck_of_the_sea(self, level: int = 1) -> None:
        self.add_enchantment("luck_of_the_sea", level)

    def add_lure(self, level: int = 1) -> None:
        self.add_enchantment("lure", level)

    def add_mending(self, level: int = 1) -> None:
        self.add_enchantment("mending", level)

    def add_multishot(self, level: int = 1) -> None:
        self.add_enchantment("multishot", level)

    def add_piercing(self, level: int = 1) -> None:
        self.add_enchantment("piercing", level)

    def add_power(self, level: int = 1) -> None:
        self.add_enchantment("power", level)

    def add_projectile_protection(self, level: int = 1) -> None:
        self.add_enchantment("projectile_protection", level)

    def add_protection(self, level: int = 1) -> None:
        self.add_enchantment("protection", level)

    def add_punch(self, level: int = 1) -> None:
        self.add_enchantment("punch", level)

    def add_quick_charge(self, level: int = 1) -> None:
        self.add_enchantment("quick_charge", level)

    def add_respiration(self, level: int = 1) -> None:
        self.add_enchantment("respiration", level)

    def add_riptide(self, level: int = 1) -> None:
        self.add_enchantment("riptide", level)

    def add_sharpness(self, level: int = 1) -> None:
        self.add_enchantment("sharpness", level)

    def add_silk_touch(self, level: int = 1) -> None:
        self.add_enchantment("silk_touch", level)

    def add_smite(self, level: int = 1) -> None:
        self.add_enchantment("smite", level)

    def add_soul_speed(self, level: int = 1) -> None:
        self.add_enchantment("soul_speed", level)

    def add_sweeping(self, level: int = 1) -> None:
        self.add_enchantment("sweeping", level)

    def add_swift_sneak(self, level: int = 1) -> None:
        self.add_enchantment("swift_sneak", level)

    def add_thorns(self, level: int = 1) -> None:
        self.add_enchantment("thorns", level)

    def add_unbreaking(self, level: int = 1) -> None:
        self.add_enchantment("unbreaking", level)
