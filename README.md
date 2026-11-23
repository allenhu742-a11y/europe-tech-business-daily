# 欧洲科技商业日报

公开访问的中文静态日报网站，使用 GitHub Pages 托管。

## 网站与数据
- 网站：https://allenhu742-a11y.github.io/europe-tech-business-daily/
- 数据源：\`data/editions.json\`；每期按日期倒序追加，历史期数不覆盖。
- 首页支持分类筛选、历史归档、复制网址和打印/PDF。
- 每条新闻支持事实摘要、核心看点、行业分析、欧洲市场影响、后续观察和来源链接；有可核验图片时显示图片及来源。

## 每日自动采编与发布
工作流 \`.github/workflows/freshness-check.yml\` 已升级为每日自动采编发布：
1. 在华沙当地时间08:00运行（兼容夏令时/冬令时）。
2. 调用 OpenAI Responses API 的 web search 检索并核验新闻。
3. 生成严格5条中文分析，校验字段、日期和来源链接。
4. 将新一期追加到 \`data/editions.json\`，不覆盖历史。
5. 提交到 \`main\`；\`pages.yml\` 检测到提交后自动部署 GitHub Pages。
6. 生成、API、校验或发布失败时创建/更新 GitHub Issue，避免静默失败。

### 必须完成一次密钥配置
自动采编需要 OpenAI API 账户和可用 API 额度。ChatGPT 订阅不等于 API 额度。

在 GitHub 仓库打开：
**Settings → Secrets and variables → Actions → New repository secret**

添加：
- Name：\`OPENAI_API_KEY\`
- Secret：你的 OpenAI API key

密钥只保存在 GitHub Actions Secrets，不会写入公开仓库。默认使用 \`gpt-6.2-sol\`，可在 workflow 的 \`OPENAI_MODEL\` 环境变量中调整。

### 手动测试
配置密钥后，进入 **Actions → Generate and publish daily briefing → Run workflow**。
手动触发会立即运行，不受08:00时间限制。成功后检查：
- \`data/editions.json\` 顶部是否出现当天日期；
- **Deploy daily briefing site** 是否成功；
- 网站显示的“数据更新时间”和最新一期是否更新。

### 故障排查
- 自动发布失败会在仓库 Issues 中创建“日报自动发布失败”问题，并附 Actions 运行链接。
- 若未配置 \`OPENAI_API_KEY\`，工作流会明确失败并在 Issue 中提示，不会伪造日报或覆盖历史。
- 若当天内容已存在，脚本会跳过，避免重复期次。
- \`pages.yml\` 仍负责网站部署；自动采编工作流负责内容生成和提交，两者职责分开。

## 本地数据结构
每期包含 \`date\`、\`title\`、\`intro\` 和 \`articles\`。每条文章包括分类、发布日期、事实摘要、核心看点、行业分析、欧洲市场影响、后续观察和来源链接。图片字段只在有可核验图片及来源时填写。
