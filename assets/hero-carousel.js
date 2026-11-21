(() => {
  'use strict';

  const hero = document.querySelector('[data-hero-carousel]');
  if (!hero) return;

  const slides = Array.from(hero.querySelectorAll('.hero-slide[data-hero-key]'));
  const dots = Array.from(hero.querySelectorAll('[data-hero-dot]'));
  const controls = hero.querySelector('[data-hero-controls]');
  const previous = hero.querySelector('[data-hero-prev]');
  const next = hero.querySelector('[data-hero-next]');
  const toggle = hero.querySelector('[data-hero-toggle]');
  const toggleLabel = hero.querySelector('[data-hero-toggle-label]');
  const caption = hero.querySelector('[data-hero-caption]');
  const counter = hero.querySelector('[data-hero-counter]');
  if (!slides.length || !controls || !previous || !next || !toggle) return;

  const copy = {
    'zh-CN': {
      group: '科研现场照片', previous: '上一张照片', next: '下一张照片',
      pause: '暂停轮播', play: '播放轮播', fallback: '科研现场',
      scenes: { server: 'GPU科研计算环境', lab: 'AI研究室', he: '何同学 · 科研学习', jin: '金同学 · 细胞培养', ma: '马同学 · 发表练习' },
      photo: (number, title) => `显示第${number}张照片：${title}`
    },
    'zh-TW': {
      group: '科研現場照片', previous: '上一張照片', next: '下一張照片',
      pause: '暫停輪播', play: '播放輪播', fallback: '科研現場',
      scenes: { server: 'GPU科研計算環境', lab: 'AI研究室', he: '何同學 · 科研學習', jin: '金同學 · 細胞培養', ma: '馬同學 · 發表練習' },
      photo: (number, title) => `顯示第${number}張照片：${title}`
    },
    ja: {
      group: '研究現場の写真', previous: '前の写真', next: '次の写真',
      pause: '自動再生を停止', play: '自動再生を開始', fallback: '研究の現場',
      scenes: { server: '研究用GPUサーバー', lab: 'AI研究室', he: '何さん · 研究活動', jin: '金さん · 細胞培養', ma: '馬さん · 発表練習' },
      photo: (number, title) => `写真${number}を表示：${title}`
    },
    en: {
      group: 'Research in practice', previous: 'Previous photo', next: 'Next photo',
      pause: 'Pause slideshow', play: 'Play slideshow', fallback: 'Research in practice',
      scenes: { server: 'GPU research computing', lab: 'AI research lab', he: 'Student He · Research in practice', jin: 'Student Jin · Cell culture', ma: 'Student Ma · Presentation practice' },
      photo: (number, title) => `Show photo ${number}: ${title}`
    }
  };

  const motion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const states = slides.map(() => 'loading');
  let active = Math.max(0, slides.findIndex(slide => slide.classList.contains('is-active')));
  let userPaused = motion.matches;
  let userChosePlayback = false;
  let allowPlaybackDuringInteraction = false;
  let hovering = false;
  let focused = controls.contains(document.activeElement);
  let timer = null;

  function language() {
    return copy[document.documentElement.lang] || copy['zh-CN'];
  }

  function ready() {
    return states.flatMap((state, index) => state === 'ready' ? [index] : []);
  }

  function stopTimer() {
    window.clearTimeout(timer);
    timer = null;
  }

  function schedule() {
    stopTimer();
    if (userPaused || ((hovering || focused) && !allowPlaybackDuringInteraction) || document.hidden || states[active] !== 'ready' || ready().length < 2) return;
    timer = window.setTimeout(() => step(1), 6000);
  }

  function render() {
    const text = language();
    const available = ready();
    const scene = slides[active] && text.scenes[slides[active].dataset.heroKey];
    slides.forEach((slide, index) => {
      slide.classList.toggle('is-active', index === active && states[index] !== 'failed');
      slide.setAttribute('aria-hidden', 'true');
    });
    dots.forEach(dot => {
      const index = Number(dot.dataset.heroDot);
      const selected = index === active;
      const title = slides[index] && text.scenes[slides[index].dataset.heroKey];
      dot.classList.toggle('is-active', selected);
      dot.setAttribute('aria-pressed', String(selected));
      dot.setAttribute('aria-label', text.photo(index + 1, title || text.fallback));
      dot.disabled = states[index] !== 'ready';
    });
    previous.disabled = next.disabled = toggle.disabled = available.length < 2;
    previous.setAttribute('aria-label', text.previous);
    next.setAttribute('aria-label', text.next);
    toggle.setAttribute('aria-label', userPaused ? text.play : text.pause);
    toggle.setAttribute('data-paused', String(userPaused));
    toggle.classList.toggle('is-paused', userPaused);
    if (toggleLabel) toggleLabel.textContent = userPaused ? text.play : text.pause;
    controls.setAttribute('aria-label', text.group);
    if (caption) caption.textContent = scene || text.fallback;
    if (counter) {
      const position = available.indexOf(active);
      counter.textContent = position < 0 ? '— / —' : `${String(position + 1).padStart(2, '0')} / ${String(available.length).padStart(2, '0')}`;
    }
  }

  function show(index) {
    if (states[index] !== 'ready') return;
    active = index;
    render();
    schedule();
  }

  function step(direction) {
    const available = ready();
    if (available.length < 2) return;
    const position = available.indexOf(active);
    const target = position < 0 ? (direction > 0 ? 0 : available.length - 1) : (position + direction + available.length) % available.length;
    show(available[target]);
  }

  function settle(index, succeeded) {
    if (states[index] === 'failed' || (succeeded && states[index] === 'ready')) return;
    states[index] = succeeded ? 'ready' : 'failed';
    if (states[active] === 'failed' || active < 0) {
      const available = ready();
      active = available.find(candidate => candidate > index) ?? available[0] ?? -1;
    }
    render();
    schedule();
  }

  previous.addEventListener('click', () => { allowPlaybackDuringInteraction = false; step(-1); });
  next.addEventListener('click', () => { allowPlaybackDuringInteraction = false; step(1); });
  dots.forEach(dot => dot.addEventListener('click', () => {
    allowPlaybackDuringInteraction = false;
    show(Number(dot.dataset.heroDot));
  }));
  toggle.addEventListener('click', () => {
    userChosePlayback = true;
    userPaused = !userPaused;
    allowPlaybackDuringInteraction = !userPaused;
    render();
    schedule();
  });
  controls.addEventListener('mouseenter', () => {
    hovering = true;
    allowPlaybackDuringInteraction = false;
    stopTimer();
  });
  controls.addEventListener('mouseleave', () => {
    hovering = false;
    if (!focused) allowPlaybackDuringInteraction = false;
    schedule();
  });
  controls.addEventListener('focusin', () => {
    focused = true;
    allowPlaybackDuringInteraction = false;
    stopTimer();
  });
  controls.addEventListener('focusout', () => {
    queueMicrotask(() => {
      focused = controls.contains(document.activeElement);
      if (!focused && !hovering) allowPlaybackDuringInteraction = false;
      schedule();
    });
  });
  controls.addEventListener('keydown', event => {
    if (event.altKey || event.ctrlKey || event.metaKey || event.shiftKey) return;
    const available = ready();
    if (!available.length) return;
    if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) return;
    allowPlaybackDuringInteraction = false;
    if (event.key === 'ArrowLeft') step(-1);
    else if (event.key === 'ArrowRight') step(1);
    else if (event.key === 'Home') show(available[0]);
    else if (event.key === 'End') show(available[available.length - 1]);
    event.preventDefault();
  });
  document.addEventListener('visibilitychange', schedule);
  window.addEventListener('pagehide', stopTimer);
  window.addEventListener('pageshow', schedule);
  motion.addEventListener('change', event => {
    if (!userChosePlayback) userPaused = event.matches;
    render();
    schedule();
  });
  new MutationObserver(render).observe(document.documentElement, { attributes: true, attributeFilter: ['lang'] });

  slides.forEach((slide, index) => {
    const image = slide.querySelector('img');
    if (!image) { settle(index, false); return; }
    image.alt = '';
    image.loading = 'eager';
    image.addEventListener('load', () => settle(index, image.naturalWidth > 0), { once: true });
    image.addEventListener('error', () => settle(index, false), { once: true });
    if (image.complete) settle(index, image.naturalWidth > 0);
  });
  render();
  schedule();
})();
