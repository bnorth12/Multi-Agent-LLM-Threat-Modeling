"""STIX export placeholder."""


class StixExporter:
    def export(self, canonical_graph) -> dict:
        # TODO: Convert approved threat-model artifacts into STIX 2.1 objects.
        graph_dict = canonical_graph.to_dict() if hasattr(canonical_graph, "to_dict") else canonical_graph
        return {"type": "bundle", "objects": [], "source": graph_dict.get("metadata", {})}
