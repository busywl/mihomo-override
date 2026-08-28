/*
 * Auto-generated from config.yaml. Edit config.yaml instead of this file.
 * This script is intended for ClashMi's custom JavaScript override.
 */
function main(config) {
  const regionNames = [
  "🇭🇰 香港节点",
  "🇯🇵 日本节点",
  "🇸🇬 新加坡节点",
  "🇺🇸 美国节点"
];
  const regionGroups = [
  {
    "name": "🇭🇰 香港节点",
    "type": "url-test",
    "include-all": true,
    "exclude-type": "direct",
    "filter": "(?i)香港|港|HK|Hong Kong|HongKong",
    "url": "https://www.gstatic.com/generate_204",
    "interval": 300,
    "tolerance": 0,
    "lazy": false
  },
  {
    "name": "🇯🇵 日本节点",
    "type": "url-test",
    "include-all": true,
    "exclude-type": "direct",
    "filter": "(?i)日本|日|JP|Japan|Tokyo|Osaka",
    "url": "https://www.gstatic.com/generate_204",
    "interval": 300,
    "tolerance": 0,
    "lazy": false
  },
  {
    "name": "🇸🇬 新加坡节点",
    "type": "url-test",
    "include-all": true,
    "exclude-type": "direct",
    "filter": "(?i)新加坡|狮城|SG|Singapore",
    "url": "https://www.gstatic.com/generate_204",
    "interval": 300,
    "tolerance": 0,
    "lazy": false
  },
  {
    "name": "🇺🇸 美国节点",
    "type": "url-test",
    "include-all": true,
    "exclude-type": "direct",
    "filter": "(?i)美国|美|US|USA|United States|Los Angeles|Seattle|San Jose",
    "url": "https://www.gstatic.com/generate_204",
    "interval": 300,
    "tolerance": 0,
    "lazy": false
  }
];
  const aiGroup = {
  "name": "🤖 AI",
  "type": "select",
  "proxies": [
    "🇯🇵 日本节点",
    "🇸🇬 新加坡节点",
    "🇺🇸 美国节点",
    "🇭🇰 香港节点"
  ]
};
  const mainGroupName = "良心云";
  const aiRule = "GEOSITE,category-ai-!cn,🤖 AI";
  const customGroupNames = regionNames.concat([aiGroup.name]);

  if (!Array.isArray(config["proxy-groups"])) {
    config["proxy-groups"] = [];
  }
  if (!Array.isArray(config.rules)) {
    config.rules = [];
  }

  // Make the script idempotent across every subscription refresh.
  config["proxy-groups"] = config["proxy-groups"].filter(function (group) {
    return !group || customGroupNames.indexOf(group.name) === -1;
  });
  config["proxy-groups"] = config["proxy-groups"].concat(regionGroups, [aiGroup]);

  // Put the four region groups at the front of the existing 良心云 group.
  const mainGroup = config["proxy-groups"].find(function (group) {
    return group && group.name === mainGroupName;
  });
  if (mainGroup) {
    const oldProxies = Array.isArray(mainGroup.proxies) ? mainGroup.proxies : [];
    mainGroup.proxies = regionNames.concat(oldProxies.filter(function (name) {
      return regionNames.indexOf(name) === -1;
    }));
  } else {
    console.warn("ClashMi override: group not found: " + mainGroupName);
  }

  // Prepend the AI rule while preserving all original subscription rules.
  config.rules = config.rules.filter(function (rule) {
    return !(typeof rule === "string" && /^GEOSITE,category-ai-!cn,/i.test(rule));
  });
  config.rules.unshift(aiRule);

  console.log("ClashMi override: region groups and AI rule applied");
  return config;
}
