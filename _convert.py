#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把《WorkBuddy 能干什么：小白 AI 实用场景集》Markdown 全本转换为响应式 HTML 阅读版。"""
import re
import markdown

SRC = "/Users/zhangliang/WorkBuddy/2026-08-24-13-51-12/WorkBuddy能干什么-小白场景手册-全本.md"
OUT = "/Users/zhangliang/WorkBuddy/2026-08-24-13-51-12/WorkBuddy能干什么-小白场景手册-全本.html"
# 反馈问卷链接：建好腾讯问卷/金数据后，把"发布链接"填到这里，重跑脚本并重新部署
FEEDBACK_FORM_URL = "https://wj.qq.com/s2/27662233/ubvs/"
ADV_URL = "jinjie/"

# 小助理二维码（base64 嵌入 HTML，避免外链依赖）
import base64
_XZ_IMG = "/Users/zhangliang/WorkBuddy/2026-08-24-13-51-12/assets/xiaozhuli.jpg"
with open(_XZ_IMG, "rb") as _f:
    XZ_QR_B64 = base64.b64encode(_f.read()).decode("ascii")

with open(SRC, encoding="utf-8") as f:
    md_text = f.read()

# 1) Markdown -> HTML（tables 表格、toc 生成标题锚点）
body = markdown.markdown(
    md_text,
    extensions=["tables", "toc", "fenced_code", "sane_lists"],
    extension_configs={"toc": {"toc_depth": "2-3"}},
)

# 2) 提取目录（h2 组 / h3 篇）
headings = re.findall(r'<h([23]) id="([^"]*)">(.*?)</h\1>', body, flags=re.S)
toc_html = []
for level, hid, htext in headings:
    text = re.sub(r"<[^>]+>", "", htext).strip()
    if level == "2":
        toc_html.append(f'<li class="toc-group"><a href="#{hid}">{text}</a></li>')
    else:
        toc_html.append(f'<li class="toc-item"><a href="#{hid}">{text}</a></li>')
toc_html = "\n".join(toc_html)

# 3) blockquote（Prompt 卡片）加类名与复制按钮
btn = '<button class="copy-btn" type="button">复制</button>'
body = body.replace("<blockquote>", f'<blockquote class="prompt">{btn}')

# 4) 用 <h3> 切分，把每篇正文包成 <section class="chapter">
tokens = re.split(r'(<h[23][^>]*>.*?</h[23]>)', body, flags=re.S)
out, buf, chapter = [], [], []

def flush_buf():
    if buf:
        out.append("".join(buf))
        buf.clear()

def flush_chapter():
    if chapter:
        out.append('<section class="chapter">' + "".join(chapter) + "</section>")
        chapter.clear()

for tok in tokens:
    if not tok:
        continue
    if tok.startswith("<h2"):
        flush_chapter(); flush_buf(); out.append(tok)
    elif tok.startswith("<h3"):
        flush_chapter(); chapter.append(tok)
    else:
        if chapter:
            chapter.append(tok)
        else:
            buf.append(tok)
flush_chapter(); flush_buf()

body = "".join(out)

