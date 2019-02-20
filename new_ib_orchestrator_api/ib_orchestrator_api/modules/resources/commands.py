import click
from .resources import Resources
from ib_orchestrator_api.core.auth import authorization



@click.group()
@click.pass_context
def resources(ctx):
    pass


@click.command()
@click.option("--name", '-n', help='Resource name')
@click.option("--domain", '-d', help="Domain name")
@click.pass_context
def get(ctx, name, domain):
    session = authorization(ctx.obj['url'])
    result = Resources(url=ctx.obj['url'], session=session).get_rescources(name, domain)
    click.echo(result)


@click.command()
@click.pass_context
def list(ctx):
    session = authorization(ctx.obj['url'])
    result = Resources(url=ctx.obj['url'], session=session).get_all_resources()
    click.echo(result)


resources.add_command(get)
resources.add_command(list)
