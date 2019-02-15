import click
from .resource_user import ResourceUser


@click.group()
@click.pass_context
def resource_user(ctx):
    pass


@click.command()
@click.option("--username", '-n', required=True, help='enter user name')
@click.option("--domain", '-d', required=True, help='enter domain name')
@click.pass_context
def get(ctx, username, domain):
    r_user = ResourceUser(url=ctx.obj['url'], session=ctx.obj['session']).get_resource_user(username=username,
                                                                                            domain=domain)
    print(r_user.to_dict())


@click.command()
@click.pass_context
def get_all(ctx):
    pass


@click.command()
@click.pass_context
def create(ctx):
    pass


@click.command()
@click.pass_context
def update(ctx):
    pass


@click.command()
@click.pass_context
def delete(ctx):
    pass


resource_user.add_command(get)
resource_user.add_command(get_all)
resource_user.add_command(create)
resource_user.add_command(update)
resource_user.add_command(delete)
