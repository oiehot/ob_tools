#!python

import logging

import typer
from typing import Optional
from typing_extensions import Annotated

from ob_tools.utils.log_utils import setup_logger
from ob_tools.bin.snow import make_snow

def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"{__app_name__} v{__app_version__}")
        raise typer.Exit()

__app_name__: str = "GeometryNodeCLI"
__app_version__: str = "0.1.0"
_log = setup_logger("GeometryNodeCLI", logging.DEBUG)
app = typer.Typer()


@app.command()
def snow(
    input_blender: Annotated[str, typer.Option(help="Input Blender Filepath", rich_help_panel="File")],
    input_fbx: Annotated[str, typer.Option(help="Input FBX Filepath", rich_help_panel="File")],
    output_fbx: Annotated[str, typer.Option(help="Output FBX Filepath", rich_help_panel="File")],
    geometry_node: Annotated[str, typer.Option(help="Geometry Node Name", rich_help_panel="File")]="GN_Snow",
	density: Annotated[float, typer.Option(help="Snow Density", rich_help_panel="Snow")]=10000,
    voxel_size: Annotated[float, typer.Option(help="Snow Voxel Size", rich_help_panel="Snow")]=0.01,
    decimate: Annotated[bool, typer.Option(help="Run Decimate", rich_help_panel="Decimate")]=False,
    decimate_ratio: Annotated[float, typer.Option(help="Decimate Ratio", rich_help_panel="Decimate")]=0.1,
):
    make_snow(input_blender, geometry_node, input_fbx, output_fbx, density, voxel_size, decimate, decimate_ratio)


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Show the app version and exit.",
        callback=_version_callback,
        is_eager=True,
    )
) -> None:
    return


if __name__ == "__main__":
    app()