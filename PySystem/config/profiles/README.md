# Runtime Profiles

This directory holds JSON profiles for different lab setups used by
`run.py`. Each profile defines paths and node names for a particular
environment. Copy one of these files and adjust the paths to match your
system.

## Available Profiles

### `default.json`
Example configuration for a generic lab with two Linux nodes. Paths use
placeholders such as `/path/to/fpx_auto/` that should be replaced with
real locations.

### `office.json`
Configuration for a single-node office environment. Useful when running
on a laptop or inside a minimal lab.
