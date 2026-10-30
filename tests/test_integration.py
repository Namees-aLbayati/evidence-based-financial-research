"""Offline integration checks: real startup/index; fake paid answer calls."""
import unittest
from fastapi.testclient import TestClient
from backend.main import app


class AppTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.client.__enter__()
        cls.real_answer = app.state.answer_question

    @classmethod
    def tearDownClass(cls):
        app.state.answer_question = cls.real_answer
        cls.client.__exit__(None, None, None)

    def tearDown(self):
        app.state.answer_question = type(self).real_answer

    def test_health_and_input_validation(self):
        self.assertEqual(self.client.get('/health').status_code, 200)
        for payload in [{}, {'question': '  '}, {'question': 123}, {'question': 'a'*4001}]:
            self.assertEqual(self.client.post('/ask', json=payload).status_code, 422)

    def test_answer_contract_and_private_fields(self):
        def answer(question):
            self.assertEqual(question, 'Apple?')
            return dict(question=question, status='partial', answer='Example answer',
                        sources=[], limitations=['Historical data'], coverage_notes=[],
                        citation_labels_valid=False, cache_hit=False,
                        validation_audit={'generation_drafts': ['private draft']})
        app.state.answer_question = answer
        response = self.client.post('/ask', json={'question': ' Apple? '})
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('validation_audit', response.json())

    def test_error_does_not_expose_upstream_details(self):
        def broken(question):
            raise RuntimeError('secret upstream body')
        app.state.answer_question = broken
        response = self.client.post('/ask', json={'question': 'Apple?'})
        self.assertEqual(response.status_code, 503)
        self.assertNotIn('secret', response.text)

    def test_cors(self):
        response = self.client.options('/ask', headers={
            'Origin': 'http://localhost:3000', 'Access-Control-Request-Method': 'POST'})
        self.assertEqual(response.headers['access-control-allow-origin'], 'http://localhost:3000')

    def test_real_vector_retrieval_without_paid_query_embedding(self):
        from unittest.mock import patch
        from backend import pipeline
        vector = pipeline.vector_store.get(limit=1, include=['embeddings'])['embeddings'][0]
        with patch.object(pipeline, 'query_vector', return_value=vector.tolist()):
            evidence = pipeline.retrieve_evidence('How did Apple perform?', pipeline.best_rag_config)
        self.assertTrue(evidence['context'])
        self.assertTrue(evidence['sources'])
        self.assertGreater(evidence['vector_passages'], 0)

    def test_real_calculation_and_empty_evidence_path(self):
        from backend import pipeline
        self.assertIsNotNone(pipeline.calculate_prices('Apple'))
        result = pipeline.generate_answer('offline integration test', pipeline.best_prompt_text,
            pipeline.best_rag_config, evidence={'context': [], 'sources': [], 'coverage_notes': [],
            'vector_passages': 0, 'supplemental_calculations': 0})
        self.assertEqual(result['status'], 'insufficient_evidence')


if __name__ == '__main__':
    unittest.main()
