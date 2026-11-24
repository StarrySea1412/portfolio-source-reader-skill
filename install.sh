#!/usr/bin/env bash
# 用法：./install.sh [skills-dir]；默认 ~/.zcode/skills
# 从脚本所在的包安装，已有目标退出；仅复制运行时资源。

set -euo pipefail

if [[ $# -gt 1 ]]; then
  printf '用法：%s [skills-dir]\n' "$0" >&2
  exit 2
fi
if [[ ${1:-} == --help || ${1:-} == -h ]]; then
  printf '用法：%s [skills-dir]\n默认：~/.zcode/skills\n' "$0"
  exit 0
fi

installation_package_dir="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
installation_skills_dir="${1:-$HOME/.zcode/skills}"
installation_skill_name="portfolio-source-reader"

fail_installation() {
  printf '安装失败：%s\n' "$1" >&2
  exit 1
}

installation_required_files=(
  SKILL.md LICENSE
  references/sources-map-template.md references/star-template.md
  references/evidence-rules.md references/examples.md
  assets/sources-map.example.md scripts/discover_sources.py
)
for installation_resource in "${installation_required_files[@]}"; do
  [[ -f "$installation_package_dir/$installation_resource" ]] ||
    fail_installation "包内缺少 $installation_resource"
done
for installation_resource in references assets scripts; do
  [[ -d "$installation_package_dir/$installation_resource" ]] ||
    fail_installation "包内缺少目录 $installation_resource"
done

installation_target_dir="$installation_skills_dir/$installation_skill_name"
[[ ! -e "$installation_target_dir" && ! -L "$installation_target_dir" ]] ||
  fail_installation "目标已存在：$installation_target_dir；请另选目录或自行处理现有安装"

mkdir -p -- "$installation_skills_dir"
installation_skills_root="$(CDPATH= cd -- "$installation_skills_dir" && pwd -P)"
installation_target_dir="${installation_skills_root%/}/$installation_skill_name"
[[ ! -e "$installation_target_dir" && ! -L "$installation_target_dir" ]] ||
  fail_installation "目标已存在：$installation_target_dir"

installation_stage_dir="$(mktemp -d "${installation_skills_root%/}/.portfolio-source-reader.install.XXXXXXXX")"

installation_stage_is_safe() {
  local installation_resolved_stage
  [[ -d "$installation_stage_dir" && ! -L "$installation_stage_dir" ]] || return 1
  [[ "$installation_stage_dir" == "${installation_skills_root%/}/.portfolio-source-reader.install."* ]] || return 1
  installation_resolved_stage="$(CDPATH= cd -- "$installation_stage_dir" && pwd -P)" || return 1
  [[ "$installation_resolved_stage" == "$installation_stage_dir" ]]
}

cleanup_installation_stage() {
  if [[ -n "$installation_stage_dir" ]] && installation_stage_is_safe; then
    rm -rf -- "$installation_stage_dir"
  fi
}
trap cleanup_installation_stage EXIT

installation_stage_is_safe || fail_installation '临时目录不在指定 skills 根目录内'
cp -R -- "$installation_package_dir/SKILL.md" "$installation_package_dir/LICENSE" \
  "$installation_package_dir/references" "$installation_package_dir/assets" \
  "$installation_package_dir/scripts" "$installation_stage_dir/"

[[ ! -e "$installation_target_dir" && ! -L "$installation_target_dir" ]] ||
  fail_installation "目标在复制期间出现：$installation_target_dir"
installation_stage_is_safe || fail_installation '临时目录已变化，未写入目标'
# GNU mv（Linux / Git Bash）：目标作为单个路径，且禁止覆盖竞态中出现的目标。
mv -T -n -- "$installation_stage_dir" "$installation_target_dir"
[[ ! -e "$installation_stage_dir" && ! -L "$installation_stage_dir" ]] ||
  fail_installation "目标已存在，未覆盖：$installation_target_dir"
installation_stage_dir=''

printf '已安装到 %s\n' "$installation_target_dir"
printf '对 agent 说：按 portfolio-source-reader 帮我挖 <项目名> 的经历素材。\n'
