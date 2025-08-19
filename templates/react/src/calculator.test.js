const Calculator = require('./calculator');

describe('Calculator', () => {
  let calc;

  beforeEach(() => {
    calc = new Calculator();
  });

  test('adds two numbers', () => {
    expect(calc.add(2, 3)).toBe(5);
  });

  test('divide returns quotient and guards divide-by-zero', () => {
    // Should fail initially: divide is missing
    expect(() => calc.divide(4, 0)).toThrow('Division by zero');
    expect(calc.divide(6, 3)).toBe(2);
  });
});
