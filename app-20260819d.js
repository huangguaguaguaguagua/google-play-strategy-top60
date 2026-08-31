"use strict";

const CACHE_VERSION = "20260831b";
const MARKET_BRIEF_PATH = "data/market-brief-20260831.json";
const REPORTS_MANIFEST_PATH = "reports/manifest.json";
const STORE_CONFIGS = {
  googlePlay: {
    key: "googlePlay",
    queryValue: "google-play",
    mark: "GP",
    storeName: "Google Play",
    platform: "Android",
    date: "2026-08-31",
    baselineDate: "2026-06-02",
    eyebrow: "GOOGLE PLAY · ANDROID · STRATEGY · TOP GROSSING",
    title: "Google Play 美国区策略游戏畅销榜 TOP60",
    headerMeta: "每日跟踪 · 美国区 · Android",
    footer: "Google Play US Strategy · TOP60 · Direct capture 2026-08-31",
    method: "直接请求Google Play美国区 GAME_STRATEGY 的 topgrossing 榜单接口，完整校验TOP60；本次直连抓取时间为2026-08-31 10:29:00（北京时间）。AppBrain仅作交叉检查（重合60款、同位45款、最大位差2位），未覆盖直连结果。",
    baselineCopy: "<strong>状态窗口：</strong>2026-06-02 → 2026-08-31。近90天内上架且当前进入TOP60的5款产品标为新上榜；较老产品因缺少精确基准快照，暂不判断飙升。",
    games: "data/games-20260831.json",
    enrichment: "data/enrichment-20260831.json",
    trends: "data/trends-20260831.json",
    counterpartGames: "data/ios-games-20260831.json",
    counterpartRankLabel: "iOS",
    assetManifest: "assets/manifest.json",
    linkHeader: "Google Play 链接",
    csvSlug: "google-play-us-strategy-top60",
    hasInstallEstimate: true,
  },
  ios: {
    key: "ios",
    queryValue: "ios",
    mark: "AS",
    storeName: "App Store",
    platform: "iPhone · iOS",
    date: "2026-08-31",
    baselineDate: "2026-06-02",
    eyebrow: "APPLE APP STORE · iPHONE · STRATEGY · TOP GROSSING",
    title: "App Store 美国区策略游戏畅销榜 TOP60",
    headerMeta: "每日跟踪 · 美国区 · iPhone",
    footer: "Apple App Store US iPhone Strategy · TOP60 · Updated 2026-08-31",
    method: "Apple App Store 美国区 iPhone Games > Strategy 畅销榜，按Apple官方公开RSS同口径收录TOP60；RSS更新时间为2026-08-30 19:25:42（美国太平洋时间），换算北京时间为8月31日。",
    baselineCopy: "<strong>状态窗口：</strong>2026-06-02 → 2026-08-31。近90天内上架且当前进入TOP60的3款产品标为新上榜；iOS精确排名历史从2026-08-19开始积累，较老产品暂不判断飙升。",
    games: "data/ios-games-20260831.json",
    enrichment: "data/ios-enrichment-20260831.json",
    trends: "data/ios-trends-20260831.json",
    counterpartGames: "data/games-20260831.json",
    counterpartRankLabel: "Google",
    assetManifest: "assets/ios-manifest.json",
    linkHeader: "App Store 链接",
    csvSlug: "apple-app-store-us-iphone-strategy-top60",
    hasInstallEstimate: false,
  },
};

const requestedStore = new URLSearchParams(window.location.search).get("store");
const initialStore = requestedStore === "ios" ? "ios" : "googlePlay";
const state = { store: initialStore, games: [], visible: [], datasets: {}, loadToken: 0 };

