# US Strategy Top 60 · Google Play + App Store

美国区 Google Play Android 与 Apple App Store iPhone / Games / Strategy / Top Grossing 双榜日常跟踪页。

- Google榜单直接请求Google Play美国区 `GAME_STRATEGY / topgrossing` 榜单接口；AppBrain只作交叉检查，不再决定页面排名或日期
- 页面日期采用北京时间；Google记录直连抓取时间，Apple保留官方RSS更新时间
- 每个商店各60款游戏，ICON与单张商店图以内嵌静态资源保存，不依赖运行时图片外链
- 支持双商店切换、独立搜索/类型/状态筛选、排序、商店图放大与 CSV 导出
- 首页提供“当日双端市场动态”和“后续关注点”，日报自2026-08-26起按真实榜单日期存入 `reports/` 并开放 Markdown / JSON 下载
- 公司归属按产品、发行品牌与最终集团溯源，无法确认时标注“疑似”
- 新上榜按“近90天内上架且当前进入TOP60”判断；较老产品仅在取得同商店、同地区、同口径90天基准后判断是否提升超过5位

手动验证Google直连榜锚点：`python scripts/google_play_direct.py`

公开页面：<https://huangguaguaguagua.github.io/google-play-strategy-top60/>

日报归档清单：<https://huangguaguaguagua.github.io/google-play-strategy-top60/reports/manifest.json>
