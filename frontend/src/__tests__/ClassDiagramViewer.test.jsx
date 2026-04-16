/**
 * ClassDiagramViewer.test.jsx
 *
 * Tests for the ClassDiagramViewer component and related utilities:
 * - クラス図 Mermaid 構文生成テスト
 * - アクセス修飾子判定テスト
 * - ステレオタイプ判定テスト
 * - フィルタ機能テスト
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';

// buildClassDiagram と getAccessModifier をテスト
import { buildClassDiagram, getAccessModifier } from '../utils/mermaidBuilder';

// ─────────────────────────────────────────────────────────────────────────────
// Test data
// ─────────────────────────────────────────────────────────────────────────────

const SAMPLE_DIAGRAM_DATA = {
  classes: [
    {
      name: 'UserService',
      properties: [
        { name: 'userId', type: 'str', access: 'private' },
        { name: 'userName', type: 'str', access: 'public' },
      ],
      methods: [
        { name: 'getUser', params: ['id'], return: 'User', access: 'public' },
        { name: '_validate', params: [], return: 'bool', access: 'private' },
      ],
      bases: ['BaseService'],
    },
    {
      name: 'BaseService',
      properties: [],
      methods: [
        { name: 'connect', params: [], return: 'None', access: 'protected' },
      ],
      bases: [],
    },
  ],
  components: [
    {
      name: 'UserForm',
      props: [
        { name: 'userId', type: 'string' },
        { name: 'onSubmit', type: 'function' },
      ],
      hooks: ['useState', 'useEffect'],
      imports: ['./UserService', './styles.css'],
    },
  ],
  dependencies: {
    'user_service.py': ['base_service.py'],
    'UserForm.jsx': ['UserService'],
  },
};

// ─────────────────────────────────────────────────────────────────────────────
// getAccessModifier テスト
// ─────────────────────────────────────────────────────────────────────────────

describe('getAccessModifier – アクセス修飾子判定', () => {
  test('public は + を返す', () => {
    expect(getAccessModifier('public')).toBe('+');
  });

  test('private は - を返す', () => {
    expect(getAccessModifier('private')).toBe('-');
  });

  test('protected は # を返す', () => {
    expect(getAccessModifier('protected')).toBe('#');
  });

  test('不明な値は + を返す（デフォルト）', () => {
    expect(getAccessModifier('unknown')).toBe('+');
  });

  test('引数なしは + を返す', () => {
    expect(getAccessModifier()).toBe('+');
  });
});

// ─────────────────────────────────────────────────────────────────────────────
// buildClassDiagram テスト
// ─────────────────────────────────────────────────────────────────────────────

describe('buildClassDiagram – クラス図 Mermaid 構文生成', () => {
  test('classDiagram ヘッダーを含む', () => {
    const result = buildClassDiagram(SAMPLE_DIAGRAM_DATA);
    expect(result).toContain('classDiagram');
  });

  test('クラス名が含まれる', () => {
    const result = buildClassDiagram(SAMPLE_DIAGRAM_DATA);
    expect(result).toContain('class UserService');
    expect(result).toContain('class BaseService');
  });

  test('プロパティが含まれる', () => {
    const result = buildClassDiagram(SAMPLE_DIAGRAM_DATA);
    expect(result).toContain('userId');
    expect(result).toContain('userName');
  });

  test('メソッドが含まれる', () => {
    const result = buildClassDiagram(SAMPLE_DIAGRAM_DATA);
    expect(result).toContain('getUser');
    expect(result).toContain('_validate');
  });

  test('アクセス修飾子が正しく使われる', () => {
    const result = buildClassDiagram(SAMPLE_DIAGRAM_DATA);
    // public は +
    expect(result).toContain('+userName');
    // private は -
    expect(result).toContain('-userId');
  });

  test('継承関係が含まれる', () => {
    const result = buildClassDiagram(SAMPLE_DIAGRAM_DATA);
    expect(result).toContain('BaseService <|-- UserService');
  });

  test('React コンポーネントが <<component>> ステレオタイプで含まれる', () => {
    const result = buildClassDiagram(SAMPLE_DIAGRAM_DATA);
    expect(result).toContain('class UserForm');
    expect(result).toContain('<<component>>');
  });

  test('コンポーネントの props が含まれる', () => {
    const result = buildClassDiagram(SAMPLE_DIAGRAM_DATA);
    expect(result).toContain('userId');
    expect(result).toContain('onSubmit');
  });

  test('コンポーネントの hooks が含まれる', () => {
    const result = buildClassDiagram(SAMPLE_DIAGRAM_DATA);
    expect(result).toContain('useState');
    expect(result).toContain('useEffect');
  });

  test('ローカルインポートの依存関係矢印が含まれる', () => {
    const result = buildClassDiagram(SAMPLE_DIAGRAM_DATA);
    // ./UserService は大文字始まりなので依存関係矢印が追加される
    expect(result).toContain('UserForm ..> UserService');
  });

  test('空のデータで classDiagram のみ返る', () => {
    const result = buildClassDiagram({});
    expect(result).toContain('classDiagram');
    expect(result).not.toContain('class ');
  });

  test('クラスのみのデータで正しく生成される', () => {
    const data = {
      classes: [
        { name: 'Simple', properties: [], methods: [], bases: [] },
      ],
      components: [],
      dependencies: {},
    };
    const result = buildClassDiagram(data);
    expect(result).toContain('class Simple');
  });
});

// ─────────────────────────────────────────────────────────────────────────────
// ClassDiagramViewer コンポーネントテスト
// ─────────────────────────────────────────────────────────────────────────────

describe('ClassDiagramViewer コンポーネント', () => {
  let ClassDiagramViewer;

  beforeAll(async () => {
    const mod = await import('../components/diagram/ClassDiagramViewer');
    ClassDiagramViewer = mod.default;
  });

  test('タイトルが表示される', () => {
    render(<ClassDiagramViewer root="." mode="detail" />);
    expect(screen.getByText('Class Diagram')).toBeInTheDocument();
  });

  test('Mode セレクトが表示される', () => {
    render(<ClassDiagramViewer root="." mode="detail" />);
    const selects = document.querySelectorAll('select');
    expect(selects.length).toBeGreaterThan(0);
  });

  test('detail モードがデフォルトで選択される', () => {
    render(<ClassDiagramViewer root="." mode="detail" />);
    const select = document.querySelector('select');
    expect(select).not.toBeNull();
    if (select) {
      expect(select.value).toBe('detail');
    }
  });

  test('overview モードに変更できる', () => {
    render(<ClassDiagramViewer root="." mode="detail" />);
    const select = document.querySelector('select');
    if (select) {
      fireEvent.change(select, { target: { value: 'overview' } });
      expect(select.value).toBe('overview');
    }
  });

  test('フッターが表示される', () => {
    render(<ClassDiagramViewer root="." mode="detail" />);
    expect(screen.getByText(/si_kensu/)).toBeInTheDocument();
  });

  test('クラッシュしない', () => {
    expect(() =>
      render(<ClassDiagramViewer root="." mode="detail" />)
    ).not.toThrow();
  });
});
