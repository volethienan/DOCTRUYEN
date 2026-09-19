// ==========================================================================
// THEME MANAGEMENT
// ==========================================================================
const THEMES = ['dark', 'sepia', 'light'];
const THEME_ICONS = {
    dark: '🌙',
    sepia: '📜',
    light: '☀️'
};

function getSavedTheme() {
    return localStorage.getItem('novel_reader_theme') || 'dark';
}

function applyTheme(theme) {
    if (!THEMES.includes(theme)) theme = 'dark';
    document.body.className = `theme-${theme}`;
    localStorage.setItem('novel_reader_theme', theme);

    // Cập nhật icon trên nút toggle navbar
    const themeIcon = document.getElementById('theme-icon');
    if (themeIcon) {
        themeIcon.textContent = THEME_ICONS[theme];
    }

    // Cập nhật active button trong toolbar reader
    document.querySelectorAll('.btn-theme-choice').forEach(btn => {
        if (btn.dataset.theme === theme) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });
}

function cycleTheme() {
    const current = getSavedTheme();
    const nextIdx = (THEMES.indexOf(current) + 1) % THEMES.length;
    applyTheme(THEMES[nextIdx]);
}

// ==========================================================================
// FONT SIZE MANAGEMENT (READER)
// ==========================================================================
let currentFontSize = parseInt(localStorage.getItem('novel_reader_font_size') || '19', 10);

function applyFontSize(size) {
    size = Math.max(15, Math.min(28, size));
    currentFontSize = size;
    localStorage.setItem('novel_reader_font_size', size.toString());

    const contentBody = document.getElementById('chapter-content-body');
    if (contentBody) {
        contentBody.style.fontSize = `${size}px`;
    }

    const indicator = document.getElementById('font-size-val');
    if (indicator) {
        indicator.textContent = `${size}px`;
    }
}

// ==========================================================================
// VIEW MODE (VI / BILINGUAL / ZH)
// ==========================================================================
function setViewMode(mode) {
    const viView = document.getElementById('content-vi-view');
    const zhView = document.getElementById('content-zh-view');
    const bilingualView = document.getElementById('content-bilingual-view');

    if (!viView || !zhView || !bilingualView) return;

    viView.style.display = 'none';
    zhView.style.display = 'none';
    bilingualView.style.display = 'none';

    if (mode === 'zh') {
        zhView.style.display = 'block';
    } else if (mode === 'bilingual') {
        bilingualView.style.display = 'block';
    } else {
        viView.style.display = 'block';
    }
    localStorage.setItem('novel_view_mode', mode);
}

// ==========================================================================
// READING PROGRESS BAR & SCROLL
// ==========================================================================
function updateReadingProgress() {
    const progressBar = document.getElementById('reading-progress-bar');
    const floatingBtn = document.getElementById('floating-top-btn');

    if (!progressBar && !floatingBtn) return;

    const scrollTop = window.scrollY || document.documentElement.scrollTop;
    const docHeight = document.documentElement.scrollHeight - window.innerHeight;
    const scrollPercent = docHeight > 0 ? (scrollTop / docHeight) * 100 : 0;

    if (progressBar) {
        progressBar.style.width = `${scrollPercent}%`;
    }

    if (floatingBtn) {
        if (scrollTop > 350) {
            floatingBtn.classList.add('visible');
        } else {
            floatingBtn.classList.remove('visible');
        }
    }
}

