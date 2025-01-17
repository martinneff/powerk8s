"""Powerk8s - a Powerline plugin for Kubernetes information.

Powerk8s reads the local $KUBECNOFIG and displays specified information, such
as:
- Current context
- Namespace
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, List, Mapping, Optional, Sequence

import yaml
from kubernetes.config.kube_config import (  # type: ignore
    KUBE_CONFIG_DEFAULT_LOCATION,
    KubeConfigLoader,
)
from powerline import PowerlineLogger  # type: ignore

KUBERNETES_LOGO: str = "\U00002388 "


class SegmentArg(Enum):
    """All possible Powerline segment argument types for Powerk8s."""

    SHOW_KUBERNETES_LOGO: str = "show_kube_logo"
    SHOW_CLUSTER: str = "show_cluster"
    SHOW_NAMESPACE: str = "show_namespace"
    SHOW_DEFAULT_NAMESPACE: str = "show_default_namespace"


class HighlightGroup(Enum):
    """All possible highlight groups for Powerk8s."""

    KUBERNETES_CLUSTER_ALERT: str = "kubernetes_cluster:alert"
    KUBERNETES_CLUSTER: str = "kubernetes_cluster"
    KUBERNETES_DIVIDER: str = "kubernetes:divider"
    KUBERNETES_NAMESPACE_ALERT: str = "kubernetes_namespace:alert"
    KUBERNETES_NAMESPACE: str = "kubernetes_namespace"


@dataclass
class SegmentData:
    """Encapsulates data for a Powerk8s segment."""

    # pylint: disable=unsubscriptable-object
    contents: Optional[str]
    highlight_groups: Sequence[str]
    # pylint: disable=unsubscriptable-object
    divider_highlight_group: Optional[str] = field(default="")


def get_kubernetes_logo(color: str) -> SegmentData:
    """Get the Kubernetes logo (it is hardcoded right now)."""
    return SegmentData(
        KUBERNETES_LOGO, [color], HighlightGroup.KUBERNETES_DIVIDER.value
    )


def get_segment_args(**kwargs: Any) -> Mapping[SegmentArg, Any]:
    """Get the arguments for a Powerk8s segment."""
    return {sa: kwargs.get(sa.value, None) for sa in SegmentArg}


def powerk8s(*_: Sequence[Any], **kwargs: Any) -> Sequence[Mapping[str, str]]:
    """Entry point to the plugin."""
    segment_args: Mapping[SegmentArg, Any] = get_segment_args(**kwargs)

    powerline_logger: PowerlineLogger = kwargs.get("pl", None)

    cfg: KubeConfigLoader = None
    with Path(KUBE_CONFIG_DEFAULT_LOCATION).expanduser().open() as file:
        cfg = KubeConfigLoader(yaml.load(file, Loader=yaml.SafeLoader))

    if powerline_logger is not None:
        powerline_logger.debug(f"Context: {cfg.current_context}")
        powerline_logger.debug(f"Segment arguments: {segment_args}")

    segments: List[SegmentData] = []

    if segment_args.get(SegmentArg.SHOW_KUBERNETES_LOGO, False):
        segments.append(get_kubernetes_logo(HighlightGroup.KUBERNETES_CLUSTER.value))

    if segment_args.get(SegmentArg.SHOW_CLUSTER, False):
        segments.append(
            SegmentData(
                contents=cfg.current_context["context"]["cluster"],
                highlight_groups=[HighlightGroup.KUBERNETES_CLUSTER.value],
                divider_highlight_group=HighlightGroup.KUBERNETES_NAMESPACE.value,
            )
        )

    if (
        segment_args.get(SegmentArg.SHOW_DEFAULT_NAMESPACE, False)
        and "namespace" in cfg.current_context["context"]
    ):
        segments.append(
            SegmentData(
                contents=cfg.current_context["context"]["namespace"],
                highlight_groups=[HighlightGroup.KUBERNETES_CLUSTER.value],
                divider_highlight_group=HighlightGroup.KUBERNETES_NAMESPACE.value,
            )
        )

    return [asdict(s) for s in segments]
