const API_BASE = "http://127.0.0.1:8000";

let courseChart = null;
let dietChart = null;

const $ = (id) => document.getElementById(id);

async function api(path) {
  const response = await fetch(`${API_BASE}${path}`);
  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || "Could not load data.");
  }
  return data;
}

function showError(message) {
  $("errorBox").textContent = message;
  $("errorBox").hidden = false;
}

function hideError() {
  $("errorBox").hidden = true;
}

function safeText(value) {
  return value === null || value === undefined || value === ""
    ? "—"
    : String(value);
}

function addOptions(id, values) {
  const select = $(id);
  const firstOption = select.options[0].outerHTML;
  select.innerHTML = firstOption;

  values.filter((value) => value && value !== "Unknown")
    .forEach((value) => {
      const option = document.createElement("option");
      option.value = value;
      option.textContent = value;
      select.appendChild(option);
    });
}

function drawChart(canvasId, existing, labels, values, type) {
  if (existing) existing.destroy();

  return new Chart($(canvasId), {
    type,
    data: {
      labels,
      datasets: [{
        data: values,
        backgroundColor: [
          "#ff9f43", "#54d6a0", "#6ca6ff", "#b79bff",
          "#ff758f", "#48c9b0", "#f4d35e", "#7bdff2",
          "#e5989b", "#a3c4f3"
        ],
        borderColor: "#151f30",
        borderWidth: 2,
        borderRadius: type === "bar" ? 5 : 0
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: type === "doughnut",
          position: "bottom",
          labels: { color: "#cbd5e1", padding: 15 }
        }
      },
      scales: type === "bar" ? {
        x: { ticks: { color: "#94a3b8" }, grid: { display: false } },
        y: {
          beginAtZero: true,
          ticks: { color: "#94a3b8", precision: 0 },
          grid: { color: "#273449" }
        }
      } : {}
    }
  });
}

function renderFoodTable(foods) {
  const body = $("foodTable");
  body.replaceChildren();

  $("resultCount").textContent = `${foods.length} results`;

  if (!foods.length) {
    const row = body.insertRow();
    const cell = row.insertCell();
    cell.colSpan = 6;
    cell.textContent = "No food items match your filters.";
    return;
  }

  foods.forEach((food) => {
    const row = body.insertRow();

    [
      food.name,
      food.diet,
      food.course,
      food.region,
      food.prep_time,
      food.cook_time
    ].forEach((value) => {
      const cell = row.insertCell();
      cell.textContent = safeText(value);
    });
  });
}

async function loadOptions() {
  const options = await api("/api/options");
  addOptions("dietFilter", options.diet || []);
  addOptions("courseFilter", options.course || []);
  addOptions("regionFilter", options.region || []);
}

async function loadSummary() {
  const summary = await api("/api/summary");

  $("totalFoods").textContent = summary.total_foods.toLocaleString();
  $("totalCourses").textContent = summary.categories.toLocaleString();
  $("totalRegions").textContent = summary.regions.toLocaleString();
  $("totalVeg").textContent = summary.vegetarian.toLocaleString();

  courseChart = drawChart(
    "courseChart",
    courseChart,
    Object.keys(summary.course_distribution || {}),
    Object.values(summary.course_distribution || {}),
    "bar"
  );

  dietChart = drawChart(
    "dietChart",
    dietChart,
    Object.keys(summary.diet_distribution || {}),
    Object.values(summary.diet_distribution || {}),
    "doughnut"
  );
}

async function loadFoods() {
  const params = new URLSearchParams();

  const filters = {
    search: $("searchInput").value.trim(),
    diet: $("dietFilter").value,
    course: $("courseFilter").value,
    region: $("regionFilter").value
  };

  Object.entries(filters).forEach(([key, value]) => {
    if (value) params.set(key, value);
  });

  params.set("limit", "100");

  const result = await api(`/api/foods?${params.toString()}`);
  renderFoodTable(result.foods || []);
}

async function loadApp() {
  $("loading").hidden = false;
  hideError();

  try {
    await Promise.all([loadSummary(), loadOptions()]);
    await loadFoods();
  } catch (error) {
    showError(
      `${error.message} Check that the dataset exists in data/ and the API is running.`
    );
  } finally {
    $("loading").hidden = true;
  }
}

$("filterBtn").addEventListener("click", async () => {
  hideError();
  try {
    await loadFoods();
  } catch (error) {
    showError(error.message);
  }
});

$("searchInput").addEventListener("keydown", (event) => {
  if (event.key === "Enter") $("filterBtn").click();
});

$("refreshBtn").addEventListener("click", loadApp);

loadApp();
