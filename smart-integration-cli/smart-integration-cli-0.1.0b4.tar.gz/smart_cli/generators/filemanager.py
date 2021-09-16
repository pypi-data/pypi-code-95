from jinja2 import Template


class FileGenerator(object):
    def __init__(self, get_filename: str, new_filename: str, params: dict) -> None:
        self.get_filename = get_filename
        self.new_filename = new_filename
        self.params = params

    def get_file(self) -> str:
        with open(self.get_filename, 'r') as f:
            s = f.read()
            return s

    def generate_data(self) -> str:
        template_data = self.get_file()
        tm = Template(template_data)
        return tm.render(params=self.params)

    def write_file(self) -> None:
        data = self.generate_data()
        with open(self.new_filename, 'w') as f:
            f.write(data)
