import typer
import os

typ = typer.Typer()

### Templates for our Scaffolding Features
templateV1 = """from solace import Solace

def greet_html(req, res, next):
    res.tpl("index.html", {"name": "World"})

def greet_json(req, res, next):
    res.json = {"Hello": "World"}

app = Solace()

# Route Definitions
app.get("/", greet_html)
app.get("/api", greet_json)
"""

### Templates for our Scaffolding Features
templateV2 = """from solace import Solace

def greet_json(req, res, next):
    res.json = {"Hello": "World"}

app = Solace()

# Route Definitions
app.get("/", greet_json)
"""

dockerfileTemplate = """FROM python:3.9.5-alpine3.13
RUN pip install gunicorn solace
EXPOSE 5000
COPY src/ /src
WORKDIR /
CMD ["gunicorn", "-b", "0.0.0.0:5000", "src.index:app"]
"""

indexHTMLTemplate = """<h1>Hello, ${name}</h1>"""

@typ.command()
def project(name: str, template: bool = typer.Option(False, help="include template support")):
  """ create a new project """
  os.mkdir(name)
  os.chdir(name)
  f = open('README.md', 'w+')
  f.close()
  f = open('Dockerfile', 'w+')
  f.write(dockerfileTemplate)
  f.close()
  os.mkdir('src')
  os.chdir('src')
  f = open('index.py', 'w+')
  if template:
    f.write(templateV1)
  else:
    f.write(templateV2)
  f.close()
  f = open('__init__.py', 'w+')
  f.close()
  if template:
    os.mkdir('templates')
    os.chdir('templates')
    f = open('index.html', 'w+')
    f.write(indexHTMLTemplate)
    f.close()
  print("You're all set!\nTo get started with development, run the following command:\n")
  print(f"cd {name} && solace run dev\n")
