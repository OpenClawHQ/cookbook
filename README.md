# OpenClaw Cookbook

A collection of example OpenClaw plugins that demonstrate real-world patterns and best practices for plugin development.

## Examples

- **[github-connector](./examples/github-connector/)** - Fetch GitHub issues, PRs, and repository information via the GitHub API
- **[webhook-listener](./examples/webhook-listener/)** - Start an HTTP server to receive and process webhook payloads
- **[csv-processor](./examples/csv-processor/)** - Read, filter, transform, and aggregate CSV files

## Quick Start

Each example is a standalone plugin. To use an example:

```bash
# Clone or download the cookbook
git clone https://github.com/OpenClawHQ/cookbook.git
cd cookbook

# Navigate to an example
cd examples/github-connector

# Install dependencies
pip install -e .

# Run the plugin
python -m plugin
```

## Our Principles

**Build First, Ship Loud, Open by Default**

The OpenClaw cookbook follows these principles:
- **Build First**: Real, functional examples with genuine logic—not stubs
- **Ship Loud**: Examples are polished and ready to inspire
- **Open by Default**: All code is open source, MIT licensed, and community-driven

## Resources

- [Plugin Template](https://github.com/OpenClawHQ/plugin-template) - Start here for new plugins
- [OpenClaw CLI](https://github.com/OpenClawHQ/openclaw-cli) - Manage and run plugins locally
- [Contributing Guide](./CONTRIBUTING.md) - Add your own examples

## License

MIT License. See [LICENSE](./LICENSE) for details.
