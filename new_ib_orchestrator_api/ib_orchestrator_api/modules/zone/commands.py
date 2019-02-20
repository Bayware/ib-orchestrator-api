import click
from .zone import Zone
from ib_orchestrator_api.core.utils import read_yaml_config
from ib_orchestrator_api.core.auth import authorization


@click.group()
@click.pass_context
def zone(ctx):
    pass


@click.command()
@click.pass_context
def get(ctx):
    session = authorization(ctx.obj['url'])


@click.command()
@click.pass_context
def list(ctx):
    session = authorization(ctx.obj['url'])
    result = Zone(url=ctx.obj['url'], session=session).get_all_zones()
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
        with click.progressbar(result['zone'], label="Create Zone") as bar:
            for zone in bar:
                # print(type(domain))
                # print(domain)
                zone = Zone(url=ctx.obj['url'], session=session, **zone)
                result = zone.create_zone()
                # click.echo(result)


@click.command()
@click.pass_context
def update(ctx):
    pass


@click.command()
@click.argument('zone_name')
@click.pass_context
def delete(ctx, zone_name):
    session = authorization(ctx.obj['url'])
    result = Zone(url=ctx.obj['url'], session=session).delete_zone(zone_name)
    print(result)


zone.add_command(get)
zone.add_command(list)
zone.add_command(create)
# zone.add_command(update)
zone.add_command(delete)