// ==========================================================================
// CHAPTER FILTER, SEARCH & SORT MANAGEMENT (HOMEPAGE)
// ==========================================================================
function initChapterFilterAndSort() {
    const grid = document.getElementById('chapters-grid');
    const searchInput = document.getElementById('chapter-search-input');
    const clearSearchBtn = document.getElementById('btn-search-clear');
    const btnSortAsc = document.getElementById('btn-sort-asc');
    const btnSortDesc = document.getElementById('btn-sort-desc');
    const rangeTabs = document.querySelectorAll('.range-tab');
    const countBadge = document.getElementById('visible-count');
    const resetBtn = document.getElementById('btn-reset-filters');
    const noResultsBox = document.getElementById('no-results-box');
    const clearAllFilterBtn = document.getElementById('btn-clear-all-filter');
    const jumpInput = document.getElementById('jump-input');
    const jumpGoBtn = document.getElementById('btn-jump-go');

    if (!grid) return;

    // Cache card elements and their parsed values
    const cardElements = Array.from(grid.querySelectorAll('.chapter-card'));
    const totalCount = cardElements.length;
    if (totalCount === 0) return;

    const cardsData = cardElements.map(el => {
        const titleSpan = el.querySelector('.chap-title-text');
        if (titleSpan) {
            const raw = titleSpan.textContent.trim();
            // Lược bỏ tiền tố trùng lặp "Chương XXXX:" để tiêu đề ngắn gọn, thanh lịch hơn
            const cleaned = raw.replace(/^(Chương|Chap|第)\s*\d+[\s:：章]+/i, '').trim();
            if (cleaned && cleaned.length > 1) {
                titleSpan.textContent = cleaned;
            }
        }

        return {
            element: el,
            num: parseInt(el.dataset.chapNum || '0', 10),
            title: (el.dataset.title || '').toLowerCase(),
            numStr: (el.dataset.chapNum || '').toString()
        };
    });

    // Filter state
    let state = {
        query: '',
        sort: 'asc', // 'asc' or 'desc'
        range: 'all' // 'all', '2000-2049', etc.
    };

    function parseRange(rangeStr) {
        if (!rangeStr || rangeStr === 'all') return { min: 0, max: Infinity };
        const parts = rangeStr.split('-');
        return {
            min: parseInt(parts[0], 10) || 0,
            max: parseInt(parts[1], 10) || Infinity
        };
    }

    function render() {
        const { min, max } = parseRange(state.range);
        const q = state.query.toLowerCase().trim();

        // 1. Filter
        let visibleCards = [];
        cardsData.forEach(item => {
            const matchesQuery = !q || item.numStr.includes(q) || item.title.includes(q);
            const matchesRange = item.num >= min && item.num <= max;

            if (matchesQuery && matchesRange) {
                item.element.style.display = '';
                visibleCards.push(item);
            } else {
                item.element.style.display = 'none';
            }
        });

        // 2. Sort
        visibleCards.sort((a, b) => {
            return state.sort === 'asc' ? a.num - b.num : b.num - a.num;
        });

        // Re-append elements in sorted order
        const fragment = document.createDocumentFragment();
        visibleCards.forEach(item => {
            fragment.appendChild(item.element);
        });
        grid.appendChild(fragment);

        // 3. Update Sort buttons active UI
        if (btnSortAsc && btnSortDesc) {
            if (state.sort === 'asc') {
                btnSortAsc.classList.add('active');
                btnSortDesc.classList.remove('active');
            } else {
                btnSortDesc.classList.add('active');
                btnSortAsc.classList.remove('active');
            }
        }

        // 4. Update count badge & states
        const count = visibleCards.length;
        if (countBadge) {
            const countText = countBadge.querySelector('.count-text') || countBadge;
            countText.textContent = `Hiển thị ${count}/${totalCount} chương`;
        }

        // Show/hide no results alert
        if (noResultsBox) {
            noResultsBox.style.display = count === 0 ? 'block' : 'none';
        }

        // Show/hide clear search button
        if (clearSearchBtn) {
            clearSearchBtn.style.display = q ? 'flex' : 'none';
        }

        // Show/hide reset filters button if non-default state
        const isFiltered = q !== '' || state.sort !== 'asc' || state.range !== 'all';
        if (resetBtn) {
            resetBtn.style.display = isFiltered ? 'inline-flex' : 'none';
        }
    }

    // Event: Search Input
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            state.query = e.target.value;
            render();
        });
    }

    // Event: Clear Search
    if (clearSearchBtn) {
        clearSearchBtn.addEventListener('click', () => {
            if (searchInput) {
                searchInput.value = '';
                searchInput.focus();
            }
            state.query = '';
            render();
        });
    }

    // Event: Sort Buttons
    if (btnSortAsc) {
        btnSortAsc.addEventListener('click', () => {
            if (state.sort !== 'asc') {
                state.sort = 'asc';
                render();
            }
        });
    }

    if (btnSortDesc) {
        btnSortDesc.addEventListener('click', () => {
            if (state.sort !== 'desc') {
                state.sort = 'desc';
                render();
            }
        });
    }

    // Event: Range Tabs
    rangeTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            rangeTabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            state.range = tab.dataset.range;
            render();
        });
    });

    // Reset all filters function
    function resetAll() {
        state.query = '';
        state.sort = 'asc';
        state.range = 'all';

        if (searchInput) searchInput.value = '';

        rangeTabs.forEach(t => {
            if (t.dataset.range === 'all') t.classList.add('active');
            else t.classList.remove('active');
        });

        render();
    }

    if (resetBtn) resetBtn.addEventListener('click', resetAll);
    if (clearAllFilterBtn) clearAllFilterBtn.addEventListener('click', resetAll);

    // Jump to chapter
    function handleJump() {
        if (!jumpInput) return;
        const targetChap = parseInt(jumpInput.value.trim(), 10);
        if (isNaN(targetChap)) return;

        // Check if chapter exists
        const targetItem = cardsData.find(item => item.num === targetChap);
        if (!targetItem) {
            alert(`Không tìm thấy Chương ${targetChap} trong danh sách (2000 - 2223).`);
            return;
        }

        // Reset filter so card is guaranteed to be visible
        resetAll();

        // Scroll smoothly to card
        targetItem.element.scrollIntoView({ behavior: 'smooth', block: 'center' });
        targetItem.element.classList.remove('card-highlight-pulse');
        void targetItem.element.offsetWidth; // Trigger DOM reflow
        targetItem.element.classList.add('card-highlight-pulse');
    }

    if (jumpGoBtn) jumpGoBtn.addEventListener('click', handleJump);
    if (jumpInput) {
        jumpInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                handleJump();
            }
        });
    }

    // Initial render
    render();
}

