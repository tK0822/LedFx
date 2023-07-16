import numpy as np
import voluptuous as vol

from ledfx.color import parse_color, validate_color, LEDFX_COLORS
from ledfx.effects.temporal import TemporalEffect


class RunningLights(TemporalEffect):
    NAME = "Running Lights"
    CATEGORY = "Non-Reactive"

    _color = None
    _forward = True
    _position = 0

    CONFIG_SCHEMA = vol.Schema(
        {
            vol.Optional(
                "color", description="Color", default="#FF0000"
            ): validate_color,

            vol.Optional(
                "direction", description="Direction of Movement", default=False
            ): bool,

            vol.Optional(
                "length", description="Wave Length", default=1
            ): vol.All(vol.Coerce(float), vol.Range(min=1, max=30)),
        },
    )

    def config_updated(self, config):
        self._color = np.array(parse_color(self._config["color"]), dtype=float)
        self._idx = 0

    def on_activate(self, pixel_count):
        pass
    
    def sin_scroll(self, i):

        r = ((np.sin((i + self._position) * self._config["length"]) * 127 + 128) / 255) * self._color[0]
        g = ((np.sin((i + self._position) * self._config["length"]) * 127 + 128) / 255) * self._color[1]
        b = ((np.sin((i + self._position) * self._config["length"]) * 127 + 128) / 255) * self._color[2]

        return np.array([r, g, b], dtype=float)
    
    def effect_loop(self):

        if self._position < self.pixel_count * 2:
            self._position += 1
        else:
            self._position = 0
        
        self.pixels = np.array([self.sin_scroll(i) for i in np.arange(0, self.pixel_count)])
        
            
        
