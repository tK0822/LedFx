import numpy as np
import voluptuous as vol

from ledfx.color import parse_color, validate_color, LEDFX_COLORS
from ledfx.effects.temporal import TemporalEffect


class BuildUp(TemporalEffect):
    NAME = "Build Up"
    CATEGORY = "Non-Reactive"

    _color = None
    _idx = 0
    _forward = True
    _black = np.array(parse_color(LEDFX_COLORS["black"]), dtype=float)

    CONFIG_SCHEMA = vol.Schema(
        {
            vol.Optional(
                "color", description="Color of dot", default="#FF0000"
            ): validate_color,
        },
    )

    def config_updated(self, config):
        self._color = np.array(parse_color(self._config["color"]), dtype=float)
        self._idx = 0

    def on_activate(self, pixel_count):
        pass

    def effect_loop(self):
        if self._forward:
            self.pixels[self._idx] = self._color
        else:
            self.pixels[self._idx] = self._black
        
        if self._idx < self.pixel_count - 1 and self._forward:
            self._idx += 1
        elif self._idx > 0 and not self._forward: 
            self._idx -= 1

        if self._idx == self.pixel_count - 1  or self._idx == 0:
            self.pixels[self._idx] = self._color
            self._forward = not self._forward

        

        
        

            
        
