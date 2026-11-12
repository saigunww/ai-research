'use strict';
(() => {
  const languages = ['zh-CN', 'zh-TW', 'ja', 'en'];
  const copy = {
    'zh-CN': {
      pageTitle:'AI 科研背景提升 · 行知学园', skip:'跳转到正文',navTopics:'研究方向',navPath:'实践路径',navHonors:'合格成果',navContact:'咨询我们',menuOpen:'打开菜单',menuClose:'关闭菜单',mainNavigation:'主导航',
      heroProgram:'AI 科研背景提升',heroLine1:'让好奇心，',heroLine2:'成为研究的起点。',heroDescription:'从生命科学到化学与智能计算，在真实的研究问题中学习、实践，建立属于自己的科研视野。',heroExplore:'探索研究方向',heroHonors:'查看合格成果',heroNote:'以问题为起点 · 以实践连接知识',artLife:'生命科学',artChemistry:'化学与材料',artAI:'智能计算',scroll:'向下探索',
      introTitle:'把兴趣，连接到更广阔的研究世界。',introDescription:'人工智能正在成为理解生命、探索分子与分析复杂数据的工具。我们从具体学科的问题出发，将科学思考、计算实践与表达能力连接起来。',
      topicsTitle:'从一个方向，开始探索。',topicsDescription:'浏览课题的研究领域与概要，找到与你的兴趣和学科背景相连的方向。',catalogLabel:'研究方向目录',searchLabel:'搜索研究方向',searchPlaceholder:'搜索研究方向、关键词',filterLabel:'研究领域筛选',catalogFallback:'研究方向涵盖生命科学、化学与智能计算。完整目录暂未加载时，可通过下方邮箱咨询。',catalogNote:'课题以领域概览呈现，具体安排结合学习基础与兴趣沟通。',all:'全部方向',practice:'已有实践',pilot:'试点探索',proposal:'方向储备',updated:'更新于',count:'个课题',visibleCount:'个方向',noResults:'暂未找到匹配的方向，试试其他关键词。',clearSearch:'清除筛选',loadError:'目录暂时无法加载，请稍后重试或邮件咨询。',retry:'重新加载',
      pathTitle:'不止了解，更要参与思考。',pathDescription:'从建立问题意识，到有条理地解释自己的发现，逐步熟悉科研的思考方式。',path1Title:'找到问题',path1Description:'结合学科兴趣与学习基础，认识领域中的研究问题。',path2Title:'建立方法',path2Description:'学习文献阅读与数据思维，理解工具与研究目标的关系。',path3Title:'动手实践',path3Description:'在实践中观察、比较与讨论，学习用证据检验自己的想法。',path4Title:'表达思考',path4Description:'梳理研究过程，清晰说明发现、局限与下一步的问题。',
      honorsTitle:'以探索，走向新的起点。',honorsDescription:'AI 科研背景提升方向的学生合格成果，记录每一次继续学习的开始。',honorsFallback:'合格成果暂未加载，可通过下方邮箱咨询。',allHonors:'查看完整合格榜',honorsNote:'录取结果按学校分别展示。',admitted:'合格',admissionYear:'年度',honorProgram:'AI 科研背景提升',posterAlt:'{year}年度 · {student} · {university}合格榜',viewPoster:'查看高清合格榜',posterNewTab:'在新窗口查看原图',
      contactLine1:'你的下一个问题，',contactLine2:'可以从这里开始。',contactDescription:'告诉我们你的专业背景与研究兴趣，一起讨论适合的探索方向。',emailUs:'邮件咨询',wechat:'微信咨询',wechatNote:'扫码联系，了解研究方向',rednote:'小红书',rednoteNote:'更多学习与科研动态',wechatAlt:'微信咨询二维码',rednoteAlt:'小红书二维码',footerProgram:'AI 科研背景提升',backTop:'返回顶部'
    },
    'zh-TW': {
      pageTitle:'AI 科研背景提升 · 行知學園',skip:'跳轉到正文',navTopics:'研究方向',navPath:'實踐路徑',navHonors:'合格成果',navContact:'諮詢我們',menuOpen:'開啟選單',menuClose:'關閉選單',mainNavigation:'主導覽',
      heroProgram:'AI 科研背景提升',heroLine1:'讓好奇心，',heroLine2:'成為研究的起點。',heroDescription:'從生命科學到化學與智慧運算，在真實的研究問題中學習、實踐，建立屬於自己的科研視野。',heroExplore:'探索研究方向',heroHonors:'查看合格成果',heroNote:'以問題為起點 · 以實踐連結知識',artLife:'生命科學',artChemistry:'化學與材料',artAI:'智慧運算',scroll:'向下探索',
      introTitle:'把興趣，連結到更廣闊的研究世界。',introDescription:'人工智慧正在成為理解生命、探索分子與分析複雜資料的工具。我們從具體學科的問題出發，將科學思考、運算實踐與表達能力連結起來。',
      topicsTitle:'從一個方向，開始探索。',topicsDescription:'瀏覽課題的研究領域與概要，找到與你的興趣和學科背景相連的方向。',catalogLabel:'研究方向目錄',searchLabel:'搜尋研究方向',searchPlaceholder:'搜尋研究方向、關鍵詞',filterLabel:'研究領域篩選',catalogFallback:'研究方向涵蓋生命科學、化學與智慧運算。完整目錄暫未載入時，可透過下方信箱諮詢。',catalogNote:'課題以領域概覽呈現，具體安排結合學習基礎與興趣溝通。',all:'全部方向',practice:'已有實踐',pilot:'試點探索',proposal:'方向儲備',updated:'更新於',count:'個課題',visibleCount:'個方向',noResults:'暫未找到符合的方向，試試其他關鍵詞。',clearSearch:'清除篩選',loadError:'目錄暫時無法載入，請稍後重試或來信諮詢。',retry:'重新載入',
      pathTitle:'不只了解，更要參與思考。',pathDescription:'從建立問題意識，到有條理地解釋自己的發現，逐步熟悉科研的思考方式。',path1Title:'找到問題',path1Description:'結合學科興趣與學習基礎，認識領域中的研究問題。',path2Title:'建立方法',path2Description:'學習文獻閱讀與資料思維，理解工具與研究目標的關係。',path3Title:'動手實踐',path3Description:'在實踐中觀察、比較與討論，學習用證據檢驗自己的想法。',path4Title:'表達思考',path4Description:'梳理研究過程，清晰說明發現、局限與下一步的問題。',
      honorsTitle:'以探索，走向新的起點。',honorsDescription:'AI 科研背景提升方向的學生合格成果，記錄每一次繼續學習的開始。',honorsFallback:'合格成果暫未載入，可透過下方信箱諮詢。',allHonors:'查看完整合格榜',honorsNote:'錄取結果按學校分別展示。',admitted:'合格',admissionYear:'年度',honorProgram:'AI 科研背景提升',posterAlt:'{year}年度 · {student} · {university}合格榜',viewPoster:'查看高清合格榜',posterNewTab:'在新視窗查看原圖',
      contactLine1:'你的下一個問題，',contactLine2:'可以從這裡開始。',contactDescription:'告訴我們你的專業背景與研究興趣，一起討論適合的探索方向。',emailUs:'郵件諮詢',wechat:'微信諮詢',wechatNote:'掃碼聯繫，了解研究方向',rednote:'小紅書',rednoteNote:'更多學習與科研動態',wechatAlt:'微信諮詢二維碼',rednoteAlt:'小紅書二維碼',footerProgram:'AI 科研背景提升',backTop:'返回頂部'
    },
    ja: {
      pageTitle:'AI研究実践プログラム · 行知学園',skip:'本文へ移動',navTopics:'研究テーマ',navPath:'学びの流れ',navHonors:'合格実績',navContact:'お問い合わせ',menuOpen:'メニューを開く',menuClose:'メニューを閉じる',mainNavigation:'メインナビゲーション',
      heroProgram:'AI研究実践プログラム',heroLine1:'好奇心を、',heroLine2:'研究の出発点に。',heroDescription:'生命科学から化学、情報科学まで。研究課題に向き合う学びと実践を通して、自分自身の研究の視野を広げます。',heroExplore:'研究テーマを見る',heroHonors:'合格実績を見る',heroNote:'問いから始め、実践で知識をつなぐ',artLife:'生命科学',artChemistry:'化学・材料',artAI:'情報科学',scroll:'もっと見る',
      introTitle:'興味の先に、広がる研究の世界。',introDescription:'AIは生命を理解し、分子を探り、複雑なデータを読み解くための道具になっています。専門分野の問いを起点に、科学的な思考、計算の実践、伝える力を結びつけます。',
      topicsTitle:'ひとつのテーマから、探究へ。',topicsDescription:'研究分野とテーマの概要から、興味や専門に合った方向を見つけてください。',catalogLabel:'研究テーマ一覧',searchLabel:'研究テーマを検索',searchPlaceholder:'研究テーマ・キーワードで検索',filterLabel:'研究分野で絞り込む',catalogFallback:'生命科学・化学・情報科学を中心に研究テーマを紹介しています。一覧が表示されない場合は、下記のメールでお問い合わせください。',catalogNote:'各テーマの概要を紹介しています。具体的な取り組みは学習経験や興味に合わせてご相談ください。',all:'すべて',practice:'実践あり',pilot:'試行段階',proposal:'構想段階',updated:'更新日',count:'テーマ',visibleCount:'テーマ',noResults:'該当するテーマがありません。別のキーワードをお試しください。',clearSearch:'絞り込みを解除',loadError:'一覧を読み込めませんでした。再試行するか、メールでお問い合わせください。',retry:'再読み込み',
      pathTitle:'知ることから、考えることへ。',pathDescription:'問いを立て、自分の発見を筋道立てて説明する。研究に必要な考え方を段階的に学びます。',path1Title:'問いを見つける',path1Description:'興味や学習経験を踏まえ、分野の研究課題を理解します。',path2Title:'方法を学ぶ',path2Description:'文献の読み方やデータの捉え方を学び、手法と研究目的を結びつけます。',path3Title:'実践する',path3Description:'観察・比較・議論を通して、根拠をもとに考えを確かめます。',path4Title:'考えを伝える',path4Description:'研究の過程を整理し、発見や限界、次の問いを説明します。',
      honorsTitle:'探究から、新しい一歩へ。',honorsDescription:'AI研究実践プログラムに取り組んだ学生の合格実績。次の学びに進む歩みを紹介します。',honorsFallback:'合格実績を読み込めない場合は、下記のメールでお問い合わせください。',allHonors:'合格実績一覧を見る',honorsNote:'合格実績は大学ごとに掲載しています。',admitted:'合格',admissionYear:'年度',honorProgram:'AI研究実践プログラム',posterAlt:'{year}年度 · {student} · {university} 合格実績ポスター',viewPoster:'合格ポスターを拡大',posterNewTab:'元画像を新しいウィンドウで開く',
      contactLine1:'次の問いは、',contactLine2:'ここから始まります。',contactDescription:'専門分野や研究への興味をお聞かせください。あなたに合う学びの方向を一緒に考えます。',emailUs:'メールで相談する',wechat:'WeChatで相談',wechatNote:'QRコードからお問い合わせ',rednote:'RED / 小紅書',rednoteNote:'学びと研究の最新情報',wechatAlt:'WeChat問い合わせ用QRコード',rednoteAlt:'REDのQRコード',footerProgram:'AI研究実践プログラム',backTop:'ページ上部へ'
    },
    en: {
      pageTitle:'AI Research Program · Coach Academy',skip:'Skip to content',navTopics:'Research directions',navPath:'The learning journey',navHonors:'Admissions',navContact:'Get in touch',menuOpen:'Open menu',menuClose:'Close menu',mainNavigation:'Main navigation',
      heroProgram:'AI RESEARCH PROGRAM',heroLine1:'Let curiosity',heroLine2:'be your starting point.',heroDescription:'Explore the intersection of life science, chemistry and computing. Develop your research perspective through meaningful questions and hands-on learning.',heroExplore:'Explore research',heroHonors:'View admissions',heroNote:'Start with a question. Connect knowledge through practice.',artLife:'Life science',artChemistry:'Chemistry',artAI:'Computing',scroll:'Explore below',
      introTitle:'Connect your interests to a wider world of research.',introDescription:'AI is becoming a tool for understanding life, exploring molecules and interpreting complex data. Starting with questions rooted in science, we connect critical thinking, computational practice and communication.',
      topicsTitle:'Find a direction. Begin exploring.',topicsDescription:'Explore research areas and topic overviews to find connections with your interests and academic background.',catalogLabel:'Research directory',searchLabel:'Search research directions',searchPlaceholder:'Search topics or keywords',filterLabel:'Filter by research area',catalogFallback:'Our research directions span life science, chemistry and computing. If the directory is unavailable, please contact us by email below.',catalogNote:'These are introductory overviews. Individual activities are discussed in relation to your interests and learning experience.',all:'All areas',practice:'Practice undertaken',pilot:'Pilot exploration',proposal:'Under consideration',updated:'Updated',count:'topics',visibleCount:'topics',noResults:'No matching topics. Try another keyword or research area.',clearSearch:'Clear filters',loadError:'The directory could not be loaded. Please retry or contact us by email.',retry:'Try again',
      pathTitle:'Go beyond knowing. Start thinking.',pathDescription:'From asking a clear question to explaining your observations, build familiarity with the way research works.',path1Title:'Find a question',path1Description:'Connect your academic interests and experience with questions in a research field.',path2Title:'Build understanding',path2Description:'Learn to read the literature, reason with data and connect methods to research goals.',path3Title:'Explore in practice',path3Description:'Observe, compare and discuss. Learn to test ideas against evidence.',path4Title:'Communicate',path4Description:'Explain your process, findings and limitations, and identify questions to explore next.',
      honorsTitle:'From exploration to a new chapter.',honorsDescription:'Admissions achieved by students in our AI research program, marking the beginning of their next stage of learning.',honorsFallback:'If admission results are unavailable, please contact us by email below.',allHonors:'View all admissions',honorsNote:'Admissions are listed separately for each university.',admitted:'ADMITTED',admissionYear:'ENTRY',honorProgram:'AI Research Program',posterAlt:'{year} admission poster: {student} — {university}',viewPoster:'View full-size poster',posterNewTab:'Open original image in a new window',
      contactLine1:'Your next question',contactLine2:'can start here.',contactDescription:'Tell us about your academic background and research interests. Let’s discuss a direction that fits your learning goals.',emailUs:'Get in touch',wechat:'WeChat',wechatNote:'Scan to ask about research',rednote:'RED / Xiaohongshu',rednoteNote:'Learning and research updates',wechatAlt:'WeChat contact QR code',rednoteAlt:'Xiaohongshu QR code',footerProgram:'AI Research Program',backTop:'Back to top'
    }
  };
  const $ = selector => document.querySelector(selector);
  const $$ = selector => [...document.querySelectorAll(selector)];
  let catalog = null;
  let loadFailed = false;
  let selectedCategory = 'all';
  let currentLanguage = 'zh-CN';
  let pendingRequest = null;
  const readStorage = key => { try { return localStorage.getItem(key); } catch (_) { return null; } };
  const writeStorage = (key, value) => { try { localStorage.setItem(key, value); } catch (_) {} };
  function fromHash() {
    const candidate = location.hash.slice(1);
    return languages.includes(candidate) ? candidate : null;
  }
  const storedLanguage = readStorage('coach-ai-language');
  currentLanguage = fromHash() || (languages.includes(storedLanguage) ? storedLanguage : 'zh-CN');
  const t = key => copy[currentLanguage][key] || copy['zh-CN'][key] || key;
  const localized = value => typeof value === 'string' ? value : value?.[currentLanguage] || value?.['zh-CN'] || '';
  function element(tag, className, content) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (content !== undefined && content !== null) node.textContent = String(content);
    return node;
  }
  function setMenu(open) {
    const toggle = $('.menu-toggle');
    toggle.setAttribute('aria-expanded', String(open));
    toggle.setAttribute('aria-label', t(open ? 'menuClose' : 'menuOpen'));
    $('#main-nav').classList.toggle('open', open);
  }
  function applyLanguage(language, changeHash = false) {
    if (!languages.includes(language)) return;
    currentLanguage = language;
    document.documentElement.lang = language;
    document.title = t('pageTitle');
    $('meta[name="description"]').content = t('heroDescription');
    $$('[data-i18n]').forEach(node => { node.textContent = t(node.dataset.i18n); });
    $$('[data-language]').forEach(button => button.setAttribute('aria-pressed', String(button.dataset.language === language)));
    $('#main-nav').setAttribute('aria-label', t('mainNavigation'));
    $('#topic-filters').setAttribute('aria-label', t('filterLabel'));
    $('#topic-search').placeholder = t('searchPlaceholder');
    $('.hero-bottom>a').setAttribute('aria-label', t('heroExplore'));
    $('.qr-card img[src*="wechat"]').alt = t('wechatAlt');
    $('.qr-card img[src*="xiaohongshu"]').alt = t('rednoteAlt');
    setMenu(false);
    writeStorage('coach-ai-language', language);
    if (changeHash) history.replaceState(null, '', '#' + language);
    if (catalog) renderCatalog();
    else if (loadFailed) renderLoadError();
  }
  function icon(index) {
    const node = element('span', 'topic-icon');
    node.setAttribute('aria-hidden', 'true');
    const paths = [
      '<path d="M6 3c0 7 12 11 12 18M18 3C18 10 6 14 6 21M7 6h10M8 10h8M8 14h8M7 18h10"/>',
      '<path d="m12 3 8 4.5v9L12 21l-8-4.5v-9L12 3Z M4 7.5l8 4.5 8-4.5M12 12v9"/>',
      '<circle cx="12" cy="12" r="3"/><ellipse cx="12" cy="12" rx="10" ry="4" transform="rotate(-35 12 12)"/><ellipse cx="12" cy="12" rx="10" ry="4" transform="rotate(35 12 12)"/>',
      '<rect x="6" y="6" width="12" height="12" rx="2"/><path d="M9 2v4m6-4v4M9 18v4m6-4v4M2 9h4m-4 6h4m12-6h4m-4 6h4"/><path d="M10 10h4v4h-4z"/>'
    ];
    // Constant SVG artwork only; all catalog content is inserted with textContent.
    node.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.15" stroke-linecap="round" stroke-linejoin="round">' + paths[index % paths.length] + '</svg>';
    return node;
  }
  function categoryLabel(id) {
    return localized(catalog.categories.find(item => item.id === id)?.label) || id;
  }
  function renderFilters() {
    const filterRoot = $('#topic-filters');
    filterRoot.replaceChildren();
    const filters = [{id:'all', label:t('all')}, ...catalog.categories.map(item => ({id:item.id,label:localized(item.label)}))];
    filters.forEach(filter => {
      const button = element('button', 'filter-button');
      button.type = 'button';
      button.dataset.category = filter.id;
      button.setAttribute('aria-pressed', String(filter.id === selectedCategory));
      button.append(element('span', '', filter.label));
      button.append(element('span', 'filter-count', filter.id === 'all' ? catalog.topics.length : catalog.topics.filter(topic => topic.category === filter.id).length));
      button.addEventListener('click', () => {
        selectedCategory = filter.id;
        $$('.filter-button').forEach(item => item.setAttribute('aria-pressed', String(item.dataset.category === selectedCategory)));
        renderTopics();
      });
      filterRoot.append(button);
    });
  }
  function searchableText(topic) {
    const entries = [topic.title, topic.summary, topic.tags, catalog.categories.find(item => item.id === topic.category)?.label];
    return entries.flatMap(entry => typeof entry === 'object' && entry !== null ? Object.values(entry).flat() : [entry]).join(' ').normalize('NFKC').toLocaleLowerCase();
  }
  function renderTopics() {
    const grid = $('#topic-grid');
    grid.replaceChildren();
    const search = $('#topic-search').value.trim().normalize('NFKC').toLocaleLowerCase();
    const terms = search.split(/\s+/).filter(Boolean);
    const topics = catalog.topics.filter(topic => (selectedCategory === 'all' || topic.category === selectedCategory) && terms.every(term => searchableText(topic).includes(term)));
    $('#catalog-status').textContent = currentLanguage === 'en' ? `${topics.length} ${t('visibleCount')} · ${selectedCategory === 'all' ? t('all') : categoryLabel(selectedCategory)}` : `${topics.length} ${t('visibleCount')} · ${selectedCategory === 'all' ? t('all') : categoryLabel(selectedCategory)}`;
    if (!topics.length) {
      const empty = element('div', 'empty-state', t('noResults'));
      const clear = element('button', 'reset-search', t('clearSearch'));
      clear.type = 'button';
      clear.addEventListener('click', () => { selectedCategory = 'all'; $('#topic-search').value = ''; renderFilters(); renderTopics(); $('#topic-search').focus(); });
      empty.append(clear);
      grid.append(empty);
      return;
    }
    topics.forEach((topic) => {
      const card = element('article', 'topic-card');
      card.dataset.topicId = topic.id;
      const top = element('div', 'topic-card-top');
      const categoryIndex = Math.max(0, catalog.categories.findIndex(item => item.id === topic.category));
      top.append(icon(categoryIndex));
      const stage = ['practice', 'pilot', 'proposal'].includes(topic.stage) ? topic.stage : 'proposal';
      top.append(element('span', `stage-label ${stage}`, t(stage)));
      card.append(top, element('h3', '', localized(topic.title)), element('p', '', localized(topic.summary)));
      const tags = element('div', 'topic-tags');
      const tagList = localized(topic.tags);
      if (Array.isArray(tagList)) tagList.forEach(tag => tags.append(element('span', 'topic-tag', tag)));
      card.append(tags, element('div', 'topic-card-category', categoryLabel(topic.category)));
      grid.append(card);
    });
  }
  function renderHonors() {
    const grid = $('#honors-grid');
    grid.replaceChildren();
    catalog.honors.forEach(honor => {
      const card = element('article', 'honor-card');
      card.dataset.honorId = honor.id;
      const top = element('div', 'honor-top');
      top.append(element('span', 'honor-year', `${honor.year} ${t('admissionYear')}`), element('span', 'honor-badge', t('admitted')));
      card.append(top);
      if (honor.poster?.src) {
        const posterLink = element('a', 'honor-poster');
        posterLink.href = honor.poster.src;
        posterLink.target = '_blank';
        posterLink.rel = 'noopener';
        const posterAlt = t('posterAlt').replace('{year}', honor.year).replace('{student}', localized(honor.student)).replace('{university}', localized(honor.university));
        posterLink.setAttribute('aria-label', `${posterAlt} · ${t('posterNewTab')}`);
        const image = element('img', 'honor-poster-image');
        image.src = honor.poster.src;
        image.alt = posterAlt;
        image.loading = 'lazy';
        image.decoding = 'async';
        if (Number.isFinite(honor.poster.width)) image.width = honor.poster.width;
        if (Number.isFinite(honor.poster.height)) image.height = honor.poster.height;
        const caption = element('span', 'honor-poster-caption');
        const arrow = element('span', '', '↗');
        arrow.setAttribute('aria-hidden', 'true');
        caption.append(element('span', '', t('viewPoster')), arrow);
        posterLink.append(image, caption);
        card.append(posterLink);
      }
      card.append(element('h3', '', localized(honor.university)));
      if (localized(honor.school)) card.append(element('p', 'honor-school', localized(honor.school)));
      if (localized(honor.department)) card.append(element('p', 'honor-department', localized(honor.department)));
      const person = element('div', 'honor-person');
      const monogram = element('span', 'person-monogram', currentLanguage === 'en' ? localized(honor.student).split(/\s+/).filter(Boolean).at(-1)?.charAt(0) || '·' : localized(honor.student).charAt(0));
      monogram.setAttribute('aria-hidden', 'true');
      const info = element('div');
      info.append(element('p', 'person-name', localized(honor.student)), element('p', 'person-program', localized(honor.program) || t('honorProgram')));
      person.append(monogram, info);
      card.append(person);
      grid.append(card);
    });
  }
  function renderCatalog() {
    $('#topic-total').textContent = `${catalog.topics.length} ${t('count')}`;
    $('#topic-total').hidden = false;
    $('#catalog-date').textContent = `${t('updated')} ${catalog.updatedAt}`;
    renderFilters();
    renderTopics();
    renderHonors();
  }
  function renderLoadError() {
    $('#catalog-status').textContent = t('loadError');
    const grid = $('#topic-grid');
    const fallback = element('div', 'catalog-placeholder');
    fallback.append(element('p', '', t('catalogFallback')));
    const retry = element('button', 'reset-search', t('retry'));
    retry.type = 'button';
    retry.addEventListener('click', loadCatalog);
    fallback.append(retry);
    grid.replaceChildren(fallback);
  }
  async function loadCatalog() {
    if (pendingRequest) return pendingRequest;
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 12000);
    pendingRequest = (async () => {
      try {
        const response = await fetch('data/catalog.json', {cache:'no-cache', signal:controller.signal});
        if (!response.ok) throw new Error('Catalog unavailable');
        const data = await response.json();
        if (!Array.isArray(data.topics) || !Array.isArray(data.categories) || !Array.isArray(data.honors)) throw new Error('Invalid catalog');
        catalog = data;
        loadFailed = false;
        renderCatalog();
      } catch (_) {
        loadFailed = true;
        renderLoadError();
      } finally {
        clearTimeout(timeout);
        pendingRequest = null;
      }
    })();
    return pendingRequest;
  }
  $$('[data-language]').forEach(button => button.addEventListener('click', () => applyLanguage(button.dataset.language, true)));
  $('.menu-toggle').addEventListener('click', () => setMenu($('.menu-toggle').getAttribute('aria-expanded') !== 'true'));
  $$('#main-nav a').forEach(link => link.addEventListener('click', () => setMenu(false)));
  document.addEventListener('keydown', event => { if (event.key === 'Escape' && $('.menu-toggle').getAttribute('aria-expanded') === 'true') { setMenu(false); $('.menu-toggle').focus(); } });
  document.addEventListener('click', event => { if (!event.target.closest('.site-header')) setMenu(false); });
  const wideScreen = matchMedia('(min-width:921px)');
  if (wideScreen.addEventListener) wideScreen.addEventListener('change', () => setMenu(false));
  $('#topic-search').addEventListener('input', () => { if (catalog) renderTopics(); });
  window.addEventListener('hashchange', () => { const language = fromHash(); if (language) applyLanguage(language); });
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => { if (entry.isIntersecting) $$('#main-nav a').forEach(link => link.classList.toggle('active', link.hash === `#${entry.target.id}`)); });
    }, {rootMargin:'-15% 0px -55% 0px',threshold:0});
    ['topics','pathway','honors','contact'].forEach(id => observer.observe(document.getElementById(id)));
  }
  applyLanguage(currentLanguage);
  loadCatalog();
})();
