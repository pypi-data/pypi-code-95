"""
This file offers the methods to automatically retrieve the graph tech-as-caida2007.

The graph is automatically retrieved from the NetworkRepository repository. 


References
---------------------
Please cite the following if you use the data:

```latex
@inproceedings{nr,
    title = {The Network Data Repository with Interactive Graph Analytics and Visualization},
    author={Ryan A. Rossi and Nesreen K. Ahmed},
    booktitle = {AAAI},
    url={http://networkrepository.com},
    year={2015}
}

@misc{routeviews,
    author = {{Internet-AS}},
    title  = {{Oregon RouteViews} Project},
    note   = {{http://www.routeviews.org/}}
}

@inproceedings{rossi2013topology,
        title={A Multi-Level Approach for Evaluating Internet Topology Generators},
        author={Ryan A. Rossi and Sonia Fahmy and Nilothpal Talukder},
        booktitle={Networking},
        pages={1--9},
        year={2013}
}
```
"""
from typing import Dict

from ..automatic_graph_retrieval import AutomaticallyRetrievedGraph
from ...ensmallen import Graph  # pylint: disable=import-error


def TechAsCaida2007(
    directed: bool = False,
    preprocess: bool = True,
    verbose: int = 2,
    cache: bool = True,
    cache_path: str = "graphs/networkrepository",
    version: str = "latest",
    **additional_graph_kwargs: Dict
) -> Graph:
    """Return new instance of the tech-as-caida2007 graph.

    The graph is automatically retrieved from the NetworkRepository repository.	

    Parameters
    -------------------
    directed: bool = False,
        Wether to load the graph as directed or undirected.
        By default false.
    preprocess: bool = True,
        Whether to preprocess the graph to be loaded in 
        optimal time and memory.
    verbose: int = 2,
        Wether to show loading bars during the retrieval and building
        of the graph.
    cache: bool = True,
        Whether to use cache, i.e. download files only once
        and preprocess them only once.
    cache_path: str = "graphs",
        Where to store the downloaded graphs.
    version: str = "latest",
        The version of the graph to retrieve.	
    additional_graph_kwargs: Dict,
        Additional graph kwargs.

    Returns
    -----------------------
    Instace of tech-as-caida2007 graph.

	References
	---------------------
	Please cite the following if you use the data:
	
	```latex
	@inproceedings{nr,
	    title = {The Network Data Repository with Interactive Graph Analytics and Visualization},
	    author={Ryan A. Rossi and Nesreen K. Ahmed},
	    booktitle = {AAAI},
	    url={http://networkrepository.com},
	    year={2015}
	}
	
	@misc{routeviews,
	    author = {{Internet-AS}},
	    title  = {{Oregon RouteViews} Project},
	    note   = {{http://www.routeviews.org/}}
	}
	
	@inproceedings{rossi2013topology,
	        title={A Multi-Level Approach for Evaluating Internet Topology Generators},
	        author={Ryan A. Rossi and Sonia Fahmy and Nilothpal Talukder},
	        booktitle={Networking},
	        pages={1--9},
	        year={2013}
	}
	```
    """
    return AutomaticallyRetrievedGraph(
        graph_name="TechAsCaida2007",
        repository="networkrepository",
        version=version,
        directed=directed,
        preprocess=preprocess,
        verbose=verbose,
        cache=cache,
        cache_path=cache_path,
        additional_graph_kwargs=additional_graph_kwargs
    )()
