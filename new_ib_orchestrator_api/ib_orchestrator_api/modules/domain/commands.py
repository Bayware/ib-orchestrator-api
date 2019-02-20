import click
from .domain import Domain
from ib_orchestrator_api.core.utils import read_yaml_config
from ib_orchestrator_api.core.auth import authorization


@click.group()
@click.pass_context
def domain(ctx):
    """Domain is a collection of Users, Nodes, and Topics.
    The visibility of a set of Users, Nodes, and Topic are limited by the domain boundaries.
    Domain serves as a logical division between different portions of the system."""
    pass


@click.command()
@click.argument('domain_name')
@click.pass_context
def get(ctx, domain_name):
    """Method return domain by name, if domain exists"""
    session = authorization(ctx.obj['url'])
    result = Domain(url=ctx.obj['url'], session=session).get_domain(domain_name)
    click.echo(result.to_dict())


@click.command()
@click.pass_context
def list(ctx):
    """Method retruns all domains that exist"""
    session = authorization(ctx.obj['url'])
    result = Domain(url=ctx.obj['url'], session=session).get_all_domains()
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
        for domain in result['domain']:
            # print(type(domain))
            # print(domain)
            session = authorization(ctx.obj['url'])
            domain = Domain(url=ctx.obj['url'], session=session, **domain)
            result = domain.create_domain()
            click.echo(result)


@click.command()
@click.option('domain_name', '-d', required=True, help='enter domain name')
@click.option('auth_method', '-auth', help='enter auth method')
@click.option('domain_description', '-descr', help='enter description')
@click.option('domain_type', '-type', help='enter domain type')
@click.pass_context
def update(ctx, domain_name, *args, **kwargs):
    """Update domain on server"""
    session = authorization(ctx.obj['url'])
    domain = Domain(url=ctx.obj['url'], session=session).get_domain(domain_name)
    # print(domain.to_dict())
    for field in kwargs:
        if not kwargs[field]:
            continue
        if field in vars(domain).keys():
            setattr(domain, field, kwargs[field])

    # print(domain.to_dict())
    if domain.update_domain():
        click.echo("Update success")


@click.command()
@click.option('domain_name', '-d', required=True, help='enter domain name')
@click.pass_context
def delete(ctx, domain_name):
    """Delete domain from server"""
    session = authorization(ctx.obj['url'])
    result = Domain(url=ctx.obj['url'], session=session).delete_domain(domain_name=domain_name)
    click.echo(result)


domain.add_command(get)
domain.add_command(list)
domain.add_command(create)
domain.add_command(update)
domain.add_command(delete)
