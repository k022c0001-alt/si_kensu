// Mermaid mock for Jest (avoids SVG rendering issues in jsdom)
const mermaid = {
  initialize: jest.fn(),
  render: jest.fn().mockResolvedValue({ svg: '<svg></svg>' }),
  init: jest.fn(),
};

module.exports = mermaid;
module.exports.default = mermaid;
