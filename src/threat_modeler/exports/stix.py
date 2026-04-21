"""STIX export placeholder."""


class StixExporter:
    def export(self, canonical_graph: dict) -> dict:
        # TODO: Convert approved threat-model artifacts into STIX 2.1 objects.
        return {"type": "bundle", "objects": [], "source": canonical_graph.get("metadata", {})}
