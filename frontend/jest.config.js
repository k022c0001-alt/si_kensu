/** @type {import('jest').Config} */
module.exports = {
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['@testing-library/jest-dom'],
  transform: {
    '^.+\\.(js|jsx|ts|tsx)$': 'babel-jest',
  },
  moduleNameMapper: {
    '\\.(css|less|scss|sass)$': '<rootDir>/src/__tests__/__mocks__/styleMock.js',
    '^mermaid$': '<rootDir>/src/__tests__/__mocks__/mermaidMock.js',
  },
  testMatch: [
    '<rootDir>/src/__tests__/**/*.test.(js|jsx)',
  ],
};
