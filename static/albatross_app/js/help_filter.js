document.addEventListener('DOMContentLoaded', function() {
// --- 🛡️ 逆止弁（バックストップ）：このページにチャートがあるか確認 ---
    const chartArea = document.getElementById('pills-tab');
    if (!chartArea) {
        // チャートのタブがないページ（ログイン画面とか）なら、
        // この下の難しい処理は全部スルーして終了するよ！
        return; 
    }

    console.log("チャート画面を検知！ロジックを起動します✨");

    // --- ページ読み込み時に、保存されたタブの状態を復元する処理 ---
const savedTabId = localStorage.getItem('activeChartTabId');
if (savedTabId) {
    console.log(`保存されたタブ (${savedTabId}) を復元します。`);
    
    // Bootstrapのタブを、JavaScriptから操作するための、おまじない！
    const tabToActivate = document.getElementById(savedTabId);
    if (tabToActivate) {
        const tab = new bootstrap.Tab(tabToActivate);
        tab.show(); // これで、指定したタブがアクティブになる！
    }
}

    // ==========================================================
    // 1. このページで共通して使う要素や変数を、最初にまとめて準備！
    // ==========================================================
    const beginnerIntermediatePane = document.getElementById('pills-chart-area');
    const advancedTabPane = document.getElementById('pills-advanced');
    
    // モーダル関連も、ここで一回だけ準備しておく！
    const confirmSaveModalElement = document.getElementById('confirmSaveModal');
    let confirmSaveModal = confirmSaveModalElement ? new bootstrap.Modal(confirmSaveModalElement) : null;
    const messageModalElement = document.getElementById('messageModal');
    let messageModal = messageModalElement ? new bootstrap.Modal(messageModalElement) : null;
    const messageModalLabel = document.getElementById('messageModalLabel');
    const messageModalText = document.getElementById('messageModalText');
    const confirmSaveButton = document.getElementById('confirmSaveButton');
    const okButton = document.getElementById('messageModalOkButton');


    // ==========================================================
    // 2. 初級/中級モード用の処理
    // ==========================================================
    if (beginnerIntermediatePane) {
        console.log("初級/中級モード用のJavaScriptを初期化します。");

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
    console.log("初級保存ボタンの存在チェック:", saveLogButton ? "OK" : "見つからないよ！");
        if (saveLogButton && confirmSaveModal) {
            // 念のため、古いイベントを一度リセットする書き方にしよっか！
            saveLogButton.onclick = function() {
                console.log("初級・中級の保存ボタンが押されました！モーダルを出します✨");
                
                // 1. モーダルを表示
                confirmSaveModal.show();
                
                // 2. モーダル内の「はい、記録する」ボタンに、この時だけの仕事を教える
                confirmSaveButton.onclick = function() {
                    console.log("モーダルで『はい』が押されました。送信を開始します🚀");
                    confirmSaveModal.hide();
                    fetchData(userAnswers); // 初級・中級用の送信関数
                };
            };
        }
        
        switchChartText('beginner');
        updateFinalStepStyles();
    }

    // --- タブの状態をlocalStorageに保存するための処理 ---
const allTabs = document.querySelectorAll('#pills-tab .nav-link'); // 全てのタブボタンを取得

allTabs.forEach(function(tab) {
    tab.addEventListener('click', function(event) {
        // クリックされたタブのID（pills-beginner-tab とか）を取得
        const activeTabId = event.target.id; 
        
        // localStorageに保存！
        localStorage.setItem('activeChartTabId', activeTabId);
        console.log(`タブの状態を保存しました: ${activeTabId}`);
    });
});

// ▲▲▲ ここまで追加！ ▲▲▲

// --- 🛡️ 上級モード：状態管理 ---
    let checkedSteps = {}; // { stepId: true/false } を管理
    const allNormalTiles = document.querySelectorAll('.tile[data-step-id]');

    // タイルをクリックした時の動き
    allNormalTiles.forEach(tile => {
        const stepId = tile.dataset.stepId;
        checkedSteps[stepId] = false; // 初期化

        tile.addEventListener('click', function() {
            checkedSteps[stepId] = !checkedSteps[stepId]; // チェック状態を反転
            
            // 見た目の切り替え（グレーアウトと時間表示）
            if (checkedSteps[stepId]) {
                this.classList.add('tile-checked'); // CSSでグレーにする
                const now = new Date();
                const timeStr = now.getHours().toString().padStart(2, '0') + ":" + now.getMinutes().toString().padStart(2, '0');
                this.querySelector('.tile-timestamp').textContent = timeStr;
            } else {
                this.classList.remove('tile-checked');
                this.querySelector('.tile-timestamp').textContent = '';
            }
        });
    });

    // --- 🛡️ 上級モード：保存実行のトリガー ---
    const saveResolvedBtn = document.getElementById('save-resolved-log-btn');
    const saveUnresolvedBtn = document.getElementById('save-unresolved-log-btn');

    if (saveResolvedBtn) {
        saveResolvedBtn.addEventListener('click', () => triggerSaveProcess(false));
    }
    if (saveUnresolvedBtn) {
        saveUnresolvedBtn.addEventListener('click', () => triggerSaveProcess(true));
    }

    // 🚀 【マサ君の最強ロジック】データを整えて送信する関数（モーダル連動版！）
    function triggerSaveProcess(isUnresolved) {
        const answersForBackend = {};
        const checkedTileIds = Object.keys(checkedSteps).filter(id => checkedSteps[id]);

        // 1. 何もしてないならモーダルを出さずに警告
        if (checkedTileIds.length === 0 && !isUnresolved) {
            messageModalText.textContent = "操作タイルを少なくとも1つ選択してください！";
            messageModal.show();
            return;
        }

        // 2. 全てのタイルの基本回答をセット
        allNormalTiles.forEach(tile => {
            const stepId = tile.dataset.stepId;
            answersForBackend[stepId] = checkedSteps[stepId] ? 'no' : 'unknown';
        });

        let resolvedStepId = null;

        // 3. 「解決」ボタンなら、一番最後の display_order を「yes」にする
        if (!isUnresolved && checkedTileIds.length > 0) {
            const lastId = checkedTileIds.reduce((a, b) => {
                const orderA = parseInt(document.querySelector(`.tile[data-step-id="${a}"]`).dataset.displayOrder);
                const orderB = parseInt(document.querySelector(`.tile[data-step-id="${b}"]`).dataset.displayOrder);
                return orderB > orderA ? b : a;
            });
            answersForBackend[lastId] = 'yes';
            resolvedStepId = lastId;
        }

        // 4. ★ここが重要！★ ブラウザのconfirmじゃなく、Bootstrapモーダルを表示！
        confirmSaveModal.show();

        // 5. モーダル内の「はい、記録する」ボタンが押された時の動きをセット
        confirmSaveButton.onclick = function() {
            confirmSaveModal.hide(); // モーダルを閉じて
            fetchDataForAdvanced(answersForBackend, !isUnresolved, resolvedStepId); // 送信！
        };
    }
    
    // ----------------------------------------------------------
    // C. 共通ヘルパー関数 (fetch処理を共通化！)
    // ----------------------------------------------------------
    function fetchData(answers) {
        fetch(ALBATROSS_CONFIG.saveLogUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken') },
            body: JSON.stringify({ chart_type_id: ALBATROSS_CONFIG.chartTypeId, answers: answers })
        })
        .then(response => {
            // ▼▼▼ ここを修正！ ▼▼▼
            if (response.ok) {
                // 成功したら、もう何もせずに、すぐにリダイレクト！
                console.log("ログの保存に成功しました。チャート選択画面に戻ります。");
                window.location.href = ALBATROSS_CONFIG.chartListUrl;
            } else {
                // 失敗した時だけ、エラーモーダルを出すようにする
                return response.json().then(data => {
                    messageModalLabel.textContent = 'エラー';
                    messageModalText.textContent = '記録に失敗しました：' + (data.message || 'サーバーエラー');
                    messageModal.show();
                });
            }
        })
        .catch(error => {
            console.error('Error:', error);
            messageModalLabel.textContent = '通信エラー';
            messageModalText.textContent = 'サーバーとの通信中にエラーが発生しました。';
            messageModal.show();
        });
    }

// ★★★ 上級モード専用のデータ送信関数（最終形態） ★★★
    function fetchDataForAdvanced(answers) { // 引数で受け取るのは、もう完成済みのanswersオブジェクトだけ！
        // 送信するデータを最終チェック
        const payload = {
            chart_type_id: ALBATROSS_CONFIG.chartTypeId,
            answers: answers // フロント側で完成させた回答リストを、そのまま入れる！
        };
        
        console.log("バックエンドに送信するデータ:", payload); // 送る直前のデータを確認！

        fetch(ALBATROSS_CONFIG.saveLogUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken') },
            body: JSON.stringify(payload)
        })
        .then(response => {
            if (response.ok) {
                console.log("ログの保存に成功しました。チャート選択画面に戻ります。");
                window.location.href = ALBATROSS_CONFIG.chartListUrl;
            } else {
                return response.json().then(errorData => {
                    messageModalLabel.textContent = 'エラー';
                    messageModalText.textContent = '記録に失敗しました：' + (errorData.message || 'サーバーエラー');
                    messageModal.show();
                });
            }
        })
        .catch(error => {
            console.error('Error:', error);
            messageModalLabel.textContent = '通信エラー';
            messageModalText.textContent = 'サーバーとの通信中にエラーが発生しました。';
            messageModal.show();
        });
    }
    // ▲▲▲ ここまで追加！ ▲▲▲


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

