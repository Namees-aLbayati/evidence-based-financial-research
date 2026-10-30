"""API contract tests without credentials, datasets, an index, or paid model calls."""
import unittest
from fastapi.testclient import TestClient
from backend.main import app


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.previous = getattr(app.state, 'answer_question', None)
        self.questions = []
        def answer(question):
            self.questions.append(question)
            return dict(question=question, status='partial', answer='Supported excerpt',
                        citation_labels_valid=True, cache_hit=False,
                        validation_audit={'generation_drafts': ['Internal draft']})
        app.state.answer_question = answer
        self.client = TestClient(app)
        self.client.__enter__()

    def tearDown(self):
        self.client.__exit__(None, None, None)
        if self.previous is None:
            del app.state.answer_question
        else:
            app.state.answer_question = self.previous

    def test_question_contract(self):
        response = self.client.post('/ask', json={'question': '  Apple?  '})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.questions, ['Apple?'])
        self.assertEqual(response.json()['status'], 'partial')
        self.assertNotIn('validation_audit', response.json())

    def test_invalid_input_does_not_call_pipeline(self):
        for payload in [{}, {'question': ''}, {'question': '  '},
                        {'question': 42}, {'question': 'x'*4001}]:
            self.assertEqual(self.client.post('/ask', json=payload).status_code, 422)
        self.assertEqual(self.questions, [])

    def test_errors_are_sanitized(self):
        def broken(question):
            raise RuntimeError('private upstream body')
        app.state.answer_question = broken
        response = self.client.post('/ask', json={'question': 'Apple?'})
        self.assertEqual(response.status_code, 503)
        self.assertNotIn('private', response.text)

    def test_health(self):
        self.assertEqual(self.client.get('/health').json(), {'status': 'ready'})

    def test_frontend_and_assets(self):
        import re
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        assets = re.findall(r'(?:src|href)="(/ui/[^\"]+)"', response.text)
        self.assertTrue(assets)
        for path in assets:
            self.assertEqual(self.client.get(path).status_code, 200)

    def test_cors_rejects_unknown_origin(self):
        response = self.client.options('/ask', headers={
            'Origin': 'https://untrusted.example', 'Access-Control-Request-Method': 'POST'})
        self.assertNotIn('access-control-allow-origin', response.headers)


if __name__ == '__main__':
    unittest.main()
