# Mihomo 覆写配置

这里的 `config.yaml` 是唯一需要维护的源配置。GitHub Actions 会根据它自动生成：

- `dist/openclash.conf`：OpenClash `[YAML]` 覆写模块
- `dist/clashmi.js`：ClashMi 自定义 JavaScript 覆写

机场原订阅仍然直接添加到 OpenClash 和 ClashMi，仓库中不保存机场链接、token 或节点信息。

## AI 节点策略

`🤖 AI` 中有三类选择：

- `🇯🇵 AI 日本故障转移`：仅在日本节点中故障转移；不会因延迟更低自动换节点。
- 原有四个地区自动测速组：适合日常访问。
- 机场全部原始节点：可直接手动固定一个具体节点，保持稳定出口 IP。

## 使用地址

OpenClash：

`https://raw.githubusercontent.com/busywl/mihomo-override/main/dist/openclash.conf`

ClashMi：

`https://raw.githubusercontent.com/busywl/mihomo-override/main/dist/clashmi.js`

以后只修改 `config.yaml` 并提交，Actions 完成后刷新客户端的覆写配置即可。
