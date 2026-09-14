import json
import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from knowledge import format_context, load_chunks, retrieve, tokenize  # noqa: E402


class KnowledgeTests(unittest.TestCase):
    def test_tokenize_ignores_accents_and_common_words(self):
        terms = tokenize("Como funciona a hidratação?")
        self.assertIn("hidratacao", terms)
        self.assertNotIn("como", terms)

    def test_retrieve_finds_relevant_source(self):
        chunks = load_chunks(PROJECT_ROOT / "data" / "knowledge.json")
        results = retrieve("qual a função das fibras?", chunks, limit=3)
        self.assertTrue(results)
        context = format_context(results)
        self.assertIn("fibr", context.lower())

    def test_generated_base_has_metadata_and_chunks(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "knowledge.json"
            path.write_text(
                json.dumps(
                    {
                        "metadata": {"documents": [{"file": "fonte.pdf", "pages": 1}]},
                        "chunks": [
                            {"source": "fonte.pdf", "page": 1, "section": "teste", "text": "Fibras"}
                        ],
                    }
                ),
                encoding="utf-8",
            )
            self.assertEqual(load_chunks(path)[0].source, "fonte.pdf")


if __name__ == "__main__":
    unittest.main()

