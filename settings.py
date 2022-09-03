import sys
from projections.map import projections_map


class Settings(dict):
    def __init__(self, cli_args, input_image, *args, **kwargs):
        super().__init__(*args, **kwargs)

        in_projection = cli_args.in_projection
        self.in_width, self.in_height = input_image.size
        in_aspect_ratio = float(self.in_width) / float(self.in_height)
        if in_projection == 'auto':
            # Detect input projection based on image aspect ratio
            for projection_name, projection_class in projections_map.items():
                if projection_class.aspect_ratio() == in_aspect_ratio:
                    in_projection = projection_name
            # No match found, ask the user to specify projection
            if in_projection == 'auto':
                print('Specify input projection using --in-projection')
                sys.exit(0)

        projection_kwargs = {
            'hemi_fov_x': cli_args.hemi_fov_x,
            'hemi_fov_y': cli_args.hemi_fov_y,
        }

        self.input_projection = projections_map[in_projection](**projection_kwargs)
        self.output_projection = projections_map[cli_args.out_projection](**projection_kwargs)

        self.out_width = cli_args.width
        self.out_height = cli_args.height
        if not self.out_width or not self.out_height:
            # Come up with reasonable output image size based on
            # input image size and desired output projection
            out_aspect_ratio = self.output_projection.aspect_ratio()
            if self.out_width:
                self.out_height = int(self.out_width / out_aspect_ratio)
            elif self.out_height:
                self.out_width = int(self.out_height * out_aspect_ratio)
            else:
                self.out_width = self.in_width
                self.out_height = int(self.out_width / out_aspect_ratio)
