
    let mealCount = 0;
    let confirmedMeals = {};

    function startLogin() {
  // 隱藏標題、副標與按鈕
      document.getElementById("mainTitle").style.display = "none";
      document.getElementById("mainSubtitle").style.display = "none";
      document.getElementById("loginStartBtn").style.display = "none";

  // 切換到登入選擇區塊
      showSection("login");
    }



    function showSection(id) {
      document.querySelectorAll(".section").forEach(el => el.classList.remove("active"));
      document.getElementById(id).classList.add("active");
    }

    function login() {
  const email = document.getElementById("loginAccount").value;
  const pw = document.getElementById("loginPassword").value;
  if (email && pw.length >= 6) {
    alert("登入成功，歡迎回來！");
    showSection("loginSuccess");
  } else {
    document.getElementById("loginError").textContent = "請輸入有效帳號與密碼";
  }
}


    function register() {
      const email = document.getElementById("registerAccount").value;
      const pw = document.getElementById("registerPassword").value;
      if (email && pw.length >= 6) {
        showSection("registerSuccess");
      } else {
        document.getElementById("registerError").textContent = "請輸入有效帳號與 6 碼以上密碼";
      }
    }

    function chooseMode(mode) {
      document.getElementById("mainSection").classList.add("hidden");
      if (mode === 'all') {
        document.getElementById("allDayInputSection").classList.remove("hidden");
      } else {
        document.getElementById("oneMealInputSection").classList.remove("hidden");
      }
    }

    function evaluateOneMeal() {
      const sample = { price: 120, cal: 600, protein: 30 };
      document.getElementById("oneMealInputSection").classList.add("hidden");
      document.getElementById("resultSection").classList.remove("hidden");
      document.getElementById("resultText").innerHTML = `價錢：$${sample.price}<br>熱量：${sample.cal} kcal<br>蛋白質：${sample.protein} g`;
    }

    function retryMeal() {
      const samples = [
        { price: 110, cal: 580, protein: 29 },
        { price: 140, cal: 640, protein: 33 }
      ];
      const pick = samples[Math.floor(Math.random() * samples.length)];
      document.getElementById("resultText").innerHTML = `價錢：$${pick.price}<br>熱量：${pick.cal} kcal<br>蛋白質：${pick.protein} g`;
    }

    function acceptMeal() {
      alert("推薦完成，祝你用餐愉快！");
      location.reload();
    }

    function evaluateCondition() {
      document.getElementById("allDayInputSection").classList.add("hidden");
      document.getElementById("mealCountSelection").classList.remove("hidden");
    }

    function selectMealCount(count) {
      mealCount = count;
      confirmedMeals = {};
      document.getElementById("mealCountSelection").classList.add("hidden");
      const container = document.getElementById("allDayResultSection");
      container.innerHTML = `<h2 class="text-2xl font-semibold text-center">推薦${count}餐組合</h2>`;
      for (let i = 0; i < count; i++) {
        const mealId = String.fromCharCode(65 + i);
        confirmedMeals[mealId] = false;
        const mealBlock = document.createElement("div");
        mealBlock.className = "space-y-4 bg-[#f9f9f9] p-6 rounded-2xl shadow";
        mealBlock.innerHTML = `
          <div id="meal${mealId}" class="mealContent"></div>
          <div class="flex gap-2">
            <button class="flex-1 border border-gray-500 py-2 rounded-full hover:bg-gray-100 transition" onclick="reselectMeal('${mealId}')">重選 ${mealId}</button>
            <button class="flex-1 bg-yellow-500 text-white py-2 rounded-full hover:bg-yellow-600 transition" onclick="confirmMeal('${mealId}')">確定 ${mealId}</button>
          </div>`;
        container.appendChild(mealBlock);
        loadMeal(mealId);
      }
      const buttonBlock = document.createElement("div");
      buttonBlock.className = "flex gap-4 pt-4";
      buttonBlock.innerHTML = `
        <button class="flex-1 border border-red-500 text-red-600 py-3 rounded-full hover:bg-red-50 transition" onclick="restartAllMeals()">全部重選</button>
        <button id="finalConfirmBtn" class="flex-1 bg-green-600 text-white py-3 rounded-full hover:bg-green-700 transition" onclick="finalConfirm()" disabled>完成推薦</button>`;
      container.appendChild(buttonBlock);
      container.classList.remove("hidden");
    }

    function restartAllMeals() {
      document.getElementById("allDayResultSection").classList.add("hidden");
      document.getElementById("mealCountSelection").classList.remove("hidden");
    }

    function loadMeal(mealId) {
      const samples = [
        { price: 120, cal: 600, protein: 30 },
        { price: 130, cal: 650, protein: 32 },
        { price: 110, cal: 550, protein: 28 }
      ];
      const pick = samples[Math.floor(Math.random() * samples.length)];
      document.getElementById("meal" + mealId).innerHTML =
        `<strong>${mealId} 餐</strong><br>
         價錢：$${pick.price}<br>
         熱量：${pick.cal} kcal<br>
         蛋白質：${pick.protein} g`;
      confirmedMeals[mealId] = false;
      updateFinalConfirm();
    }

    function reselectMeal(mealId) {
      loadMeal(mealId);
    }

    function confirmMeal(mealId) {
      confirmedMeals[mealId] = true;
      alert(`${mealId} 餐已確認！`);
      updateFinalConfirm();
    }

    function updateFinalConfirm() {
      const allConfirmed = Object.values(confirmedMeals).every(val => val);
      const confirmBtn = document.getElementById("finalConfirmBtn");
      if (confirmBtn) confirmBtn.disabled = !allConfirmed;
    }

    function finalConfirm() {
      alert("整天推薦已完成！");
      location.reload();
    }