// --- 使い方フィルター：BP版ロジック（マサ君専用✨） ---
    const helpToggleBtn = document.getElementById('help-toggle-link');
    const helpOverlay = document.getElementById('help-overlay');

    if (helpToggleBtn && helpOverlay) {
        let isHelpActive = false;

        // 1. 全ての吹き出しを隠す「初期化（リセット）」関数
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

            // 今光ってるタブボタンを特定
            const activeTabBtn = document.querySelector('#pills-tab .nav-link.active');
            if (!activeTabBtn) return;
            const currentTabId = activeTabBtn.id;

            // デバッグ：今何のIDを読み取ってるか確認（これ大事！）
            console.log("今アクティブなタブID:", currentTabId);

            const allTooltipGroups = helpOverlay.querySelectorAll('.help-tooltip-group');
            
            allTooltipGroups.forEach(group => {
                // ★ここがポイント！：スペースで区切られた名前をバラバラにしてチェックする
                const targets = group.dataset.tabTarget.split(' '); 
                
                if (targets.includes(currentTabId)) {
                    // 一致するグループだけ表示！
                    group.style.display = 'block'; 
                    
                    const tooltips = group.querySelectorAll('.help-tooltip');
                    tooltips.forEach(tooltip => {
                        const targetSelector = tooltip.dataset.targetSelector;
                        const targetElement = document.querySelector(targetSelector);

                        if (targetElement && targetElement.offsetParent !== null) {
                            const targetRect = targetElement.getBoundingClientRect();
                            const position = tooltip.dataset.position || 'top-center';

                            // 座標計算ロジック（ここは今のままでOK！）
                            let top = targetRect.top;
                            let left = targetRect.left;

                            if (position.includes('top')) {
                                top -= (tooltip.offsetHeight + 15);
                            } else if (position.includes('bottom')) {
                                top += (targetRect.height + 15);
                            } else {
                                top += (targetRect.height / 2) - (tooltip.offsetHeight / 2);
                            }

                            if (position.includes('center')) {
                                left += (targetRect.width / 2) - (tooltip.offsetWidth / 2);
                            } else if (position.includes('left')) {
                                left -= (tooltip.offsetWidth + 15);
                            } else if (position.includes('right')) {
                                left += (targetRect.width + 15);
                            }

                            tooltip.style.top = `${top}px`;
                            tooltip.style.left = `${left}px`;

                            // ★ここを追加！ 吹き出しに「今の向き」を教えてあげる魔法の3行✨
                            tooltip.classList.remove('position-top', 'position-bottom', 'position-right', 'position-left'); // 一旦脱がせて
                            const finalPos = position.split('-')[0]; // 'top' とか 'right' を取り出す
                            tooltip.classList.add('position-' + finalPos); // 新しい衣装を着せる！

                            tooltip.style.visibility = 'visible';
                            tooltip.style.opacity = '1';
                        }
                    });
                } else {
                    // 当てはまらないグループは「絶対に」隠す！
                    group.style.display = 'none'; 
                }
            });
        }

        // --- 監視マジック（ここも重要！） ---

        // スクロール中も「ぬるぬる」追いかけるための命令
        window.addEventListener('scroll', () => {
            if (isHelpActive) {
                // requestAnimationFrameを使うと、ブラウザの描画に合わせてスムーズに更新されるよ✨
                window.requestAnimationFrame(updateTooltipsPosition);
            }
        }, { passive: true }); // パフォーマンス向上のためのおまじない

        window.addEventListener('resize', () => {
            if (isHelpActive) window.requestAnimationFrame(updateTooltipsPosition);
        });

        // 3. 使い方ボタンを押した時の動き
        helpToggleBtn.addEventListener('click', function(event) {
            event.preventDefault();
            isHelpActive = !isHelpActive;

            if (isHelpActive) {
                helpOverlay.style.display = 'block';
                setTimeout(() => {
                    helpOverlay.classList.add('is-active');
                    updateTooltipsPosition();
                }, 10);
            } else {
                helpOverlay.classList.remove('is-active');
                setTimeout(() => {
                    helpOverlay.style.display = 'none';
                    resetAllTooltips();
                }, 300);
            }
        });

        // 背景クリックで閉じる
        helpOverlay.addEventListener('click', () => {
            isHelpActive = false;
            helpOverlay.classList.remove('is-active');
            setTimeout(() => helpOverlay.style.display = 'none', 300);
        });

        // 4. 監視マジック（リサイズ・スクロール）
        window.addEventListener('resize', updateTooltipsPosition);
        window.addEventListener('scroll', updateTooltipsPosition);
        
        // ★重要：タブが切り替わったら再計算！
        document.querySelectorAll('button[data-bs-toggle="pill"]').forEach(tab => {
            tab.addEventListener('shown.bs.tab', () => {
                if (isHelpActive) updateTooltipsPosition();
            });
        });
    }

});