import React, { useState } from "react";
import { draftClause, improveWriting, proofreadSelection } from "./api";

/* global Word */

export function WordPanel() {
  const [selection, setSelection] = useState<string>("");
  const [insertText, setInsertText] = useState<string>("Hello from Legal Assistant AI");
  const [status, setStatus] = useState<string>("");
  const [improveInstructions, setImproveInstructions] = useState<string>("");

  const [clauseRequest, setClauseRequest] = useState<string>("");
  const [clauseStyle, setClauseStyle] = useState<string>("US English, formal, concise");
  const [useSelectionAsContext, setUseSelectionAsContext] = useState<boolean>(true);

  const getSelection = async () => {
    setStatus("Reading selection...");
    try {
      await Word.run(async (context) => {
        const range = context.document.getSelection();
        range.load("text");
        await context.sync();
        setSelection(range.text);
      });
      setStatus("✅ Selection loaded");
    } catch (e: any) {
      setStatus(`❌ Failed: ${e.message}`);
    }
  };

  const insertAfterSelection = async () => {
    setStatus("Inserting text...");
    try {
      await Word.run(async (context) => {
        const range = context.document.getSelection();
        range.insertText(`\n${insertText}\n`, Word.InsertLocation.after);
        await context.sync();
      });
      setStatus("✅ Inserted");
    } catch (e: any) {
      setStatus(`❌ Failed: ${e.message}`);
    }
  };

  const applyOperationToWord = async (op: any) => {
    await Word.run(async (context) => {
      // Best-effort enable track revisions
      try {
        // @ts-ignore
        context.document.trackRevisions = true;
      } catch {
        // ignore
      }

      const range = context.document.getSelection();

      if (op.type === "replace_selection") {
        range.insertText(op.new_text, Word.InsertLocation.replace);
      } else if (op.type === "insert_after_selection") {
        range.insertText(op.new_text, Word.InsertLocation.after);
      } else if (op.type === "insert_before_selection") {
        range.insertText(op.new_text, Word.InsertLocation.before);
      }

      if (op.type === "comment_on_quote") {
        const quote = (op.quote || "").trim();
        if (!quote) {
          await context.sync();
          return;
        }

        // Find quote within current selection
        const results = range.search(quote, { matchCase: false, matchWholeWord: false });
        results.load("items");
        await context.sync();

        if (results.items.length > 0) {
          const found = results.items[0];

          // Optional highlight
          if (op.highlight) {
            try {
              // @ts-ignore
              found.font.highlightColor = "yellow";
            } catch {
              // ignore
            }
          }

          if (op.comment?.body) {
            const commentText = op.comment.title ? `${op.comment.title}: ${op.comment.body}` : op.comment.body;
            // @ts-ignore
            found.insertComment(commentText);
          }
        }

        await context.sync();
        return;
      }

      if (op.comment?.body) {
        const commentText = op.comment.title ? `${op.comment.title}: ${op.comment.body}` : op.comment.body;
        // @ts-ignore
        range.insertComment(commentText);
      }

      await context.sync();
    });
  };

  const runImproveWriting = async () => {
    setStatus("Improving writing (calling API)...");
    try {
      // Read selection first
      let selectedText = "";
      await Word.run(async (context) => {
        const range = context.document.getSelection();
        range.load("text");
        await context.sync();
        selectedText = range.text || "";
      });

      if (!selectedText.trim()) {
        setStatus("⚠️ Please select some text first");
        return;
      }

      const resp = await improveWriting(selectedText, improveInstructions || undefined);
      const op = resp.operations?.[0];
      if (!op) {
        setStatus("❌ No operation returned");
        return;
      }

      await applyOperationToWord(op);

      setStatus("✅ Improve writing applied (tracked if enabled)");
    } catch (e: any) {
      setStatus(`❌ Improve writing failed: ${e.message}`);
    }
  };

  return (
    <div style={{ border: "1px solid #ddd", borderRadius: 8, padding: 12 }}>
      <h3 style={{ marginTop: 0 }}>Word Actions</h3>

      <div style={{ display: "flex", gap: 8, marginBottom: 8, flexWrap: "wrap" }}>
        <button onClick={getSelection}>Get selection</button>
        <button onClick={insertAfterSelection}>Insert after selection</button>
        <button onClick={runImproveWriting}>Improve writing (selection)</button>

        <button
          onClick={async () => {
            setStatus("Proofreading selection (calling API)...");
            try {
              let selectedText = "";
              await Word.run(async (context) => {
                const range = context.document.getSelection();
                range.load("text");
                await context.sync();
                selectedText = range.text || "";
              });

              if (!selectedText.trim()) {
                setStatus("⚠️ Please select some text first");
                return;
              }

              const resp = await proofreadSelection(selectedText);
              const ops = resp.operations || [];
              if (ops.length === 0) {
                setStatus("✅ No issues found");
                return;
              }

              for (const op of ops) {
                await applyOperationToWord(op);
              }

              setStatus(`✅ Added ${ops.length} comments`);
            } catch (e: any) {
              setStatus(`❌ Proofread failed: ${e.message}`);
            }
          }}
        >
          Proofread + highlight
        </button>

        <button
          onClick={async () => {
            setStatus("Drafting clause (calling API)...");
            try {
              let contextText: string | undefined = undefined;
              if (useSelectionAsContext) {
                await Word.run(async (context) => {
                  const range = context.document.getSelection();
                  range.load("text");
                  await context.sync();
                  contextText = (range.text || "").trim() || undefined;
                });
              }

              if (!clauseRequest.trim()) {
                setStatus("⚠️ Enter a clause request first");
                return;
              }

              const resp = await draftClause({
                clause_request: clauseRequest,
                context_text: contextText,
                style_instructions: clauseStyle || undefined,
              });

              const op = resp.operations?.[0];
              if (!op) {
                setStatus("❌ No operation returned");
                return;
              }

              await applyOperationToWord(op);
              setStatus("✅ Clause inserted (tracked if enabled)");
            } catch (e: any) {
              setStatus(`❌ Draft clause failed: ${e.message}`);
            }
          }}
        >
          Draft clause
        </button>
      </div>
      <div style={{ marginBottom: 12 }}>
        <div style={{ fontSize: 12, color: "#666", marginBottom: 4 }}>
          Insert text (for smoke test)
        </div>
        <textarea
          value={insertText}
          onChange={(e) => setInsertText(e.target.value)}
          rows={3}
          style={{ width: "100%", padding: 8 }}
        />
      </div>

      <div style={{ marginBottom: 12 }}>
        <div style={{ fontSize: 12, color: "#666", marginBottom: 4 }}>
          Improve writing instructions (optional)
        </div>
        <input
          value={improveInstructions}
          onChange={(e) => setImproveInstructions(e.target.value)}
          style={{ width: "100%", padding: 8 }}
          placeholder="e.g., make more formal, remove passive voice, tighten legal language"
        />
      </div>

      <div style={{ marginBottom: 12 }}>
        <div style={{ fontSize: 12, color: "#666", marginBottom: 4 }}>
          Draft clause request
        </div>
        <input
          value={clauseRequest}
          onChange={(e) => setClauseRequest(e.target.value)}
          style={{ width: "100%", padding: 8 }}
          placeholder="e.g., termination for convenience, limitation of liability, confidentiality"
        />
        <div style={{ display: 'flex', gap: 8, marginTop: 8, alignItems: 'center' }}>
          <label style={{ display: 'flex', gap: 6, alignItems: 'center', fontSize: 12, color: '#666' }}>
            <input
              type="checkbox"
              checked={useSelectionAsContext}
              onChange={(e) => setUseSelectionAsContext(e.target.checked)}
            />
            Use selection as context
          </label>
        </div>
      </div>

      <div style={{ marginBottom: 12 }}>
        <div style={{ fontSize: 12, color: "#666", marginBottom: 4 }}>
          Draft clause style (optional)
        </div>
        <input
          value={clauseStyle}
          onChange={(e) => setClauseStyle(e.target.value)}
          style={{ width: "100%", padding: 8 }}
          placeholder="e.g., UK English, formal, short"
        />
      </div>
      <div style={{ marginTop: 8, color: "#666" }}>
        <div>
          <b>Selection:</b>
        </div>
        <pre style={{ whiteSpace: "pre-wrap", background: "#f7f7f7", padding: 8 }}>
          {selection || "(nothing selected)"}
        </pre>
      </div>
      {status && <div style={{ marginTop: 8 }}>{status}</div>}
    </div>
  );
}
