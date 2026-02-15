# Contributing to VCP Specification

Thank you for your interest in contributing to the Value-Context Protocol specification.

## Types of Contributions

### Documentation Fixes

Typos, broken links, and clarifications can be submitted as pull requests directly. One reviewer approval is required.

### Specification Changes

Changes to the protocol specification follow the **VCP Enhancement Proposal (VEP)** process described in [GOVERNANCE.md](./GOVERNANCE.md):

1. Open a [Spec Amendment](https://github.com/Creed-Space/vcp-spec/issues/new?template=spec_amendment.yml) issue
2. A maintainer assigns a VEP number
3. 7-14 day discussion period (14 days minimum for breaking changes)
4. Decision recorded on the issue
5. Implementation via PR with spec text, schema updates, and SDK reference implementation

### Schema Changes

JSON Schema changes in `schemas/` must accompany a specification change. They cannot be submitted independently.

## Pull Request Process

1. Fork the repository and create a branch from `main`
2. Make your changes
3. Ensure all Markdown renders correctly
4. Submit a pull request with a clear description of the change and motivation
5. Reference the relevant VEP issue if applicable

## Style Guide

- **Markdown**: Use standard GitHub-flavored Markdown
- **Headings**: Use sentence case ("Identity encoding" not "Identity Encoding")
- **Code examples**: Use fenced code blocks with language identifiers
- **Tables**: Use Markdown tables with alignment
- **Links**: Use relative links within the repository

## Code of Conduct

This project adheres to the [Contributor Covenant Code of Conduct](./CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## Questions

Open a [Discussion](https://github.com/Creed-Space/vcp-spec/discussions) for questions about the specification or contributing process.
