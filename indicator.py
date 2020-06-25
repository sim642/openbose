import gi

gi.require_version("AppIndicator3", "0.1")
from gi.repository import AppIndicator3

from typing import Dict


class IndicatorManager:
    active: Dict[str, AppIndicator3.Indicator] = {}
    inactive: Dict[str, AppIndicator3.Indicator] = {}

    @classmethod
    def create(cls, id, icon_name, category):
        if id in cls.active:
            raise RuntimeError(f"indicator {id} already active")
        else:
            if id in cls.inactive:
                indicator = cls.inactive.pop(id)
                indicator.set_icon(icon_name)
                indicator.set_property("category", category.value_nick)
            else:
                indicator = AppIndicator3.Indicator.new(id, icon_name, category)

            indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
            cls.active[id] = indicator
            return indicator

    @classmethod
    def destroy(cls, id):
        if id in cls.active:
            indicator = cls.active.pop(id)
            indicator.set_status(AppIndicator3.IndicatorStatus.PASSIVE)
            cls.inactive[id] = indicator
        else:
            raise RuntimeError(f"indicator {id} isn't active")
