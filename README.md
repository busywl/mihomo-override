# Mihomo 覆写配置

这里的 `config.yaml` 是唯一需要维护的源配置。GitHub Actions 会根据它自动生成：

- `dist/openclash.conf`：OpenClash `[YAML]` 覆写模块
- `dist/clashmi.js`：ClashMi 自定义 JavaScript 覆写

机场原订阅仍然直接添加到 OpenClash 和 ClashMi，仓库中不保存机场链接、token 或节点信息。

## 使用地址

OpenClash：

`https://raw.githubusercontent.com/busywl/CF-Workers-SUB/main/mihomo-override/dist/openclash.conf`

ClashMi：

`https://raw.githubusercontent.com/busywl/CF-Workers-SUB/main/mihomo-override/dist/clashmi.js`

以后只修改 `config.yaml` 并提交，Actions 完成后刷新客户端的覆写配置即可。
