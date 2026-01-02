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
        if (saveLogButton && confirmSaveModal) {
            saveLogButton.addEventListener('click', function() {
                confirmSaveModal.show();
                const newConfirmBtn = confirmSaveButton.cloneNode(true);
                confirmSaveButton.parentNode.replaceChild(newConfirmBtn, confirmSaveButton);
                newConfirmBtn.addEventListener('click', () => {
                    confirmSaveModal.hide();
                    fetchData(userAnswers);
                }, { once: true });
            });
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
    // ----------------------------------------------------------
    // B. 上級モード用の処理
    // ----------------------------------------------------------
    if (advancedTabPane) {
        console.log("上級モード用のJavaScriptを初期化します。");

        // --- (1) 使う要素と、状態管理変数を準備 ---
        const allNormalTiles = advancedTabPane.querySelectorAll('.tile[data-step-id]');
        const unresolvedTriggerButton = document.getElementById('unresolved-trigger-button');
        const advancedSaveButton = document.getElementById('advanced-save-button');
        
        let checkedSteps = {}; // { stepId: true/false } を管理するオブジェクト
        let isUnresolvedMode = false;

        // ▼▼▼ 見た目を更新する関数 (リニューアル版) ▼▼▼
function updateAllTileStyles() {
    allNormalTiles.forEach(tile => {
        const stepId = tile.dataset.stepId;
        if (checkedSteps[stepId]) {
            tile.classList.add('tile-checked');
        } else {
            tile.classList.remove('tile-checked');
        }
    });
}

function checkUnresolvedButtonState() {
    // checkedSteps の中で、true のものの数を数える
    const checkedCount = Object.values(checkedSteps).filter(isChecked => isChecked).length;
    
    if (checkedCount === allNormalTiles.length) {
        unresolvedTriggerButton.disabled = false;
        unresolvedTriggerButton.classList.add('is-active'); 
    } else {
        unresolvedTriggerButton.disabled = true;
        unresolvedTriggerButton.classList.remove('is-active');
    }
}

        // ▼▼▼ クリックイベント (超シンプル版) ▼▼▼
allNormalTiles.forEach(tile => {
    const stepId = tile.dataset.stepId;
    const timestampElement = tile.querySelector('.tile-timestamp');

    // 初期状態をセット
    checkedSteps[stepId] = false;

    tile.addEventListener('click', function() {
        // true と false を、ただ入れ替えるだけ！
        checkedSteps[stepId] = !checkedSteps[stepId];
        
        // タイムスタンプを管理
        if (checkedSteps[stepId]) {
            const now = new Date();
            const hours = now.getHours().toString().padStart(2, '0');
            const minutes = now.getMinutes().toString().padStart(2, '0');
            timestampElement.textContent = `${hours}:${minutes}`;
        } else {
            timestampElement.textContent = '';
        }
        
        // 最後に、見た目を更新
        updateAllTileStyles();
        checkUnresolvedButtonState();
        
        console.log("クリック後 (チェック状態):", checkedSteps);
    });
});

        // --- (6) 未解決トリガーボタンの処理 ---
        if (unresolvedTriggerButton) {
            unresolvedTriggerButton.addEventListener('click', function() {
                isUnresolvedMode = !isUnresolvedMode;
                if (isUnresolvedMode) {
                    advancedSaveButton.innerHTML = `
                        <i class="bi bi-exclamation-circle-fill"></i> 
                        <span style="color: #fff; background-color: #dc3545; padding: 2px 6px; border-radius: 4px; font-weight: bold;">未解決</span>
                        として記録する`;
                        unresolvedTriggerButton.classList.remove('is-active'); // 「押せる」クラスは、もう用済みだから消す
                        unresolvedTriggerButton.classList.add('is-confirmed'); // 「押された後」クラスを追加！
                } else {
                    advancedSaveButton.innerHTML = `<i class="bi bi-pencil-square"></i> この内容で記録する`; // (元に戻すHTMLは省略)
                    unresolvedTriggerButton.classList.remove('is-confirmed'); // 「押された後」クラスを消して
                    unresolvedTriggerButton.classList.add('is-active'); // 「押せる」クラスに戻す！
                }
            });
        }

                // 【新しいコード（手術後）】

        if (advancedSaveButton && confirmSaveModal) {
            advancedSaveButton.addEventListener('click', function() {
                // --- ▼▼▼ ここからが、新しいロジック！ ▼▼▼ ---
                
                // 1. チェックされているタイルのIDを、配列として全部抜き出す
                const checkedTileIds = Object.keys(checkedSteps).filter(id => checkedSteps[id]);

                // 2. もし、チェックが一個もなくて、未解決モードでもないなら、処理を中断
                if (checkedTileIds.length === 0 && !isUnresolvedMode) {
                    if(messageModal) { // 丁寧なエラーメッセージを出す
                        messageModalLabel.textContent = '情報';
                        messageModalText.textContent = '記録するには、少なくとも1つの操作タイルを選択してください。';
                        messageModal.show();
                    }
                    return; // ここで、関数を強制終了！
                }

                // 3. チェック済みのタイルの中から、一番 display_order が大きいものを探す
                let lastStepId = null;
                if (checkedTileIds.length > 0) {
                    lastStepId = checkedTileIds.reduce((lastId, currentId) => {
                        const lastTile = document.querySelector(`.tile[data-step-id="${lastId}"]`);
                        const currentTile = document.querySelector(`.tile[data-step-id="${currentId}"]`);
                        // nullチェックを追加して、より安全に！
                        if (!lastTile) return currentId;
                        if (!currentTile) return lastId;
                        
                        const lastOrder = parseInt(lastTile.dataset.displayOrder);
                        const currentOrder = parseInt(currentTile.dataset.displayOrder);
                        return currentOrder > lastOrder ? currentId : lastId;
                    });
                }
                
                // 4. バックエンドに送るための、最終的なデータ(answersForBackend)を作る
                const answersForBackend = {};
                allNormalTiles.forEach(tile => {
                    const stepId = tile.dataset.stepId;
                    if (checkedSteps[stepId]) {
                        answersForBackend[stepId] = 'no'; // まずは、チェック済みを全部 'no' に
                    } else {
                        answersForBackend[stepId] = 'unknown'; // 未チェックは 'unknown'
                    }
                });

                // 5. もし「未解決モード」じゃなければ、一番最後のやつだけ 'yes' に上書き！
                if (lastStepId && !isUnresolvedMode) {
                    answersForBackend[lastStepId] = 'yes';
                }
                
                // --- ▲▲▲ 新しいロジック、ここまで！ ▲▲▲ ---

                // 6. 確認モーダルを表示して、完成したデータを送信する (ここは、ほぼ今まで通り)
                confirmSaveModal.show();
                const newConfirmBtn = confirmSaveButton.cloneNode(true);
                confirmSaveButton.parentNode.replaceChild(newConfirmBtn, confirmSaveButton);

                newConfirmBtn.addEventListener('click', () => {
                    confirmSaveModal.hide();
                    // ★★★ ちゃんと、新しい賢いデータ(answersForBackend)を渡す！ ★★★
                    fetchDataForAdvanced(answersForBackend);
                }, { once: true });
            });
        }
    }
    
    // ----------------------------------------------------------
    // C. 共通ヘルパー関数 (fetch処理を共通化！)
    // ----------------------------------------------------------
    function fetchData(answers) {
        fetch("{% url 'albatross_app:save_chart_log' %}", {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken') },
            body: JSON.stringify({ chart_type_id: "{{ chart_type.id }}", answers: answers })
        })
        .then(response => {
            // ▼▼▼ ここを修正！ ▼▼▼
            if (response.ok) {
                // 成功したら、もう何もせずに、すぐにリダイレクト！
                console.log("ログの保存に成功しました。チャート選択画面に戻ります。");
                window.location.href = "{% url 'albatross_app:chart_type_list' %}";
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
});