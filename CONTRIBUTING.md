# Contributing to OpenClaw Cookbook

Thank you for your interest in contributing to the OpenClaw Cookbook! We welcome new examples that demonstrate useful patterns and best practices.

## Adding a New Example

1. **Create a directory** under `examples/` with a descriptive name:
   ```
   examples/my-awesome-plugin/
   ├── README.md
   ├── pyproject.toml
   └── src/
       ├── __init__.py
       └── plugin.py
   ```

2. **Write a clear README** that explains:
   - What the plugin does
   - How to configure it (if needed)
   - How to run it
   - Example usage or output

3. **Implement the plugin** using the PluginBase pattern:
   - Include the PluginBase and PluginConfig classes inline (make it self-contained)
   - Use only Python standard library dependencies
   - Write genuine, functional code with real logic
   - Include docstrings

4. **Create pyproject.toml** with minimal, standard metadata:
   ```toml
   [build-system]
   requires = ["setuptools", "wheel"]
   build-backend = "setuptools.build_meta"

   [project]
   name = "openclaw-plugin-my-awesome-plugin"
   version = "0.1.0"
   description = "Brief description"
   ```

5. **Update the root README.md** to list your new example in the Examples section.

## Guidelines

- **Standalone**: Each example should be self-contained and runnable independently
- **No external dependencies**: Use only Python's standard library
- **Real logic**: Write functional code that actually does something, not stubs
- **Documentation**: Clear READMEs and inline comments
- **MIT Licensed**: All contributions are licensed under MIT

## Principles

Our cookbook follows the OpenClawHQ principles:
- **Build First**: Make something real and useful
- **Ship Loud**: Polish it and be proud of it
- **Open by Default**: Open source, transparent, community-driven

## Questions?

Open an issue or discussion in the repository!
