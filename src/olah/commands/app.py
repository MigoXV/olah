# coding=utf-8
# Copyright 2024 XiaHan
#
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.

"""
Olah CLI - Command Line Interface for Olah Huggingface Mirror Server

This module provides multiple entry points for different backend modes:
- proxy: Pure proxy mode, forwards requests to HuggingFace
- mirror: Local git mirror mode, serves from local git repositories
- model-bin: Model binary mode, serves from local model binary files
- s3: S3 storage mode, caches to S3-compatible storage
- serve: Full mode with all features (config file based)
"""

import typer

from olah.commands.proxy import proxy
from olah.commands.mirror import mirror
from olah.commands.model_bin import model_bin
from olah.commands.s3 import s3
from olah.commands.serve import serve

# Create main CLI app with subcommands
app = typer.Typer(
    name="olah-cli",
    help="Olah Huggingface Mirror Server CLI",
    no_args_is_help=True,
)

# Register commands
app.command()(proxy)
app.command()(mirror)
app.command(name="model-bin")(model_bin)
app.command()(s3)
app.command()(serve)


def main():
    app()


if __name__ == "__main__":
    app()
