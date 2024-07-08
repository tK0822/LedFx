import numpy as np
import voluptuous as vol
import random as rand

from ledfx.color import parse_color, validate_color, LEDFX_COLORS
from ledfx.effects.temporal import TemporalEffect
from ledfx.effects.gradient import GradientEffect



class Meteor(TemporalEffect, GradientEffect):
    NAME = "Meteor"
    CATEGORY = "Non-Reactive"

    _color = None
    _led_idx = None
    _idx = 0
    _gradient_idx = 0    
    _forward = True
    _gradient_samples = 200

    CONFIG_SCHEMA = vol.Schema(
        {
            vol.Optional(
                "meteor_length",
                default=2,
                description="Length of meteor",
            ): vol.All(vol.Coerce(int), vol.Range(min=1, max=40)),

            vol.Optional(
                "color_rate",
                default=2,
                description="Color change rate",
            ): vol.All(vol.Coerce(int), vol.Range(min=1, max=20)),

            vol.Optional(
                "decay_rate",
                default=100,
                description="Decay rate of stars",
            ): vol.All(vol.Coerce(int), vol.Range(min=10, max=250)),
        },
    )
    def config_updated(self, config):
        self._gradient_idx = 0
        self._forward = True
        self._assert_gradient()

    def on_activate(self, pixel_count):
        self._color = self.get_gradient_color(0)
    
    @staticmethod
    def _fade_to_black(fade_value: float, curr_color: np.ndarray):

        r = 0 if curr_color[0] <= 5 else curr_color[0] - (curr_color[0] * fade_value / 256)
        g = 0 if curr_color[1] <= 5 else curr_color[1] - (curr_color[1] * fade_value / 256)
        b = 0 if curr_color[2] <= 5 else curr_color[2] - (curr_color[2] * fade_value / 256)

        return np.array([r, g, b])
    
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
        self._led_idx = range(0, self.pixel_count)
       
        if self._idx == self.pixel_count * 2:
            self._idx = 0

        # Fade meteor randomly
        self.pixels = np.array([self._fade_to_black(fade_value=self._config["decay_rate"], curr_color=self.pixels[idx]) 
                            if (rand.randint(0, 10) > 5)
                            else self.pixels[idx] for idx in self._led_idx])

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
        
        # Draw Meteor
        for k in np.arange(0, self._config["meteor_length"]):
            if (self._idx - k < self.pixel_count) & (self._idx - k >= 0):
                self.pixels[self._idx - k] = self._color

        self._idx += 1 