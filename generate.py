#!/usr/bin/env python3
"""Generate OpenClash YAML and ClashMi JavaScript overrides from config.yaml."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "config.yaml"
DIST = ROOT / "dist"


def require_mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a mapping")
    return value


def require_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a non-empty string")
    return value


def load_source() -> dict[str, Any]:
    with SOURCE.open("r", encoding="utf-8") as handle:
        source = yaml.safe_load(handle) or {}

    source = require_mapping(source, "root")
    regions = require_mapping(source.get("regions"), "regions")
    if not regions:
        raise ValueError("regions must contain at least one region")

    for region_id, raw_region in regions.items():
        region = require_mapping(raw_region, f"regions.{region_id}")
        require_string(region.get("name"), f"regions.{region_id}.name")
        require_string(region.get("filter"), f"regions.{region_id}.filter")

    url_test = require_mapping(source.get("url_test"), "url_test")
    require_string(url_test.get("url"), "url_test.url")
    for key in ("interval", "tolerance"):
        if not isinstance(url_test.get(key), int) or isinstance(url_test.get(key), bool):
            raise ValueError(f"url_test.{key} must be an integer")
    if not isinstance(url_test.get("lazy"), bool):
        raise ValueError("url_test.lazy must be true or false")

    require_string(source.get("main_group"), "main_group")
    ai = require_mapping(source.get("ai"), "ai")
    require_string(ai.get("name"), "ai.name")
    ai_regions = ai.get("regions")
    if not isinstance(ai_regions, list) or not ai_regions:
        raise ValueError("ai.regions must be a non-empty list")
    unknown = [region_id for region_id in ai_regions if region_id not in regions]
    if unknown:
        raise ValueError(f"ai.regions contains unknown region ids: {', '.join(unknown)}")
    manual_node_group = ai.get("manual_node_group", "🌐 AI 手动节点")
    require_string(manual_node_group, "ai.manual_node_group")

    fallback_groups = ai.get("fallback_groups", [])
    if not isinstance(fallback_groups, list):
        raise ValueError("ai.fallback_groups must be a list")
    for index, raw_fallback in enumerate(fallback_groups):
        fallback = require_mapping(raw_fallback, f"ai.fallback_groups[{index}]")
        require_string(fallback.get("name"), f"ai.fallback_groups[{index}].name")
        fallback_region = require_string(
            fallback.get("region"), f"ai.fallback_groups[{index}].region"
        )
        if fallback_region not in regions:
            raise ValueError(
                f"ai.fallback_groups[{index}].region is unknown: {fallback_region}"
            )
        for key in ("interval", "max_failed_times"):
            if not isinstance(fallback.get(key), int) or isinstance(fallback.get(key), bool):
                raise ValueError(f"ai.fallback_groups[{index}].{key} must be an integer")

    return source


def build_model(source: dict[str, Any]) -> dict[str, Any]:
    regions = source["regions"]
    url_test = source["url_test"]
    main_group = source["main_group"]
    ai = source["ai"]

    region_names = [regions[region_id]["name"] for region_id in regions]
    region_groups: list[dict[str, Any]] = []
    for region_id, region in regions.items():
        region_groups.append(
            {
                "name": region["name"],
                "type": "url-test",
                "include-all": True,
                "exclude-type": "direct",
                "filter": region["filter"],
                "url": url_test["url"],
                "interval": url_test["interval"],
                "tolerance": url_test["tolerance"],
                "lazy": url_test["lazy"],
            }
        )

    fallback_groups: list[dict[str, Any]] = []
    for fallback in ai.get("fallback_groups", []):
        region = regions[fallback["region"]]
        fallback_groups.append(
            {
                "name": fallback["name"],
                "type": "fallback",
                "include-all": True,
                "exclude-type": "direct",
                "filter": region["filter"],
                "url": url_test["url"],
                "interval": fallback["interval"],
                "lazy": True,
                "max-failed-times": fallback["max_failed_times"],
            }
        )

    manual_node_group = {
        "name": ai.get("manual_node_group", "🌐 AI 手动节点"),
        "type": "select",
        "include-all": True,
        "exclude-type": "direct",
    }

    ai_group_name = ai["name"]
    ai_group = {
        "name": ai_group_name,
        "type": "select",
        "proxies": [fallback["name"] for fallback in fallback_groups]
        + [manual_node_group["name"]]
        + [regions[region_id]["name"] for region_id in ai["regions"]],
    }

    return {
        "main_group": main_group,
        "region_names": region_names,
        "region_groups": region_groups,
        "fallback_groups": fallback_groups,
        "manual_node_group": manual_node_group,
        "ai_group": ai_group,
        "ai_rule": f"GEOSITE,category-ai-!cn,{ai_group_name}",
    }


def write_openclash(model: dict[str, Any]) -> None:
    # OpenClash's [YAML] module syntax is intentionally used here:
    # proxy-groups+ appends groups, proxy-groups* updates the existing 良心云
    # group, and +rules prepends the AI rule without discarding airport rules.
    override = {
        "proxy-groups+": model["region_groups"]
        + model["fallback_groups"]
        + [model["manual_node_group"], model["ai_group"]],
        "proxy-groups*": {
            "where": {"name": model["main_group"]},
            "set": {"+proxies": model["region_names"]},
        },
        "+rules": [model["ai_rule"]],
    }
    content = "[YAML]\n\n" + yaml.safe_dump(
        override,
        allow_unicode=True,
        sort_keys=False,
        default_flow_style=False,
        width=120,
    )
    (DIST / "openclash.conf").write_text(content, encoding="utf-8")


def write_clashmi(model: dict[str, Any]) -> None:
    region_names = json.dumps(model["region_names"], ensure_ascii=False, indent=2)
    region_groups = json.dumps(model["region_groups"], ensure_ascii=False, indent=2)
    fallback_groups = json.dumps(model["fallback_groups"], ensure_ascii=False, indent=2)
    manual_node_group = json.dumps(model["manual_node_group"], ensure_ascii=False, indent=2)
    ai_group = json.dumps(model["ai_group"], ensure_ascii=False, indent=2)
    main_group = json.dumps(model["main_group"], ensure_ascii=False)
    ai_rule = json.dumps(model["ai_rule"], ensure_ascii=False)

    content = f'''/*
 * Auto-generated from config.yaml. Edit config.yaml instead of this file.
 * This script is intended for ClashMi's custom JavaScript override.
 */
function main(config) {{
  const regionNames = {region_names};
  const regionGroups = {region_groups};
  const fallbackGroups = {fallback_groups};
  const manualNodeGroup = {manual_node_group};
  const aiGroup = {ai_group};
  const mainGroupName = {main_group};
  const aiRule = {ai_rule};
  const fallbackGroupNames = fallbackGroups.map(function (group) {{ return group.name; }});
  const customGroupNames = regionNames.concat(fallbackGroupNames, [manualNodeGroup.name, aiGroup.name]);

  if (!Array.isArray(config["proxy-groups"])) {{
    config["proxy-groups"] = [];
  }}
  if (!Array.isArray(config.rules)) {{
    config.rules = [];
  }}

  // Make the script idempotent across every subscription refresh.
  config["proxy-groups"] = config["proxy-groups"].filter(function (group) {{
    return !group || customGroupNames.indexOf(group.name) === -1;
  }});
  config["proxy-groups"] = config["proxy-groups"].concat(regionGroups, fallbackGroups, [manualNodeGroup, aiGroup]);

  // Put the four region groups at the front of the existing 良心云 group.
  const mainGroup = config["proxy-groups"].find(function (group) {{
    return group && group.name === mainGroupName;
  }});
  if (mainGroup) {{
    const oldProxies = Array.isArray(mainGroup.proxies) ? mainGroup.proxies : [];
    mainGroup.proxies = regionNames.concat(oldProxies.filter(function (name) {{
      return regionNames.indexOf(name) === -1;
    }}));
  }} else {{
    console.warn("ClashMi override: group not found: " + mainGroupName);
  }}

  // Prepend the AI rule while preserving all original subscription rules.
  config.rules = config.rules.filter(function (rule) {{
    return !(typeof rule === "string" && /^GEOSITE,category-ai-!cn,/i.test(rule));
  }});
  config.rules.unshift(aiRule);

  console.log("ClashMi override: region groups and AI rule applied");
  return config;
}}
'''
    (DIST / "clashmi.js").write_text(content, encoding="utf-8")


def main() -> None:
    DIST.mkdir(parents=True, exist_ok=True)
    model = build_model(load_source())
    write_openclash(model)
    write_clashmi(model)
    print("Generated dist/openclash.conf and dist/clashmi.js")


if __name__ == "__main__":
    main()
