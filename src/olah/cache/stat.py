# coding=utf-8
# Copyright 2024 XiaHan
#
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.

import os
import sys

import typer

from olah.cache.olah_cache import OlahCache


def get_size_human(size: int) -> str:
    if size > 1024 * 1024 * 1024:
        return f"{int(size / (1024 * 1024 * 1024)):.4f}GB"
    elif size > 1024 * 1024:
        return f"{int(size / (1024 * 1024)):.4f}MB"
    elif size > 1024:
        return f"{int(size / (1024)):.4f}KB"
    else:
        return f"{size:.4f}B"


def insert_newlines(input_str, every=10):
    return "\n".join(input_str[i:i + every] for i in range(0, len(input_str), every))


def main(
    file: str = typer.Option(..., "--file", "-f", help="The path of Olah cache file"),
    export: str = typer.Option("", "--export", "-e", help="Export the cached file if all blocks are cached"),
):
    with open(file, "rb") as f:
        f.seek(0, os.SEEK_END)
        bin_size = f.tell()

    try:
        cache = OlahCache(file)
    except Exception as e:
        print(e)
        sys.exit(1)
    print(f"File: {file}")
    print(f"Olah Cache Version: {cache.header.version}")
    print(f"File Size: {get_size_human(cache.header.file_size)}")
    print(f"Cache Total Size: {get_size_human(bin_size)}")
    print(f"Block Size: {cache.header.block_size}")
    print(f"Block Number: {cache.header.block_number}")
    print(f"Cache Status: ")
    cache_status = cache.header.block_mask.__str__()[:cache.header._block_number]
    print(insert_newlines(cache_status, every=50))

    if export != "":
        if all([c == "1" for c in cache_status]):
            with open(file, "rb") as f:
                f.seek(cache._get_header_size(), os.SEEK_SET)
                with open(export, "wb") as fout:
                    fout.write(f.read())
        else:
            print("Some blocks are not cached, so the export is skipped.")


if __name__ == "__main__":
    typer.run(main)
