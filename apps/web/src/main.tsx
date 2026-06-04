import React from "react";
import ReactDOM from "react-dom/client";
import { AuthProvider } from "./app/AuthProvider";
import { SnackbarProvider } from "./app/SnackbarProvider";
import { App } from "./App";
import "./styles.css";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <AuthProvider>
      <SnackbarProvider>
        <App />
      </SnackbarProvider>
    </AuthProvider>
  </React.StrictMode>
);

// Register the service worker so the app is installable (PWA).
if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    navigator.serviceWorker.register("/sw.js").catch(() => {
      /* ignore — app works fine without it */
    });
  });
}
