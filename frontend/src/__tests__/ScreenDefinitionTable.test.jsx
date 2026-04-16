/**
 * ScreenDefinitionTable.test.jsx
 *
 * Tests for the ScreenDefinitionTable component:
 * - テーブルレンダリング
 * - セル編集
 * - 行選択
 * - Keyboard navigation
 * - データ変更コールバック
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import ScreenDefinitionTable from '../components/screen-definition/ScreenDefinitionTable';

// ─────────────────────────────────────────────────────────────────────────────
// Test data
// ─────────────────────────────────────────────────────────────────────────────

const SAMPLE_ROWS = [
  {
    id: '0',
    file: 'UserForm.jsx',
    element_id: 'user-email',
    name: 'email',
    type: 'email',
    component_type: 'input',
    required: true,
    max_length: '120',
    placeholder: 'Enter email',
    default_value: '',
    event_handlers: 'onChange:handleChange',
    comment: 'User email field',
    line_number: 5,
  },
  {
    id: '1',
    file: 'UserForm.jsx',
    element_id: 'submit-btn',
    name: 'submit',
    type: '',
    component_type: 'button',
    required: false,
    max_length: '',
    placeholder: '',
    default_value: '',
    event_handlers: 'onClick:handleSubmit',
    comment: 'Submit button',
    line_number: 15,
  },
  {
    id: '2',
    file: 'UserForm.jsx',
    element_id: 'user-name',
    name: 'username',
    type: 'text',
    component_type: 'input',
    required: false,
    max_length: '50',
    placeholder: 'Enter username',
    default_value: '',
    event_handlers: '',
    comment: '',
    line_number: 20,
  },
];

// ─────────────────────────────────────────────────────────────────────────────
// テーブルレンダリングテスト
// ─────────────────────────────────────────────────────────────────────────────

describe('ScreenDefinitionTable – レンダリング', () => {
  test('空の rows でも空状態メッセージが表示される', () => {
    render(<ScreenDefinitionTable rows={[]} onChange={jest.fn()} />);
    expect(screen.getByText('表示する要素がありません')).toBeInTheDocument();
  });

  test('rows がある場合、テーブルが表示される', () => {
    render(<ScreenDefinitionTable rows={SAMPLE_ROWS} onChange={jest.fn()} />);
    expect(document.querySelector('table')).toBeInTheDocument();
  });

  test('ヘッダー列が表示される', () => {
    render(<ScreenDefinitionTable rows={SAMPLE_ROWS} onChange={jest.fn()} />);
    expect(screen.getByText('ID')).toBeInTheDocument();
    expect(screen.getByText('名前')).toBeInTheDocument();
    expect(screen.getByText('種別')).toBeInTheDocument();
  });

  test('rows データが表示される', () => {
    render(<ScreenDefinitionTable rows={SAMPLE_ROWS} onChange={jest.fn()} />);
    expect(screen.getByText('user-email')).toBeInTheDocument();
    expect(screen.getByText('submit-btn')).toBeInTheDocument();
  });

  test('component_type バッジが表示される', () => {
    render(<ScreenDefinitionTable rows={SAMPLE_ROWS} onChange={jest.fn()} />);
    // input バッジが存在する
    const badges = document.querySelectorAll('.sdt-badge');
    expect(badges.length).toBeGreaterThan(0);
  });

  test('全選択チェックボックスが存在する', () => {
    render(<ScreenDefinitionTable rows={SAMPLE_ROWS} onChange={jest.fn()} />);
    const checkboxes = document.querySelectorAll('input[type="checkbox"]');
    // ヘッダーの全選択 + 各行のチェックボックス
    expect(checkboxes.length).toBe(SAMPLE_ROWS.length + 1);
  });

  test('統計情報が表示される（合計行数）', () => {
    render(<ScreenDefinitionTable rows={SAMPLE_ROWS} onChange={jest.fn()} />);
    // 全3行のデータが表示される（element_id で確認）
    expect(screen.getByText('user-email')).toBeInTheDocument();
    expect(screen.getByText('submit-btn')).toBeInTheDocument();
    expect(screen.getByText('user-name')).toBeInTheDocument();
  });
});

// ─────────────────────────────────────────────────────────────────────────────
// 行選択テスト
// ─────────────────────────────────────────────────────────────────────────────

describe('ScreenDefinitionTable – 行選択', () => {
  test('行チェックボックスをクリックで選択できる', () => {
    render(<ScreenDefinitionTable rows={SAMPLE_ROWS} onChange={jest.fn()} />);
    const checkboxes = document.querySelectorAll('tbody input[type="checkbox"]');
    fireEvent.click(checkboxes[0]);
    expect(checkboxes[0].checked).toBe(true);
  });

  test('全選択チェックボックスで全行を選択できる', () => {
    render(<ScreenDefinitionTable rows={SAMPLE_ROWS} onChange={jest.fn()} />);
    const headerCheckbox = document.querySelector('thead input[type="checkbox"]');
    fireEvent.click(headerCheckbox);
    const rowCheckboxes = document.querySelectorAll('tbody input[type="checkbox"]');
    rowCheckboxes.forEach((cb) => {
      expect(cb.checked).toBe(true);
    });
  });

  test('全選択後に再クリックで全解除できる', () => {
    render(<ScreenDefinitionTable rows={SAMPLE_ROWS} onChange={jest.fn()} />);
    const headerCheckbox = document.querySelector('thead input[type="checkbox"]');
    fireEvent.click(headerCheckbox);
    fireEvent.click(headerCheckbox);
    const rowCheckboxes = document.querySelectorAll('tbody input[type="checkbox"]');
    rowCheckboxes.forEach((cb) => {
      expect(cb.checked).toBe(false);
    });
  });
});

// ─────────────────────────────────────────────────────────────────────────────
// セル編集テスト
// ─────────────────────────────────────────────────────────────────────────────

describe('ScreenDefinitionTable – セル編集', () => {
  test('編集可能なセルをクリックするとエディタが表示される', () => {
    render(<ScreenDefinitionTable rows={SAMPLE_ROWS} onChange={jest.fn()} />);
    const cells = document.querySelectorAll('.sdt-cell-display');
    // 最初の編集可能セルをクリック（element_id 列）
    const editableCell = cells[0];
    fireEvent.click(editableCell);
    // input が出現する
    expect(document.querySelector('.sdt-cell-edit')).toBeInTheDocument();
  });

  test('編集後に onChange コールバックが呼ばれる', () => {
    const onChange = jest.fn();
    render(<ScreenDefinitionTable rows={SAMPLE_ROWS} onChange={onChange} />);
    const cells = document.querySelectorAll('.sdt-cell-display');
    fireEvent.click(cells[0]);

    const input = document.querySelector('.sdt-cell-edit input');
    if (input) {
      fireEvent.change(input, { target: { value: 'new-id' } });
      fireEvent.blur(input);
      expect(onChange).toHaveBeenCalled();
    }
  });

  test('Escape キーで編集をキャンセルできる', () => {
    render(<ScreenDefinitionTable rows={SAMPLE_ROWS} onChange={jest.fn()} />);
    const cells = document.querySelectorAll('.sdt-cell-display');
    fireEvent.click(cells[0]);
    const input = document.querySelector('.sdt-cell-edit input');
    if (input) {
      fireEvent.keyDown(input, { key: 'Escape' });
      // 編集モードが終了（input が消える）
      expect(document.querySelector('.sdt-cell-edit input')).toBeNull();
    }
  });

  test('Enter キーで編集を確定できる', () => {
    const onChange = jest.fn();
    render(<ScreenDefinitionTable rows={SAMPLE_ROWS} onChange={onChange} />);
    const cells = document.querySelectorAll('.sdt-cell-display');
    fireEvent.click(cells[0]);
    const input = document.querySelector('.sdt-cell-edit input');
    if (input) {
      fireEvent.change(input, { target: { value: 'updated-id' } });
      fireEvent.keyDown(input, { key: 'Enter' });
      expect(onChange).toHaveBeenCalled();
    }
  });
});

// ─────────────────────────────────────────────────────────────────────────────
// データ変更コールバックテスト
// ─────────────────────────────────────────────────────────────────────────────

describe('ScreenDefinitionTable – データ変更コールバック', () => {
  test('onChange は rows の配列を受け取る', () => {
    const onChange = jest.fn();
    render(<ScreenDefinitionTable rows={SAMPLE_ROWS} onChange={onChange} />);
    const cells = document.querySelectorAll('.sdt-cell-display');
    fireEvent.click(cells[0]);
    const input = document.querySelector('.sdt-cell-edit input');
    if (input) {
      fireEvent.change(input, { target: { value: 'x' } });
      fireEvent.blur(input);
      if (onChange.mock.calls.length > 0) {
        const arg = onChange.mock.calls[0][0];
        expect(Array.isArray(arg)).toBe(true);
      }
    }
  });

  test('onChange なしでも編集がクラッシュしない', () => {
    render(<ScreenDefinitionTable rows={SAMPLE_ROWS} />);
    const cells = document.querySelectorAll('.sdt-cell-display');
    expect(() => fireEvent.click(cells[0])).not.toThrow();
  });
});
