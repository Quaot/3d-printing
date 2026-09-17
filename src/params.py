"""Every dimension for the fidget, in millimetres.

Change fit_clearance after printing the tolerance coupon; everything
else follows from it.
"""

from dataclasses import dataclass


@dataclass
class Params:
    # MX-style switch
    switch_cutout: float = 14.0      # nominal square plate cutout
    plate_thickness: float = 1.5     # MX clips expect a 1.5 mm plate
    switch_depth: float = 8.5        # switch body and pins below the plate

    # Fit
    fit_clearance: float = 0.10      # added to each side of the switch cutout
    cap_clearance: float = 0.10      # gap on each side of the bottom cap lip
    stem_clearance: float = 0.05     # added to each side of the keycap cross

    # Housing
    body_size: float = 30.0
    body_height: float = 16.0
    wall_thickness: float = 2.0
    corner_radius: float = 5.0

    # Bottom cap
    cap_thickness: float = 1.6
    cap_lip_height: float = 3.0

    # Keycap
    keycap_size: float = 18.0
    keycap_height: float = 6.0
    keycap_top_thickness: float = 1.5
    keycap_skirt_thickness: float = 0.9
    stem_socket_diameter: float = 5.5
    stem_cross_length: float = 4.0
    stem_bar_h: float = 1.3          # horizontal bar thickness
    stem_bar_v: float = 1.1          # vertical bar thickness
    stem_socket_depth: float = 3.8

    # Tolerance coupon
    coupon_cutouts: tuple = (13.8, 13.9, 14.0, 14.1, 14.2, 14.3)
    coupon_stem_clearances: tuple = (0.0, 0.05, 0.10, 0.15, 0.20, 0.25)
    coupon_pitch: float = 19.0

    @property
    def cutout_size(self) -> float:
        return self.switch_cutout + 2 * self.fit_clearance

    @property
    def inner_size(self) -> float:
        return self.body_size - 2 * self.wall_thickness