// ==========================================================================
// CONTINUE READING (HOMEPAGE)
// ==========================================================================
function initContinueReading() {
    const lastRead = localStorage.getItem('novel_last_read_chap');
    const continueBtn = document.getElementById('btn-continue-read');
    const chapNumSpan = document.getElementById('continue-chap-num');

    if (lastRead && continueBtn && chapNumSpan) {
        chapNumSpan.textContent = lastRead;
        continueBtn.style.display = 'inline-flex';
        continueBtn.addEventListener('click', () => {
            window.location.href = `/chapter/${lastRead}`;
        });
    }
}

// ==========================================================================
// KEYBOARD NAVIGATION (READER: ARROW LEFT/RIGHT)
// ==========================================================================
function initKeyboardNav() {
    document.addEventListener('keydown', (e) => {
        // Tránh kích hoạt khi người dùng đang gõ trong input
        if (['INPUT', 'TEXTAREA', 'SELECT'].includes(e.target.tagName)) return;

        if (e.key === 'ArrowLeft') {
            const prevBtn = document.getElementById('btn-prev-chap');
            if (prevBtn && prevBtn.href) {
                window.location.href = prevBtn.href;
            }
        } else if (e.key === 'ArrowRight') {
            const nextBtn = document.getElementById('btn-next-chap');
            if (nextBtn && nextBtn.href) {
                window.location.href = nextBtn.href;
            }
        }
    });
}

