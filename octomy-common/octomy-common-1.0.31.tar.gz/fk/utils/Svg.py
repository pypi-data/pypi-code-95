from pathlib import Path
import pystache


class Svg:
    def __init__(self):
        # Load SVG template from file
        svg_template_fn = "template.svg"
        svg_template_file = Path(svg_template_fn)
        if svg_template_file.is_file():
            with open(svg_template_fn, "r") as svg_template_handle:
                print("Loading svg template from file")
                svg_template_text = svg_template_handle.read()
                # Render the template
                svg_output_fn = "output.svg"
                print("Applying data to template")
                svg_output_text = pystache.render(svg_template_text, {"from": "BGO", "to": "KBP"})
                # Save rendered text into SVG output file
                with open(svg_output_fn, "w") as svg_output_handle:
                    print("Writing output svg")
                    svg_output_handle.write(svg_output_text)
        else:
            print("Template not found, aboring")
