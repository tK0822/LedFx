import numpy as np
import voluptuous as vol

from ledfx.color import parse_color, validate_color, LEDFX_COLORS
from ledfx.effects.temporal import TemporalEffect
from ledfx.effects.gradient import GradientEffect



class BuildUp(TemporalEffect, GradientEffect):
    NAME = "Build Up"
    CATEGORY = "Non-Reactive"

    _color = None
    _idx = 0
    _forward = True
    _black = np.array(parse_color(LEDFX_COLORS["black"]), dtype=float)
    _gradient_idx = 0    
    _gradient_forward = True
    _gradient_samples = 200

    CONFIG_SCHEMA = vol.Schema(
        {
            vol.Optional(
                "color rate",
                default=2,
                description="Color change rate",
            ): vol.All(vol.Coerce(int), vol.Range(min=1, max=200)),
        },
    )

    def config_updated(self, config):
        self._gradient_idx = 0
        self._gradient_forward = True
        self._assert_gradient()
        self._forward = True
        self._idx = 0

    def on_activate(self, pixel_count):
        pass

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
        if self._gradient_forward:
            self._gradient_idx += self._config["color rate"]
        else:
            self._gradient_idx -= self._config["color rate"]

        if self._gradient_idx >= self._gradient_samples:
            self._gradient_idx = self._gradient_samples - 1
            self._gradient_forward = not self._gradient_forward
        elif self._gradient_idx <= 0:
            self._gradient_idx = 0
            self._gradient_forward = not self._gradient_forward

        self._color = self._gradient_curve[:, self._gradient_idx]

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

        

        
        

            
        