# 5) 内嵌页面模板
CSS = """
:root{
  --blue:#2563eb; --blue-dark:#1d4ed8; --blue-soft:#eff6ff;
  --ink:#1f2937; --ink-2:#4b5563; --ink-3:#9ca3af;
  --line:#e5e7eb; --bg:#f6f8fb; --card:#ffffff;
  --prompt-bg:#1e293b; --prompt-fg:#e2e8f0;
  --radius:14px; --shadow:0 1px 3px rgba(15,23,42,.06),0 8px 24px rgba(15,23,42,.06);
}
*{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth}
body{
  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif;
  background:var(--bg); color:var(--ink); line-height:1.9; font-size:17px;
  -webkit-font-smoothing:antialiased;
}

/* ===== 顶栏（移动端） ===== */
.topbar{
  position:sticky; top:0; z-index:60; display:none; align-items:center; gap:10px;
  background:rgba(255,255,255,.92); backdrop-filter:blur(8px);
  border-bottom:1px solid var(--line); padding:10px 16px;
}
.menu-btn{
  border:1px solid var(--line); background:#fff; color:var(--ink);
  border-radius:10px; padding:6px 12px; font-size:14px; cursor:pointer;
}
.topbar .tb-title{font-weight:700;font-size:15px;color:var(--ink);flex:1;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}

/* ===== Hero ===== */
.hero{
  background:linear-gradient(160deg,#eff6ff 0%,#f8fafc 55%,#f6f8fb 100%);
  border-bottom:1px solid var(--line); padding:64px 24px 48px; text-align:center;
}
.hero .kicker{
  display:inline-block; font-size:13px; font-weight:600; color:var(--blue);
  background:#dbeafe; border-radius:999px; padding:4px 14px; margin-bottom:18px;
}
.hero h1{font-size:clamp(30px,5vw,44px); letter-spacing:1px; color:#0f172a;}
.hero .sub{font-size:clamp(16px,2.4vw,20px); color:var(--ink-2); margin-top:10px; font-weight:500;}
.hero .tagline{max-width:640px; margin:18px auto 0; color:var(--ink-2); font-size:15px;}
.hero .stats{display:flex; justify-content:center; gap:10px; flex-wrap:wrap; margin-top:24px;}
.hero .stat{
  background:#fff; border:1px solid var(--line); border-radius:999px;
  padding:6px 16px; font-size:13px; color:var(--ink-2);
}
.hero .stat b{color:var(--blue);}

/* ===== 布局 ===== */
.layout{max-width:1200px; margin:0 auto; display:flex; gap:40px; padding:0 24px 80px;}
.sidebar{
  width:280px; flex-shrink:0; position:sticky; top:0; align-self:flex-start;
  height:100vh; overflow-y:auto; padding:36px 8px 40px 0;
}
.sidebar .sb-head{font-size:13px; font-weight:700; color:var(--ink-3); letter-spacing:2px; padding:0 14px 10px;}
.sidebar ul{list-style:none;}
.sidebar .toc-group{margin-top:6px;}
.sidebar .toc-group>a{
  display:block; font-weight:700; font-size:14px; color:var(--ink);
  padding:8px 14px; border-radius:10px; text-decoration:none;
}
.sidebar .toc-item{margin-left:8px;}
.sidebar .toc-item a{
  display:block; font-size:13px; color:var(--ink-2); padding:5px 14px 5px 22px;
  border-left:2px solid var(--line); border-radius:0 8px 8px 0; text-decoration:none;
  white-space:nowrap; overflow:hidden; text-overflow:ellipsis;
}
.sidebar a:hover{background:var(--blue-soft); color:var(--blue-dark);}
.sidebar a.active{background:var(--blue-soft); color:var(--blue-dark); font-weight:600;}
.content{flex:1; min-width:0; max-width:860px;}
.backdrop{display:none;}

/* ===== 正文排版 ===== */
.content article{padding-top:36px;}
.content h2{
  display:flex; align-items:center; gap:12px;
  font-size:clamp(21px,3vw,26px); color:#0f172a; margin:52px 0 24px;
  scroll-margin-top:24px;
}
.content h2::before{
  content:""; width:6px; height:26px; border-radius:4px;
  background:linear-gradient(180deg,var(--blue),#60a5fa); flex-shrink:0;
}
.content h3{
  font-size:19px; color:#0f172a; margin:0 0 16px; scroll-margin-top:24px;
  display:flex; align-items:baseline; gap:8px;
}
.content h3::before{
  content:""; width:14px; height:14px; border-radius:4px;
  background:var(--blue); flex-shrink:0; align-self:center; display:inline-block;
}
.chapter{
  background:var(--card); border:1px solid var(--line); border-radius:var(--radius);
  box-shadow:var(--shadow); padding:28px 30px; margin-bottom:28px;
}
.chapter p{margin-bottom:14px; color:var(--ink);}
.chapter p:last-child{margin-bottom:0;}
.chapter strong{color:#0f172a; font-weight:700;}
.content ul{margin:0 0 14px; padding-left:22px;}
.content li{margin-bottom:8px;}
.content code{
  font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
  font-size:.86em; background:#eef2ff; color:#4338ca; border-radius:6px; padding:1px 6px;
}
/* Prompt 卡片 */
blockquote.prompt{
  position:relative; background:var(--prompt-bg); color:var(--prompt-fg);
  border-radius:12px; padding:22px 20px 20px; margin:14px 0 18px;
  font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
  font-size:.92em; line-height:1.9; overflow-x:auto;
}
blockquote.prompt p{margin-bottom:8px; color:var(--prompt-fg);}
blockquote.prompt p:last-child{margin-bottom:0;}
.copy-btn{
  position:absolute; top:10px; right:10px; z-index:2;
  background:rgba(255,255,255,.12); color:#cbd5e1; border:1px solid rgba(255,255,255,.18);
  border-radius:8px; font-size:12px; padding:3px 10px; cursor:pointer; font-family:inherit;
  transition:all .15s;
}
.copy-btn:hover{background:var(--blue); color:#fff; border-color:var(--blue);}
.copy-btn.done{background:#22c55e; color:#fff; border-color:#22c55e;}
/* 表格 */
.content table{
  width:100%; border-collapse:collapse; margin:14px 0 18px; font-size:14.5px;
  background:#fff; border-radius:10px; overflow:hidden;
}
.content th{
  background:#f1f5f9; color:#0f172a; font-weight:700; text-align:left;
  padding:10px 14px; border-bottom:1px solid var(--line);
}
.content td{padding:10px 14px; border-bottom:1px solid var(--line); color:var(--ink-2); vertical-align:top;}
.content tr:last-child td{border-bottom:none;}
.content tr:nth-child(even) td{background:#fafbfd;}
.content hr{border:none;border-top:1px dashed var(--line);margin:28px 0;}
.chapter hr{display:none;}

/* 反馈区 */
.feedback{margin:6px 0 0;}
.feedback .fb-inner{
  background:linear-gradient(160deg,#eff6ff,#f8fafc);
  border:1px solid var(--line); border-radius:var(--radius);
  padding:30px 28px; text-align:center; box-shadow:var(--shadow);
}
.feedback .fb-title{font-size:21px;color:#0f172a;margin:0 0 10px;display:block;}
.feedback .fb-title::before{display:none;}
.feedback .fb-sub{max-width:560px;margin:0 auto 18px;color:var(--ink-2);font-size:15px;}
.feedback .fb-btn{
  display:inline-block; background:var(--blue); color:#fff; text-decoration:none;
  font-weight:600; font-size:15px; padding:12px 26px; border-radius:999px;
  box-shadow:0 8px 20px rgba(37,99,235,.25); transition:all .2s;
}
.feedback .fb-btn:hover{background:var(--blue-dark); transform:translateY(-1px);}
.feedback .fb-note{margin:14px 0 0; font-size:12.5px; color:var(--ink-3);}

/* 小助理二维码卡 */
.assistant{margin:36px 0 8px;}
.assistant .a-card{
  background:var(--card); border:1px solid var(--line); border-radius:var(--radius);
  box-shadow:var(--shadow); padding:28px 24px; text-align:center;
  max-width:420px; margin:0 auto;
}
.assistant img{
  max-width:240px; width:100%; height:auto; border-radius:12px;
  display:block; margin:0 auto 16px;
}
.assistant .a-text{font-size:15px; color:var(--ink-2); margin:0;}
.content a{color:var(--blue-dark); text-decoration:none;}
.content a:hover{text-decoration:underline;}
.figure{margin:18px 0 22px; background:#f8fafc; border:1px solid var(--line); border-radius:12px; padding:18px 16px 14px; text-align:center;}
.figure svg{width:100%; height:auto; max-width:680px; display:inline-block; vertical-align:middle;}
.figure figcaption{margin-top:10px; font-size:13px; color:var(--ink-3); line-height:1.6;}
.xref{margin:16px 0; border-left:4px solid var(--blue); background:var(--blue-soft); border-radius:0 10px 10px 0; padding:12px 16px; font-size:14.5px; color:var(--ink-2); line-height:1.7;}
.xref b{color:#0f172a;}
.xref a{color:var(--blue-dark); font-weight:600;}
.xref a:hover{text-decoration:underline;}
.relate{margin:30px 0 8px;}
.relate .relate-inner{background:linear-gradient(135deg,#fff7ed,#fef2f2); border:1px solid #fed7aa; border-radius:var(--radius); padding:18px 22px; box-shadow:var(--shadow);}
.relate .relate-tag{display:inline-block; font-size:12px; font-weight:700; color:#c2410c; background:#ffedd5; border-radius:999px; padding:3px 12px; margin-bottom:8px;}
.relate .relate-inner p{margin:0; font-size:14.5px; color:var(--ink-2); line-height:1.7;}
.relate a{color:var(--blue-dark); font-weight:600;}
.relate a:hover{text-decoration:underline;}

/* 回到顶部 */
.top-btn{
  position:fixed; right:26px; bottom:26px; z-index:50;
  background:#0f172a; color:#fff; border:none; border-radius:999px;
  padding:10px 18px; font-size:13px; cursor:pointer; opacity:0; pointer-events:none;
  transition:all .25s; box-shadow:0 8px 24px rgba(15,23,42,.25);
}
.top-btn.show{opacity:1; pointer-events:auto;}

/* ===== 响应式 ===== */
@media (max-width:1023px){
  .topbar{display:flex;}
  .sidebar{
    position:fixed; top:0; left:0; z-index:70; width:min(300px,84vw);
    height:100vh; background:#fff; box-shadow:8px 0 40px rgba(15,23,42,.15);
    transform:translateX(-105%); transition:transform .28s ease; padding-top:24px;
  }
  .sidebar.open{transform:translateX(0);}
  .backdrop{
    display:block; position:fixed; inset:0; z-index:65; background:rgba(15,23,42,.4);
    opacity:0; pointer-events:none; transition:opacity .25s;
  }
  .backdrop.show{opacity:1; pointer-events:auto;}
  .layout{display:block; padding:0 16px 70px;}
  .hero{padding:44px 20px 34px;}
  .content article{padding-top:20px;}
  .chapter{padding:22px 18px;}
}
@media (max-width:640px){
  body{font-size:16px;}
  .chapter{padding:20px 16px; border-radius:12px;}
  .hero h1{font-size:28px;}
}
"""

