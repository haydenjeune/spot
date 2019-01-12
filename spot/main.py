import click
from spot.manager import SpotManager


@click.group()
@click.option("--profile", default="spot", type=click.STRING)
@click.pass_context
def main(ctx, profile):
    ctx.ensure_object(dict)
    ctx.obj["manager"] = SpotManager(profile)


@main.command()
@click.pass_context
def list(ctx):
    ctx.obj["manager"].list()


@main.command()
@click.pass_context
def launch(ctx):
    # TODO: document which policies are required for this to work
    ctx.obj['manager'].launch("spot/gpu.yaml")


@main.command()
@click.argument('instance_id')
@click.pass_context
def terminate(ctx, instance_id):
    ctx.obj["manager"].terminate(instance_id)


if __name__ == "__main__":
    main()
