/**
 * screenDefinition.ts
 * Type definitions for the Screen Definition engine.
 */

export type ElementType =
  | "input"
  | "button"
  | "select"
  | "textarea"
  | "checkbox"
  | "radio"
  | "custom"
  | "unknown";

export interface UIElement {
  element_id: string;
  name: string;
  type: string;
  component_type: ElementType;
  required: boolean;
  max_length: number | null;
  placeholder: string;
  default_value: string;
  event_handlers: Record<string, string>;
  comment: string;
  line_number: number;
}

export interface FileResult {
  file: string;
  elements: UIElement[];
  error?: string;
}

export interface ParseDirectoryResult {
  root: string;
  files: FileResult[];
  total_elements: number;
}

/** A single row in the editable ScreenDefinitionTable. */
export interface TableRow {
  /** Unique row identifier (internal). */
  id: string;
  /** Source file path. */
  file: string;
  element_id: string;
  name: string;
  type: string;
  component_type: ElementType;
  required: boolean;
  max_length: string;
  placeholder: string;
  default_value: string;
  event_handlers: string; // serialised as comma-separated "event:handler"
  comment: string;
  line_number: number;
}
