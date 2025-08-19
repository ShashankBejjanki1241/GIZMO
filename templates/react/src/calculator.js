class Calculator {
  add(a, b) {
    return a + b;
  }

  subtract(a, b) {
    return a - b;
  }

  multiply(a, b) {
    return a * b;
  }

  // Intentionally missing divide(a, b) to make tests fail; agents should add it with divide-by-zero guard
}

module.exports = Calculator;
