import React, { useEffect, useState } from "react";
import { clearToken, getToken, saveToken } from "./auth";
import { login, me } from "./api";

export function AuthPanel() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [status, setStatus] = useState<string>("");
  const [userEmail, setUserEmail] = useState<string | null>(null);

  const refreshMe = async () => {
    const token = getToken();
    if (!token) {
      setUserEmail(null);
      return;
    }
    try {
      const user = await me();
      setUserEmail(user.email);
      setStatus("✅ Logged in");
    } catch (e: any) {
      setUserEmail(null);
      setStatus(`⚠️ Session invalid: ${e.message}`);
    }
  };

  useEffect(() => {
    refreshMe();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const onLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setStatus("Logging in...");
    try {
      const res = await login(email, password);
      await saveToken(res.access_token);
      await refreshMe();
    } catch (e: any) {
      setStatus(`❌ Login failed: ${e.message}`);
    }
  };

  const onLogout = async () => {
    await clearToken();
    setUserEmail(null);
    setStatus("Logged out");
  };

  return (
    <div style={{ border: "1px solid #ddd", borderRadius: 8, padding: 12 }}>
      <h3 style={{ marginTop: 0 }}>Account</h3>

      {userEmail ? (
        <div>
          <div style={{ marginBottom: 8 }}>
            Signed in as: <b>{userEmail}</b>
          </div>
          <button onClick={onLogout}>Log out</button>
        </div>
      ) : (
        <form onSubmit={onLogin} style={{ display: "grid", gap: 8 }}>
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            style={{ padding: 8 }}
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            style={{ padding: 8 }}
          />
          <button type="submit">Log in</button>
        </form>
      )}

      {status && <div style={{ marginTop: 8, color: "#444" }}>{status}</div>}
      <div style={{ marginTop: 8 }}>
        <button onClick={refreshMe}>Check session</button>
      </div>
    </div>
  );
}
