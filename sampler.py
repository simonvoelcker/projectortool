from typing import Tuple, Callable

from settings import Settings
from projections.base import Point


class Sampler:
    def __init__(self, cli_args, settings: Settings, sampling_callback: Callable):
        self.cli_args = cli_args
        self.settings = settings
        self.sampling_callback = sampling_callback
        self.total_samples = cli_args.samples * cli_args.samples

        if self.cli_args.rotation:
            angle_x, angle_y, angle_z = self.cli_args.rotation.split(',')
            self.rotation_angles = int(angle_x), int(angle_y), int(angle_z)
        else:
            self.rotation_angles = None

    def _get_sample(self, point: Point) -> Tuple[int, int, int]:
        direction = self.settings.output_projection.to_direction(point)
        if not direction:
            # Projection gaps may exist -> Return black
            return 0, 0, 0

        if self.rotation_angles:
            direction = direction.rotated(*self.rotation_angles)

        input_point = self.settings.input_projection.to_point(direction)
        if not input_point:
            return 0, 0, 0

        return self.sampling_callback(
            in_x=int(input_point.x * (self.settings.in_width - 1)),
            in_y=int(input_point.y * (self.settings.in_height - 1)),
        )

    def get_supersample(self, out_x: int, out_y: int) -> Tuple[int, int, int]:
        if self.total_samples == 1:
            # One sample per pixel
            output_point = Point(
                out_x / self.settings.out_width,
                out_y / self.settings.out_height
            )
            return self._get_sample(output_point)
        else:
            # Super-sampling (slow, even if args.samples==1)
            r, g, b = 0, 0, 0
            for y_sample in range(self.cli_args.samples):
                for x_sample in range(self.cli_args.samples):
                    output_point = Point(
                        (out_x + x_sample/self.cli_args.samples) / self.settings.out_width,
                        (out_y + y_sample/self.cli_args.samples) / self.settings.out_height
                    )
                    sample = self._get_sample(output_point)
                    r += sample[0]
                    g += sample[1]
                    b += sample[2]
            return (
                r // self.total_samples,
                g // self.total_samples,
                b // self.total_samples
            )
