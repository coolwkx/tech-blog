// MathJax 配置 + 本地优先加载（CDN 仅作兜底）
//
// 背景：pymdownx.arithmatex 会把 $...$ 包成 <span class="arithmatex">，
// 必须由 MathJax 负责渲染。如果只依赖 CDN，一旦 CDN 在用户网络下不可达，
// 公式就会以纯文本形式裸露在页面上。
//
// 策略：优先加载仓库内置的 tex-mml-chtml.js（离线可用、不受网络影响），
// 只有当本地文件缺失或加载失败时才回退到 CDN。

window.MathJax = {
  tex: {
    inlineMath: [["\\(", "\\)"], ["$", "$"]],
    displayMath: [["\\[", "\\]"], ["$$", "$$"]],
    processEscapes: true,
    processEnvironments: true,
    tags: "none"
  },
  options: {
    ignoreHtmlClass: ".*|",
    processHtmlClass: "arithmatex"
  },
  svg: {
    fontCache: "global"
  }
};

(function () {
  // 本地文件优先；找不到时回退到这些 CDN
  var SOURCES = [
    "javascripts/tex-mml-chtml.js",
    "https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js",
    "https://unpkg.com/mathjax@3/es5/tex-mml-chtml.js",
    "https://cdnjs.cloudflare.com/ajax/libs/mathjax/3.2.2/es5/tex-mml-chtml.min.js",
    "https://npm.elemecdn.com/mathjax@3/es5/tex-mml-chtml.js"
  ];

  var idx = 0;
  var loaded = false;

  function tryNext() {
    if (loaded) return;
    if (idx >= SOURCES.length) {
      console.warn(
        "[mathjax] 本地文件与所有 CDN 均不可用，公式将以 LaTeX 源码显示。"
      );
      return;
    }
    var url = SOURCES[idx++];
    var s = document.createElement("script");
    s.src = url;
    s.async = true;
    s.onload = function () {
      loaded = true;
      // 脚本就绪后主动排版一次，不单纯依赖自动排版
      if (window.MathJax && window.MathJax.typesetPromise) {
        window.MathJax.typesetPromise();
      }
    };
    s.onerror = function () {
      console.warn("[mathjax] 加载失败，尝试下一个源：" + url);
      tryNext();
    };
    document.head.appendChild(s);
  }

  tryNext();

  // Material 的 instant navigation 换页后需要重新排版
  if (typeof document$ !== "undefined") {
    document$.subscribe(function () {
      if (window.MathJax && window.MathJax.typesetPromise) {
        window.MathJax.startup.output.clearCache();
        window.MathJax.typesetClear();
        window.MathJax.texReset();
        window.MathJax.typesetPromise();
      }
    });
  }
})();
