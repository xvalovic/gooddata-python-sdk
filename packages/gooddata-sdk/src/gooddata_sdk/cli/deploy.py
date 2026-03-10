# (C) 2024 GoodData Corporation
import argparse
from pathlib import Path

from gooddata_sdk import (
    CatalogDeclarativeDataSources,
    CatalogDeclarativeUserGroups,
    CatalogDeclarativeUsers,
    CatalogDeclarativeWorkspaceDataFilters,
    GoodDataSdk,
)
from gooddata_sdk.cli.constants import (
    BASE_DIR,
    CONFIG_FILE,
    DATA_SOURCES,
    USER_GROUPS,
    USERS,
    WORKSPACES,
    WORKSPACES_DATA_FILTERS,
)
from gooddata_sdk.cli.utils import measure_deploy
from gooddata_sdk.utils import profile_content


@measure_deploy(step=WORKSPACES)
def _deploy_workspaces_with_filters(sdk: GoodDataSdk, path: Path) -> None:
    """Deploy workspace LDM and analytics via AAC API (no gd CLI)."""
    analytics_root_dir = path / BASE_DIR
    if not analytics_root_dir.exists():
        raise ValueError(f"Analytics directory not found: {analytics_root_dir}")

    content = profile_content(profiles_path=path / CONFIG_FILE)
    workspace_id = content.get("workspace_id")
    if not workspace_id:
        raise ValueError(
            "workspace_id is required in gooddata.yaml profile for AAC deploy. "
            "Add workspace_id to your profile, e.g.: profiles.default.workspace_id: demo"
        )

    sdk.catalog_workspace_content.load_and_put_workspace_aac(
        workspace_id=workspace_id,
        path=path,
    )


@measure_deploy(step="data sources")
def _deploy_data_sources(sdk: GoodDataSdk, analytics_root_dir: Path) -> None:
    data_sources = CatalogDeclarativeDataSources.load_from_disk(analytics_root_dir)
    sdk.catalog_data_source.put_declarative_data_sources(
        data_sources, config_file=analytics_root_dir.parent / "gooddata.yaml"
    )


@measure_deploy(step="user groups")
def _deploy_user_groups(sdk: GoodDataSdk, analytics_root_dir: Path) -> None:
    user_groups = CatalogDeclarativeUserGroups.load_from_disk(analytics_root_dir)
    sdk.catalog_user.put_declarative_user_groups(user_groups)


@measure_deploy(step=USERS)
def _deploy_users(sdk: GoodDataSdk, analytics_root_dir: Path) -> None:
    users = CatalogDeclarativeUsers.load_from_disk(analytics_root_dir)
    sdk.catalog_user.put_declarative_users(users)


@measure_deploy(step="workspace data filters")
def _deploy_workspace_data_filters(sdk: GoodDataSdk, analytics_root_dir: Path) -> None:
    workspace_data_filters = CatalogDeclarativeWorkspaceDataFilters.load_from_disk(analytics_root_dir)
    sdk.catalog_workspace.put_declarative_workspace_data_filters(workspace_data_filters)


def deploy_all(path: Path) -> None:
    init_file = path / CONFIG_FILE
    sdk = GoodDataSdk.create_from_profile(profiles_path=init_file)

    analytics_root_dir = path / BASE_DIR

    print("Deploying the whole organization... ⏲️⏲️⏲️")
    _deploy_data_sources(sdk, analytics_root_dir)
    _deploy_user_groups(sdk, analytics_root_dir)
    _deploy_users(sdk, analytics_root_dir)
    _deploy_workspaces_with_filters(sdk, path)
    print("Deployed 🚀🚀🚀")


def deploy_granular(path: Path, args: argparse.Namespace) -> None:
    init_file = path / CONFIG_FILE
    analytics_root_dir = path / BASE_DIR
    selected_entities = set(args.only)
    sdk = GoodDataSdk.create_from_profile(profiles_path=init_file)
    if DATA_SOURCES in selected_entities:
        _deploy_data_sources(sdk, analytics_root_dir)
    if USER_GROUPS in selected_entities:
        _deploy_user_groups(sdk, analytics_root_dir)
    if USERS in selected_entities:
        _deploy_users(sdk, analytics_root_dir)
    if WORKSPACES_DATA_FILTERS in selected_entities:
        _deploy_workspace_data_filters(sdk, analytics_root_dir)
    if WORKSPACES in selected_entities:
        _deploy_workspaces_with_filters(sdk, path)
