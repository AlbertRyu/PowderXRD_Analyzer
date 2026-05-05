# PowderXRD Analyzer - Project Guidelines

## Python Execution

This project uses `uv` for dependency management. Always use `uv run` to execute Python code:

```bash
uv run python script.py
uv run python -c "print('hello')"
```

## Project Structure

- `powder_xrd_analyzer/` - Main Python package
- `scripts/` - Command-line scripts
- `examples/` - Example usage and Jupyter notebook
- `20260422/` - Sample XRD data files (.brml, .raw, .txt)

## Data Formats

- `.txt` - Bruker text format with [Data] section (CSV: 2θ, intensity)
- `.raw` - Bruker RAW4 binary format
- `.brml` - Bruker XML-based measurement format
