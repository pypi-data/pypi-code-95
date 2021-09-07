from click import UsageError
import oyaml as yaml


csv = {
    "language": "data",
    "title": "My Title",
    "type": "csv"
}

image = {
    "language": "image",
    "title": "My Title",
    "type": "png"
}

json = {
    "language": "data",
    "title": "My Title",
    "type": "json"
}

pdf = {
    "language": "pdf",
    "title": "My Title",
    "type": "pdf"
}

yml = {
    "language": "data",
    "title": "My Title",
    "type": "yml"
}

flask = {
    "language": "python",
    "title": "My Title",
    "type": "flask",
    "python_conda_packages": None,
    "requirement": True,
    "version": 3.5
}

jupyter = {
    "format": "html",
    "language": "python",
    "python_conda_packages": {"jupyter": "latest"},
    "requirement": False,
    "version": 3.5,
    "title": "My Title",
    "recreate": True
}

streamlit = {
    "language": "python",
    "title": "My Title",
    "type": "streamlit",
    "python_conda_packages": {},
    "requirement": True,
    "version": 3.5
}


r_markdown = {
    "language": "r",
    "title": "My Title",
    "type": "markdown",
    "r_cran_packages": {"dplyr": "latest", "rmarkdown": "latest"},
    "r_packages": [{"package": "r-dt",  "method": "conda",  "channel": "conda-forge"}, 
                  {"package": "tidyverse/ggplot2",  "method": "github"},
                  {"package": "tseries",  "method": "cran"},
                  {"package": "DT",  "code": "install.packages(\"DT\", dependencies = TRUE, repos = \"http://cran.us.r-project.org\")"},

    ],   
    "requirement": True,
    "version": 3.4
}

golem = {
    "language": "r",
    "title": "My Title",
    "type": "golem",
    "r_cran_packages": {"dplyr": "latest", "rmarkdown": "latest"},
    "r_packages": [{"package": "r-dt",  "method": "conda",  "channel": "conda-forge"}, 
                  {"package": "tidyverse/ggplot2",  "method": "github"},
                  {"package": "tseries",  "method": "cran"},
                  {"package": "DT",  "code": "install.packages(\"DT\", dependencies = TRUE, repos = \"http://cran.us.r-project.org\")"},

    ],
    "requirement": True,
    "version": 3.4
}


shiny = {
    "language": "r",
    "title": "My Title",
    "type": "shiny",
    "r_cran_packages": {"dplyr": "latest", "rmarkdown": "latest"},
    "r_packages": [{"package": "r-dt",  "method": "conda",  "channel": "conda-forge"}, 
                  {"package": "tidyverse/ggplot2",  "method": "github"},
                  {"package": "tseries",  "method": "cran"},
                  {"package": "DT",  "code": "install.packages(\"DT\", dependencies = TRUE, repos = \"http://cran.us.r-project.org\")"},

    ],
    "requirement": True,
    "version": 3.6
}

all_map = {
    "csv": csv,
    "image": image,
    "json": json,
    "pdf": pdf,
    "yml": yml,
    "flask": flask,
    "streamlit": streamlit,
    "jupyter": jupyter,
    "r_markdown": r_markdown,
    "golem": golem,
    "shiny": shiny
    }

def create_config(path, type):
    if type not in all_map.keys():
        raise UsageError("zen report data is not present please use zen create command")


    data = all_map.all_map[type]
    with open(path, "w") as f:
        yaml.safe_dump(data, f)