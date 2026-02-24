const layout = document.getElementById("layout");
const contentFrame = document.getElementById("contentFrame");
const navLinks = document.querySelectorAll(".nav-link[data-src]");
const pinButton = document.getElementById("togglePin");
const collapseButton = document.getElementById("toggleCollapse");

const PIN_KEY = "sidebarPinned";
const COLLAPSE_KEY = "sidebarCollapsed";
const ACTIVE_PAGE_KEY = "sidebarActivePage";

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
  if (!pinButton || !collapseButton) {
    return;
  }

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

function setActiveLink(link) {
  if (!link) {
    return;
  }

  navLinks.forEach((item) => item.classList.remove("active"));
  link.classList.add("active");
  saveState(ACTIVE_PAGE_KEY, link.dataset.src);
}

function initContentSwitching() {
  if (!contentFrame || navLinks.length === 0) {
    return;
  }

  const savedSrc = localStorage.getItem(ACTIVE_PAGE_KEY);
  let initialLink = navLinks[0];

  if (savedSrc) {
    const matched = Array.from(navLinks).find((link) => link.dataset.src === savedSrc);
    if (matched) {
      initialLink = matched;
    }
  }

  setActiveLink(initialLink);
  contentFrame.src = initialLink.dataset.src;

  navLinks.forEach((link) => {
    link.addEventListener("click", (event) => {
      event.preventDefault();
      setActiveLink(link);
      contentFrame.src = link.dataset.src;
    });
  });
}

function initSidebarControls() {
  if (!pinButton || !collapseButton) {
    return;
  }

  updateButtons();

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
}

if (layout) {
  applyInitialState();
  initSidebarControls();
  initContentSwitching();
}
