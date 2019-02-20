import click
from ib_orchestrator_api.core.errors import IceBreakerError
from ib_orchestrator_api.modules.domain.commands import domain
from ib_orchestrator_api.modules.user.commands import user
from ib_orchestrator_api.modules.resource_user.commands import resource_user
from ib_orchestrator_api.modules.contract.commands import contract
from ib_orchestrator_api.modules.controller.commands import controller
from ib_orchestrator_api.modules.resources.commands import resources
from ib_orchestrator_api.modules.zone.commands import zone
from ib_orchestrator_api.modules.subnet.commands import subnet

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(context_settings=CONTEXT_SETTINGS)
@click.option('--hostname', '-host', required=True)
@click.pass_context
def bwctl_api(ctx, hostname):
    base_url = "http://%s/" % hostname
    ctx.obj = {
        'url': base_url}


bwctl_api.add_command(domain)
bwctl_api.add_command(user)
bwctl_api.add_command(resource_user)
bwctl_api.add_command(contract)
bwctl_api.add_command(controller)
bwctl_api.add_command(resources)
bwctl_api.add_command(zone)
bwctl_api.add_command(subnet)

if __name__ == '__main__':
    try:
        bwctl_api()
    except IceBreakerError as error:
        print(error.error_message)
