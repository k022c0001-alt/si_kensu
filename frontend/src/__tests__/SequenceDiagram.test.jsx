/**
 * SequenceDiagram.test.jsx
 *
 * Tests for the SequenceDiagram component and related utilities:
 * - Mermaid 構文生成テスト
 * - フィルタパネルテスト
 * - コンポーネントレンダリングテスト
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';

// buildSequenceDiagram をテスト（ユーティリティ関数）
import { buildSequenceDiagram, buildMermaid } from '../utils/mermaidBuilder';

// ─────────────────────────────────────────────────────────────────────────────
// Test data
// ─────────────────────────────────────────────────────────────────────────────

const SAMPLE_CALLS = [
  {
    caller_file: 'app',
    caller_func: 'run',
    callee_object: 'api',
    callee_func: 'fetch_user',
    line: 5,
    layer: 'api',
    note: 'ユーザー取得',
  },
  {
    caller_file: 'api',
    caller_func: 'fetch_user',
    callee_object: 'db',
    callee_func: 'query',
    line: 12,
    layer: 'db',
    note: null,
  },
  {
    caller_file: 'api',
    caller_func: 'fetch_user',
    callee_object: 'db',
    callee_func: 'close',
    line: 15,
    layer: 'db',
    note: null,
  },
];

const SAMPLE_SEQUENCE_DATA = {
  participants: ['app', 'api', 'db'],
  source_files: ['app.py', 'api.py', 'db.py'],
  calls: SAMPLE_CALLS,
  notes: [],
};

// ─────────────────────────────────────────────────────────────────────────────
// Mermaid 構文生成テスト (buildSequenceDiagram)
// ─────────────────────────────────────────────────────────────────────────────

describe('buildSequenceDiagram – Mermaid 構文生成', () => {
  test('sequenceDiagram ヘッダーを含む', () => {
    const result = buildSequenceDiagram(SAMPLE_CALLS);
    expect(result).toContain('sequenceDiagram');
  });

  test('参加者が participant として含まれる', () => {
    const result = buildSequenceDiagram(SAMPLE_CALLS);
    expect(result).toContain('participant app');
    expect(result).toContain('participant api');
    expect(result).toContain('participant db');
  });

  test('関数呼び出し矢印が含まれる', () => {
    const result = buildSequenceDiagram(SAMPLE_CALLS);
    expect(result).toContain('fetch_user()');
    expect(result).toContain('query()');
  });

  test('note が含まれる', () => {
    const result = buildSequenceDiagram(SAMPLE_CALLS);
    expect(result).toContain('ユーザー取得');
  });

  test('空の calls で sequenceDiagram のみ返る', () => {
    const result = buildSequenceDiagram([]);
    expect(result).toContain('sequenceDiagram');
    expect(result).not.toContain('participant');
  });

  test('特殊文字を含む名前がサニタイズされる', () => {
    const calls = [
      {
        caller_file: 'my-app.py',
        caller_func: 'run',
        callee_object: 'my_api',
        callee_func: 'fetch',
        layer: 'api',
        note: null,
      },
    ];
    const result = buildSequenceDiagram(calls);
    // ハイフンが _ に変換される
    expect(result).toContain('participant my_app_py');
  });

  test('caller と callee が同じ場合でも重複しない', () => {
    const calls = [
      {
        caller_file: 'app',
        caller_func: 'init',
        callee_object: 'app',
        callee_func: 'setup',
        layer: 'ui',
        note: null,
      },
    ];
    const result = buildSequenceDiagram(calls);
    // app は1回だけ participant として登録される
    const matches = result.match(/participant app/g);
    expect(matches).toHaveLength(1);
  });
});

// ─────────────────────────────────────────────────────────────────────────────
// buildMermaid (後方互換 API) テスト
// ─────────────────────────────────────────────────────────────────────────────

describe('buildMermaid – 後方互換 API', () => {
  test('sequenceDiagram ヘッダーを含む', () => {
    const result = buildMermaid(SAMPLE_SEQUENCE_DATA);
    expect(result).toContain('sequenceDiagram');
  });

  test('participants が含まれる', () => {
    const result = buildMermaid(SAMPLE_SEQUENCE_DATA);
    expect(result).toContain('participant app');
    expect(result).toContain('participant api');
    expect(result).toContain('participant db');
  });

  test('note が含まれる', () => {
    const result = buildMermaid(SAMPLE_SEQUENCE_DATA);
    expect(result).toContain('ユーザー取得');
  });

  test('フィルタ済みの calls が優先される', () => {
    const filteredCalls = [SAMPLE_CALLS[0]]; // 最初の1件のみ
    const result = buildMermaid(SAMPLE_SEQUENCE_DATA, filteredCalls);
    expect(result).toContain('fetch_user()');
    expect(result).not.toContain('query()');
  });

  test('空のデータで sequenceDiagram を返す', () => {
    const result = buildMermaid({ participants: [], calls: [] });
    expect(result).toContain('sequenceDiagram');
  });
});

// ─────────────────────────────────────────────────────────────────────────────
// SequenceDiagram コンポーネントテスト
// ─────────────────────────────────────────────────────────────────────────────

describe('SequenceDiagram コンポーネント', () => {
  // useMermaid と mermaid は mock で動作するためコンポーネントをテスト可能
  let SequenceDiagram;

  beforeAll(async () => {
    // dynamic import to allow mocks to be set up first
    const mod = await import('../components/sequence/SequenceDiagram');
    SequenceDiagram = mod.default;
  });

  const SAMPLE_DIAGRAM_DATA = {
    project_root: '/path/to/project',
    calls: SAMPLE_CALLS,
    stats: { total_files: 3, total_calls: 3, filtered_calls: 3 },
    config: { mode: 'detail', exclude_private: false, exclude_builtins: true },
  };

  test('タイトルが表示される', () => {
    render(
      <SequenceDiagram diagramData={SAMPLE_DIAGRAM_DATA} title="テストシーケンス図" />
    );
    expect(screen.getByText('テストシーケンス図')).toBeInTheDocument();
  });

  test('stats が表示される', () => {
    render(<SequenceDiagram diagramData={SAMPLE_DIAGRAM_DATA} title="Test" />);
    expect(screen.getByText(/Calls: 3/)).toBeInTheDocument();
  });

  test('フィルタパネルの Mode セレクトが存在する', () => {
    render(<SequenceDiagram diagramData={SAMPLE_DIAGRAM_DATA} title="Test" />);
    const selects = document.querySelectorAll('select');
    expect(selects.length).toBeGreaterThan(0);
  });

  test('Mode を Summary に変更できる', () => {
    render(<SequenceDiagram diagramData={SAMPLE_DIAGRAM_DATA} title="Test" />);
    const modeSelect = document.querySelector('select');
    if (modeSelect) {
      fireEvent.change(modeSelect, { target: { value: 'summary' } });
      expect(modeSelect.value).toBe('summary');
    }
  });

  test('diagramData が null でも空メッセージが表示される', () => {
    render(<SequenceDiagram diagramData={null} title="Empty" />);
    expect(screen.getByText(/データを読み込んでください/)).toBeInTheDocument();
  });

  test('フッターが表示される', () => {
    render(<SequenceDiagram diagramData={SAMPLE_DIAGRAM_DATA} title="Test" />);
    expect(screen.getByText(/si_kensu/)).toBeInTheDocument();
  });
});