// ==========================================================================
// INITIALIZATION
// ==========================================================================
document.addEventListener('DOMContentLoaded', () => {
    // 1. Áp dụng Theme
    applyTheme(getSavedTheme());

    const themeToggleBtn = document.getElementById('theme-toggle-btn');
    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', cycleTheme);
    }

    document.querySelectorAll('.btn-theme-choice').forEach(btn => {
        btn.addEventListener('click', () => {
            applyTheme(btn.dataset.theme);
        });
    });

    // 2. Cỡ chữ
    applyFontSize(currentFontSize);
    const btnFontInc = document.getElementById('btn-font-inc');
    const btnFontDec = document.getElementById('btn-font-dec');
    if (btnFontInc) btnFontInc.addEventListener('click', () => applyFontSize(currentFontSize + 1));
    if (btnFontDec) btnFontDec.addEventListener('click', () => applyFontSize(currentFontSize - 1));

    // 3. Chế độ xem
    const viewModeSelect = document.getElementById('view-mode-select');
    if (viewModeSelect) {
        const savedViewMode = localStorage.getItem('novel_view_mode') || 'vi';
        viewModeSelect.value = savedViewMode;
        setViewMode(savedViewMode);
        viewModeSelect.addEventListener('change', (e) => {
            setViewMode(e.target.value);
        });
    }

    // 4. Scroll events
    window.addEventListener('scroll', updateReadingProgress, { passive: true });
    const floatingBtn = document.getElementById('floating-top-btn');
    if (floatingBtn) {
        floatingBtn.addEventListener('click', () => {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }

    // 5. Trang chủ features
    initChapterFilterAndSort();
    initContinueReading();

    // 6. Phím tắt reader
    initKeyboardNav();

    // 7. Khởi tạo Trình đọc giọng nói AI (TTS)
    initTTSPlayer();
});

// ==========================================================================
// AI VOICE TEXT-TO-SPEECH (TTS) PLAYER
// ==========================================================================
function initTTSPlayer() {
    const playerRoot = document.getElementById('tts-floating-player');
    const launchBtn = document.getElementById('btn-tts-launch');
    if (!playerRoot) return;

    if (!('speechSynthesis' in window)) {
        if (launchBtn) {
            launchBtn.addEventListener('click', () => {
                alert('Rất tiếc! Trình duyệt của bạn không hỗ trợ tính năng Web Speech Synthesis.');
            });
        }
        return;
    }

    // DOM Elements
    const miniPill = document.getElementById('tts-mini-pill');
    const mainCard = document.getElementById('tts-main-card');
    const voiceSelect = document.getElementById('tts-voice-select');
    const speedSelect = document.getElementById('tts-speed-select');
    const autoScrollCheck = document.getElementById('tts-toggle-autoscroll');
    const autoNextCheck = document.getElementById('tts-toggle-autonext');
    
    const playPauseBtn = document.getElementById('tts-btn-play-pause');
    const playIcon = document.getElementById('tts-play-icon');
    const stopBtn = document.getElementById('tts-btn-stop');
    const prevBtn = document.getElementById('tts-btn-prev');
    const nextBtn = document.getElementById('tts-btn-next');
    
    const minimizeBtn = document.getElementById('tts-btn-minimize');
    const closeBtn = document.getElementById('tts-btn-close');
    const miniPlayBtn = document.getElementById('tts-mini-play-btn');
    const miniExpandBtn = document.getElementById('tts-mini-expand');
    
    const progressTrack = document.getElementById('tts-progress-track');
    const progressFill = document.getElementById('tts-progress-fill');
    const paraCounter = document.getElementById('tts-para-counter');
    const percentIndicator = document.getElementById('tts-percent-indicator');
    const readingStatus = document.getElementById('tts-reading-status');
    const miniStatus = document.getElementById('tts-mini-status');

    const nextChapNum = playerRoot.dataset.nextChapNum;
    const currentChapNum = playerRoot.dataset.currentChapNum;

    // Collect valid paragraphs
    const paragraphs = Array.from(document.querySelectorAll('#content-vi-view .chapter-paragraph'))
        .filter(p => p.textContent.trim().length > 0);

    // State
    let currentIndex = -1;
    let isPlaying = false;
    let isPaused = false;
    let voices = [];
    let selectedVoice = null;
    let keepAliveTimer = null;
    let autoNextTimeout = null;
    let currentAudio = null; // Đối tượng Audio HTML5 cho giọng AI Studio (Edge-TTS)

    // Danh sách Giọng AI Studio Siêu Thực (Edge-TTS Neural)
    const EDGE_STUDIO_VOICES = [
        { id: 'edge:vi-VN-HoaiMyNeural', name: '🌸 Hoài My (Nữ AI Studio - Truyền cảm)' },
        { id: 'edge:vi-VN-NamMinhNeural', name: '⚡ Nam Minh (Nam AI Studio - Hào sảng)' }
    ];

    // Load saved preferences
    if (autoScrollCheck) {
        const savedScroll = localStorage.getItem('novel_tts_autoscroll');
        if (savedScroll !== null) autoScrollCheck.checked = (savedScroll === 'true');
        autoScrollCheck.addEventListener('change', () => {
            localStorage.setItem('novel_tts_autoscroll', autoScrollCheck.checked);
        });
    }

    if (autoNextCheck) {
        const savedNext = localStorage.getItem('novel_tts_autonext');
        if (savedNext !== null) autoNextCheck.checked = (savedNext === 'true');
        autoNextCheck.addEventListener('change', () => {
            localStorage.setItem('novel_tts_autonext', autoNextCheck.checked);
        });
    }

    if (speedSelect) {
        const savedSpeed = localStorage.getItem('novel_tts_speed') || '1';
        speedSelect.value = savedSpeed;
        speedSelect.addEventListener('change', () => {
            localStorage.setItem('novel_tts_speed', speedSelect.value);
            // Nếu đang đọc, phát lại đoạn hiện tại với tốc độ mới
            if (isPlaying && !isPaused && currentIndex >= 0) {
                speakParagraph(currentIndex);
            }
        });
    }

    // Sound Wave & Keep Alive
    function startKeepAlive() {
        stopKeepAlive();
        keepAliveTimer = setInterval(() => {
            if (window.speechSynthesis.speaking && !window.speechSynthesis.paused) {
                window.speechSynthesis.pause();
                window.speechSynthesis.resume();
            }
        }, 8000);
    }

    function stopKeepAlive() {
        if (keepAliveTimer) {
            clearInterval(keepAliveTimer);
            keepAliveTimer = null;
        }
    }

    function stopCurrentAudio() {
        if (currentAudio) {
            currentAudio.pause();
            currentAudio.onended = null;
            currentAudio.onerror = null;
            currentAudio.onplay = null;
            currentAudio = null;
        }
        window.speechSynthesis.cancel();
        stopKeepAlive();
    }

    // Voice Loading
    function formatVoiceLabel(v) {
        const name = v.name;
        if (name.includes('HoaiMy')) return 'Hoài My (Nữ - Microsoft Natural)';
        if (name.includes('NamMinh')) return 'Nam Minh (Nam - Microsoft Natural)';
        if (name.includes('Google') && (name.includes('tiếng Việt') || v.lang.includes('vi'))) return 'Google Tiếng Việt';
        if (name.includes('An') && v.lang.includes('vi')) return 'An (Microsoft Tiếng Việt)';
        return `${v.name} (${v.lang})`;
    }

    function populateVoices() {
        const allVoices = window.speechSynthesis.getVoices() || [];
        voiceSelect.innerHTML = '';

        // 1. Nhóm Giọng AI Studio (Chất lượng phòng thu siêu thực)
        const studioGroup = document.createElement('optgroup');
        studioGroup.label = '🌟 Giọng AI Studio (Chuẩn MC Audio)';
        EDGE_STUDIO_VOICES.forEach(ev => {
            const opt = document.createElement('option');
            opt.value = ev.id;
            opt.textContent = ev.name;
            studioGroup.appendChild(opt);
        });
        voiceSelect.appendChild(studioGroup);

        // 2. Nhóm Giọng Trình duyệt / Thiết bị (Web Speech)
        let viVoices = allVoices.filter(v => {
            const lang = (v.lang || '').toLowerCase();
            const name = (v.name || '').toLowerCase();
            return lang.startsWith('vi') || lang.includes('vietnam') || name.includes('vietnamese') || name.includes('tiếng việt');
        });

        if (allVoices.length > 0) {
            const localGroup = document.createElement('optgroup');
            localGroup.label = '💻 Giọng Trình Duyệt / Thiết Bị';

            if (viVoices.length > 0) {
                viVoices.forEach(v => {
                    const opt = document.createElement('option');
                    opt.value = v.voiceURI;
                    opt.textContent = formatVoiceLabel(v);
                    localGroup.appendChild(opt);
                });
            } else {
                allVoices.slice(0, 8).forEach(v => {
                    const opt = document.createElement('option');
                    opt.value = v.voiceURI;
                    opt.textContent = `${v.name} (${v.lang})`;
                    localGroup.appendChild(opt);
                });
            }
            voiceSelect.appendChild(localGroup);
        }

        // Chọn giọng đã lưu hoặc mặc định Hoài My AI Studio
        const savedVoiceURI = localStorage.getItem('novel_tts_voice_uri') || 'edge:vi-VN-HoaiMyNeural';
        voiceSelect.value = savedVoiceURI;
        if (!voiceSelect.value) {
            voiceSelect.value = 'edge:vi-VN-HoaiMyNeural';
        }

        // Cập nhật selectedVoice nếu là giọng Web Speech
        if (!voiceSelect.value.startsWith('edge:')) {
            selectedVoice = allVoices.find(v => v.voiceURI === voiceSelect.value) || null;
        } else {
            selectedVoice = null;
        }
    }

    populateVoices();
    if (window.speechSynthesis.onvoiceschanged !== undefined) {
        window.speechSynthesis.onvoiceschanged = populateVoices;
    }

    if (voiceSelect) {
        voiceSelect.addEventListener('change', () => {
            const val = voiceSelect.value;
            localStorage.setItem('novel_tts_voice_uri', val);

            if (val.startsWith('edge:')) {
                selectedVoice = null;
            } else {
                const allVoices = window.speechSynthesis.getVoices();
                selectedVoice = allVoices.find(v => v.voiceURI === val) || null;
            }

            if (isPlaying && !isPaused && currentIndex >= 0) {
                speakParagraph(currentIndex);
            }
        });
    }

    // UI Updates
    function updateProgressUI() {
        const total = paragraphs.length;
        if (total === 0) return;
        const currentNum = Math.max(1, currentIndex + 1);
        const percent = Math.min(100, Math.round((currentNum / total) * 100));

        if (paraCounter) paraCounter.textContent = `Đoạn ${currentNum} / ${total}`;
        if (percentIndicator) percentIndicator.textContent = `${percent}%`;
        if (progressFill) progressFill.style.width = `${percent}%`;
        if (miniStatus) miniStatus.textContent = `🎧 Chương ${currentChapNum} (${percent}%)`;
    }

    function highlightParagraph(idx) {
        paragraphs.forEach((p, i) => {
            if (i === idx) {
                p.classList.add('speaking-paragraph');
                if (autoScrollCheck && autoScrollCheck.checked) {
                    p.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }
            } else {
                p.classList.remove('speaking-paragraph');
            }
        });
    }

    function clearHighlight() {
        paragraphs.forEach(p => p.classList.remove('speaking-paragraph'));
    }

    function setPlayerState(playing, paused, statusText) {
        isPlaying = playing;
        isPaused = paused;

        if (playing && !paused) {
            playerRoot.classList.add('is-playing');
            if (playIcon) playIcon.textContent = '⏸';
            if (miniPlayBtn) miniPlayBtn.textContent = '⏸';
            if (launchBtn) launchBtn.classList.add('active');
            if (readingStatus) readingStatus.textContent = statusText || 'Đang đọc...';
        } else if (paused) {
            playerRoot.classList.remove('is-playing');
            if (playIcon) playIcon.textContent = '▶';
            if (miniPlayBtn) miniPlayBtn.textContent = '▶';
            if (readingStatus) readingStatus.textContent = statusText || 'Tạm dừng';
        } else {
            playerRoot.classList.remove('is-playing');
            if (playIcon) playIcon.textContent = '▶';
            if (miniPlayBtn) miniPlayBtn.textContent = '▶';
            if (launchBtn) launchBtn.classList.remove('active');
            if (readingStatus) readingStatus.textContent = statusText || 'Sẵn sàng';
        }
    }

    function showPlayer() {
        playerRoot.classList.add('visible');
        mainCard.style.display = 'block';
        miniPill.style.display = 'none';
    }

    function minimizePlayer() {
        mainCard.style.display = 'none';
        miniPill.style.display = 'inline-flex';
    }

    function closePlayer() {
        stopReading();
        playerRoot.classList.remove('visible');
        mainCard.style.display = 'none';
        miniPill.style.display = 'none';
        if (launchBtn) launchBtn.classList.remove('active');
    }

    // Playback Core Logic
    function speakParagraph(idx) {
        if (autoNextTimeout) {
            clearTimeout(autoNextTimeout);
            autoNextTimeout = null;
        }

        if (idx < 0) idx = 0;
        if (idx >= paragraphs.length) {
            handleChapterEnd();
            return;
        }

        stopCurrentAudio();
        currentIndex = idx;
        const pEl = paragraphs[currentIndex];
        const text = pEl.textContent.trim();

        if (!text) {
            speakParagraph(currentIndex + 1);
            return;
        }

        highlightParagraph(currentIndex);
        updateProgressUI();

        const currentVoiceVal = voiceSelect ? voiceSelect.value : 'edge:vi-VN-HoaiMyNeural';
        const rate = parseFloat(speedSelect ? speedSelect.value : '1') || 1.0;

        if (currentVoiceVal.startsWith('edge:')) {
            // Giọng AI Studio (Edge-TTS Neural)
            const edgeVoiceName = currentVoiceVal.replace('edge:', '');
            const audioUrl = `/api/tts/audio?text=${encodeURIComponent(text)}&voice=${encodeURIComponent(edgeVoiceName)}&speed=${rate}`;

            setPlayerState(true, false, 'Đang chuẩn bị giọng AI...');

            currentAudio = new Audio(audioUrl);

            currentAudio.onplay = () => {
                setPlayerState(true, false, 'Đang đọc (AI Studio)...');

                // Tải trước (prefetch) đoạn kế tiếp để chuyển câu không bị trễ
                if (currentIndex + 1 < paragraphs.length) {
                    const nextTxt = paragraphs[currentIndex + 1].textContent.trim();
                    if (nextTxt) {
                        const prefetchUrl = `/api/tts/audio?text=${encodeURIComponent(nextTxt)}&voice=${encodeURIComponent(edgeVoiceName)}&speed=${rate}`;
                        fetch(prefetchUrl, { priority: 'low' }).catch(() => {});
                    }
                }
            };

            currentAudio.onended = () => {
                if (isPlaying && !isPaused) {
                    speakParagraph(currentIndex + 1);
                }
            };

            currentAudio.onerror = (e) => {
                console.warn('Lỗi phát âm thanh Edge-TTS:', e);
                if (isPlaying && !isPaused) {
                    speakParagraph(currentIndex + 1);
                }
            };

            currentAudio.play().catch(err => {
                if (err.name !== 'AbortError') {
                    console.warn('Lỗi Audio play:', err);
                }
            });
        } else {
            // Giọng Hệ thống / Trình duyệt (SpeechSynthesis)
            const utterance = new SpeechSynthesisUtterance(text);
            if (selectedVoice) {
                utterance.voice = selectedVoice;
                utterance.lang = selectedVoice.lang || 'vi-VN';
            } else {
                utterance.lang = 'vi-VN';
            }
            utterance.rate = rate;

            utterance.onstart = () => {
                setPlayerState(true, false, 'Đang đọc...');
                startKeepAlive();
            };

            utterance.onend = () => {
                stopKeepAlive();
                if (isPlaying && !isPaused) {
                    speakParagraph(currentIndex + 1);
                }
            };

            utterance.onerror = (e) => {
                stopKeepAlive();
                if (e.error === 'canceled' || e.error === 'interrupted') return;
                console.warn('Lỗi SpeechSynthesis:', e);
                if (isPlaying && !isPaused) {
                    speakParagraph(currentIndex + 1);
                }
            };

            window.speechSynthesis.speak(utterance);
        }
    }

    function handleChapterEnd() {
        stopCurrentAudio();
        clearHighlight();
        
        if (autoNextCheck && autoNextCheck.checked && nextChapNum) {
            setPlayerState(true, false, `Hết chương! Đang chuyển Chương ${nextChapNum}...`);
            if (readingStatus) {
                readingStatus.innerHTML = `🎉 Đọc xong! <strong style="color: var(--color-accent)">Chuyển Chương ${nextChapNum}...</strong>`;
            }
            try {
                sessionStorage.setItem('novel_tts_autoplay', '1');
            } catch(e) {}

            autoNextTimeout = setTimeout(() => {
                window.location.href = `/chapter/${nextChapNum}`;
            }, 1400);
        } else {
            setPlayerState(false, false, '🏁 Đã đọc xong toàn bộ chương!');
            if (readingStatus) readingStatus.textContent = '🏁 Đã đọc xong toàn bộ chương!';
        }
    }

    function playPauseToggle() {
        const isEdge = voiceSelect && voiceSelect.value.startsWith('edge:');

        if (!isPlaying) {
            const targetIdx = currentIndex >= 0 ? currentIndex : 0;
            speakParagraph(targetIdx);
        } else if (isPaused) {
            if (isEdge && currentAudio) {
                currentAudio.play();
                setPlayerState(true, false, 'Đang đọc (AI Studio)...');
            } else {
                window.speechSynthesis.resume();
                setPlayerState(true, false, 'Đang đọc...');
                startKeepAlive();
            }
        } else {
            if (isEdge && currentAudio) {
                currentAudio.pause();
                setPlayerState(true, true, 'Tạm dừng');
            } else {
                window.speechSynthesis.pause();
                setPlayerState(true, true, 'Tạm dừng');
                stopKeepAlive();
            }
        }
    }

    function stopReading() {
        stopCurrentAudio();
        if (autoNextTimeout) {
            clearTimeout(autoNextTimeout);
            autoNextTimeout = null;
        }
        setPlayerState(false, false, 'Sẵn sàng');
        clearHighlight();
        currentIndex = -1;
        updateProgressUI();
    }

    function prevParagraph() {
        if (currentIndex > 0) {
            speakParagraph(currentIndex - 1);
        } else {
            speakParagraph(0);
        }
    }

    function nextParagraph() {
        if (currentIndex < paragraphs.length - 1) {
            speakParagraph(currentIndex + 1);
        } else {
            handleChapterEnd();
        }
    }

    // Click on progress track to seek
    if (progressTrack) {
        progressTrack.addEventListener('click', (e) => {
            const rect = progressTrack.getBoundingClientRect();
            const clickX = e.clientX - rect.left;
            const ratio = Math.max(0, Math.min(1, clickX / rect.width));
            const targetIdx = Math.floor(ratio * paragraphs.length);
            showPlayer();
            speakParagraph(targetIdx);
        });
    }

    // Attach Paragraph Click & Hover Tooltips
    paragraphs.forEach((p, idx) => {
        p.title = "Nhấp để nghe đọc từ đoạn này";
        p.addEventListener('click', (e) => {
            // Nếu người dùng đang bôi đen chữ thì không kích hoạt
            if (window.getSelection && window.getSelection().toString().trim().length > 0) {
                return;
            }
            showPlayer();
            speakParagraph(idx);
        });
    });

    // Control Buttons Events
    if (launchBtn) {
        launchBtn.addEventListener('click', () => {
            showPlayer();
            if (!isPlaying) {
                speakParagraph(currentIndex >= 0 ? currentIndex : 0);
            }
        });
    }

    if (playPauseBtn) playPauseBtn.addEventListener('click', playPauseToggle);
    if (miniPlayBtn) miniPlayBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        playPauseToggle();
    });

    if (stopBtn) stopBtn.addEventListener('click', stopReading);
    if (prevBtn) prevBtn.addEventListener('click', prevParagraph);
    if (nextBtn) nextBtn.addEventListener('click', nextParagraph);

    if (minimizeBtn) minimizeBtn.addEventListener('click', minimizePlayer);
    if (miniExpandBtn) miniExpandBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        showPlayer();
    });
    if (miniPill) miniPill.addEventListener('click', showPlayer);
    if (closeBtn) closeBtn.addEventListener('click', closePlayer);

    // Keyboard Shortcuts (Space for Play/Pause, Esc for close)
    document.addEventListener('keydown', (e) => {
        if (['INPUT', 'TEXTAREA', 'SELECT'].includes(e.target.tagName)) return;

        if (e.code === 'Space' && playerRoot.classList.contains('visible')) {
            e.preventDefault();
            playPauseToggle();
        } else if (e.key === 'Escape' && playerRoot.classList.contains('visible')) {
            closePlayer();
        }
    });

    // Check for Autoplay flag from previous chapter
    try {
        if (sessionStorage.getItem('novel_tts_autoplay') === '1') {
            sessionStorage.removeItem('novel_tts_autoplay');
            showPlayer();
            // Đợi 400ms để trình duyệt khởi động voice synthesis ổn định
            setTimeout(() => {
                populateVoices();
                speakParagraph(0);
            }, 450);
        }
    } catch(e) {}
}

