import ddgcli as ddg
import html2text
import textwrap
import click
import os

@click.group()
def ddgcli():
    pass

banner = {"message": "DuckDuckGo Unoficial CLI", "fg": "blue"}

@ddgcli.command(name = "search", help = "Search's an query on DDG")
@click.argument("query", required = True)
@click.option("-r/--retry", default = True)
def search(**kwargs):
    data = ddg.getURLs(ddg.get_page(kwargs["query"], retry = kwargs["r"]))
    click.secho(**banner)
    for d in data:
        click.secho(" " + d["link"], fg = "cyan")
        click.secho(" " + "-" * len(d["link"]), fg = "yellow")
        for data in textwrap.wrap(d["description"], width = int(os.get_terminal_size()[0]*60/100)):
            click.secho(" " + html2text.html2text(data).strip("\n") + "\n", fg = "cyan", nl = False)
        click.secho("\n")
    click.secho(f"Results Len: {len(data)}")

@ddgcli.command(name = "abstract", help = "Get's the duckduckgo abstract information")
@click.argument("query", required = True)
@click.option("-r/--retry", default = True)
def abstract(**kwargs):
    data = ddg.getAbstractInfo(
        ddg.get_page(
            kwargs["query"],
            retry = kwargs["r"]
        )
    )
    click.secho(**banner)
    if data:
        click.secho(fg = "cyan", message = "\nData:")

        for d in textwrap.wrap(data["data"]["Abstract"], width = int(os.get_terminal_size()[0]*60/100)):
            click.secho(" " + html2text.html2text(d).strip("\n")+"\n", fg = "green", nl = False, bold = True)

        click.secho(fg = "cyan", message = "\nSource:")
        click.secho(fg = "green", message = " " + data['data']['AbstractSource'], bold = True)
    else:
        click.secho(fg = "red", message = "No abstract data was founded!", bold = True)
