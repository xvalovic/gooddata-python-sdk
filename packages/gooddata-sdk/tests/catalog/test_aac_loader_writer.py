# (C) 2025 GoodData Corporation
"""Unit tests for AAC YAML loader and writer."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from gooddata_sdk.catalog.workspace.aac.loader import (
    load_analytics_model_aac,
    load_logical_model_aac,
)
from gooddata_sdk.catalog.workspace.aac.writer import (
    store_analytics_model_aac,
    store_logical_model_aac,
)


@pytest.fixture
def analytics_dir_with_metric(tmp_path: Path) -> Path:
    """Create analytics/ with a minimal metric YAML."""
    metrics_dir = tmp_path / "metrics"
    metrics_dir.mkdir(parents=True)
    metric_yaml = """
id: test_metric
maql: "SELECT SUM({fact/amount})"
type: metric
title: Test Metric
"""
    (metrics_dir / "test_metric.yaml").write_text(metric_yaml.strip())
    return tmp_path


@pytest.fixture
def analytics_dir_with_dataset(tmp_path: Path) -> Path:
    """Create analytics/ with a minimal dataset YAML."""
    datasets_dir = tmp_path / "datasets"
    datasets_dir.mkdir(parents=True)
    dataset_yaml = """
id: test_dataset
type: dataset
data_source: demo_ds
title: Test Dataset
fields: {}
primary_key:
  columns: [id]
"""
    (datasets_dir / "test_dataset.yaml").write_text(dataset_yaml.strip())
    return tmp_path


def test_load_logical_model_aac_empty(tmp_path: Path) -> None:
    """Empty analytics dir returns empty AacLogicalModel."""
    model = load_logical_model_aac(tmp_path)
    assert model.datasets is None or len(model.datasets) == 0
    assert model.date_datasets is None or len(model.date_datasets) == 0


def test_load_logical_model_aac_with_dataset(analytics_dir_with_dataset: Path) -> None:
    """Load AacLogicalModel with one dataset."""
    model = load_logical_model_aac(analytics_dir_with_dataset)
    assert model.datasets is not None
    assert len(model.datasets) == 1
    assert model.datasets[0].id == "test_dataset"
    assert model.datasets[0].type == "dataset"
    assert model.datasets[0].data_source == "demo_ds"


def test_load_analytics_model_aac_empty(tmp_path: Path) -> None:
    """Empty analytics dir returns empty AacAnalyticsModel."""
    model = load_analytics_model_aac(tmp_path)
    assert model.metrics is None or len(model.metrics) == 0
    assert model.visualizations is None or len(model.visualizations) == 0


def test_load_analytics_model_aac_with_metric(analytics_dir_with_metric: Path) -> None:
    """Load AacAnalyticsModel with one metric."""
    model = load_analytics_model_aac(analytics_dir_with_metric)
    assert model.metrics is not None
    assert len(model.metrics) == 1
    assert model.metrics[0].id == "test_metric"
    assert model.metrics[0].maql == "SELECT SUM({fact/amount})"
    assert model.metrics[0].type == "metric"


def test_store_and_load_logical_model_roundtrip(
    analytics_dir_with_dataset: Path, tmp_path: Path
) -> None:
    """Store then load AacLogicalModel preserves data."""
    model = load_logical_model_aac(analytics_dir_with_dataset)
    store_logical_model_aac(model, tmp_path)
    loaded = load_logical_model_aac(tmp_path)
    assert loaded.datasets is not None
    assert len(loaded.datasets) == 1
    assert loaded.datasets[0].id == model.datasets[0].id
    assert loaded.datasets[0].data_source == model.datasets[0].data_source


def test_store_and_load_analytics_model_roundtrip(
    analytics_dir_with_metric: Path, tmp_path: Path
) -> None:
    """Store then load AacAnalyticsModel preserves data."""
    model = load_analytics_model_aac(analytics_dir_with_metric)
    store_analytics_model_aac(model, tmp_path)
    loaded = load_analytics_model_aac(tmp_path)
    assert loaded.metrics is not None
    assert len(loaded.metrics) == 1
    assert loaded.metrics[0].id == model.metrics[0].id
    assert loaded.metrics[0].maql == model.metrics[0].maql


def test_store_logical_model_creates_dirs(tmp_path: Path) -> None:
    """store_logical_model_aac creates datasets/ and dates/ dirs."""
    from gooddata_api_client.model.aac_dataset import AacDataset
    from gooddata_api_client.model.aac_logical_model import AacLogicalModel

    ds = AacDataset(
        id="ds1",
        type="dataset",
        data_source="ds",
        title="DS1",
        fields={},
        primary_key=["id"],
    )
    model = AacLogicalModel(datasets=[ds], date_datasets=[])
    store_logical_model_aac(model, tmp_path)
    assert (tmp_path / "datasets" / "ds1.yaml").exists()
    assert (tmp_path / "datasets" / "ds1.yaml").read_text().find("ds1") >= 0


def test_store_analytics_model_creates_dirs(tmp_path: Path) -> None:
    """store_analytics_model_aac creates metrics/ dir."""
    from gooddata_api_client.model.aac_analytics_model import AacAnalyticsModel
    from gooddata_api_client.model.aac_metric import AacMetric

    m = AacMetric(id="m1", maql="SELECT 1", type="metric", title="M1")
    model = AacAnalyticsModel(
        metrics=[m],
        visualizations=[],
        dashboards=[],
        attribute_hierarchies=[],
        plugins=[],
    )
    store_analytics_model_aac(model, tmp_path)
    assert (tmp_path / "metrics" / "m1.yaml").exists()
    assert (tmp_path / "metrics" / "m1.yaml").read_text().find("m1") >= 0
