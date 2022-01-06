"""Command-line interface."""
import click


@click.command()
@click.version_option()
def main() -> None:
    """Vorze Script."""


if __name__ == "__main__":
    main(prog_name="vorze-script")  # pragma: no cover
