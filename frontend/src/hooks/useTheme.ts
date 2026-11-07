import { useSyncExternalStore } from "react";

export type Theme = "light" | "dark";

const QUERY = "(prefers-color-scheme: dark)";
const listeners = new Set<() => void>();

function systemTheme(): Theme {
  return window.matchMedia(QUERY).matches ? "dark" : "light";
}

/** The explicit choice if there is one, otherwise the OS preference. */
function currentTheme(): Theme {
  const chosen = document.documentElement.dataset.theme;
  return chosen === "dark" || chosen === "light" ? chosen : systemTheme();
}

function subscribe(onChange: () => void) {
  listeners.add(onChange);
  const media = window.matchMedia(QUERY);
  media.addEventListener("change", onChange);
  return () => {
    listeners.delete(onChange);
    media.removeEventListener("change", onChange);
  };
}

export function toggleTheme() {
  const next: Theme = currentTheme() === "dark" ? "light" : "dark";
  document.documentElement.dataset.theme = next;
  try {
    localStorage.setItem("theme", next);
  } catch {
    // Storage can be blocked (private mode); the choice then lasts for this visit only.
  }
  listeners.forEach((listener) => listener());
}

/** Shared by every consumer, so toggling in one place updates all of them. */
export function useTheme() {
  const theme = useSyncExternalStore(subscribe, currentTheme, () => "light" as Theme);
  return { theme, toggle: toggleTheme };
}
