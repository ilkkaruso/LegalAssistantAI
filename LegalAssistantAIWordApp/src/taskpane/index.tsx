import React from "react";
import { createRoot } from "react-dom/client";
import { App } from "./ui/App";

/* global Office */

Office.onReady(() => {
  const el = document.getElementById("root");
  if (!el) return;
  createRoot(el).render(<App />);
});