JS = """
(function(){
  var sidebar=document.getElementById('sidebar'),
      backdrop=document.getElementById('backdrop'),
      menuBtn=document.getElementById('menuBtn'),
      topBtn=document.getElementById('topBtn');
  function openNav(){sidebar.classList.add('open');backdrop.classList.add('show');}
  function closeNav(){sidebar.classList.remove('open');backdrop.classList.remove('show');}
  if(menuBtn){menuBtn.addEventListener('click',openNav);}
  if(backdrop){backdrop.addEventListener('click',closeNav);}

  // 点击目录：移动端自动收起
  var tocLinks=document.querySelectorAll('#toc a');
  tocLinks.forEach(function(a){a.addEventListener('click',function(){closeNav();});});

  // 滚动高亮当前章节
  var sections=document.querySelectorAll('h2,h3');
  var map=new Map();
  sections.forEach(function(el){
    if(el.id) map.set(el.id, el);
  });
  var activeLink=null;
  function setActive(id){
    tocLinks.forEach(function(a){
      if(a.getAttribute('href')==='#'+id){
        a.classList.add('active'); activeLink=a;
      } else a.classList.remove('active');
    });
  }
  var io=new IntersectionObserver(function(entries){
    entries.forEach(function(en){
      if(en.isIntersecting) setActive(en.target.id);
    });
  },{rootMargin:'-15% 0px -70% 0px'});
  sections.forEach(function(el){ if(el.id) io.observe(el); });

  // 回到顶部
  window.addEventListener('scroll',function(){
    topBtn.classList.toggle('show',window.scrollY>600);
  });
  topBtn.addEventListener('click',function(){window.scrollTo({top:0,behavior:'smooth'});});

  // 复制 Prompt
  document.querySelectorAll('blockquote.prompt').forEach(function(bq){
    var btn=bq.querySelector('.copy-btn');
    if(!btn) return;
    btn.addEventListener('click',function(){
      var clone=bq.cloneNode(true);
      var b=clone.querySelector('.copy-btn'); if(b) b.remove();
      var text=clone.innerText.replace(/\\n{3,}/g,'\\n\\n').trim();
      var done=function(){btn.textContent='已复制';btn.classList.add('done');setTimeout(function(){btn.textContent='复制';btn.classList.remove('done');},1800);};
      if(navigator.clipboard&&navigator.clipboard.writeText){
        navigator.clipboard.writeText(text).then(done).catch(function(){fallback();});
      } else fallback();
      function fallback(){
        var ta=document.createElement('textarea');
        ta.value=text; ta.style.position='fixed'; ta.style.opacity='0';
        document.body.appendChild(ta); ta.select();
        try{document.execCommand('copy');done();}catch(e){btn.textContent='复制失败';}
        document.body.removeChild(ta);
      }
    });
  });
})();
"""

