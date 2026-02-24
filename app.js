const layout = document.getElementById("layout");
const pinButton = document.getElementById("togglePin");
const collapseButton = document.getElementById("toggleCollapse");

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

function updateButtons() {
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

  updateButtons();
}

pinButton.addEventListener("click", () => {
  layout.classList.toggle("sidebar-pinned");
  saveState(PIN_KEY, layout.classList.contains("sidebar-pinned"));
  updateButtons();
});

collapseButton.addEventListener("click", () => {
  layout.classList.toggle("sidebar-collapsed");
  saveState(COLLAPSE_KEY, layout.classList.contains("sidebar-collapsed"));
  updateButtons();
});

applyInitialState();
