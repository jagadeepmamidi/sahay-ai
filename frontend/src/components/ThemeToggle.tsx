"use client";

import { Moon, Sun } from "@phosphor-icons/react";
import { useEffect, useState } from "react";

export function ThemeToggle() {
  const [theme, setTheme] = useState<"light" | "dark">("light");

  useEffect(() => {
    const current =
      (document.documentElement.getAttribute("data-theme") as "light" | "dark") ||
      "light";
    setTheme(current);
  }, []);

  const toggle = () => {
    const next = theme === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", next);
    localStorage.setItem("sahay-theme", next);
    setTheme(next);
  };

  return (
    <button
      type="button"
      className="icon-btn"
      onClick={toggle}
      aria-label={theme === "dark" ? "Switch to light theme" : "Switch to dark theme"}
    >
      {theme === "dark" ? <Sun size={18} /> : <Moon size={18} />}
    </button>
  );
}
