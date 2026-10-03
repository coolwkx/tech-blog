// Mermaid 初始化 + 多源回退加载
//
// 背景：mermaid 不是纯函数库，无法只靠一个 js 文件离线加载（它的解析器与渲染器
// 分散在多个 chunk 里），所以这里走 CDN；但按顺序尝试多个源，避免单一 CDN 不可达
// 导致图示全部退化为代码块。
//
// GitHub 原生支持 ```mermaid 代码块，即使站点脚本加载失败，在 GitHub 上依然能看图。

(function () {
  var SOURCES = [
    "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js",
    "https://unpkg.com/mermaid@11/dist/mermaid.min.js",
    "https://cdnjs.cloudflare.com/ajax/libs/mermaid/11.4.1/mermaid.min.js",
    "https://npm.elemecdn.com/mermaid@11/dist/mermaid.min.js"
  ];

  var idx = 0;
  var libLoaded = false;

  function initMermaid() {
    if (!window.mermaid) return false;
    mermaid.initialize({
      startOnLoad: false,
      theme: "base",
      themeVariables: {
        primaryColor: "#e8eaf6",
        primaryTextColor: "#1a1a1a",
        primaryBorderColor: "#5c6bc0",
        lineColor: "#5c6bc0",
        secondaryColor: "#f3f4f6",
        tertiaryColor: "#fafafa",
        fontFamily:
          '-apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif',
        fontSize: "14px"
      },
      flowchart: { curve: "basis", useMaxWidth: true },
      sequence: { useMaxWidth: true },
      state: { useMaxWidth: true },
      gantt: { useMaxWidth: true }
    });
    return true;
  }

  function renderMermaid() {
    if (!window.mermaid) return;
    // 已处理过的节点会被 mermaid 标记，避免重复渲染
    var blocks = document.querySelectorAll(".mermaid:not([data-processed])");
    if (blocks.length === 0) return;
    try {
      mermaid.run({ nodes: blocks });
    } catch (e) {
      // 单个图语法错误不应该影响整页
      console.warn("[mermaid] 渲染失败：", e);
    }
  }

  function tryNext() {
    if (libLoaded) return;
    if (idx >= SOURCES.length) {
      console.warn("[mermaid] 所有源均不可达，图示将保持为代码块（GitHub 上仍可正常查看）");
      return;
    }
    var url = SOURCES[idx++];
    var s = document.createElement("script");
    s.src = url;
    s.async = true;
    s.onload = function () {
      libLoaded = true;
      if (initMermaid()) renderMermaid();
    };
    s.onerror = function () {
      console.warn("[mermaid] 加载失败，尝试下一个源：" + url);
      tryNext();
    };
    document.head.appendChild(s);
  }

  tryNext();

  // Material 的 instant navigation 换页后需要重新渲染
  if (typeof document$ !== "undefined") {
    document$.subscribe(function () {
      renderMermaid();
    });
  }
})();
