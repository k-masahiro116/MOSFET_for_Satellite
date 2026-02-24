const layout = document.getElementById("layout");
const sidebarMount = document.getElementById("sidebarMount");

const PIN_KEY = "sidebarPinned";
const COLLAPSE_KEY = "sidebarCollapsed";

function loadState(key, defaultValue) {
  const value = localStorage.getItem(key);
  if (value === null) {
    return defaultValue;
  }
  return value === "true";
}

function saveState(key, value) {
  localStorage.setItem(key, String(value));
}

function updateButtons(pinButton, collapseButton) {
  const isPinned = layout.classList.contains("sidebar-pinned");
  const isCollapsed = layout.classList.contains("sidebar-collapsed");

  pinButton.textContent = isPinned ? "固定を解除" : "固定する";
  collapseButton.textContent = isCollapsed ? "展開する" : "折りたたむ";
}

function applyInitialState() {
  if (loadState(PIN_KEY, true)) {
    layout.classList.add("sidebar-pinned");
  } else {
    layout.classList.remove("sidebar-pinned");
  }

  if (loadState(COLLAPSE_KEY, false)) {
    layout.classList.add("sidebar-collapsed");
  } else {
    layout.classList.remove("sidebar-collapsed");
  }

}

function highlightCurrentPage() {
  const page = document.body.dataset.page;
  if (!page) {
    return;
  }

  const link = sidebarMount.querySelector(`.nav-link[data-page="${page}"]`);
  if (link) {
    link.classList.add("active");
  }
}

function initSidebarControls() {
  const pinButton = document.getElementById("togglePin");
  const collapseButton = document.getElementById("toggleCollapse");
  if (!pinButton || !collapseButton) {
    return;
  }

  updateButtons(pinButton, collapseButton);

  pinButton.addEventListener("click", () => {
    layout.classList.toggle("sidebar-pinned");
    saveState(PIN_KEY, layout.classList.contains("sidebar-pinned"));
    updateButtons(pinButton, collapseButton);
  });

  collapseButton.addEventListener("click", () => {
    layout.classList.toggle("sidebar-collapsed");
    saveState(COLLAPSE_KEY, layout.classList.contains("sidebar-collapsed"));
    updateButtons(pinButton, collapseButton);
  });
}

async function loadSidebar() {
  if (!sidebarMount) {
    return;
  }

  try {
    const response = await fetch("./sidebar.html");
    if (!response.ok) {
      return;
    }

    sidebarMount.innerHTML = await response.text();
    highlightCurrentPage();
    initSidebarControls();
  } catch (error) {
    console.error("Failed to load sidebar:", error);
  }
}

applyInitialState();
loadSidebar();
