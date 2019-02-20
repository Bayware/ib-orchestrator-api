import click
from .subnet import Subnet
from ib_orchestrator_api.core.utils import read_yaml_config
from ib_orchestrator_api.core.auth import authorization



@click.group()
@click.pass_context
def subnet(ctx):
    pass


@click.command()
@click.pass_context
def get(ctx):
    session = authorization(ctx.obj['url'])

@click.command()
@click.pass_context
def list(ctx):
    session = authorization(ctx.obj['url'])
    result = Subnet(url=ctx.obj['url'], session=session).get_all_subnets()
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
        session = authorization(ctx.obj['url'])

        with click.progressbar(result['subnet'], label="add subnet") as bar:
            for subnet in bar:
                # print(type(domain))
                # print(domain)
                subnet = Subnet(url=ctx.obj['url'], session=session, **subnet)
                result = subnet.create_subnet()
                # click.echo(result)


@click.command()
@click.pass_context
def update(ctx):
    pass


@click.command()
@click.argument('subnet')
@click.pass_context
def delete(ctx, zone_name):
    session = authorization(ctx.obj['url'])
    result = Subnet(url=ctx.obj['url'], session=session).delete_subnet()
    print(result)

subnet.add_command(get)
subnet.add_command(list)
subnet.add_command(create)
#subnet.add_command(update)
subnet.add_command(delete)
