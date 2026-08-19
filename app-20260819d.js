"use strict";

const DATA_DATE = "2026-08-19";
const BASELINE_DATE = "2026-05-21";
const CACHE_VERSION = "20260819f";
const state = { games: [], visible: [] };

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
};

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

function padRank(rank) {
  return String(rank).padStart(2, "0");
}

function parseInstalls(value = "0") {
  const number = Number.parseFloat(value.replaceAll(",", "")) || 0;
  if (/M/i.test(value)) return number * 1_000_000;
  if (/K/i.test(value)) return number * 1_000;
  return number;
}

function statusLabel(game) {
  const comparison = game.comparison90d;
  if (comparison.status === "new") return "近3月新";
  if (comparison.status === "surge") return "近3月 ↑" + comparison.delta;
  return "常规";
}

function fullTrendText(trend) {
  const sections = trend.sections;
  return [
    "上线后发展：" + sections.development,
    "榜位走向：" + sections.rankPath,
    "关键转折：" + sections.turningPoints,
    "主力素材：" + sections.creative,
    "后续观察：" + sections.watch,
  ].join(" ");
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
  const sections = [
    text.slice(0, turningIndex + 1),
    text.slice(turningIndex + 1, creativeIndex + 1),
    text.slice(creativeIndex + 1),
  ];
  return sections.map((section) => "<span>" + escapeHtml(section) + "</span>").join("");
}

function mergeData(rawGames, enrichment, assets, trends) {
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
    return {
      ...game,
      company,
      trend,
      status: game.comparison90d?.status || "pending",
      icon: game.iconData || assets[assetPrefix + "_icon"],
      storeImage: game.storeImageData || assets[assetPrefix + "_store"],
    };
  });
}

async function loadAssets() {
  const manifestResponse = await fetch("assets/manifest.json?v=" + CACHE_VERSION);
  if (!manifestResponse.ok) throw new Error("图片清单加载失败：" + manifestResponse.status);
  const manifest = await manifestResponse.json();
  const bundles = await Promise.all(manifest.files.map((name) =>
    fetch("assets/" + name + "?v=" + CACHE_VERSION).then((response) => {
      if (!response.ok) throw new Error("图片资源加载失败：" + response.status);
      return response.json();
    })
  ));
  return Object.assign({}, ...bundles);
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
  elements.genre.insertAdjacentHTML(
    "beforeend",
    genres.map((genre) => '<option value="' + escapeHtml(genre) + '">' + escapeHtml(genre) + "</option>").join(""),
  );
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
  const confidenceClass = game.company.confidence.includes("疑似") ? " suspected" : "";
  const secondary = game.recentInstalls30d ? "近30日新增 " + game.recentInstalls30d : game.developer;
  const displayStatus = game.status === "pending" ? "normal" : game.status;
  return '<tr class="status-' + displayStatus + '">' +
    '<td class="rank-cell"><span>' + padRank(game.rank) + '</span><small>' + escapeHtml(statusLabel(game)) + "</small></td>" +
    '<td><div class="game-cell"><img src="' + escapeHtml(game.icon) + '" alt="' + escapeHtml(game.gameName) +
      ' icon" loading="lazy" /><div><strong>' + escapeHtml(game.gameName) + "</strong><small>" +
      escapeHtml(secondary) + "</small></div></div></td>" +
    '<td class="taxonomy-cell"><strong>' + escapeHtml(game.genre) + "</strong><p>" +
      escapeHtml(game.keywords) + "</p></td>" +
    '<td><button class="shot-button" type="button" data-rank="' + game.rank +
      '" aria-label="放大查看 ' + escapeHtml(game.gameName) + ' 商店图"><img src="' +
      escapeHtml(game.storeImage) + '" alt="' + escapeHtml(game.gameName) +
      ' Google Play 商店图" loading="lazy" /><span>查看</span></button></td>' +
    '<td class="company-cell"><strong>' + escapeHtml(game.company.en) + "</strong><p>" +
      escapeHtml(game.company.cn) + '</p><div><span class="confidence' + confidenceClass + '">' +
      escapeHtml(game.company.confidence) + '</span><a href="' + escapeHtml(safeUrl(game.company.source)) +
      '" target="_blank" rel="noreferrer" title="' + escapeHtml(game.company.basis) +
      '">归属依据 ↗</a></div></td>' +
    '<td class="date-cell">' + escapeHtml(game.releaseDateIso) + '</td>' +
    '<td class="note-cell"><button class="note-summary" type="button" data-rank="' + game.rank +
      '" aria-describedby="trend-tooltip">' + trendSummaryHtml(game.trend.summary) + "</button></td>" +
    '<td><a class="store-link" href="' + escapeHtml(safeUrl(game.storeUrl)) +
      '" target="_blank" rel="noreferrer">打开<br />Google Play <span>↗</span></a></td>' +
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
  elements.modalImage.alt = game.gameName + " Google Play 商店图大图";
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
  const header = ["排名", "榜单状态", "游戏名称", "游戏类型", "游戏关键字", "出品公司（英文）", "出品公司（中文）", "上架时间", "Google Play 链接", "趋势摘要", "趋势全文"];
  const rows = state.visible.map((game) => [
    game.rank,
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
  ]);
  const content = [header, ...rows].map((row) => row.map(csvEscape).join(",")).join("\n");
  const url = URL.createObjectURL(new Blob(["\ufeff", content], { type: "text/csv;charset=utf-8" }));
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = "google-play-us-strategy-top60-" + DATA_DATE + ".csv";
  anchor.click();
  URL.revokeObjectURL(url);
}

function bindEvents() {
  [elements.search, elements.genre, elements.status, elements.sort].forEach((control) => {
    control.addEventListener(control === elements.search ? "input" : "change", renderTable);
  });
  document.querySelector("#reset").addEventListener("click", () => {
    elements.search.value = "";
    elements.genre.value = "all";
    elements.status.value = "all";
    elements.sort.value = "rank";
    renderTable();
  });
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
  window.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      hideTooltip();
      if (!elements.modal.hidden) closeModal();
    }
  });
}

async function init() {
  document.querySelectorAll("[data-date]").forEach((element) => { element.textContent = DATA_DATE; });
  document.querySelectorAll("[data-baseline-date]").forEach((element) => { element.textContent = BASELINE_DATE; });
  bindEvents();
  try {
    const [rawGames, enrichment, assets, trends] = await Promise.all([
      fetch("data/games-20260819d.json?v=" + CACHE_VERSION).then((response) => {
        if (!response.ok) throw new Error("榜单数据加载失败：" + response.status);
        return response.json();
      }),
      fetch("data/enrichment-20260819d.json?v=" + CACHE_VERSION).then((response) => {
        if (!response.ok) throw new Error("溯源数据加载失败：" + response.status);
        return response.json();
      }),
      loadAssets(),
      fetch("data/trends-20260819d.json?v=" + CACHE_VERSION).then((response) => {
        if (!response.ok) throw new Error("趋势数据加载失败：" + response.status);
        return response.json();
      }),
    ]);
    state.games = mergeData(rawGames, enrichment, assets, trends);
    renderGenres();
    renderLeader();
    renderStats();
    renderTable();
    window.__APP_READY__ = true;
  } catch (error) {
    console.error(error);
    elements.body.innerHTML = '<tr><td colspan="8" class="empty-state">数据加载失败，请稍后刷新页面。<br /><small>' +
      escapeHtml(error.message) + "</small></td></tr>";
    window.__APP_READY__ = false;
  }
}

init();
