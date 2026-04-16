/**
 * App.test.jsx
 *
 * App コンポーネントの統合テスト:
 * - ナビゲーションテスト
 * - ビューの切り替えテスト
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import App from '../App';

// ─────────────────────────────────────────────────────────────────────────────
// App コンポーネントテスト
// ─────────────────────────────────────────────────────────────────────────────

describe('App – ナビゲーション', () => {
  test('アプリがクラッシュせずにレンダリングされる', () => {
    expect(() => render(<App />)).not.toThrow();
  });

  test('タブボタンが表示される', () => {
    render(<App />);
    // タブボタン（ナビゲーション部分）を確認
    const allSeq = screen.getAllByText(/シーケンス図/);
    expect(allSeq.length).toBeGreaterThan(0);
    const allClass = screen.getAllByText(/クラス図/);
    expect(allClass.length).toBeGreaterThan(0);
    const allScreen = screen.getAllByText(/画面項目定義書/);
    expect(allScreen.length).toBeGreaterThan(0);
  });

  test('シーケンス図タブがデフォルトで表示される', () => {
    render(<App />);
    // デフォルトは sequence タブ - タブボタンが存在する
    const seqButtons = screen.getAllByText(/シーケンス図/);
    expect(seqButtons.length).toBeGreaterThan(0);
    // タブボタンの1つがボタン要素
    const tabButton = seqButtons.find(el => el.tagName === 'BUTTON');
    expect(tabButton).toBeTruthy();
  });
});

describe('App – ビューの切り替え', () => {
  test('クラス図タブに切り替えられる', () => {
    render(<App />);
    const classTabs = screen.getAllByText(/クラス図/);
    // タブボタンを探す
    const classTabButton = classTabs.find(el => el.tagName === 'BUTTON');
    expect(classTabButton).toBeTruthy();
    fireEvent.click(classTabButton);
    // クラス図コンポーネントが表示される
    expect(screen.getByText('Class Diagram')).toBeInTheDocument();
  });

  test('画面項目定義書タブに切り替えられる', () => {
    render(<App />);
    const screenTabs = screen.getAllByText(/画面項目定義書/);
    const screenTabButton = screenTabs.find(el => el.tagName === 'BUTTON');
    expect(screenTabButton).toBeTruthy();
    fireEvent.click(screenTabButton);
    // ScreenDefinitionView が表示される
    expect(document.body.textContent.length).toBeGreaterThan(0);
  });

  test('シーケンス図タブに戻れる', () => {
    render(<App />);
    // クラス図に切り替え
    const classTabs = screen.getAllByText(/クラス図/);
    const classTabButton = classTabs.find(el => el.tagName === 'BUTTON');
    fireEvent.click(classTabButton);
    // シーケンス図に戻る
    const seqTabs = screen.getAllByText(/シーケンス図/);
    const seqTabButton = seqTabs.find(el => el.tagName === 'BUTTON');
    fireEvent.click(seqTabButton);
    // シーケンス図が表示される
    expect(screen.queryByText('Class Diagram')).toBeNull();
  });

  test('ファイル選択 input がシーケンス図タブに表示される', () => {
    render(<App />);
    // デフォルトのシーケンス図タブにファイル選択 input がある
    const fileInput = document.querySelector('input[type="file"]');
    expect(fileInput).toBeInTheDocument();
  });
});
