/**
 * ScreenDefinitionTable.jsx
 *
 * Editable, Excel-like table for displaying UI element definitions.
 *
 * Props
 * -----
 * rows      : TableRow[]  – array of row data
 * onChange  : (rows: TableRow[]) => void  – called on any cell edit
 */

import React, { useState, useCallback, useRef } from "react";
import "../../styles/ScreenDefinitionTable.css";

// ── Column definitions ────────────────────────────────────────────────

const COLUMNS = [
  { key: "element_id",    label: "ID",           width: 100, editable: true,  inputType: "input" },
  { key: "name",          label: "名前",          width: 120, editable: true,  inputType: "input" },
  { key: "component_type",label: "種別",          width: 90,  editable: false, inputType: "badge" },
  { key: "type",          label: "Type属性",      width: 90,  editable: true,  inputType: "input" },
  { key: "required",      label: "必須",          width: 60,  editable: true,  inputType: "select",
    options: ["true", "false"] },
  { key: "max_length",    label: "最大文字数",    width: 90,  editable: true,  inputType: "input" },
  { key: "placeholder",   label: "プレースホルダ", width: 160, editable: true,  inputType: "input" },
  { key: "default_value", label: "デフォルト値",  width: 120, editable: true,  inputType: "input" },
  { key: "event_handlers",label: "イベント",      width: 140, editable: true,  inputType: "input" },
  { key: "comment",       label: "コメント",      width: 180, editable: true,  inputType: "textarea" },
  { key: "line_number",   label: "行番号",        width: 70,  editable: false, inputType: "input" },
];

// Badge colour mapping
const BADGE_CLASS = {
  input:    "sdt-badge-input",
  button:   "sdt-badge-button",
  select:   "sdt-badge-select",
  textarea: "sdt-badge-textarea",
  checkbox: "sdt-badge-checkbox",
  radio:    "sdt-badge-radio",
  custom:   "sdt-badge-custom",
  unknown:  "sdt-badge-unknown",
};

// ── Editable cell ─────────────────────────────────────────────────────

function EditableCell({ row, col, onCommit }) {
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState("");
  const inputRef = useRef(null);

  const displayValue = () => {
    const v = row[col.key];
    if (col.inputType === "badge") {
      return (
        <span className={`sdt-badge ${BADGE_CLASS[v] ?? "sdt-badge-unknown"}`}>
          {v}
        </span>
      );
    }
    if (col.key === "required") {
      return v ? <span className="sdt-required">✔</span> : "—";
    }
    return v ?? "";
  };

  const startEdit = () => {
    if (!col.editable) return;
    const v = row[col.key];
    setDraft(col.key === "required" ? String(v) : (v ?? ""));
    setEditing(true);
    // Focus after render
    setTimeout(() => inputRef.current?.focus(), 0);
  };

  const commit = () => {
    setEditing(false);
    const value =
      col.key === "required"
        ? draft === "true"
        : col.key === "max_length"
        ? draft === "" ? "" : draft
        : draft;
    onCommit(row.id, col.key, value);
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && col.inputType !== "textarea") commit();
    if (e.key === "Escape") setEditing(false);
    if (e.key === "Tab") commit();
  };

  if (editing) {
    const commonProps = {
      ref: inputRef,
      value: draft,
      onChange: (e) => setDraft(e.target.value),
      onBlur: commit,
      onKeyDown: handleKeyDown,
    };

    let editor;
    if (col.inputType === "textarea") {
      editor = <textarea {...commonProps} rows={3} />;
    } else if (col.inputType === "select") {
      editor = (
        <select {...commonProps}>
          {col.options.map((o) => (
            <option key={o} value={o}>{o}</option>
          ))}
        </select>
      );
    } else {
      editor = <input type="text" {...commonProps} />;
    }

    return <td className="sdt-cell-edit" style={{ minWidth: col.width }}>{editor}</td>;
  }

  return (
    <td
      className="sdt-cell-display"
      style={{ minWidth: col.width, maxWidth: col.width }}
      onClick={col.editable ? startEdit : undefined}
      title={col.editable ? "クリックして編集" : undefined}
    >
      {displayValue()}
    </td>
  );
}

// ── Main table ────────────────────────────────────────────────────────

export default function ScreenDefinitionTable({ rows = [], onChange }) {
  const [selected, setSelected] = useState(new Set());

  const toggleSelect = useCallback((id) => {
    setSelected((prev) => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  }, []);

  const toggleAll = useCallback(() => {
    setSelected((prev) =>
      prev.size === rows.length ? new Set() : new Set(rows.map((r) => r.id))
    );
  }, [rows]);

  const handleCommit = useCallback(
    (id, key, value) => {
      if (!onChange) return;
      const updated = rows.map((r) => (r.id === id ? { ...r, [key]: value } : r));
      onChange(updated);
    },
    [rows, onChange]
  );

  if (rows.length === 0) {
    return (
      <div className="sdt-wrapper">
        <p style={{ color: "#aaa", textAlign: "center", padding: "32px 0" }}>
          表示する要素がありません
        </p>
      </div>
    );
  }

  return (
    <div className="sdt-wrapper">
      <table className="sdt-table">
        <thead>
          <tr>
            <th className="sdt-col-check">
              <input
                type="checkbox"
                checked={selected.size === rows.length && rows.length > 0}
                onChange={toggleAll}
                aria-label="全選択"
              />
            </th>
            {COLUMNS.map((col) => (
              <th key={col.key} style={{ minWidth: col.width }}>
                {col.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr
              key={row.id}
              className={selected.has(row.id) ? "sdt-selected" : ""}
            >
              <td className="sdt-col-check">
                <input
                  type="checkbox"
                  checked={selected.has(row.id)}
                  onChange={() => toggleSelect(row.id)}
                  aria-label={`行 ${row.id} を選択`}
                />
              </td>
              {COLUMNS.map((col) => (
                <EditableCell
                  key={col.key}
                  row={row}
                  col={col}
                  onCommit={handleCommit}
                />
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
