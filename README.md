# 欧洲科技商业日报

一个公开访问的中文静态日报网站，使用 GitHub Pages 托管。

## 目前包含
- 响应式中文首页，支持分类筛选、历史期数入口、复制网址和打印/PDF。
- `data/editions.json` 作为日报内容数据源。
- GitHub Actions 在推送到 `main` 或手动触发时自动部署网站。

## 发布一篇日报
编辑 `data/editions.json`，在 `editions` 数组最前面添加一期。示例结构：

```json
{
  "schema_version": 1,
  "updated_at": "2026-11-05T08:00:00+01:00",
  "editions": [
    {
      "date": "2026-11-05",
      "articles": [
        {
          "category": "消费电子",
          "published_at": "2026-11-05",
          "title": "新闻标题",
          "summary": "事实摘要。",
          "europe_impact": "对欧洲市场、渠道或产业竞争的影响。",
          "source_name": "来源名称",
          "source_url": "https://example.com/article"
        }
      ]
    }
  ]
}
```

支持分类：消费电子、AI与科技、商业与财经、国际与地缘政治。

## 自动部署
仓库已配置 GitHub Actions。每次向 `main` 推送，或在 Actions 页面手动运行 Deploy daily briefing site，都会重新发布静态网站。

首次启用请进入 **Settings → Pages**，将 **Build and deployment → Source** 设为 **GitHub Actions**。部署完成后，GitHub Actions 的部署记录会显示网站地址。

## 内容自动采编状态
当前版本已经具备网站和静态数据发布链路，但**尚未接入自动新闻采集、事实核验和每日内容生成**。后续需要单独配置可信新闻源与定时采编流程；不要把 API 密钥或访问令牌放进公开网页仓库。
