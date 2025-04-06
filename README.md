# hexo-weread
获取微信读书的书单，包含笔记，并推送到自己的hexo博客

参考[malinkang/weread2notion: 将微信读书划线同步到Notion](https://github.com/malinkang/weread2notion?tab=readme-ov-file)

## 配置步骤

### 1. Fork 仓库并修改环境变量

Fork 本项目仓库后，需要修改 `.github/workflows/weread.yml` 文件里的环境变量为你自己的信息，具体如下：

- **`GITHUB_REPO`**：填写你要推送数据到的 GitHub 仓库名称，格式为 `用户名/仓库名`，例如 `GladiousZhang/gladiouszhang.github.io`。
- **`GITHUB_BRANCH`**：指定要推送数据到的 GitHub 仓库分支，一般为 `main` 或 `master`。
- **`DATA_DIR`**：指定数据文件（`books.json`）要存放的文件夹路径，例如 `data`。

### 2. 设置 Cookie

要获取微信读书的 Cookie，可以按以下步骤操作：

1. 打开微信读书网页版（https://weread.qq.com/），使用你的账号登录。
2. 登录成功后，打开浏览器的开发者工具（一般按 `F12` 或 `Ctrl + Shift + I` 打开）。
3. 在开发者工具中，切换到 `Network`（网络）选项卡。
4. 随便刷新一下微信读书页面，在请求列表中找到一个请求，然后查看其 `Headers`（请求头）部分。
5. 在请求头中找到 `Cookie` 字段，复制其内容。
6. 将复制的 Cookie 内容设置为环境变量 `WEREAD_COOKIE` 的值。你可以在 GitHub 仓库的 `Settings` -> `Secrets` 中添加该环境变量。

## 功能说明

本项目仅负责爬取你自己微信读书的书单信息，包含笔记内容，并将这些信息以 JSON 文件（`books.json`）的形式推送到你指定的 GitHub 仓库分支。具体如何在你的 Hexo 博客中对这些信息进行渲染展示，需要你自行完成。你可以编写 Hexo 插件或模板代码，读取 `books.json` 文件中的数据，并将其呈现在博客页面上。
