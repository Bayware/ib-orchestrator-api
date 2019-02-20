import click
from .contract import Contract
from ib_orchestrator_api.core.utils import read_yaml_config
from ib_orchestrator_api.core.auth import authorization


@click.group()
@click.pass_context
def contract(ctx):
    pass


@click.command()
@click.option("--contract_name", '-c', help="contract_name")
@click.option("--domain_name", '-d', help="domain name")
@click.pass_context
def get(ctx, contract_name, domain_name):
    session = authorization(ctx.obj['url'])
    contract = Contract(url=ctx.obj['url'], session=session).get_contract(contract_name, domain_name)
    click.echo(contract.to_dict())
    print(contract.id)


@click.command()
@click.option("--domain_name", '-d', help='enter domain name')
@click.pass_context
def list(ctx, domain_name):
    pass


@click.command()
@click.option('--file', '-f', type=click.Path(exists=True))
@click.pass_context
def create(ctx, file):
    """Create Contract on server"""
    if not file:
        click.echo("None File")
    else:
        result = read_yaml_config(file)
        for resource_user in result['contracts']:
            # print(resource_user)
            session = authorization(ctx.obj['url'])
            contract = Contract(url=ctx.obj['url'], session=session, **resource_user)
            result = contract.create_contract()
            click.echo(result)


@click.command()
@click.pass_context
def update(ctx, username, domain_name, **kwargs):
    pass

@click.command()
@click.pass_context
def delete(ctx, username, domain_name):
    session = authorization(ctx.obj['url'])


contract.add_command(get)
contract.add_command(list)
contract.add_command(create)
contract.add_command(update)
contract.add_command(delete)
