#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 || -z ${1:-} ]]; then
  printf 'Usage: bash %s /path/to/skills\n' "$0" >&2
  exit 2
fi

source_dir=$(cd -P -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
assets=("$source_dir/SKILL.md" "$source_dir/LICENSE" "$source_dir/references" "$source_dir/assets")
for item in "${assets[@]}"; do
  if [[ ! -e $item ]]; then
    printf 'Missing skill file: %s\n' "$item" >&2
    exit 1
  fi
done

target_dir="$1/portfolio-source-reader"
mkdir -p -- "$1"
if ! mkdir -- "$target_dir"; then
  printf 'Could not create %s; existing files were not overwritten.\n' "$target_dir" >&2
  exit 1
fi

if ! cp -R -- "${assets[@]}" "$target_dir/"; then
  printf 'Copy failed; inspect the incomplete directory: %s\n' "$target_dir" >&2
  exit 1
fi
printf 'Installed to %s\n' "$target_dir"
