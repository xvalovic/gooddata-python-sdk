# (C) 2025 GoodData Corporation
"""Write AAC (Analytics as Code) models to YAML files on disk."""

from __future__ import annotations

from pathlib import Path

import yaml
from gooddata_api_client.model.aac_analytics_model import AacAnalyticsModel
from gooddata_api_client.model.aac_logical_model import AacLogicalModel

from gooddata_sdk.catalog.workspace.aac.loader import (
    ATTRIBUTE_HIERARCHIES_DIR,
    DASHBOARDS_DIR,
    DATASETS_DIR,
    DATES_DIR,
    METRICS_DIR,
    PLUGINS_DIR,
    VISUALISATIONS_DIR,
)


def _get_id_from_model(obj) -> str:
    """Extract id from an AAC model object."""
    if hasattr(obj, "id") and obj.id is not None:
        return str(obj.id)
    return "unknown"


def _write_yaml(path: Path, data: dict) -> None:
    """Write dict to YAML file with consistent formatting."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fp:
        yaml.dump(
            data,
            fp,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False,
        )


def store_logical_model_aac(model: AacLogicalModel, path: Path) -> None:
    """Write AacLogicalModel to AAC YAML layout under the given path.

    Creates:
        - path/datasets/<id>.yaml
        - path/dates/<id>.yaml

    Args:
        model: AacLogicalModel from API
        path: Root path (e.g. analytics/)
    """
    if model.datasets:
        datasets_dir = path / DATASETS_DIR
        datasets_dir.mkdir(parents=True, exist_ok=True)
        for ds in model.datasets:
            obj_id = _get_id_from_model(ds)
            file_path = datasets_dir / f"{obj_id}.yaml"
            _write_yaml(file_path, ds.to_dict(camel_case=False))

    if model.date_datasets:
        dates_dir = path / DATES_DIR
        dates_dir.mkdir(parents=True, exist_ok=True)
        for dd in model.date_datasets:
            obj_id = _get_id_from_model(dd)
            file_path = dates_dir / f"{obj_id}.yaml"
            _write_yaml(file_path, dd.to_dict(camel_case=False))


def store_analytics_model_aac(model: AacAnalyticsModel, path: Path) -> None:
    """Write AacAnalyticsModel to AAC YAML layout under the given path.

    Creates:
        - path/metrics/<id>.yaml
        - path/visualisations/<id>.yaml
        - path/dashboards/<id>.yaml
        - path/attribute_hierarchies/<id>.yaml
        - path/plugins/<id>.yaml

    Args:
        model: AacAnalyticsModel from API
        path: Root path (e.g. analytics/)
    """
    if model.metrics:
        metrics_dir = path / METRICS_DIR
        metrics_dir.mkdir(parents=True, exist_ok=True)
        for m in model.metrics:
            obj_id = _get_id_from_model(m)
            file_path = metrics_dir / f"{obj_id}.yaml"
            _write_yaml(file_path, m.to_dict(camel_case=False))

    if model.visualizations:
        vis_dir = path / VISUALISATIONS_DIR
        vis_dir.mkdir(parents=True, exist_ok=True)
        for v in model.visualizations:
            obj_id = _get_id_from_model(v)
            file_path = vis_dir / f"{obj_id}.yaml"
            _write_yaml(file_path, v.to_dict(camel_case=False))

    if model.dashboards:
        dash_dir = path / DASHBOARDS_DIR
        dash_dir.mkdir(parents=True, exist_ok=True)
        for d in model.dashboards:
            obj_id = _get_id_from_model(d)
            file_path = dash_dir / f"{obj_id}.yaml"
            _write_yaml(file_path, d.to_dict(camel_case=False))

    if model.attribute_hierarchies:
        ah_dir = path / ATTRIBUTE_HIERARCHIES_DIR
        ah_dir.mkdir(parents=True, exist_ok=True)
        for ah in model.attribute_hierarchies:
            obj_id = _get_id_from_model(ah)
            file_path = ah_dir / f"{obj_id}.yaml"
            _write_yaml(file_path, ah.to_dict(camel_case=False))

    if model.plugins:
        plugins_dir = path / PLUGINS_DIR
        plugins_dir.mkdir(parents=True, exist_ok=True)
        for p in model.plugins:
            obj_id = _get_id_from_model(p)
            file_path = plugins_dir / f"{obj_id}.yaml"
            _write_yaml(file_path, p.to_dict(camel_case=False))