ASSISTANT = """
<section class="assistant">
  <div class="a-card">
    <img src="data:image/jpeg;base64,__XZB64__" alt="亮哥小助理苏打微信二维码">
    <p class="a-text">有任何问题、建议、想法，欢迎联系小助理</p>
  </div>
</section>
""".replace("__XZB64__", XZ_QR_B64)

FEEDBACK = """
<section class="feedback">
  <div class="fb-inner">
    <h3 class="fb-title">有话想说？👋</h3>
    <p class="fb-sub">这本手册是给你写的。哪篇最有用、哪里没看懂、还想让 AI 帮你干点啥——花 1 分钟告诉我，下一篇就写你最想要的。</p>
    <a class="fb-btn" href="__FBURL__" target="_blank" rel="noopener">去填反馈问卷（约 1 分钟）↗</a>
    <p class="fb-note">问卷在另一个页面打开，填完直接关掉就好 · 匿名、不用登录</p>
  </div>
</section>
""".replace("__FBURL__", FEEDBACK_FORM_URL)

RELATE = """
<section class="relate">
  <div class="relate-inner">
    <span class="relate-tag">两册联动</span>
    <p>这 22 篇够你上手了。想系统搞懂原理、自己搭网站和做自动化？看 <a href="__ADV__" target="_blank" rel="noopener">《WorkBuddy 进阶指南》</a>——五大板块十六章，讲清原理，每段附可抄指令。</p>
  </div>
</section>
""".replace("__ADV__", ADV_URL)

HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>WorkBuddy 能干什么：小白 AI 实用场景集</title>
<meta name="description" content="22 篇场景短文，每篇解决一个具体问题，给一段能直接抄的 Prompt。翻到哪篇，用到哪篇。">
<style>{css}</style>
</head>
<body>
<header class="hero">
  <span class="kicker">小白友好 · 零基础可用</span>
  <h1>WorkBuddy 能干什么</h1>
  <div class="sub">小白 AI 实用场景集</div>
  <p class="tagline">不是教程，是手册。每篇解决一个真实问题，给一段能直接抄的指令。读 3 分钟，就能上手。</p>
  <div class="stats">
    <span class="stat"><b>22</b> 篇场景</span>
    <span class="stat">每篇 <b>3 分钟</b>读完</span>
    <span class="stat">手机 / 电脑都能看</span>
  </div>
</header>

<div class="topbar">
  <button class="menu-btn" id="menuBtn" type="button">☰ 目录</button>
  <span class="tb-title">WorkBuddy 能干什么</span>
</div>

<div class="layout">
  <nav class="sidebar" id="sidebar">
    <div class="sb-head">全书目录</div>
    <ul id="toc">
{toc}
    </ul>
  </nav>
  <div class="backdrop" id="backdrop"></div>
  <main class="content">
    <article>
{assistant}
{related}
{body}
    </article>
{feedback}
  </main>
</div>

<button class="top-btn" id="topBtn" type="button">↑ 回到顶部</button>

<script>{js}</script>
</body>
</html>
"""

html = HTML.format(css=CSS, toc=toc_html, assistant=ASSISTANT, related=RELATE, body=body, js=JS, feedback=FEEDBACK)
with open(OUT, "w", encoding="utf-8") as f:
    f.write(html)

print("OK ->", OUT)
print("章节数(h3):", body.count('<h3'))
print("Prompt 卡片数:", body.count('class="prompt"'))
