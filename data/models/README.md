# ML Model Configurations

**Purpose:** Centralized configuration for embedding models and ML artifacts used by RAG pipeline.

## Contents

- `embeddings.yaml`: Catalog of available embedding models with configurations

## embeddings.yaml Format

```yaml
models:
  - name: "model_identifier"
    dimension: 384
    speed: "fast|medium|slow"
    accuracy: "good|excellent"
    provider: "huggingface|openai|custom"
    config:
      batch_size: 32
      normalize: true
```

## Model Selection Criteria

- **Dimension**: Trade-off between performance and storage (384 vs 768 vs 1536)
- **Speed**: Inference latency for real-time queries
- **Accuracy**: Quality of embedding representations
- **Provider**: Licensing and deployment constraints

## Future Expansion

- Fine-tuned domain-specific models
- Multi-modal embeddings (text + diagrams)
- Quantized models for edge deployment
- Custom embedding layers

## Integration

```python
import yaml

with open("data/models/embeddings.yaml") as f:
    config = yaml.safe_load(f)
    
selected_model = next(m for m in config["models"] 
                     if m["name"] == "all-MiniLM-L6-v2")
```

## References

- HuggingFace Model Hub: https://huggingface.co/models
- MTEB Benchmark: https://huggingface.co/spaces/mteb/leaderboard
