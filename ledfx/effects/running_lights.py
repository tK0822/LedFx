import numpy as np
import voluptuous as vol

from ledfx.color import parse_color, validate_color, LEDFX_COLORS
from ledfx.effects.temporal import TemporalEffect
from ledfx.effects.gradient import GradientEffect



class RunningLights(TemporalEffect, GradientEffect):
    NAME = "Running Lights"
    CATEGORY = "Non-Reactive"

    _color = None
    _forward = True
    _position = 0
    _gradient_idx = 0
    _gradient_samples = 200

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

            vol.Optional(
                "color_rate",
                default=2,
                description="Color change rate",
            ): vol.All(vol.Coerce(int), vol.Range(min=1, max=20)),

        },
    )

    def config_updated(self, config):
        self._gradient_idx = 0
        self._forward = True
        self._assert_gradient()
        self._idx = 0

    def on_activate(self, pixel_count):
        pass
    
    def sin_scroll(self, i):

        r = ((np.sin((i + self._position) * self._config["length"]) * 127 + 128) / 255) * self._color[0]
        g = ((np.sin((i + self._position) * self._config["length"]) * 127 + 128) / 255) * self._color[1]
        b = ((np.sin((i + self._position) * self._config["length"]) * 127 + 128) / 255) * self._color[2]

        return np.array([r, g, b], dtype=float)
    
    def _assert_gradient(self):
        if (
            self._gradient_curve is None  # Uninitialized gradient
            or len(self._gradient_curve[0])
            !=self._gradient_samples  # Incorrect size
        ):
            self._generate_gradient_curve(
                self._config["gradient"],
                self._gradient_samples,
            )
    
    def effect_loop(self):
        
        # Get gradient color
        if self._forward:
            self._gradient_idx += self._config["color_rate"]
        else:
            self._gradient_idx -= self._config["color_rate"]

        if self._gradient_idx >= self._gradient_samples:
            self._gradient_idx = self._gradient_samples - 1
            self._forward = not self._forward
        elif self._gradient_idx <= 0:
            self._gradient_idx = 0
            self._forward = not self._forward

        self._color = self._gradient_curve[:, self._gradient_idx]

        if self._position < self.pixel_count * 2:
            self._position += 1
        else:
            self._position = 0
        
        self.pixels = np.array([self.sin_scroll(i) for i in np.arange(0, self.pixel_count)])
        
            
        
