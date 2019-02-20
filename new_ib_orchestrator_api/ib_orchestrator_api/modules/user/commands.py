import click
from .user import User
from ib_orchestrator_api.core.auth import authorization
from ib_orchestrator_api.core.utils import read_yaml_config


@click.group()
@click.pass_context
def user(ctx):
    """
    User is an entity that receives access to the resources that are isolated in the domain
    """
    pass


@click.command()
@click.option("--username", '-u', required=True, help='User name')
@click.option("--domain", '-d', required=True, help='Domain name')
@click.pass_context
def get(ctx, username, domain):
    """
    Get user from domain. Enter username and domain, User name must be unique only within a domain
    """
    session = authorization(ctx.obj['url'])
    user = User(url=ctx.obj['url'], session=session).get_user(username=username, domain=domain)
    click.echo(user.to_dict())


@click.command()
@click.option('--domain', '-d', help='Domain name')
@click.pass_context
def list(ctx, domain):
    """
    Get all user, with flag -d --get all user from domain
    """
    session = authorization(ctx.obj['url'])
    if domain:
        result = User(url=ctx.obj['url'], session=session).get_all_user_from_domain(domain_name=domain)
        click.echo(result)
    else:
        result = User(url=ctx.obj['url'], session=session).get_all_user()
        # print(result)
        click.echo(result)


@click.command()
@click.option('--file', '-f', type=click.Path(exists=True), help='User config file')
@click.pass_context
def create(ctx, file):
    """
    Create user, data upload from file

    """
    if not file:
        click.echo("None File")
    else:
        result = read_yaml_config(file)
        print(result)
        for user in result['user']:
            session = authorization(ctx.obj['url'])
            user = User(url=ctx.obj['url'], session=session, **user)
            result = user.create_user()
            click.echo(result)


@click.command()
@click.option('--first_name')
@click.option('--is_active')
@click.option('--password')
@click.option('--roles')
@click.option('--user_auth_method')
@click.option('--user_domain', '-d', required=True)
@click.option('--username', '-u', required=True)
@click.pass_context
def update(ctx, username, user_domain, **kwargs):
    session = authorization(ctx.obj['url'])
    user = User(url=ctx.obj['url'], session=session).get_user(username=username, domain=user_domain)
    for field in kwargs:
        if not kwargs[field]:
            continue
        if field in vars(user).keys():
            setattr(user, field, kwargs[field])

    # print("BEFORE UPDATE")
    # print(user.to_dict())
    if user.update_user():
        click.echo("Update success")


@click.command()
@click.option("--username", '-u', required=True, help='enter user name')
@click.option("--domain", '-d', required=True, help='enter domain name')
@click.pass_context
def delete(ctx, username, domain):
    """Delete user, input user name and domain name"""
    session = authorization(ctx.obj['url'])
    result = User(url=ctx.obj['url'], session=session).delete_user(username=username, domain_name=domain)
    click.echo(result)


user.add_command(get)
user.add_command(list)
user.add_command(create)
user.add_command(update)
user.add_command(delete)
