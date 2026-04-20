/* ==========================================================================
    新アルバトロス：統合コントロールスクリプト (new_help_filter.js)
   ========================================================================== */

document.addEventListener('DOMContentLoaded', function() {

    // 🛡️ 逆止弁：チャート画面以外では実行しない
    const chartTabContainer = document.getElementById('pills-tab');
    if (!chartTabContainer) return;

    console.log("アルバトロス・システム起動...🚀");

    // 各エリアの「器」を準備
    const beginnerIntermediatePane = document.getElementById('pills-chart-area');
    const advancedTabPane = document.getElementById('pills-advanced');

    /* ---------------------------------------------------------
        1. 共通・初期化ブロック (Common Setup)
       --------------------------------------------------------- */
    // モーダルの初期化
    const confirmModalEl = document.getElementById('confirmSaveModal');
    const confirmSaveModal = confirmModalEl ? new bootstrap.Modal(confirmModalEl) : null;
    const confirmSaveButton = document.getElementById('confirmSaveButton');
    
    const messageModalEl = document.getElementById('messageModal');
    const messageModal = messageModalEl ? new bootstrap.Modal(messageModalEl) : null;
    const messageModalText = document.getElementById('messageModalText');

    // タブ復元 ＆ 保存ロジック (まとめちゃったよ！✨)
    const allTabs = document.querySelectorAll('#pills-tab .nav-link');
    
    // ① ページ読み込み時に復元
    const savedTabId = localStorage.getItem('activeChartTabId');
    if (savedTabId) {
        const tabToActivate = document.getElementById(savedTabId);
        if (tabToActivate) new bootstrap.Tab(tabToActivate).show();
    }

    // ② クリック時に保存
    allTabs.forEach(tab => {
        tab.addEventListener('click', (e) => {
            const activeTabId = e.target.id;
            localStorage.setItem('activeChartTabId', activeTabId);
            console.log(`タブの状態を保存しました: ${activeTabId}`);
        });
    });


    /* ---------------------------------------------------------
        2. 初級・中級モードブロック (Beginner/Intermediate)
       --------------------------------------------------------- */
    if (beginnerIntermediatePane) {
        console.log("初級/中級モード接続完了✨");

        const allStepElements = beginnerIntermediatePane.querySelectorAll('.chart-step');
        let userAnswers = {};
        allStepElements.forEach(step => { userAnswers[step.dataset.stepId] = null; });
        
        const allQuestionTextElements = beginnerIntermediatePane.querySelectorAll('.step-question-text');
        const beginnerTab = document.getElementById('pills-beginner-tab');
        const intermediateTab = document.getElementById('pills-intermediate-tab');
        let improvementWasFound = false;

        function switchChartText(level) {
            allQuestionTextElements.forEach(p => {
                const card = p.closest('.chart-step');
                let newText = (level === 'beginner') ? card.dataset.textBeginner : card.dataset.textIntermediate;
                p.innerHTML = newText.replace(/\n/g, '<br>');
            });
        }

        function updateStepAppearance(stepElement, yesButton, noButton, currentAnswer) {
            yesButton.classList.remove('selected-button');
            noButton.classList.remove('selected-button');
            if (currentAnswer) {
                stepElement.classList.add('answered-step');
                if (currentAnswer === 'yes') yesButton.classList.add('selected-button');
                else noButton.classList.add('selected-button');
            } else {
                stepElement.classList.remove('answered-step');
            }
        }
        
        function updateFinalStepStyles() {
            const finalCards = beginnerIntermediatePane.querySelectorAll('.chart-step[data-is-final-step="true"]');
            finalCards.forEach(card => {
                card.classList.remove('final-step-improved', 'final-step-unresolved');
                if (improvementWasFound) {
                    if (card.dataset.solutionType === 'improved') card.classList.add('final-step-improved');
                } else {
                    if (card.dataset.solutionType === 'unresolved') card.classList.add('final-step-unresolved');
                }
            });
        }

        function handleAnswer(buttonType, stepElement, yesButton, noButton) {
            const currentStepId = stepElement.dataset.stepId;
            const previousAnswer = userAnswers[currentStepId];
            userAnswers[currentStepId] = (previousAnswer === buttonType) ? null : buttonType;
            
            improvementWasFound = Object.values(userAnswers).includes('yes');
            updateStepAppearance(stepElement, yesButton, noButton, userAnswers[currentStepId]);
            updateFinalStepStyles();

            if (userAnswers[currentStepId]) {
                const nextStepId = (userAnswers[currentStepId] === 'yes') ? yesButton.dataset.nextStepId : noButton.dataset.nextStepId;
                if (nextStepId) {
                    const nextStepElement = document.querySelector(`.chart-step[data-step-id="${nextStepId}"]`);
                    if (nextStepElement && !nextStepElement.classList.contains('answered-step')) {
                        nextStepElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    }
                }
            }
        }
        
        allStepElements.forEach(stepElement => {
            const yesButton = stepElement.querySelector('.btn-yes');
            const noButton = stepElement.querySelector('.btn-no');
            if(yesButton && noButton) {
                yesButton.addEventListener('click', () => handleAnswer('yes', stepElement, yesButton, noButton));
                noButton.addEventListener('click', () => handleAnswer('no', stepElement, yesButton, noButton));
            }
        });

        if (beginnerTab) beginnerTab.addEventListener('click', () => switchChartText('beginner'));
        if (intermediateTab) intermediateTab.addEventListener('click', () => switchChartText('intermediate'));

        const saveLogButton = document.getElementById('save-log-button');
        if (saveLogButton && confirmSaveModal) {
            saveLogButton.onclick = function() {
                confirmSaveModal.show();
                confirmSaveButton.onclick = function() {
                    confirmSaveModal.hide();
                    fetchData(userAnswers);
                };
            };
        }
        
        // 初期表示をセット！
        switchChartText('beginner');
        updateFinalStepStyles();
    }


    /* ---------------------------------------------------------
        3. 上級モードブロック (Advanced Mode)
       --------------------------------------------------------- */
    if (advancedTabPane) {
        console.log("上級モード接続完了✨");

        let checkedSteps = {}; 
        const allNormalTiles = advancedTabPane.querySelectorAll('.tile[data-step-id]');

        allNormalTiles.forEach(tile => {
            const stepId = tile.dataset.stepId;
            checkedSteps[stepId] = false;

            tile.addEventListener('click', function() {
                checkedSteps[stepId] = !checkedSteps[stepId];
                if (checkedSteps[stepId]) {
                    this.classList.add('tile-checked');
                    const now = new Date();
                    const timeStr = now.getHours().toString().padStart(2, '0') + ":" + now.getMinutes().toString().padStart(2, '0');
                    this.querySelector('.tile-timestamp').textContent = timeStr;
                } else {
                    this.classList.remove('tile-checked');
                    this.querySelector('.tile-timestamp').textContent = '';
                }
            });
        });

        const saveResolvedBtn = document.getElementById('save-resolved-log-btn');
        const saveUnresolvedBtn = document.getElementById('save-unresolved-log-btn');

        if (saveResolvedBtn) saveResolvedBtn.onclick = () => triggerSaveProcess(false);
        if (saveUnresolvedBtn) saveUnresolvedBtn.onclick = () => triggerSaveProcess(true);

        function triggerSaveProcess(isUnresolved) {
            const answersForBackend = {};
            const checkedTileIds = Object.keys(checkedSteps).filter(id => checkedSteps[id]);

            if (checkedTileIds.length === 0 && !isUnresolved) {
                messageModalText.textContent = "操作タイルを少なくとも1つ選択してください！";
                messageModal.show();
                return;
            }

            allNormalTiles.forEach(tile => {
                const stepId = tile.dataset.stepId;
                answersForBackend[stepId] = checkedSteps[stepId] ? 'no' : 'unknown';
            });

            let lastStepId = null;
            if (!isUnresolved && checkedTileIds.length > 0) {
                lastStepId = checkedTileIds.reduce((a, b) => {
                    const orderA = parseInt(document.querySelector(`.tile[data-step-id="${a}"]`).dataset.displayOrder);
                    const orderB = parseInt(document.querySelector(`.tile[data-step-id="${b}"]`).dataset.displayOrder);
                    return orderB > orderA ? b : a;
                });
                answersForBackend[lastStepId] = 'yes';
            }

            confirmSaveModal.show();
            confirmSaveButton.onclick = function() {
                confirmSaveModal.hide();
                fetchDataForAdvanced(answersForBackend, !isUnresolved, lastStepId);
            };
        }
    }

    /* ---------------------------------------------------------
        4. 使い方ヘルプ機能ブロック (Help Filter)
       --------------------------------------------------------- */
    const helpToggleBtn = document.getElementById('help-toggle-link');
    const helpOverlay = document.getElementById('help-overlay');

    if (helpToggleBtn && helpOverlay) {
        let isHelpActive = false;

        function resetAllTooltips() {
            const groups = helpOverlay.querySelectorAll('.help-tooltip-group');
            groups.forEach(g => g.style.display = 'none');
            const tooltips = helpOverlay.querySelectorAll('.help-tooltip');
            tooltips.forEach(t => {
                t.style.visibility = 'hidden';
                t.style.opacity = '0';
            });
        }

        function updateTooltipsPosition() {
            if (!isHelpActive) return;
            resetAllTooltips();

            const activeTabBtn = document.querySelector('#pills-tab .nav-link.active');
            if (!activeTabBtn) return;
            const currentTabId = activeTabBtn.id;

            const allTooltipGroups = helpOverlay.querySelectorAll('.help-tooltip-group');
            allTooltipGroups.forEach(group => {
                const targets = group.dataset.tabTarget.split(' '); 
                if (targets.includes(currentTabId)) {
                    group.style.display = 'block'; 
                    const tooltips = group.querySelectorAll('.help-tooltip');
                    tooltips.forEach(tooltip => {
                        const targetSelector = tooltip.dataset.targetSelector;
                        const targetElement = document.querySelector(targetSelector);
                        if (targetElement && targetElement.offsetParent !== null) {
                            const targetRect = targetElement.getBoundingClientRect();
                            const position = tooltip.dataset.position || 'top-center';
                            let top = targetRect.top;
                            let left = targetRect.left;

                            if (position.includes('top')) top -= (tooltip.offsetHeight + 15);
                            else if (position.includes('bottom')) top += (targetRect.height + 15);
                            else top += (targetRect.height / 2) - (tooltip.offsetHeight / 2);

                            if (position.includes('center')) left += (targetRect.width / 2) - (tooltip.offsetWidth / 2);
                            else if (position.includes('left')) left -= (tooltip.offsetWidth + 15);
                            else if (position.includes('right')) left += (targetRect.width + 15);

                            tooltip.style.top = `${top}px`;
                            tooltip.style.left = `${left}px`;
                            tooltip.classList.remove('position-top', 'position-bottom', 'position-right', 'position-left');
                            tooltip.classList.add('position-' + position.split('-')[0]);
                            tooltip.style.visibility = 'visible';
                            tooltip.style.opacity = '1';
                        }
                    });
                } else {
                    group.style.display = 'none'; 
                }
            });
        }

        helpToggleBtn.addEventListener('click', function(event) {
            event.preventDefault();
            isHelpActive = !isHelpActive;

            if (isHelpActive) {
                // 【改善内容】style.display操作を廃止しクラスの付け外しのみで制御
                // 【改善理由】表示制御のロジックをCSS側に一本化することで、
                //             JSはクラスを付け外しするだけでよくなり、
                //             setTimeoutによるタイミング制御も不要になる。
                helpOverlay.classList.add('is-active');
                updateTooltipsPosition();
            } else {
                helpOverlay.classList.remove('is-active');
            }
        });

helpOverlay.addEventListener('click', () => {
    isHelpActive = false;
    helpOverlay.classList.remove('is-active');
});

        helpOverlay.addEventListener('click', () => {
            isHelpActive = false;
            helpOverlay.classList.remove('is-active');
            setTimeout(() => helpOverlay.style.display = 'none', 300);
        });

        window.addEventListener('resize', () => { if (isHelpActive) window.requestAnimationFrame(updateTooltipsPosition); });
        window.addEventListener('scroll', () => { if (isHelpActive) window.requestAnimationFrame(updateTooltipsPosition); }, { passive: true });
        
        document.querySelectorAll('button[data-bs-toggle="pill"]').forEach(tab => {
            tab.addEventListener('shown.bs.tab', () => { if (isHelpActive) updateTooltipsPosition(); });
        });
    }


    /* ---------------------------------------------------------
        5. 共通通信・ユーティリティ (API/Helpers)
       --------------------------------------------------------- */
    function fetchData(answers) {
        fetch(ALBATROSS_CONFIG.saveLogUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken') },
            body: JSON.stringify({ chart_type_id: ALBATROSS_CONFIG.chartTypeId, answers: answers })
        })
        .then(response => {
            if (response.ok) window.location.href = ALBATROSS_CONFIG.chartListUrl;
            else return response.json().then(data => {
                messageModalText.textContent = '記録に失敗しました：' + (data.message || 'サーバーエラー');
                messageModal.show();
            });
        })
        .catch(error => { console.error('Error:', error); });
    }

    function fetchDataForAdvanced(answers, isResolved, resolvedStepId) {
        const payload = {
            chart_type_id: ALBATROSS_CONFIG.chartTypeId,
            answers: answers,
            is_resolved: isResolved,
            resolved_step_id: resolvedStepId
        };
        fetch(ALBATROSS_CONFIG.saveLogUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken') },
            body: JSON.stringify(payload)
        })
        .then(response => {
            if (response.ok) window.location.href = ALBATROSS_CONFIG.chartListUrl;
            else return response.json().then(data => {
                messageModalText.textContent = '記録に失敗しました：' + (data.message || 'サーバーエラー');
                messageModal.show();
            });
        })
        .catch(error => { console.error('Error:', error); });
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

}); // DOMContentLoaded End