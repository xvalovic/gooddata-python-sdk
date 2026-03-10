# (C) 2024 GoodData Corporation
import argparse
import shutil
from pathlib import Path

from gooddata_sdk import GoodDataSdk
from gooddata_sdk.cli.constants import (
    BASE_DIR,
    CONFIG_FILE,
    DATA_SOURCES,
    USER_GROUPS,
    USERS,
    WORKSPACES,
    WORKSPACES_DATA_FILTERS,
)
from gooddata_sdk.cli.utils import measure_clone
from gooddata_sdk.utils import profile_content


@measure_clone(step="workspaces")
def _clone_workspaces(sdk: GoodDataSdk, path: Path) -> None:
    """Clone workspace LDM and analytics via AAC API (no gd CLI)."""
    analytics_root_dir = path / BASE_DIR
    analytics_root_dir.mkdir(parents=True, exist_ok=True)

    content = profile_content(profiles_path=path / CONFIG_FILE)
    workspace_id = content.get("workspace_id")
    if not workspace_id:
        raise ValueError(
            "workspace_id is required in gooddata.yaml profile for AAC clone. "
            "Add workspace_id to your profile, e.g.: profiles.default.workspace_id: demo"
        )

    sdk.catalog_workspace_content.store_workspace_aac(
        workspace_id=workspace_id,
        path=path,
    )


@measure_clone(step="data sources")
def _clone_data_sources(sdk: GoodDataSdk, analytics_root_dir: Path) -> None:
    data_sources = sdk.catalog_data_source.get_declarative_data_sources()
    data_sources.store_to_disk(analytics_root_dir)


@measure_clone(step="user groups")
def _clone_user_groups(sdk: GoodDataSdk, analytics_root_dir: Path) -> None:
    user_groups = sdk.catalog_user.get_declarative_user_groups()
    user_groups.store_to_disk(analytics_root_dir)


@measure_clone(step="users")
def _clone_users(sdk: GoodDataSdk, analytics_root_dir: Path) -> None:
    users = sdk.catalog_user.get_declarative_users()
    users.store_to_disk(analytics_root_dir)


@measure_clone(step="workspace data filters")
def _clone_workspace_data_filters(sdk: GoodDataSdk, analytics_root_dir: Path) -> None:
    workspace_data_filters = sdk.catalog_workspace.get_declarative_workspace_data_filters()
    workspace_data_filters.store_to_disk(analytics_root_dir)


def clone_all(path: Path) -> None:
    init_file = path / CONFIG_FILE
    sdk = GoodDataSdk.create_from_profile(profiles_path=init_file)
    analytics_root_dir = path / BASE_DIR

    # clean the directory
    if analytics_root_dir.exists():
        shutil.rmtree(analytics_root_dir)
    # create directory
    analytics_root_dir.mkdir()

    print("Cloning the whole organization... ⏲️⏲️️⏲️️")
    _clone_data_sources(sdk, analytics_root_dir)
    _clone_user_groups(sdk, analytics_root_dir)
    _clone_users(sdk, analytics_root_dir)
    _clone_workspace_data_filters(sdk, analytics_root_dir)
    _clone_workspaces(sdk, path)
    print("Cloning finished 🚀🚀🚀")


def clone_granular(path: Path, args: argparse.Namespace) -> None:
    init_file = path / CONFIG_FILE
    analytics_root_dir = path / BASE_DIR
    sdk = GoodDataSdk.create_from_profile(profiles_path=init_file)
    selected_entities = set(args.only)
    if DATA_SOURCES in selected_entities:
        _clone_data_sources(sdk, analytics_root_dir)
    if USER_GROUPS in selected_entities:
        _clone_user_groups(sdk, analytics_root_dir)
    if USERS in selected_entities:
        _clone_users(sdk, analytics_root_dir)
    if WORKSPACES_DATA_FILTERS in selected_entities:
        _clone_workspace_data_filters(sdk, analytics_root_dir)
    if WORKSPACES in selected_entities:
        _clone_workspaces(sdk, path)
