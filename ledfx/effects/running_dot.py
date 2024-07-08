import numpy as np
import voluptuous as vol

from ledfx.color import parse_color, validate_color, LEDFX_COLORS
from ledfx.effects.temporal import TemporalEffect


class RunningDotEffect(TemporalEffect):
    NAME = "Running Dot"
    CATEGORY = "Non-Reactive"

    _dot_color = None
    _idx = 0
    _forward = True

    CONFIG_SCHEMA = vol.Schema(
        {
            vol.Optional(
                "color", description="Color of dot", default="#FF0000"
            ): validate_color,

            vol.Optional(
                "one_way", description="One way movement of the dot", default=False
            ): bool,
        },
    )

    def config_updated(self, config):
        self._dot_color = np.array(parse_color(self._config["color"]), dtype=float)
        self._idx = 0

    def on_activate(self, pixel_count):
        pass

    def effect_loop(self):
        
        color_array = np.tile(np.array(parse_color(LEDFX_COLORS["black"]), dtype=float), (self.pixel_count, 1))
        color_array[self._idx] = self._dot_color
        self.pixels = color_array

        if self._idx < self.pixel_count - 1 and self._forward:
            self._idx += 1
        elif self._idx > 0 and not self._forward: 
            self._idx -= 1
         
        if (self._idx == self.pixel_count - 1 or self._idx == 0) and not self._config["one_way"]:
            self._forward = not self._forward
        elif self._config["one_way"] and self._idx == self.pixel_count -1:
            self._idx = -1
            
        
