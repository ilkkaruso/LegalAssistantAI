/* global Office */

Office.onReady(() => {
  // No-op
});

// Example event handler
// Expose functions to Office
// eslint-disable-next-line @typescript-eslint/no-explicit-any
;(globalThis as any).onDocumentOpen = onDocumentOpen

export async function onDocumentOpen(event: Office.AddinCommands.Event) {
  try {
    // Could refresh auth state, etc.
  } finally {
    event.completed();
  }
}
