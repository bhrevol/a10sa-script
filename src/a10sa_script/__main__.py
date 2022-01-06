"""Command-line interface."""
import click


@click.command()
@click.version_option()
def main() -> None:
    """A10SA Script."""


if __name__ == "__main__":
    main(prog_name="a10sa-script")  # pragma: no cover
