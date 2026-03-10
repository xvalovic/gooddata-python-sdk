# (C) 2024 GoodData Corporation
import argparse
from pathlib import Path

from gooddata_sdk.cli.clone import clone_all, clone_granular
from gooddata_sdk.cli.constants import CONFIG_FILE
from gooddata_sdk.cli.deploy import deploy_all, deploy_granular
from gooddata_sdk.cli.utils import _SUPPORTED, Bcolors


def get_manifest_directory() -> Path:
    """
    Find the directory containing gooddata.yaml by walking up from cwd.
    """
    cwd = Path.cwd().resolve()
    current = cwd
    while True:
        if (current / CONFIG_FILE).exists():
            return current
        parent = current.parent
        if parent == current:
            print(f"{Bcolors.FAIL}Manifest {CONFIG_FILE} was not found. Run from a project with gooddata.yaml.{Bcolors.ENDC}")
            raise SystemExit(1)
        current = parent


def _deploy(path: Path, args: argparse.Namespace) -> None:
    """
    Handles deploy command use cases.
    """
    if not path.is_dir():
        raise ValueError(f"Path {path} is not a directory.")

    if args.only is None:
        deploy_all(path)
    else:
        deploy_granular(path, args)


def _clone(path: Path, args: argparse.Namespace) -> None:
    """
    Handles clone command use cases.
    """
    if args.only is None:
        clone_all(path)
    else:
        clone_granular(path, args)


def main() -> None:
    """
    The entrypoint for gdc cli.
    """
    parser = argparse.ArgumentParser(
        prog="gdc",
        description="Process GoodData as code file structure (AAC-only, no gd CLI). "
        "Note that this is an EXPERIMENTAL feature.",
    )
    parser.add_argument("action", help="Specify if you want to deploy or clone project.", choices=("deploy", "clone"))
    parser.add_argument("--only", help="Specify available granularity for action.", nargs="+", choices=_SUPPORTED)

    args = parser.parse_args()
    manifest_directory = get_manifest_directory()
    if args.action == "clone":
        _clone(manifest_directory, args)
    elif args.action == "deploy":
        _deploy(manifest_directory, args)


if __name__ == "__main__":
    main()
