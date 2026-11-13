'use strict';
(() => {
  const languages = ['zh-CN', 'zh-TW', 'ja', 'en'];
  const copy = {
    'zh-CN': {
      pageTitle:'行知学园AI科研背景提升｜日本学部・大学院升学科研实践',pageDescription:"行知学园（行知学園 Coach Academy）AI科研背景提升：面向日本学部与大学院升学，提供生命科学、化学、智能计算、人文社会与经济经营方向的科研实践，并汇总大学官方招生要求与合格成果。",headerProgram:'AI科研背景提升',footerBrand:'行知学园 · COACH ACADEMY', skip:'跳转到正文',navTopics:'研究方向',navPath:'实践路径',navHonors:'合格成果',navContact:'咨询我们',menuOpen:'打开菜单',menuClose:'关闭菜单',mainNavigation:'主导航',
      heroProgram:'让好奇心，成为研究的起点。',heroLine1:'行知学园',heroLine2:'AI科研背景提升',heroDescription:"从生命科学、化学与智能计算，到人文社会与经济经营，在真实的研究问题中学习、实践，建立属于自己的科研视野。",heroExplore:'探索研究方向',heroHonors:'查看合格成果',heroNote:'以问题为起点 · 以实践连接知识',artLife:'生命科学',artChemistry:'化学与材料',artAI:'智能计算',artBusiness:"经济与经营",artHumanities:"人文与社会",scroll:'向下探索',
      introTitle:'把兴趣，连接到更广阔的研究世界。',introDescription:"人工智能既能帮助理解生命、探索分子，也能用于分析经济社会数据、理解经营议题、讨论技术公平性与研究伦理。我们从具体学科的问题出发，将证据分析、计算实践与表达能力连接起来。",
      topicsTitle:'从一个方向，开始探索。',topicsDescription:'浏览课题的研究领域与概要，找到与你的兴趣和学科背景相连的方向。',catalogLabel:'研究方向目录',searchLabel:'搜索研究方向',searchPlaceholder:'搜索研究方向、关键词',filterLabel:'研究领域筛选',catalogFallback:"研究方向涵盖生命科学、化学、智能计算、人文社会与经济经营。完整目录暂未加载时，可通过下方邮箱咨询。",catalogNote:'课题以领域概览呈现，具体安排结合学习基础与兴趣沟通。',all:'全部方向',practice:'已有实践',pilot:'试点探索',proposal:'方向储备',updated:'更新于',count:'个课题',visibleCount:'个方向',noResults:'暂未找到匹配的方向，试试其他关键词。',clearSearch:'清除筛选',loadError:'目录暂时无法加载，请稍后重试或邮件咨询。',retry:'重新加载',
      pathTitle:'不止了解，更要参与思考。',pathDescription:'从建立问题意识，到有条理地解释自己的发现，逐步熟悉科研的思考方式。',path1Title:'找到问题',path1Description:'结合学科兴趣与学习基础，认识领域中的研究问题。',path2Title:'建立方法',path2Description:'学习文献阅读与数据思维，理解工具与研究目标的关系。',path3Title:'动手实践',path3Description:'在实践中观察、比较与讨论，学习用证据检验自己的想法。',path4Title:'表达思考',path4Description:'梳理研究过程，清晰说明发现、局限与下一步的问题。',
      honorsTitle:'以探索，走向新的起点。',honorsDescription:'AI 科研背景提升方向的学生合格成果，记录每一次继续学习的开始。',honorsFallback:'合格成果暂未加载，可通过下方邮箱咨询。',allHonors:'查看完整合格榜',honorsNote:'录取结果按学校分别展示。',admitted:'合格',admissionYear:'年度',honorProgram:'AI 科研背景提升',posterAlt:'{year}年度 · {student} · {university}合格榜',viewPoster:'查看高清合格榜',posterNewTab:'在新窗口查看原图',
      contactLine1:'你的下一个问题，',contactLine2:'可以从这里开始。',contactDescription:'告诉我们你的专业背景与研究兴趣，一起讨论适合的探索方向。',emailUs:'邮件咨询',wechat:'微信咨询',wechatNote:'扫码联系，了解研究方向',rednote:'小红书',rednoteNote:'更多学习与科研动态',wechatAlt:'微信咨询二维码',rednoteAlt:'小红书二维码',footerProgram:'AI科研背景提升',backTop:'返回顶部'
    },
    'zh-TW': {
      pageTitle:'行知學園AI科研背景提升｜日本學部・大學院升學科研實踐',pageDescription:"行知學園（行知学园 Coach Academy）AI科研背景提升：面向日本學部與大學院升學，提供生命科學、化學、智慧運算、人文社會與經濟經營方向的科研實踐，並彙整大學官方招生要求與合格成果。",headerProgram:'AI科研背景提升',footerBrand:'行知學園 · COACH ACADEMY',skip:'跳轉到正文',navTopics:'研究方向',navPath:'實踐路徑',navHonors:'合格成果',navContact:'諮詢我們',menuOpen:'開啟選單',menuClose:'關閉選單',mainNavigation:'主導覽',
      heroProgram:'讓好奇心，成為研究的起點。',heroLine1:'行知學園',heroLine2:'AI科研背景提升',heroDescription:"從生命科學、化學與智慧運算，到人文社會與經濟經營，在真實的研究問題中學習、實踐，建立屬於自己的科研視野。",heroExplore:'探索研究方向',heroHonors:'查看合格成果',heroNote:'以問題為起點 · 以實踐連結知識',artLife:'生命科學',artChemistry:'化學與材料',artAI:'智慧運算',artBusiness:"經濟與經營",artHumanities:"人文與社會",scroll:'向下探索',
      introTitle:'把興趣，連結到更廣闊的研究世界。',introDescription:"人工智慧既能幫助理解生命、探索分子，也能用於分析經濟社會資料、理解經營議題、討論技術公平性與研究倫理。我們從具體學科的問題出發，將證據分析、運算實踐與表達能力連結起來。",
      topicsTitle:'從一個方向，開始探索。',topicsDescription:'瀏覽課題的研究領域與概要，找到與你的興趣和學科背景相連的方向。',catalogLabel:'研究方向目錄',searchLabel:'搜尋研究方向',searchPlaceholder:'搜尋研究方向、關鍵詞',filterLabel:'研究領域篩選',catalogFallback:"研究方向涵蓋生命科學、化學、智慧運算、人文社會與經濟經營。完整目錄暫未載入時，可透過下方信箱諮詢。",catalogNote:'課題以領域概覽呈現，具體安排結合學習基礎與興趣溝通。',all:'全部方向',practice:'已有實踐',pilot:'試點探索',proposal:'方向儲備',updated:'更新於',count:'個課題',visibleCount:'個方向',noResults:'暫未找到符合的方向，試試其他關鍵詞。',clearSearch:'清除篩選',loadError:'目錄暫時無法載入，請稍後重試或來信諮詢。',retry:'重新載入',
      pathTitle:'不只了解，更要參與思考。',pathDescription:'從建立問題意識，到有條理地解釋自己的發現，逐步熟悉科研的思考方式。',path1Title:'找到問題',path1Description:'結合學科興趣與學習基礎，認識領域中的研究問題。',path2Title:'建立方法',path2Description:'學習文獻閱讀與資料思維，理解工具與研究目標的關係。',path3Title:'動手實踐',path3Description:'在實踐中觀察、比較與討論，學習用證據檢驗自己的想法。',path4Title:'表達思考',path4Description:'梳理研究過程，清晰說明發現、局限與下一步的問題。',
      honorsTitle:'以探索，走向新的起點。',honorsDescription:'AI 科研背景提升方向的學生合格成果，記錄每一次繼續學習的開始。',honorsFallback:'合格成果暫未載入，可透過下方信箱諮詢。',allHonors:'查看完整合格榜',honorsNote:'錄取結果按學校分別展示。',admitted:'合格',admissionYear:'年度',honorProgram:'AI 科研背景提升',posterAlt:'{year}年度 · {student} · {university}合格榜',viewPoster:'查看高清合格榜',posterNewTab:'在新視窗查看原圖',
      contactLine1:'你的下一個問題，',contactLine2:'可以從這裡開始。',contactDescription:'告訴我們你的專業背景與研究興趣，一起討論適合的探索方向。',emailUs:'郵件諮詢',wechat:'微信諮詢',wechatNote:'掃碼聯繫，了解研究方向',rednote:'小紅書',rednoteNote:'更多學習與科研動態',wechatAlt:'微信諮詢二維碼',rednoteAlt:'小紅書二維碼',footerProgram:'AI科研背景提升',backTop:'返回頂部'
    },
    ja: {
      pageTitle:'行知学園 AI研究実践プログラム｜日本の学部・大学院進学',pageDescription:"行知学園（Coach Academy）のAI研究実践プログラム。生命科学・化学・情報科学から人文・社会科学、経済・経営まで、日本の学部・大学院進学に向けた研究実践を支援し、大学の公式募集要項と合格実績を紹介します。",headerProgram:'AI研究実践プログラム',footerBrand:'行知学園 · COACH ACADEMY',skip:'本文へ移動',navTopics:'研究テーマ',navPath:'学びの流れ',navHonors:'合格実績',navContact:'お問い合わせ',menuOpen:'メニューを開く',menuClose:'メニューを閉じる',mainNavigation:'メインナビゲーション',
      heroProgram:'好奇心を、研究の出発点に。',heroLine1:'行知学園',heroLine2:'AI研究実践プログラム',heroDescription:"生命科学・化学・情報科学から、人文・社会科学や経済・経営まで。研究課題に向き合う学びと実践を通して、自分自身の研究の視野を広げます。",heroExplore:'研究テーマを見る',heroHonors:'合格実績を見る',heroNote:'問いから始め、実践で知識をつなぐ',artLife:'生命科学',artChemistry:'化学・材料',artAI:'情報科学',artBusiness:"経済・経営",artHumanities:"人文・社会科学",scroll:'もっと見る',
      introTitle:'興味の先に、広がる研究の世界。',introDescription:"AIは生命や分子の理解に加え、経済・社会データの分析、経営課題の検討、技術の公平性や研究倫理を考えるためにも活用できます。専門分野の問いを起点に、根拠の分析、計算の実践、伝える力を結びつけます。",
      topicsTitle:'ひとつのテーマから、探究へ。',topicsDescription:'研究分野とテーマの概要から、興味や専門に合った方向を見つけてください。',catalogLabel:'研究テーマ一覧',searchLabel:'研究テーマを検索',searchPlaceholder:'研究テーマ・キーワードで検索',filterLabel:'研究分野で絞り込む',catalogFallback:"生命科学・化学・情報科学から人文・社会科学、経済・経営まで、研究の方向性を紹介しています。一覧が表示されない場合は、下記のメールでお問い合わせください。",catalogNote:'各テーマの概要を紹介しています。具体的な取り組みは学習経験や興味に合わせてご相談ください。',all:'すべて',practice:'実践あり',pilot:'試行段階',proposal:'構想段階',updated:'更新日',count:'テーマ',visibleCount:'テーマ',noResults:'該当するテーマがありません。別のキーワードをお試しください。',clearSearch:'絞り込みを解除',loadError:'一覧を読み込めませんでした。再試行するか、メールでお問い合わせください。',retry:'再読み込み',
      pathTitle:'知ることから、考えることへ。',pathDescription:'問いを立て、自分の発見を筋道立てて説明する。研究に必要な考え方を段階的に学びます。',path1Title:'問いを見つける',path1Description:'興味や学習経験を踏まえ、分野の研究課題を理解します。',path2Title:'方法を学ぶ',path2Description:'文献の読み方やデータの捉え方を学び、手法と研究目的を結びつけます。',path3Title:'実践する',path3Description:'観察・比較・議論を通して、根拠をもとに考えを確かめます。',path4Title:'考えを伝える',path4Description:'研究の過程を整理し、発見や限界、次の問いを説明します。',
      honorsTitle:'探究から、新しい一歩へ。',honorsDescription:'AI研究実践プログラムに取り組んだ学生の合格実績。次の学びに進む歩みを紹介します。',honorsFallback:'合格実績を読み込めない場合は、下記のメールでお問い合わせください。',allHonors:'合格実績一覧を見る',honorsNote:'合格実績は大学ごとに掲載しています。',admitted:'合格',admissionYear:'年度',honorProgram:'AI研究実践プログラム',posterAlt:'{year}年度 · {student} · {university} 合格実績ポスター',viewPoster:'合格ポスターを拡大',posterNewTab:'元画像を新しいウィンドウで開く',
      contactLine1:'次の問いは、',contactLine2:'ここから始まります。',contactDescription:'専門分野や研究への興味をお聞かせください。あなたに合う学びの方向を一緒に考えます。',emailUs:'メールで相談する',wechat:'WeChatで相談',wechatNote:'QRコードからお問い合わせ',rednote:'RED / 小紅書',rednoteNote:'学びと研究の最新情報',wechatAlt:'WeChat問い合わせ用QRコード',rednoteAlt:'REDのQRコード',footerProgram:'AI研究実践プログラム',backTop:'ページ上部へ'
    },
    en: {
      pageTitle:'Coach Academy AI Research Program | Japanese university admissions',pageDescription:"Coach Academy AI Research Program: research practice spanning life science, chemistry, computing, humanities, social sciences, economics and business for Japanese university applicants, with official admission requirements and acceptance results.",headerProgram:'AI Research Program',footerBrand:'COACH ACADEMY',skip:'Skip to content',navTopics:'Research directions',navPath:'The learning journey',navHonors:'Admissions',navContact:'Get in touch',menuOpen:'Open menu',menuClose:'Close menu',mainNavigation:'Main navigation',
      heroProgram:'Let curiosity be your starting point.',heroLine1:'Coach Academy',heroLine2:'AI Research Program',heroDescription:"From life science, chemistry and computing to humanities, social sciences, economics and business, build your research perspective through real questions and hands-on learning.",heroExplore:'Explore research',heroHonors:'View admissions',heroNote:'Start with a question. Connect knowledge through practice.',artLife:'Life science',artChemistry:'Chemistry',artAI:'Computing',artBusiness:"Economics & business",artHumanities:"Humanities & society",scroll:'Explore below',
      introTitle:'Connect your interests to a wider world of research.',introDescription:"AI can help us understand life and molecules, analyze economic and social data, explore business questions, and examine fairness and research ethics. Starting with questions rooted in each discipline, we connect evidence analysis, computational practice and communication.",
      topicsTitle:'Find a direction. Begin exploring.',topicsDescription:'Explore research areas and topic overviews to find connections with your interests and academic background.',catalogLabel:'Research directory',searchLabel:'Search research directions',searchPlaceholder:'Search topics or keywords',filterLabel:'Filter by research area',catalogFallback:"Our research directions span life science, chemistry, computing, humanities, social sciences, economics and business. If the directory is unavailable, please contact us by email below.",catalogNote:'These are introductory overviews. Individual activities are discussed in relation to your interests and learning experience.',all:'All areas',practice:'Practice undertaken',pilot:'Pilot exploration',proposal:'Under consideration',updated:'Updated',count:'topics',visibleCount:'topics',noResults:'No matching topics. Try another keyword or research area.',clearSearch:'Clear filters',loadError:'The directory could not be loaded. Please retry or contact us by email.',retry:'Try again',
      pathTitle:'Go beyond knowing. Start thinking.',pathDescription:'From asking a clear question to explaining your observations, build familiarity with the way research works.',path1Title:'Find a question',path1Description:'Connect your academic interests and experience with questions in a research field.',path2Title:'Build understanding',path2Description:'Learn to read the literature, reason with data and connect methods to research goals.',path3Title:'Explore in practice',path3Description:'Observe, compare and discuss. Learn to test ideas against evidence.',path4Title:'Communicate',path4Description:'Explain your process, findings and limitations, and identify questions to explore next.',
      honorsTitle:'From exploration to a new chapter.',honorsDescription:'Admissions achieved by students in our AI research program, marking the beginning of their next stage of learning.',honorsFallback:'If admission results are unavailable, please contact us by email below.',allHonors:'View all admissions',honorsNote:'Admissions are listed separately for each university.',admitted:'ADMITTED',admissionYear:'ENTRY',honorProgram:'AI Research Program',posterAlt:'{year} admission poster: {student} — {university}',viewPoster:'View full-size poster',posterNewTab:'Open original image in a new window',
      contactLine1:'Your next question',contactLine2:'can start here.',contactDescription:'Tell us about your academic background and research interests. Let’s discuss a direction that fits your learning goals.',emailUs:'Get in touch',wechat:'WeChat',wechatNote:'Scan to ask about research',rednote:'RED / Xiaohongshu',rednoteNote:'Learning and research updates',wechatAlt:'WeChat contact QR code',rednoteAlt:'Xiaohongshu QR code',footerProgram:'AI Research Program',backTop:'Back to top'
    }
  };
  const applicationCopy = {
  "zh-CN": {
    "navApplications": "升学应用",
    "navAdmissions": "大学招生要求",
    "applicationsTitle": "科研经历，如何连接升学申请？",
    "applicationsDescription": "从真实参与出发，说明你发现了什么、做过什么，以及希望继续探索什么。",
    "undergraduateLabel": "学部申请",
    "undergraduateTitle": "高中生：让经历体现思考与成长。",
    "undergraduateLead": "把自己真正参与的 AI 科研经历，转化为有事实支撑的申请表达。",
    "undergraduateUse1Title": "志望理由书",
    "undergraduateUse1": "依照学校格式，说明兴趣如何形成、经历带来的认识，以及与志望专业的联系。",
    "undergraduateUse2Title": "校内考小论文",
    "undergraduateUse2": "先回应考试题目，再选择相关经历或思考作为论据；不把科研故事硬套进所有题目。",
    "undergraduateUse3Title": "面试交流",
    "undergraduateUse3": "讲清研究问题、本人贡献、支持结论的证据与反思，展示科研思维和学习经验。",
    "undergraduateNote": "科研经历用于支持申请和展示成长，不能替代学校要求，也不保证录取。",
    "graduateLabel": "大学院申请",
    "graduateTitle": "本科生：让研究设想更具体。",
    "graduateLead": "将研究经历整理为清晰的问题意识与研究计划，帮助导师理解你的准备和兴趣。",
    "graduateUse1Title": "形成研究计划",
    "graduateUse1": "结合已有阅读与实践，说明研究问题、拟探索的方向及与目标研究室的契合度。",
    "graduateUse2Title": "联系教授",
    "graduateUse2": "先核对是否允许提前联系、发送计划书或附件；仅在允许时提供可公开的数据或结果摘要，并说明本人贡献及局限。",
    "graduateUse3Title": "沟通研究设想",
    "graduateUse3": "用具体经历支撑讨论，回应导师的问题；按选考规则沟通接收意向或争取内诺。",
    "graduateNote": "并非所有导师都要求已有科研经历。是否需要事前联系、内诺或同意书依具体选考规定，内诺不等于最终录取。",
    "admissionsTitle": "官方大学招生要求动态",
    "admissionsDescription": "按学部与大学院查看相关选考要求，理解科研经历与申请材料的具体关系。",
    "admissionsFrequency": "每小时核对官网变化",
    "admissionsAll": "全部",
    "admissionsFilterLabel": "按申请阶段筛选",
    "admissionsFallback": "具体要求因学校、项目和选考方式而异。暂未载入核对记录时，可先查看下方申请指导，并以学校当年度募集要项为准。",
    "applicationGuide": "查看科研经历的申请用途",
    "admissionsNote": "以下摘要仅适用于标注的项目、年度与选考方式；提交材料前，请打开官方来源确认。",
    "admissionsVerified": "已核对",
    "admissionsChanged": "新版本待核对",
    "admissionsUnavailable": "本次检查未成功",
    "admissionsChangedMessage": "官方页面已发生变化，旧摘要暂不展示。新版本核对完成前，请直接查看官方来源。",
    "admissionsUnavailableMessage": "本次官网检查未成功，以下保留上次核对的摘要，请打开官方来源确认。",
    "admissionsScope": "适用范围",
    "admissionsRoute": "选考方式",
    "admissionsYear": "适用年度",
    "admissionsVerifiedAt": "摘要核对日期",
    "admissionsCheckedAt": "最近检查",
    "admissionsSource": "查看官方来源",
    "admissionsCount": "条要求",
    "admissionsEmpty": "这一申请阶段暂未收录核对记录。",
    "admissionsLoadError": "暂时无法载入大学招生要求。可重试，或先查看科研经历的申请用途。",
    "admissionsRefreshError": "最新核对记录暂时无法载入，当前显示上次载入的内容；请以官方来源为准。",
    "admissionsRetry": "重新载入要求",
    "topicUpdated": "课题更新",
    "admissionsNewTab": "在新窗口打开官方来源"
  },
  "zh-TW": {
    "navApplications": "升學應用",
    "navAdmissions": "大學招生要求",
    "applicationsTitle": "科研經歷，如何連結升學申請？",
    "applicationsDescription": "從真實參與出發，說明你發現了什麼、做過什麼，以及希望繼續探索什麼。",
    "undergraduateLabel": "學部申請",
    "undergraduateTitle": "高中生：讓經歷體現思考與成長。",
    "undergraduateLead": "把自己真正參與的 AI 科研經歷，轉化為有事實支持的申請表達。",
    "undergraduateUse1Title": "志望理由書",
    "undergraduateUse1": "依照學校格式，說明興趣如何形成、經歷帶來的認識，以及與志望專業的聯繫。",
    "undergraduateUse2Title": "校內考小論文",
    "undergraduateUse2": "先回應考試題目，再選擇相關經歷或思考作為論據；不把科研故事硬套進所有題目。",
    "undergraduateUse3Title": "面試交流",
    "undergraduateUse3": "講清研究問題、本人貢獻、支持結論的證據與反思，展示科研思維和學習經驗。",
    "undergraduateNote": "科研經歷用於支持申請和展示成長，不能替代學校要求，也不保證錄取。",
    "graduateLabel": "大學院申請",
    "graduateTitle": "本科生：讓研究構想更具體。",
    "graduateLead": "將研究經歷整理為清晰的問題意識與研究計畫，幫助導師理解你的準備和興趣。",
    "graduateUse1Title": "形成研究計畫",
    "graduateUse1": "結合已有閱讀與實踐，說明研究問題、擬探索的方向及與目標研究室的契合度。",
    "graduateUse2Title": "聯繫教授",
    "graduateUse2": "先核對是否允許提前聯繫、傳送計畫書或附件；僅在允許時提供可公開的資料或結果摘要，並說明本人貢獻及局限。",
    "graduateUse3Title": "溝通研究構想",
    "graduateUse3": "用具體經歷支持討論，回應導師的問題；按選考規則溝通接收意向或爭取內諾。",
    "graduateNote": "並非所有導師都要求已有科研經歷。是否需要事前聯繫、內諾或同意書依具體選考規定，內諾不等於最終錄取。",
    "admissionsTitle": "官方大學招生要求動態",
    "admissionsDescription": "按學部與大學院查看相關選考要求，理解科研經歷與申請材料的具體關係。",
    "admissionsFrequency": "每小時核對官網變化",
    "admissionsAll": "全部",
    "admissionsFilterLabel": "按申請階段篩選",
    "admissionsFallback": "具體要求因學校、項目和選考方式而異。暫未載入核對記錄時，可先查看下方申請指引，並以學校當年度募集要項為準。",
    "applicationGuide": "查看科研經歷的申請用途",
    "admissionsNote": "以下摘要僅適用於標註的項目、年度與選考方式；提交材料前，請開啟官方來源確認。",
    "admissionsVerified": "已核對",
    "admissionsChanged": "新版本待核對",
    "admissionsUnavailable": "本次檢查未成功",
    "admissionsChangedMessage": "官方頁面已發生變化，舊摘要暫不展示。新版本核對完成前，請直接查看官方來源。",
    "admissionsUnavailableMessage": "本次官網檢查未成功，以下保留上次核對的摘要，請開啟官方來源確認。",
    "admissionsScope": "適用範圍",
    "admissionsRoute": "選考方式",
    "admissionsYear": "適用年度",
    "admissionsVerifiedAt": "摘要核對日期",
    "admissionsCheckedAt": "最近檢查",
    "admissionsSource": "查看官方來源",
    "admissionsCount": "條要求",
    "admissionsEmpty": "這一申請階段暫未收錄核對記錄。",
    "admissionsLoadError": "暫時無法載入大學招生要求。可重試，或先查看科研經歷的申請用途。",
    "admissionsRefreshError": "最新核對記錄暫時無法載入，目前顯示上次載入的內容；請以官方來源為準。",
    "admissionsRetry": "重新載入要求",
    "topicUpdated": "課題更新",
    "admissionsNewTab": "在新視窗開啟官方來源"
  },
  "ja": {
    "navApplications": "出願への活用",
    "navAdmissions": "募集要項",
    "applicationsTitle": "研究経験を、進学への準備に。",
    "applicationsDescription": "実際に取り組んだことを出発点に、発見、役割、これから探究したい問いを伝えます。",
    "undergraduateLabel": "学部出願",
    "undergraduateTitle": "高校生：経験から思考と成長を伝える。",
    "undergraduateLead": "自分が参加したAI研究の経験を、事実に基づく出願時の説明につなげます。",
    "undergraduateUse1Title": "志望理由書",
    "undergraduateUse1": "大学指定の形式に沿って、関心のきっかけ、経験から学んだこと、志望分野とのつながりを説明します。",
    "undergraduateUse2Title": "小論文試験",
    "undergraduateUse2": "設問に答えることを優先し、関連する経験や考察を論拠にします。研究の話をすべての設問に当てはめるものではありません。",
    "undergraduateUse3Title": "面接",
    "undergraduateUse3": "研究の問い、自分の貢献、結論を支える根拠と振り返りを説明し、科学的な思考と学びの経験を伝えます。",
    "undergraduateNote": "研究経験は出願を支える材料です。大学の要件に代わるものではなく、合格を保証するものでもありません。",
    "graduateLabel": "大学院出願",
    "graduateTitle": "大学生：研究の構想を具体的に。",
    "graduateLead": "研究経験を問題意識と研究計画に整理し、指導教員に自分の準備と関心を伝えます。",
    "graduateUse1Title": "研究計画を組み立てる",
    "graduateUse1": "文献や実践を踏まえ、研究課題、探究したい方向、志望研究室との接点を説明します。",
    "graduateUse2Title": "教員に連絡する",
    "graduateUse2": "事前連絡、研究計画書や添付資料の送付が認められるかを先に確認します。認められる場合に限り、公開可能なデータや結果の要約を示し、自分の貢献と限界を説明します。",
    "graduateUse3Title": "研究構想を話し合う",
    "graduateUse3": "経験をもとに議論し、教員の質問に答えます。選考規定に従って受入れの意向や内諾について相談します。",
    "graduateNote": "研究経験を必須としない教員もいます。事前連絡・内諾・同意書の要否は各選考の規定によります。内諾は最終的な合格ではありません。",
    "admissionsTitle": "公式募集要項の更新情報",
    "admissionsDescription": "学部・大学院別に選考要件を確認し、研究経験と出願書類の関係を理解しましょう。",
    "admissionsFrequency": "公式情報の変更を毎時確認",
    "admissionsAll": "すべて",
    "admissionsFilterLabel": "出願区分で絞り込む",
    "admissionsFallback": "要件は大学・課程・選考によって異なります。記録を読み込めない場合は出願への活用例をご覧のうえ、当該年度の公式募集要項を確認してください。",
    "applicationGuide": "研究経験の活用例を見る",
    "admissionsNote": "要約は記載の課程・年度・選考にのみ適用されます。出願前に必ず公式資料を確認してください。",
    "admissionsVerified": "確認済み",
    "admissionsChanged": "新版の確認待ち",
    "admissionsUnavailable": "今回の確認に失敗",
    "admissionsChangedMessage": "公式ページの変更を検出したため、旧要約は表示していません。新版の確認が完了するまでは公式資料をご覧ください。",
    "admissionsUnavailableMessage": "今回は公式ページを確認できませんでした。以下は前回確認時の要約です。公式資料も確認してください。",
    "admissionsScope": "対象範囲",
    "admissionsRoute": "選考区分",
    "admissionsYear": "対象年度",
    "admissionsVerifiedAt": "要約の確認日",
    "admissionsCheckedAt": "最終確認",
    "admissionsSource": "公式資料を見る",
    "admissionsCount": "件の要件",
    "admissionsEmpty": "この出願区分の確認記録はまだありません。",
    "admissionsLoadError": "募集情報を読み込めませんでした。再試行するか、研究経験の活用例をご覧ください。",
    "admissionsRefreshError": "最新の確認記録を読み込めませんでした。前回取得した情報を表示しています。公式資料をご確認ください。",
    "admissionsRetry": "募集情報を再読み込み",
    "topicUpdated": "テーマ更新",
    "admissionsNewTab": "公式資料を新しいウィンドウで開く"
  },
  "en": {
    "navTopics": "Research",
    "navPath": "Journey",
    "navHonors": "Results",
    "navContact": "Contact",
    "navApplications": "Applications",
    "navAdmissions": "Requirements",
    "applicationsTitle": "Connecting research with your application.",
    "applicationsDescription": "Start with work you actually participated in. Explain what you discovered, what you contributed and what you want to explore next.",
    "undergraduateLabel": "Undergraduate",
    "undergraduateTitle": "High school students: show how you think and grow.",
    "undergraduateLead": "Turn your own AI research experience into an application narrative grounded in what you have done.",
    "undergraduateUse1Title": "Statement of purpose",
    "undergraduateUse1": "Follow the university’s format. Explain how your interest developed, what you learned and how it connects to your chosen field.",
    "undergraduateUse2Title": "Entrance-exam essays",
    "undergraduateUse2": "Answer the actual question first. Use relevant experience as evidence rather than forcing a research story into every prompt.",
    "undergraduateUse3Title": "Interviews",
    "undergraduateUse3": "Explain the research question, your contribution, the evidence and your reflections to demonstrate scientific thinking and learning.",
    "undergraduateNote": "Research experience can support an application. It does not replace university requirements or guarantee admission.",
    "graduateLabel": "Graduate",
    "graduateTitle": "University students: make your research ideas concrete.",
    "graduateLead": "Organize your experience into a clear research question and plan to help a prospective supervisor understand your preparation and interests.",
    "graduateUse1Title": "Develop a research plan",
    "graduateUse1": "Connect your reading and practice to a research question, a possible direction and the interests of your target laboratory.",
    "graduateUse2Title": "Contact a professor",
    "graduateUse2": "First check whether advance contact, research plans or attachments are permitted. Only when allowed, share public data or a results summary and explain your contribution and limitations.",
    "graduateUse3Title": "Discuss your proposal",
    "graduateUse3": "Ground the discussion in your experience and respond to questions. Follow the selection rules when seeking supervisory interest or preliminary acceptance.",
    "graduateNote": "Not every professor requires prior research. Requirements for contact, preliminary acceptance or written consent depend on the selection process. Preliminary acceptance is not final admission.",
    "admissionsTitle": "Official admissions requirements",
    "admissionsDescription": "Browse undergraduate and graduate requirements to understand how research experience relates to application materials.",
    "admissionsFrequency": "Official sources checked hourly",
    "admissionsAll": "All levels",
    "admissionsFilterLabel": "Filter by application level",
    "admissionsFallback": "Requirements vary by university, program and selection route. If records are unavailable, explore the application guidance and consult the official guidelines for the relevant year.",
    "applicationGuide": "Explore how research supports applications",
    "admissionsNote": "Each summary applies only to the named program, year and selection route. Open the official source before submitting an application.",
    "admissionsVerified": "Verified",
    "admissionsChanged": "New version awaiting review",
    "admissionsUnavailable": "Latest check unsuccessful",
    "admissionsChangedMessage": "The official page has changed, so the previous summary is hidden. Please consult the official source while the new version is reviewed.",
    "admissionsUnavailableMessage": "The latest source check was unsuccessful. The last verified summary is shown below; please also consult the official source.",
    "admissionsScope": "Applies to",
    "admissionsRoute": "Selection route",
    "admissionsYear": "Academic year",
    "admissionsVerifiedAt": "Summary verified",
    "admissionsCheckedAt": "Last checked",
    "admissionsSource": "View official source",
    "admissionsCount": "requirements",
    "admissionsEmpty": "No verified records are listed for this application level yet.",
    "admissionsLoadError": "Admissions records could not be loaded. Retry or explore the research application guidance.",
    "admissionsRefreshError": "The latest records could not be loaded. Previously loaded information remains visible; please consult the official sources.",
    "admissionsRetry": "Reload requirements",
    "topicUpdated": "Topic updated",
    "admissionsNewTab": "Open official source in a new window"
  }
};
  languages.forEach(language => Object.assign(copy[language], applicationCopy[language]));
  const $ = selector => document.querySelector(selector);
  const $$ = selector => [...document.querySelectorAll(selector)];
  let catalog = null;
  let loadFailed = false;
  let selectedCategory = 'all';
  let currentLanguage = 'zh-CN';
  let pendingRequest = null;
  let admissionsData = null;
  let admissionsLoadFailed = false;
  let pendingAdmissions = null;
  let selectedLevel = 'all';
  let lastAdmissionsLoad = 0;
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
    $('.brand').setAttribute('aria-label', `${t('heroLine1')} · ${t('headerProgram')}`);
    $('meta[name="description"]').content = t('pageDescription');
    $$('[data-i18n]').forEach(node => { node.textContent = t(node.dataset.i18n); });
    $$('[data-language]').forEach(button => button.setAttribute('aria-pressed', String(button.dataset.language === language)));
    $('#main-nav').setAttribute('aria-label', t('mainNavigation'));
    $('#topic-filters').setAttribute('aria-label', t('filterLabel'));
    $('#admissions-filters').setAttribute('aria-label', t('admissionsFilterLabel'));
    $('#topic-search').placeholder = t('searchPlaceholder');
    $('.hero-bottom>a').setAttribute('aria-label', t('heroExplore'));
    $('.qr-card img[src*="wechat"]').alt = t('wechatAlt');
    $('.qr-card img[src*="xiaohongshu"]').alt = t('rednoteAlt');
    setMenu(false);
    writeStorage('coach-ai-language', language);
    if (changeHash) history.replaceState(null, '', '#' + language);
    if (catalog) renderCatalog();
    else if (loadFailed) renderLoadError();
    if (admissionsData) renderAdmissions();
    else if (admissionsLoadFailed) renderAdmissionsError();
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
      if (topic.updatedAt) card.append(element('p', 'topic-updated', `${t('topicUpdated')} ${formatRecordDate(topic.updatedAt)}`));
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
  function formatRecordDate(value) {
    if (!value) return '';
    const text = String(value);
    if (/^\d{4}-\d{2}-\d{2}$/.test(text)) return text;
    const date = new Date(text);
    if (Number.isNaN(date.getTime())) return text;
    return new Intl.DateTimeFormat(currentLanguage, {timeZone:'Asia/Tokyo',year:'numeric',month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit',hour12:false}).format(date) + ' JST';
  }
  function sourceLink(url) {
    try {
      const parsed = new URL(url);
      if (!['https:', 'http:'].includes(parsed.protocol)) return null;
      const link = element('a', 'admission-source');
      link.href = parsed.href;
      link.target = '_blank';
      link.rel = 'noopener';
      link.setAttribute('aria-label', t('admissionsNewTab'));
      const arrow = element('span', '', '↗');
      arrow.setAttribute('aria-hidden', 'true');
      link.append(element('span', '', t('admissionsSource')), arrow);
      return link;
    } catch (_) { return null; }
  }
  function admissionDetail(list, label, value) {
    if (!value) return;
    const row = element('div', 'admission-detail');
    row.append(element('dt', '', label), element('dd', '', value));
    list.append(row);
  }
  function renderAdmissions() {
    const grid = $('#admissions-grid');
    grid.replaceChildren();
    const records = admissionsData.items.filter(item => selectedLevel === 'all' || item.level === selectedLevel);
    const status = $('#admissions-status');
    status.replaceChildren(element('span', '', admissionsLoadFailed ? t('admissionsRefreshError') : `${records.length} ${t('admissionsCount')}`));
    status.classList.toggle('has-error', admissionsLoadFailed);
    if (admissionsLoadFailed) {
      const retry = element('button', 'admissions-retry', t('admissionsRetry'));
      retry.type = 'button';
      retry.addEventListener('click', loadAdmissions);
      status.append(retry);
    }
    $('#admissions-checked').textContent = admissionsData.checkedAt ? `${t('admissionsCheckedAt')} ${formatRecordDate(admissionsData.checkedAt)}` : '';
    $('#admissions-updated').textContent = admissionsData.updatedAt ? `${t('updated')} ${formatRecordDate(admissionsData.updatedAt)}` : '';
    if (!records.length) grid.append(element('p', 'empty-state', t('admissionsEmpty')));
    records.forEach(item => {
      const recordStatus = ['verified','changed','unavailable'].includes(item.status) ? item.status : 'unavailable';
      const card = element('article', `admission-card admission-${recordStatus}`);
      card.dataset.admissionId = item.id;
      card.dataset.status = recordStatus;
      const top = element('div', 'admission-card-top');
      top.append(element('span', 'admission-level', t(item.level === 'undergraduate' ? 'undergraduateLabel' : 'graduateLabel')));
      const statusKey = {verified:'admissionsVerified',changed:'admissionsChanged',unavailable:'admissionsUnavailable'}[recordStatus];
      top.append(element('span', `admission-status-badge ${recordStatus}`, t(statusKey)));
      card.append(top, element('h3', '', localized(item.university)));
      if (localized(item.program)) card.append(element('h4', 'admission-program', localized(item.program)));
      if (recordStatus !== 'verified') card.append(element('p', 'admission-notice', t(recordStatus === 'changed' ? 'admissionsChangedMessage' : 'admissionsUnavailableMessage')));
      // A changed source has no current verified summary. Hide old requirements,
      // scope and tags until editorial review confirms the new version.
      if (recordStatus !== 'changed') {
        const details = element('dl', 'admission-details');
        admissionDetail(details, t('admissionsYear'), item.academicYear);
        admissionDetail(details, t('admissionsRoute'), localized(item.route));
        admissionDetail(details, t('admissionsScope'), localized(item.scope));
        card.append(details);
        if (localized(item.summary)) card.append(element('p', 'admission-summary', localized(item.summary)));
        const tags = localized(item.tags);
        if (Array.isArray(tags) && tags.length) {
          const tagList = element('div', 'admission-tags');
          tags.forEach(tag => tagList.append(element('span', 'topic-tag', tag)));
          card.append(tagList);
        }
      }
      const bottom = element('div', 'admission-card-bottom');
      const dates = element('div', 'admission-dates');
      if (item.verifiedAt) dates.append(element('p', '', `${t('admissionsVerifiedAt')} ${formatRecordDate(item.verifiedAt)}`));
      if (item.checkedAt) dates.append(element('p', '', `${t('admissionsCheckedAt')} ${formatRecordDate(item.checkedAt)}`));
      bottom.append(dates);
      const official = sourceLink(item.sourceUrl);
      if (official) bottom.append(official);
      card.append(bottom);
      grid.append(card);
    });
  }
  function renderAdmissionsError() {
    $('#admissions-status').textContent = t('admissionsLoadError');
    $('#admissions-status').classList.add('has-error');
    const fallback = element('div', 'admissions-fallback');
    fallback.append(element('p', '', t('admissionsFallback')));
    const actions = element('div', 'admissions-fallback-actions');
    const retry = element('button', 'button button-dark', t('admissionsRetry'));
    retry.type = 'button';
    retry.addEventListener('click', loadAdmissions);
    const guide = element('a', 'text-link', t('applicationGuide'));
    guide.href = '#applications';
    actions.append(retry, guide);
    fallback.append(actions);
    $('#admissions-grid').replaceChildren(fallback);
  }
  async function loadAdmissions() {
    if (pendingAdmissions) return pendingAdmissions;
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 12000);
    pendingAdmissions = (async () => {
      try {
        const response = await fetch('data/admissions.json', {cache:'no-cache', signal:controller.signal});
        if (!response.ok) throw new Error('Admissions unavailable');
        const data = await response.json();
        if (!data || !Array.isArray(data.items) || !data.items.every(item => item && typeof item.id === 'string' && ['undergraduate','graduate'].includes(item.level))) throw new Error('Invalid admissions data');
        admissionsData = data;
        admissionsLoadFailed = false;
        lastAdmissionsLoad = Date.now();
        renderAdmissions();
      } catch (_) {
        admissionsLoadFailed = true;
        if (admissionsData) renderAdmissions();
        else renderAdmissionsError();
      } finally {
        clearTimeout(timeout);
        pendingAdmissions = null;
      }
    })();
    return pendingAdmissions;
  }
  $$('[data-language]').forEach(button => button.addEventListener('click', () => applyLanguage(button.dataset.language, true)));
  $('.menu-toggle').addEventListener('click', () => setMenu($('.menu-toggle').getAttribute('aria-expanded') !== 'true'));
  $$('#main-nav a').forEach(link => link.addEventListener('click', () => setMenu(false)));
  document.addEventListener('keydown', event => { if (event.key === 'Escape' && $('.menu-toggle').getAttribute('aria-expanded') === 'true') { setMenu(false); $('.menu-toggle').focus(); } });
  document.addEventListener('click', event => { if (!event.target.closest('.site-header')) setMenu(false); });
  const wideScreen = matchMedia('(min-width:1201px)');
  if (wideScreen.addEventListener) wideScreen.addEventListener('change', () => setMenu(false));
  $('#topic-search').addEventListener('input', () => { if (catalog) renderTopics(); });
  window.addEventListener('hashchange', () => { const language = fromHash(); if (language) applyLanguage(language); });
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => { if (entry.isIntersecting) $$('#main-nav a').forEach(link => link.classList.toggle('active', link.hash === `#${entry.target.id}`)); });
    }, {rootMargin:'-15% 0px -55% 0px',threshold:0});
    ['topics','pathway','applications','admissions','honors','contact'].forEach(id => observer.observe(document.getElementById(id)));
  }
  $$('#admissions-filters [data-level]').forEach(button => button.addEventListener('click', () => {
    selectedLevel = button.dataset.level;
    $$('#admissions-filters [data-level]').forEach(item => item.setAttribute('aria-pressed', String(item.dataset.level === selectedLevel)));
    if (admissionsData) renderAdmissions();
  }));
  const admissionsRefreshInterval = 60 * 60 * 1000;
  setInterval(() => { if (!document.hidden) loadAdmissions(); }, admissionsRefreshInterval);
  document.addEventListener('visibilitychange', () => {
    if (!document.hidden && Date.now() - lastAdmissionsLoad >= admissionsRefreshInterval) loadAdmissions();
  });
  applyLanguage(currentLanguage);
  loadCatalog();
  loadAdmissions();
})();
