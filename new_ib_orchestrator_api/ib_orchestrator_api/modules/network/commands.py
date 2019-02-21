import click
from .network import Network
from ib_orchestrator_api.core.utils import read_yaml_config
from ib_orchestrator_api.core.auth import authorization



@click.group()
@click.pass_context
def subnet(ctx):
    pass


@click.command()
@click.pass_context
def get(ctx):
    session = authorization(ctx)

@click.command()
@click.pass_context
def list(ctx):
    session = authorization(ctx)
    result = Network(url=ctx.obj['url'], session=session).get_all_subnets()
    click.echo(result)

@click.command()
@click.option('--file', '-f', type=click.Path(exists=True))
@click.pass_context
def create(ctx, file):
    """Create Zone on server"""
    if not file:
        click.echo("None File")
    else:
        result = read_yaml_config(file)
        session = authorization(ctx)

        with click.progressbar(result['network'], label="add network") as bar:
            for subnet in bar:
                # print(type(domain))
                # print(domain)
                subnet = Network(url=ctx.obj['url'], session=session, **subnet)
                result = subnet.create_subnet()
                # click.echo(result)


@click.command()
@click.pass_context
def update(ctx):
    pass


@click.command()
@click.argument('network')
@click.pass_context
def delete(ctx, zone_name):
    session = authorization(ctx)
    result = Network(url=ctx.obj['url'], session=session).delete_subnet()
    print(result)

subnet.add_command(get)
subnet.add_command(list)
subnet.add_command(create)
#network.add_command(update)
subnet.add_command(delete)
