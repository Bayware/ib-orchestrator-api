import click
from .controller import Controller
from ib_orchestrator_api.core.utils import read_yaml_config
from ib_orchestrator_api.core.auth import authorization



@click.group()
@click.pass_context
def controller(ctx):
    pass


@click.command()
@click.option("--controller_name", '-n', required=True, help='Controller name')
@click.pass_context
def get(ctx, controller_name):
    session = authorization(ctx)
    controller = Controller(url=ctx.obj['url'], session=session).get_contrroler(controller_name)
    click.echo(controller.to_dict())


@click.command()
@click.pass_context
def list(ctx):
    session = authorization(ctx)
    result = Controller(url=ctx.obj['url'], session=session).get_all_controllers()
    click.echo(result)

@click.command()
@click.option('--file', '-f', type=click.Path(exists=True))
@click.pass_context
def create(ctx, file):
    """Create controller on server"""
    if not file:
        click.echo("None File")
    else:
        result = read_yaml_config(file)
        for controller in result['controller']:
            session = authorization(ctx)
            controller = Controller(url=ctx.obj['url'], session=session, **controller)
            result = controller.create_controller()
            click.echo(result)


@click.command()
@click.option("--controller_name", '-n', required=True, help='enter user name')
@click.pass_context
def update(ctx, controller_name):
    pass


@click.command()
@click.option("--controller_name", '-n', required=True, help='enter user name')
@click.pass_context
def delete(ctx,controller_name):
    session = authorization(ctx)
    result = Controller(url=ctx.obj['url'], session=session).delete_controller(controller_name)
    click.echo(result)

controller.add_command(get)
controller.add_command(list)
controller.add_command(create)
controller.add_command(update)
controller.add_command(delete)
