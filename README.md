# 厄尔尼诺数据监控面板 🌡️

基于同花顺 thsdk 的实时行情监控面板。

## 功能

- 📊 4大板块实时行情（农业、电力、家电、有色）
- 📈 板块走势对比图（ECharts）
- 🔄 自动刷新（30秒）

## 快速开始

### 方式1：本地运行（推荐开发）

```bash
cd elnino-dashboard
pip install thsdk
python server.py
# 浏览器打开 http://localhost:5000
```

### 方式2：部署到 GitHub Pages

```bash
# 1. 推送到 GitHub 仓库
git init
git add .
git commit -m "init"
git remote add origin https://github.com/你的用户名/elnino-dashboard.git
git push -u origin main

# 2. 在 GitHub 仓库设置 Pages
# Settings → Pages → Source: main branch → Save
```

## 技术架构

```
前端: HTML + Vue3 + ECharts
后端: Python Flask + thsdk (数据获取)
托管: GitHub Pages (前端) + Railway/Render (后端API)
```

## 目录结构

```
elnino-dashboard/
├── index.html      # 前端页面
├── server.py      # 数据API服务器
├── package.json  # Node配置
└── README.md
```

## 环境变量

如需使用自己的同花顺账户，创建 `.env` 文件：

```bash
THS_USERNAME=你的用户名
THS_PASSWORD=你的密码
THS_MAC=你的MAC地址
```

## 注意事项

⚠️ thsdk 游客模式有并发限制，建议生产环境使用自己的账户

⚠️ GitHub Pages 在国内访问可能不稳定，可考虑国内托管平台