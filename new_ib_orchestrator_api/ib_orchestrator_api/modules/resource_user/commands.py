import click
from .resource_user import ResourceUser
from ib_orchestrator_api.core.utils import read_yaml_config
from ib_orchestrator_api.core.auth import authorization


@click.group()
@click.pass_context
def resource_user(ctx):
    pass


@click.command()
@click.option("--username", '-u', required=True, help='enter user name')
@click.option("--domain", '-d', required=True, help='enter domain name')
@click.pass_context
def get(ctx, username, domain):
    session = authorization(ctx.obj['url'])
    r_user = ResourceUser(url=ctx.obj['url'], session=session).get_resource_user(username=username,
                                                                                 domain=domain)
    click.echo(r_user.to_dict())


@click.command()
@click.option("--domain_name", '-d', help='enter domain name')
@click.pass_context
def list(ctx, domain_name):
    if domain_name:
        session = authorization(ctx.obj['url'])
        result = ResourceUser(url=ctx.obj['url'], session=session).get_all_in_domain(domain_name)
        click.echo(result)
    else:
        session = authorization(ctx.obj['url'])
        result = ResourceUser(url=ctx.obj['url'], session=session).get_all_resource_user()
        click.echo(result)


@click.command()
@click.option('--file', '-f', type=click.Path(exists=True))
@click.pass_context
def create(ctx, file):
    """Create domain on server"""
    if not file:
        click.echo("None File")
    else:
        result = read_yaml_config(file)
        for resource_user in result['resource_user']:
            # print(resource_user)
            session = authorization(ctx.obj['url'])
            resource_user = ResourceUser(url=ctx.obj['url'], session=session, **resource_user)
            result = resource_user.create_resource_user()
            click.echo(result)


@click.command()
@click.option("--username", '-u', required=True, help='enter user name')
@click.option("--domain_name", '-d', required=True, help='enter domain name')
@click.option("--is_active", "-status", help='enter status Enabled(True)/Disabled(False)')
@click.option("--password", "-p", help='enter password')
@click.option("--role", "-r", help='enter resource_user_role')
@click.pass_context
def update(ctx, username, domain_name, **kwargs):
    #TODO
    session = authorization(ctx.obj['url'])
    r_user = ResourceUser(url=ctx.obj['url'], session=session).get_resource_user(username, domain_name)
    print(r_user.to_dict())
    r_user.update_resource_user()
    update_data = {}
    for field in kwargs:
        if not kwargs[field]:
            continue
        update_data.update({field:kwargs[field]})

    print(update_data)
    r_user.update_resource_user()

@click.command()
@click.option("--username", '-u', required=True, help='enter user name')
@click.option("--domain_name", '-d', required=True, help='enter domain name')
@click.pass_context
def delete(ctx, username, domain_name):
    session = authorization(ctx.obj['url'])
    resource_user = ResourceUser(url=ctx.obj['url'], session=session).delete_resource_user(username=username,
                                                                                           domain_name=domain_name)
    click.echo(resource_user)


resource_user.add_command(get)
resource_user.add_command(list)
resource_user.add_command(create)
resource_user.add_command(update)
resource_user.add_command(delete)
