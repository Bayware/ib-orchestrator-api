import click
from ib_orchestrator_api.core.errors import IceBreakerError
from ib_orchestrator_api.modules.domain.commands import domain
from ib_orchestrator_api.modules.user.commands import user
from ib_orchestrator_api.modules.resource_user.commands import resource_user

@click.group()
@click.option('--hostname', '-h', required=True)
@click.pass_context
def bwctl_api(ctx, hostname):
    base_url = "http://%s/" % hostname
    ctx.obj = {
               'url': base_url}


bwctl_api.add_command(domain)
bwctl_api.add_command(user)
bwctl_api.add_command(resource_user)

if __name__ == '__main__':
    try:
        bwctl_api()
    except IceBreakerError as error:
        print(error.error_message)