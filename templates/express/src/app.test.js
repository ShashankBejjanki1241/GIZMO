const request = require('supertest');
const app = require('./app');

describe('Express App', () => {
  it('GET / responds', async () => {
    const res = await request(app).get('/');
    expect(res.status).toBe(200);
    expect(res.body.message).toBe('Hello World');
  });

  it('GET /healthz returns healthy', async () => {
    // Should fail initially: /healthz route missing
    const res = await request(app).get('/healthz');
    expect(res.status).toBe(200);
    expect(res.body.status).toBe('healthy');
  });
});