const elements = {
  search: document.querySelector("#search"),
  genre: document.querySelector("#genre"),
  status: document.querySelector("#status"),
  sort: document.querySelector("#sort"),
  body: document.querySelector("#ranking-body"),
  resultCount: document.querySelector("#result-count"),
  totalCount: document.querySelector("#total-count"),
  tooltip: document.querySelector("#trend-tooltip"),
  modal: document.querySelector("#image-modal"),
  modalImage: document.querySelector("#modal-image"),
  modalRank: document.querySelector("#modal-rank"),
  modalTitle: document.querySelector("#modal-title"),
  modalKeywords: document.querySelector("#modal-keywords"),
  marketBriefLead: document.querySelector("#market-brief-lead"),
  marketBriefDate: document.querySelector("#market-brief-date"),
  marketBriefDownload: document.querySelector("#market-brief-download"),
  marketBriefJson: document.querySelector("#market-brief-json"),
  marketPlatforms: document.querySelector("#market-platforms"),
  marketNewsMethod: document.querySelector("#market-news-method"),
  marketNewsList: document.querySelector("#market-news-list"),
  marketClosingList: document.querySelector("#market-closing-list"),
  reportList: document.querySelector("#report-list"),
};

function config() {
  return STORE_CONFIGS[state.store];
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function safeUrl(value) {
  try {
    const url = new URL(value);
    return ["https:", "http:"].includes(url.protocol) ? url.href : "#";
  } catch {
    return "#";
  }
}

function safeLocalPath(value) {
  const path = String(value ?? "").trim();
  if (!/^(reports|data)\/[a-z0-9._/-]+$/i.test(path) || path.includes("..")) return "#";
  return path;
}

function safeInlineImage(value) {
  const source = String(value ?? "").trim();
  return /^data:image\/(?:png|jpe?g|webp|gif);base64,[a-z0-9+/=]+$/i.test(source) ? source : "";
}

function padRank(rank) {
  return String(rank).padStart(2, "0");
}

function parseInstalls(value = "0") {
  const number = Number.parseFloat(String(value).replaceAll(",", "")) || 0;
  if (/M/i.test(value)) return number * 1_000_000;
  if (/K/i.test(value)) return number * 1_000;
  return number;
}

function productKey(name) {
  const normalized = String(name ?? "")
    .normalize("NFKD")
    .toLowerCase()
    .replaceAll("™", "")
    .replaceAll("®", "")
    .replace(/[^a-z0-9]+/g, " ")
    .trim();
  const aliases = {
    "last war survival game": "last war survival",
    "evony the king s return": "evony",
    "rise of kingdoms lost crusade": "rise of kingdoms",
    "age of origins tower defense": "age of origins",
    "forge master idle rpg": "forge master",
    "marvel snap hero strategy ccg": "marvel snap",
    "marvel snap hero card game": "marvel snap",
    "top force commander": "top force",
    "kingdom guard tower defense td": "kingdom guard tower defense",
  };
  return aliases[normalized] || normalized;
}

function statusLabel(game) {
  const comparison = game.comparison90d || {};
  if (comparison.status === "new") return "近3月新";
  if (comparison.status === "surge") return "近3月 ↑" + comparison.delta;
  return "常规";
}

function sourceAuditText(audit) {
  const labels = (audit.sources || []).map((source) => source.label).join("、");
  return "状态：" + audit.status + "；可信度：" + audit.confidence + "；" +
    audit.basis + " 纠偏说明：" + audit.changeReason + " 来源：" + labels + "。";
}

function lifecycleAuditText(audit) {
  const labels = (audit.sources || []).map((source) => source.label).join("、");
  return "可信度：" + audit.confidence + "；" + audit.scope + " " +
    audit.evidenceNote + " 来源：" + labels + "。";
}

function fullTrendText(trend) {
  const sections = trend.sections;
  const items = [
    "上线后发展：" + sections.development,
    "榜位走向：" + sections.rankPath,
    "关键转折：" + sections.turningPoints,
    "主力素材：" + sections.creative,
    "后续观察：" + sections.watch,
  ];
  return items.join(" ");
}

function trendSummaryHtml(summary) {
  const text = String(summary ?? "");
  const turningMarker = "；关键转折：";
  const creativeMarker = "；主力素材：";
  const turningIndex = text.indexOf(turningMarker);
  const creativeIndex = text.indexOf(creativeMarker);
  if (turningIndex < 0 || creativeIndex < turningIndex) {
    return "<span>" + escapeHtml(text) + "</span>";
  }
  return [
    text.slice(0, turningIndex + 1),
    text.slice(turningIndex + 1, creativeIndex + 1),
    text.slice(creativeIndex + 1),
  ].map((section) => "<span>" + escapeHtml(section) + "</span>").join("");
}

function mergeData(rawGames, enrichment, assets, trends, counterpartGames, counterpartRankLabel) {
  const counterpartByProduct = new Map(counterpartGames.map((game) => [productKey(game.gameName), game]));
  return rawGames.map((game) => {
    const key = String(game.rank);
    const company = enrichment.productCompaniesByRank?.[key] ?? {
      en: game.developer,
      cn: "归属待核验",
      confidence: "待核验",
      basis: "暂无补充溯源信息。",
      source: game.storeUrl,
    };
    const assetPrefix = padRank(game.assetRank ?? game.rank);
    const trend = trends[key] ?? {
      summary: game.note || "趋势资料待补充。",
      sections: { development: "待补充。", rankPath: "待补充。", turningPoints: "待补充。", creative: "待补充。", watch: "待补充。" },
    };
    const counterpart = counterpartByProduct.get(productKey(game.gameName));
    return {
      ...game,
      company,
      trend,
      counterpartRank: counterpart?.rank ?? null,
      counterpartRankLabel,
      status: game.comparison90d?.status || "pending",
      icon: game.iconData || assets[assetPrefix + "_icon"],
      storeImage: game.storeImageData || assets[assetPrefix + "_store"],
    };
  });
}

async function fetchJson(path, label) {
  const response = await fetch(path + "?v=" + CACHE_VERSION);
  if (!response.ok) throw new Error(label + "加载失败：" + response.status);
  return response.json();
}

function movementProductHtml(item, icons) {
  const tone = ["entry", "exit", "up", "down"].includes(item.tone) ? item.tone : "flat";
  const icon = safeInlineImage(icons[item.iconKey]);
  const iconHtml = icon
    ? '<img src="' + icon + '" alt="' + escapeHtml(item.gameName) + ' ICON" loading="lazy">'
    : '<span class="market-product__fallback" aria-hidden="true">' + escapeHtml(item.gameName.slice(0, 1)) + '</span>';
  return '<article class="market-product market-product--' + tone + '">' +
    '<div class="market-product__icon">' + iconHtml + '</div><div class="market-product__body">' +
    '<div class="market-product__top"><strong>' + escapeHtml(item.gameName) + '</strong>' +
    '<span class="market-move market-move--' + tone + '">' + escapeHtml(item.changeLabel) + '</span></div>' +
    '<p>' + escapeHtml(item.analysis) + '</p></div></article>';
}

function rankingPlatformHtml(platform, key, icons) {
  const badge = key === "googlePlay" ? "ANDROID" : "iPHONE · iOS";
  const products = (platform.products || []).map((item) => movementProductHtml(item, icons)).join("");
  return '<article class="market-platform-card market-platform-card--' + escapeHtml(key) + '">' +
    '<div class="market-platform-card__head"><div><span>' + escapeHtml(badge) + '</span><h4>' +
      escapeHtml(platform.label) + '</h4></div><small>' + escapeHtml(platform.sourceTime) + '</small></div>' +
    '<p class="market-platform-card__anchors">' + escapeHtml(platform.anchors) + '</p>' +
    '<div class="market-product-list">' + (products || '<p class="market-loading">今日无主要异动产品。</p>') +
    '</div></article>';
}

function marketNewsHtml(item, index) {
  const url = safeUrl(item.url);
  return '<article class="market-news-item"><div class="market-news-item__rank">' +
    String(index + 1).padStart(2, "0") + '</div><div class="market-news-item__body">' +
    '<div class="market-news-item__meta"><span>' + escapeHtml(item.category) + '</span><time datetime="' +
    escapeHtml(item.date) + '">' + escapeHtml(item.date) + '</time></div><h4><a href="' + escapeHtml(url) +
    '" target="_blank" rel="noopener noreferrer">' + escapeHtml(item.title) + '</a></h4><p>' +
    escapeHtml(item.summary) + '</p><small><strong>市场含义：</strong>' + escapeHtml(item.impact) +
    ' · 来源：' + escapeHtml(item.source) + '</small></div></article>';
}

function closingItemHtml(item) {
  const typeClass = item.type === "关注" ? " watch" : "";
  return '<article class="market-closing-item"><span class="market-closing-item__type' + typeClass + '">' +
    escapeHtml(item.type) + '</span><div><strong>' + escapeHtml(item.title) + '</strong><p>' +
    escapeHtml(item.detail) + '</p></div></article>';
}

function reportItemHtml(report) {
  const markdown = safeLocalPath(report.markdown);
  const json = safeLocalPath(report.json);
  return '<article class="report-item"><time datetime="' + escapeHtml(report.date) + '">' +
    escapeHtml(report.date) + '</time><div><strong>' + escapeHtml(report.title) + '</strong><p>' +
    escapeHtml(report.summary) + '</p></div><div class="report-item__links"><a href="' + escapeHtml(markdown) +
    '" download>Markdown ↓</a><a href="' + escapeHtml(json) + '" download>JSON ↓</a></div></article>';
}

async function loadMarketBrief() {
  try {
    const [brief, archive] = await Promise.all([
      fetchJson(MARKET_BRIEF_PATH, "市场日报"),
      fetchJson(REPORTS_MANIFEST_PATH, "日报归档"),
    ]);
    const icons = brief.iconBundle ? await fetchJson(brief.iconBundle, "市场动态ICON") : {};
    elements.marketBriefLead.textContent = brief.title + "。" + brief.summary;
    elements.marketBriefDate.textContent = brief.date + " · 北京时间";
    elements.marketBriefDownload.href = safeLocalPath(brief.downloads?.markdown);
    elements.marketBriefJson.href = safeLocalPath(brief.downloads?.json);
    elements.marketPlatforms.innerHTML = [
      rankingPlatformHtml(brief.rankingDynamics.googlePlay, "googlePlay", icons),
      rankingPlatformHtml(brief.rankingDynamics.ios, "ios", icons),
    ].join("");
    elements.marketNewsMethod.textContent = brief.newsMethod || elements.marketNewsMethod.textContent;
    elements.marketNewsList.innerHTML = (brief.marketNews || []).map(marketNewsHtml).join("") ||
      '<p class="market-loading">今日暂无可核验热点新闻。</p>';
    elements.marketClosingList.innerHTML = (brief.closing || []).map(closingItemHtml).join("") ||
      '<p class="market-loading">今日暂无综合判断。</p>';
    elements.reportList.innerHTML = (archive.reports || []).length
      ? archive.reports.map(reportItemHtml).join("")
      : '<span class="market-loading">暂无已归档日报。</span>';
    window.__MARKET_BRIEF_READY__ = true;
  } catch (error) {
    console.error(error);
    elements.marketBriefLead.textContent = "当日市场日报暂时加载失败，榜单明细仍可正常使用。";
    elements.marketPlatforms.innerHTML = '<article class="market-platform-card"><p class="market-loading">' +
      escapeHtml(error.message) + '</p></article>';
    elements.marketNewsList.innerHTML = '<p class="market-loading">热点新闻加载失败。</p>';
    elements.marketClosingList.innerHTML = '<p class="market-loading">综合判断加载失败。</p>';
    elements.reportList.innerHTML = '<span class="market-loading">日报归档加载失败。</span>';
    window.__MARKET_BRIEF_READY__ = false;
  }
}

async function loadAssets(storeConfig) {
  const manifest = await fetchJson(storeConfig.assetManifest, "图片清单");
  const basePath = storeConfig.assetManifest.slice(0, storeConfig.assetManifest.lastIndexOf("/") + 1);
  const bundles = await Promise.all(manifest.files.map((name) => fetchJson(basePath + name, "图片资源")));
  return Object.assign({}, ...bundles);
}

async function loadStoreData(storeKey) {
  if (state.datasets[storeKey]) return state.datasets[storeKey];
  const storeConfig = STORE_CONFIGS[storeKey];
  const promise = Promise.all([
    fetchJson(storeConfig.games, "榜单数据"),
    fetchJson(storeConfig.enrichment, "溯源数据"),
    loadAssets(storeConfig),
    fetchJson(storeConfig.trends, "趋势数据"),
    fetchJson(storeConfig.counterpartGames, "跨商店排名数据"),
  ]).then(([rawGames, enrichment, assets, trends, counterpartGames]) =>
    mergeData(rawGames, enrichment, assets, trends, counterpartGames, storeConfig.counterpartRankLabel));
  state.datasets[storeKey] = promise;
  try {
    return await promise;
  } catch (error) {
    delete state.datasets[storeKey];
    throw error;
  }
}

function refreshStoreChrome() {
  const storeConfig = config();
  document.documentElement.dataset.store = state.store;
  document.title = storeConfig.title;
  document.querySelector('meta[name="description"]').content = storeConfig.title + "：排名、玩法、素材、公司归属与产品趋势。";
  document.querySelector("#brand-mark").textContent = storeConfig.mark;
  document.querySelector("#header-meta-text").textContent = storeConfig.headerMeta;
  document.querySelector("#store-eyebrow").textContent = storeConfig.eyebrow;
  document.querySelector("#hero-title").innerHTML = escapeHtml(storeConfig.storeName) + " 美国区策略游戏<br />畅销榜 TOP60";
  document.querySelectorAll("[data-date]").forEach((element) => { element.textContent = storeConfig.date; });
  document.querySelectorAll("[data-baseline-date]").forEach((element) => { element.textContent = storeConfig.baselineDate; });
  document.querySelector("#baseline-copy").innerHTML = storeConfig.baselineCopy;
  document.querySelector("#method-current").textContent = storeConfig.method;
  document.querySelector("#footer-store").textContent = storeConfig.footer;
  document.querySelectorAll(".store-tab").forEach((button) => {
    const selected = button.dataset.store === state.store;
    button.classList.toggle("is-active", selected);
    button.setAttribute("aria-selected", String(selected));
  });
  const installOption = elements.sort.querySelector('option[value="installs"]');
  installOption.disabled = !storeConfig.hasInstallEstimate;
  installOption.textContent = storeConfig.hasInstallEstimate ? "按近30日新增" : "近30日新增（iOS无公开口径）";
  if (!storeConfig.hasInstallEstimate && elements.sort.value === "installs") elements.sort.value = "rank";
}

function renderLeader() {
  const game = state.games.find((item) => item.rank === 1) || state.games[0];
  if (!game) return;
  document.querySelector("#leader-game").innerHTML =
    '<img src="' + escapeHtml(game.icon) + '" alt="' + escapeHtml(game.gameName) + ' icon" />' +
    "<div><strong>" + escapeHtml(game.gameName) + "</strong><p>" + escapeHtml(game.genre) + "</p></div>";
  document.querySelector("#leader-keywords").textContent = game.keywords;
}

function renderStats() {
  const count = (status) => state.games.filter((game) => game.status === status).length;
  document.querySelector("#stat-total").textContent = state.games.length;
  document.querySelector("#stat-normal").textContent = count("normal") + count("pending");
  document.querySelector("#stat-new").textContent = count("new");
  document.querySelector("#stat-surge").textContent = count("surge");
  elements.totalCount.textContent = state.games.length;
}

function renderGenres() {
  const genres = [...new Set(state.games.map((game) => game.genre.split("/")[0].trim()))]
    .sort((a, b) => a.localeCompare(b, "zh-CN"));
  elements.genre.innerHTML = '<option value="all">全部类型</option>' +
    genres.map((genre) => '<option value="' + escapeHtml(genre) + '">' + escapeHtml(genre) + "</option>").join("");
}

function getVisibleGames() {
  const query = elements.search.value.trim().toLowerCase();
  const filtered = state.games.filter((game) => {
    const haystack = [
      game.gameName,
      game.genre,
      game.keywords,
      game.company.en,
      game.company.cn,
      game.trend.summary,
      fullTrendText(game.trend),
    ].join(" ").toLowerCase();
    return (!query || haystack.includes(query))
      && (elements.genre.value === "all" || game.genre.startsWith(elements.genre.value))
      && (elements.status.value === "all"
        || (elements.status.value === "normal" && ["normal", "pending"].includes(game.status))
        || game.status === elements.status.value);
  });
  return filtered.sort((a, b) => {
    if (elements.sort.value === "release") return b.releaseDateIso.localeCompare(a.releaseDateIso);
    if (elements.sort.value === "installs") return parseInstalls(b.recentInstalls30d) - parseInstalls(a.recentInstalls30d);
    return a.rank - b.rank;
  });
}

function rowHtml(game) {
  const storeConfig = config();
  const confidenceClass = game.company.confidence.includes("疑似") ? " suspected" : "";
  const secondary = game.recentInstalls30d ? "近30日新增 " + game.recentInstalls30d : game.developer;
  const counterpartRank = game.counterpartRank === null
    ? "（无" + game.counterpartRankLabel + "排名）"
    : "（" + game.counterpartRankLabel + "排名 #" + game.counterpartRank + "）";
  const displayStatus = game.status === "pending" ? "normal" : game.status;
  return '<tr class="status-' + displayStatus + '">' +
    '<td class="rank-cell"><span>' + padRank(game.rank) + '</span><small>' + escapeHtml(statusLabel(game)) + "</small></td>" +
    '<td><div class="game-cell"><img src="' + escapeHtml(game.icon) + '" alt="' + escapeHtml(game.gameName) +
      ' icon" loading="lazy" /><div><strong>' + escapeHtml(game.gameName) + "</strong><small>" +
      escapeHtml(secondary) + '</small><small class="cross-rank">' + escapeHtml(counterpartRank) + "</small></div></div></td>" +
    '<td class="taxonomy-cell"><strong>' + escapeHtml(game.genre) + "</strong><p>" + escapeHtml(game.keywords) + "</p></td>" +
    '<td><button class="shot-button" type="button" data-rank="' + game.rank + '" aria-label="放大查看 ' +
      escapeHtml(game.gameName) + ' 商店图"><img src="' + escapeHtml(game.storeImage) + '" alt="' +
      escapeHtml(game.gameName) + " " + escapeHtml(storeConfig.storeName) + ' 商店图" loading="lazy" /><span>查看</span></button></td>' +
    '<td class="company-cell"><strong>' + escapeHtml(game.company.en) + "</strong><p>" + escapeHtml(game.company.cn) +
      '</p><div><span class="confidence' + confidenceClass + '">' + escapeHtml(game.company.confidence) +
      '</span><a href="' + escapeHtml(safeUrl(game.company.source)) + '" target="_blank" rel="noreferrer" title="' +
      escapeHtml(game.company.basis) + '">归属依据 ↗</a></div></td>' +
    '<td class="date-cell">' + escapeHtml(game.releaseDateIso) + '</td>' +
    '<td class="note-cell"><button class="note-summary" type="button" data-rank="' + game.rank +
      '" aria-describedby="trend-tooltip">' + trendSummaryHtml(game.trend.summary) + "</button></td>" +
    '<td><a class="store-link" href="' + escapeHtml(safeUrl(game.storeUrl)) +
      '" target="_blank" rel="noreferrer">打开<br />' + escapeHtml(storeConfig.storeName) + " <span>↗</span></a></td>" +
  "</tr>";
}

function renderTable() {
  hideTooltip();
  state.visible = getVisibleGames();
  elements.resultCount.textContent = state.visible.length;
  elements.body.innerHTML = state.visible.length
    ? state.visible.map(rowHtml).join("")
    : '<tr><td colspan="8" class="empty-state">没有匹配结果，请调整筛选条件。</td></tr>';
}

function tooltipHtml(game) {
  const sections = game.trend.sections;
  const items = [
    ["上线后发展", sections.development],
    ["榜位走向", sections.rankPath],
    ["关键转折", sections.turningPoints],
    ["主力素材", sections.creative],
    ["后续观察", sections.watch],
  ];
  return '<div class="trend-tooltip__head"><span>#' + game.rank + "</span><strong>" + escapeHtml(game.gameName) + "</strong></div>" +
    items.map(([label, text]) => '<section><strong>' + label + '</strong><p>' + escapeHtml(text) + "</p></section>").join("");
}

function placeTooltip(clientX, clientY, anchor) {
  const gap = 14;
  const rect = elements.tooltip.getBoundingClientRect();
  const anchorRect = anchor?.getBoundingClientRect();
  let left = Number.isFinite(clientX) ? clientX + gap : (anchorRect?.left || gap);
  let top = Number.isFinite(clientY) ? clientY + gap : ((anchorRect?.bottom || gap) + 8);
  left = Math.min(left, window.innerWidth - rect.width - gap);
  top = Math.min(top, window.innerHeight - rect.height - gap);
  elements.tooltip.style.left = Math.max(gap, left) + "px";
  elements.tooltip.style.top = Math.max(gap, top) + "px";
}

function showTooltip(target, event) {
  const game = state.games.find((item) => item.rank === Number(target.dataset.rank));
  if (!game) return;
  elements.tooltip.innerHTML = tooltipHtml(game);
  elements.tooltip.hidden = false;
  placeTooltip(event?.clientX, event?.clientY, target);
}

function hideTooltip() {
  elements.tooltip.hidden = true;
}

function openModal(rank) {
  const game = state.games.find((item) => item.rank === rank);
  if (!game) return;
  hideTooltip();
  elements.modalImage.src = game.storeImage;
  elements.modalImage.alt = game.gameName + " " + config().storeName + " 商店图大图";
  elements.modalRank.textContent = "#" + game.rank;
  elements.modalTitle.textContent = game.gameName;
  elements.modalKeywords.textContent = game.keywords;
  elements.modal.hidden = false;
  document.body.classList.add("modal-open");
  document.querySelector("#modal-close").focus();
}

function closeModal() {
  elements.modal.hidden = true;
  elements.modalImage.removeAttribute("src");
  document.body.classList.remove("modal-open");
}

function csvEscape(value) {
  return '"' + String(value ?? "").replaceAll('"', '""') + '"';
}

function exportCsv() {
  const storeConfig = config();
  const header = ["商店", "排名", storeConfig.counterpartRankLabel + "排名", "榜单状态", "游戏名称", "游戏类型", "游戏关键字", "出品公司（英文）", "出品公司（中文）", "上架时间", storeConfig.linkHeader, "趋势摘要", "趋势全文", "素材核验", "生命周期核验"];
  const rows = state.visible.map((game) => [
    storeConfig.storeName,
    game.rank,
    game.counterpartRank ?? "无排名",
    statusLabel(game),
    game.gameName,
    game.genre,
    game.keywords,
    game.company.en,
    game.company.cn,
    game.releaseDateIso,
    game.storeUrl,
    game.trend.summary,
    fullTrendText(game.trend),
    game.trend.sourceAudit ? sourceAuditText(game.trend.sourceAudit) : "",
    game.trend.lifecycleAudit ? lifecycleAuditText(game.trend.lifecycleAudit) : "",
  ]);
  const content = [header, ...rows].map((row) => row.map(csvEscape).join(",")).join("\n");
  const url = URL.createObjectURL(new Blob(["\ufeff", content], { type: "text/csv;charset=utf-8" }));
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = storeConfig.csvSlug + "-" + storeConfig.date + ".csv";
  anchor.click();
  URL.revokeObjectURL(url);
}

function resetFilters(render = true) {
  elements.search.value = "";
  elements.genre.value = "all";
  elements.status.value = "all";
  elements.sort.value = "rank";
  if (render) renderTable();
}

async function switchStore(storeKey, updateUrl = true) {
  if (!STORE_CONFIGS[storeKey]) return;
  const token = ++state.loadToken;
  state.store = storeKey;
  hideTooltip();
  if (!elements.modal.hidden) closeModal();
  refreshStoreChrome();
  resetFilters(false);
  elements.body.innerHTML = '<tr><td colspan="8" class="empty-state">正在加载 ' + escapeHtml(config().storeName) + " 榜单数据…</td></tr>";
  elements.resultCount.textContent = "0";
  if (updateUrl) {
    const url = new URL(window.location.href);
    if (storeKey === "ios") url.searchParams.set("store", "ios");
    else url.searchParams.delete("store");
    window.history.replaceState({ store: storeKey }, "", url);
  }
  try {
    const games = await loadStoreData(storeKey);
    if (token !== state.loadToken || storeKey !== state.store) return;
    state.games = games;
    renderGenres();
    renderLeader();
    renderStats();
    renderTable();
    window.__APP_READY__ = true;
    window.__ACTIVE_STORE__ = storeKey;
  } catch (error) {
    console.error(error);
    if (token !== state.loadToken) return;
    elements.body.innerHTML = '<tr><td colspan="8" class="empty-state">数据加载失败，请稍后刷新页面。<br /><small>' +
      escapeHtml(error.message) + "</small></td></tr>";
    window.__APP_READY__ = false;
  }
}

function bindEvents() {
  [elements.search, elements.genre, elements.status, elements.sort].forEach((control) => {
    control.addEventListener(control === elements.search ? "input" : "change", renderTable);
  });
  document.querySelectorAll(".store-tab").forEach((button) => {
    button.addEventListener("click", () => switchStore(button.dataset.store));
  });
  document.querySelector("#reset").addEventListener("click", () => resetFilters());
  document.querySelector("#export").addEventListener("click", exportCsv);
  elements.body.addEventListener("click", (event) => {
    const shot = event.target.closest(".shot-button");
    if (shot) openModal(Number(shot.dataset.rank));
  });
  elements.body.addEventListener("pointerover", (event) => {
    const note = event.target.closest(".note-summary");
    if (note) showTooltip(note, event);
  });
  elements.body.addEventListener("pointermove", (event) => {
    const note = event.target.closest(".note-summary");
    if (note && !elements.tooltip.hidden) placeTooltip(event.clientX, event.clientY, note);
  });
  elements.body.addEventListener("pointerout", (event) => {
    const note = event.target.closest(".note-summary");
    if (note && !note.contains(event.relatedTarget)) hideTooltip();
  });
  elements.body.addEventListener("focusin", (event) => {
    const note = event.target.closest(".note-summary");
    if (note) showTooltip(note);
  });
  elements.body.addEventListener("focusout", (event) => {
    if (event.target.closest(".note-summary")) hideTooltip();
  });
  document.querySelector("#modal-close").addEventListener("click", closeModal);
  elements.modal.addEventListener("click", (event) => {
    if (event.target === elements.modal) closeModal();
  });
  window.addEventListener("scroll", hideTooltip, true);
  window.addEventListener("resize", hideTooltip);
  window.addEventListener("popstate", () => {
    const value = new URLSearchParams(window.location.search).get("store");
    switchStore(value === "ios" ? "ios" : "googlePlay", false);
  });
  window.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      hideTooltip();
      if (!elements.modal.hidden) closeModal();
    }
  });
}

function init() {
  bindEvents();
  loadMarketBrief();
  switchStore(initialStore, false);
}

init();
