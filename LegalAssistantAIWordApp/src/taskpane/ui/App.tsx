import React, { useEffect, useState } from "react";
import { AuthPanel } from "./AuthPanel";
import { WordPanel } from "./WordPanel";

export function App() {
  const [ready, setReady] = useState(false);

  useEffect(() => {
    setReady(true);
  }, []);

  if (!ready) return <div style={{ padding: 12 }}>Loading…</div>;

  return (
    <div style={{ fontFamily: "Segoe UI, sans-serif", padding: 12 }}>
      <h2 style={{ marginTop: 0 }}>Legal Assistant AI</h2>
      <p style={{ marginTop: 4, color: "#666" }}>
        Word Desktop add-in (dev). Login to connect to your account.
      </p>
      <AuthPanel />
      <hr style={{ margin: "16px 0" }} />
      <WordPanel />
    </div>
  );
}
