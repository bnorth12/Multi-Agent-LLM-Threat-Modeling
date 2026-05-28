"""
STIX 2.1 exporter — maps canonical graph threats and mitigations to STIX objects.

Each threat becomes an ``attack-pattern`` STIX object.
Each mitigation (technical or administrative) becomes a ``course-of-action`` object.
Relationships between them are emitted as ``mitigates`` relationship objects.
All objects are wrapped in a STIX ``Bundle``.
"""

from __future__ import annotations

import uuid
from typing import Any

import stix2

from ..models import CanonicalThreatModelGraph
from ..models.canonical import Threat, Mitigation


def _stix_id(type_name: str) -> str:
    return f"{type_name}--{uuid.uuid4()}"


def _attack_pattern(threat: Threat) -> stix2.AttackPattern:
    ext_refs = []
    if threat.mitre_attack_technique:
        for technique in threat.mitre_attack_technique:
            ext_refs.append(
                stix2.ExternalReference(
                    source_name="mitre-attack",
                    external_id=technique,
                )
            )
    if threat.capec_id:
        ext_refs.append(
            stix2.ExternalReference(source_name="capec", external_id=threat.capec_id)
        )
    if threat.cwe_id:
        ext_refs.append(
            stix2.ExternalReference(source_name="cwe", external_id=threat.cwe_id)
        )

    kwargs: dict[str, Any] = {
        "name": threat.name,
        "description": threat.description,
    }
    if ext_refs:
        kwargs["external_references"] = ext_refs

    return stix2.AttackPattern(**kwargs)


def _course_of_action(mitigation: Mitigation) -> stix2.CourseOfAction:
    return stix2.CourseOfAction(
        name=mitigation.title,
        description=mitigation.description,
    )


def export_stix(graph: CanonicalThreatModelGraph) -> stix2.Bundle:
    """Return a STIX 2.1 Bundle containing attack-patterns, courses-of-action, and relationships.

    Parameters
    ----------
    graph:
        The canonical threat model graph to export.

    Returns
    -------
    stix2.Bundle
        A STIX 2.1 bundle with all threat and mitigation objects.
    """
    objects: list[Any] = []

    for iface in graph.interfaces:
        for threat in iface.threats:
            ap = _attack_pattern(threat)
            objects.append(ap)

            all_mitigations = list(threat.mitigations_technical) + list(
                threat.mitigations_administrative
            )
            for mitigation in all_mitigations:
                coa = _course_of_action(mitigation)
                objects.append(coa)
                rel = stix2.Relationship(
                    relationship_type="mitigates",
                    source_ref=coa.id,
                    target_ref=ap.id,
                )
                objects.append(rel)

    if not objects:
        # Return an empty bundle rather than raising.
        return stix2.Bundle()

    return stix2.Bundle(objects=objects)
