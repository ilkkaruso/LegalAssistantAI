/* global Office */

const TOKEN_KEY = "legal_assistant_access_token";

export async function saveToken(token: string): Promise<void> {
  return new Promise((resolve, reject) => {
    try {
      Office.context.roamingSettings.set(TOKEN_KEY, token);
      Office.context.roamingSettings.saveAsync((res) => {
        if (res.status === Office.AsyncResultStatus.Succeeded) resolve();
        else reject(res.error);
      });
    } catch (e) {
      reject(e);
    }
  });
}

export function getToken(): string | null {
  try {
    return Office.context.roamingSettings.get(TOKEN_KEY) || null;
  } catch {
    return null;
  }
}

export async function clearToken(): Promise<void> {
  return new Promise((resolve, reject) => {
    try {
      Office.context.roamingSettings.remove(TOKEN_KEY);
      Office.context.roamingSettings.saveAsync((res) => {
        if (res.status === Office.AsyncResultStatus.Succeeded) resolve();
        else reject(res.error);
      });
    } catch (e) {
      reject(e);
    }
  });
}
