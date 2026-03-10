# (C) 2025 GoodData Corporation
"""Load AAC (Analytics as Code) models from YAML files on disk."""

from __future__ import annotations

from pathlib import Path

import yaml
from gooddata_api_client.model.aac_analytics_model import AacAnalyticsModel
from gooddata_api_client.model.aac_attribute_hierarchy import AacAttributeHierarchy
from gooddata_api_client.model.aac_dashboard import AacDashboard
from gooddata_api_client.model.aac_dataset import AacDataset
from gooddata_api_client.model.aac_date_dataset import AacDateDataset
from gooddata_api_client.model.aac_logical_model import AacLogicalModel
from gooddata_api_client.model.aac_metric import AacMetric
from gooddata_api_client.model.aac_plugin import AacPlugin
from gooddata_api_client.model.aac_visualization import AacVisualization

# AAC directory names (match gdc-analytics-as-code layout)
DATASETS_DIR = "datasets"
DATES_DIR = "dates"
METRICS_DIR = "metrics"
VISUALISATIONS_DIR = "visualisations"
DASHBOARDS_DIR = "dashboards"
ATTRIBUTE_HIERARCHIES_DIR = "attribute_hierarchies"
PLUGINS_DIR = "plugins"


def _load_yaml_files(dir_path: Path) -> list[dict]:
    """Load all YAML files from a directory, return list of parsed dicts."""
    if not dir_path.exists() or not dir_path.is_dir():
        return []
    result = []
    for pattern in ("*.yaml", "*.yml"):
        for f in sorted(dir_path.glob(pattern)):
            with open(f, encoding="utf-8") as fp:
                data = yaml.safe_load(fp)
                if data is not None:
                    result.append(data)
    return result


def _model_from_dict(model_class: type, data: dict):
    """Construct API model from dict with snake_case (camel_case=False)."""
    return model_class.from_dict(data, camel_case=False)


def _normalize_dataset_primary_key(data: dict) -> dict:
    """Normalize primary_key from YAML shape {columns: [...]} to list for AacDataset API."""
    data = dict(data)
    pk = data.get("primary_key")
    if isinstance(pk, dict) and "columns" in pk:
        data["primary_key"] = pk["columns"]
    return data


def _normalize_dashboard_aac(data: dict) -> dict:
    """Normalize dashboard payload into shape accepted by AAC set API."""
    if not isinstance(data, dict):
        return data

    # API accepts either tabbed OR non-tabbed dashboard shape.
    if data.get("tabs") and data.get("sections"):
        data = {k: v for k, v in data.items() if k != "sections"}

    def _normalize_widgets(sections: list[dict] | None) -> None:
        for section in sections or []:
            if not isinstance(section, dict):
                continue
            for widget in section.get("widgets", []) or []:
                if not isinstance(widget, dict):
                    continue
                # "inherit" matches two oneOf string schemas on server side.
                if widget.get("description") == "inherit":
                    widget["description"] = False
                # Disambiguate widget oneOf matching on write.
                if "type" not in widget:
                    if "visualization" in widget:
                        widget["type"] = "visualization"
                    elif "visualizations" in widget:
                        widget["type"] = "switcher"
                    elif "content" in widget:
                        widget["type"] = "rich_text"
                    elif "sections" in widget:
                        widget["type"] = "container"

    _normalize_widgets(data.get("sections"))
    for tab in data.get("tabs", []) or []:
        if isinstance(tab, dict):
            _normalize_widgets(tab.get("sections"))

    return data


def load_logical_model_aac(path: Path) -> AacLogicalModel:
    """Load AacLogicalModel from AAC YAML layout under the given path.

    Expects:
        - path/datasets/*.yaml - dataset definitions
        - path/dates/*.yaml - date dataset definitions

    Args:
        path: Root path (e.g. analytics/ or analytics root dir)

    Returns:
        AacLogicalModel with datasets and date_datasets
    """
    datasets_dir = path / DATASETS_DIR
    datasets = [
        _model_from_dict(AacDataset, _normalize_dataset_primary_key(data))
        for data in _load_yaml_files(datasets_dir)
    ]

    dates_dir = path / DATES_DIR
    date_datasets = [_model_from_dict(AacDateDataset, data) for data in _load_yaml_files(dates_dir)]

    return AacLogicalModel(
        datasets=datasets,
        date_datasets=date_datasets,
    )


def load_analytics_model_aac(path: Path) -> AacAnalyticsModel:
    """Load AacAnalyticsModel from AAC YAML layout under the given path.

    Expects:
        - path/metrics/*.yaml
        - path/visualisations/*.yaml
        - path/dashboards/*.yaml
        - path/attribute_hierarchies/*.yaml
        - path/plugins/*.yaml

    Args:
        path: Root path (e.g. analytics/)

    Returns:
        AacAnalyticsModel with metrics, visualizations, dashboards, etc.
    """
    metrics = [_model_from_dict(AacMetric, data) for data in _load_yaml_files(path / METRICS_DIR)]

    visualizations = [
        _model_from_dict(AacVisualization, data) for data in _load_yaml_files(path / VISUALISATIONS_DIR)
    ]

    dashboards = [
        _model_from_dict(AacDashboard, _normalize_dashboard_aac(data))
        for data in _load_yaml_files(path / DASHBOARDS_DIR)
    ]

    attribute_hierarchies = [
        _model_from_dict(AacAttributeHierarchy, data)
        for data in _load_yaml_files(path / ATTRIBUTE_HIERARCHIES_DIR)
    ]

    plugins = [_model_from_dict(AacPlugin, data) for data in _load_yaml_files(path / PLUGINS_DIR)]

    return AacAnalyticsModel(
        metrics=metrics,
        visualizations=visualizations,
        dashboards=dashboards,
        attribute_hierarchies=attribute_hierarchies,
        plugins=plugins,
    )
