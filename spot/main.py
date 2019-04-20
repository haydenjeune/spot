import click
from spot.manager import SpotManager


@click.group()
@click.option("--profile", default="spot", type=click.STRING)
@click.option("--region", default="us-east-1", type=click.STRING)
@click.pass_context
def main(ctx, profile, region):
    """Main entry point for spot command line"""
    ctx.ensure_object(dict)
    # TODO: Move region selection to a config file
    ctx.obj["manager"] = SpotManager(profile, region)


@main.command()
@click.pass_context
def list(ctx):
    """Lists all instances in the default region and some useful information"""
    ctx.obj["manager"].list()


@main.command()
@click.argument('config_path')
@click.pass_context
def launch(ctx, config_path):
    """Launches an instance based on the config file at the path passed in"""
    # TODO: document which policies are required for this to work
    ctx.obj['manager'].launch(config_path)


@main.command()
@click.argument('instance_id')
@click.pass_context
def terminate(ctx, instance_id):
    """Terminates an instance based on the instance id"""
    ctx.obj["manager"].terminate(instance_id)


@main.command()
@click.argument('instance_id')
@click.argument('user')
@click.pass_context
def ssh(ctx, instance_id, user):
    """Opens an interactive ssh session to an instance based on the instance id"""
    ctx.obj["manager"].ssh(instance_id, user)


if __name__ == "__main__":
    main()
