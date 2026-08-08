import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
ANALYSIS_SCRIPTS = REPO_ROOT / "literature-analysis" / "scripts"
if str(ANALYSIS_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(ANALYSIS_SCRIPTS))

from analysis_runtime import reference_api  # noqa: E402


class ReferenceApiTests(unittest.TestCase):
    @staticmethod
    def resolution_fixture(local_title: str, api_candidates: list[dict[str, object]], *, raw: str = ""):
        entries = [{"entry_index": 0, "raw": raw or f"Author. {local_title}. 2020.", "metadata": {}}]
        parsed = [
            {
                "entry_index": 0,
                "candidate_index": 0,
                "pattern": "author_title_year",
                "title_candidate": local_title,
                "year_candidate": 2020,
                "confidence": 0.9,
                "metadata": {},
            }
        ]
        return reference_api.resolve_candidates(entries, parsed, api_candidates)[0]

    def test_identifier_normalization_supports_doi_and_arxiv_forms(self):
        doi = reference_api.normalize_identifier("https://doi.org/10.1109/CVPR.2016.90")
        arxiv = reference_api.normalize_identifier("https://arxiv.org/pdf/1706.03762v5.pdf")
        legacy = reference_api.normalize_identifier("arXiv:hep-th/9901001v2")

        self.assertEqual(doi.canonical, "DOI:10.1109/cvpr.2016.90")
        self.assertEqual(arxiv.canonical, "ARXIV:1706.03762")
        self.assertEqual(legacy.canonical, "ARXIV:hep-th/9901001")
        self.assertIsNone(reference_api.normalize_identifier("ResNet paper"))

    def test_provider_adapters_normalize_sparse_crossref_and_complete_s2(self):
        crossref = reference_api.crossref_candidates(
            {
                "reference": [
                    {"key": "r1", "DOI": "10.1000/example"},
                    {
                        "key": "r2",
                        "article-title": "A Useful Paper",
                        "author": "Smith",
                        "year": "2020",
                        "journal-title": "Journal A",
                    },
                ]
            }
        )
        s2 = reference_api.semantic_scholar_candidates(
            [
                {
                    "citedPaper": {
                        "paperId": "paper-1",
                        "externalIds": {"DOI": "10.1000/example", "ArXiv": "2001.00001"},
                        "title": "An Example Paper",
                        "authors": [{"name": "Ada Author"}, {"name": "Bob Writer"}],
                        "year": 2019,
                        "venue": "Venue B",
                        "publicationDate": "2019-06-01",
                        "url": "https://www.semanticscholar.org/paper/paper-1",
                    }
                }
            ]
        )

        self.assertEqual(crossref[0]["identifiers"]["DOI"], "10.1000/example")
        self.assertEqual(crossref[0]["title"], "")
        self.assertEqual(crossref[1]["metadata"]["publicationTitle"], "Journal A")
        self.assertEqual(s2[0]["authors"], ["Ada Author", "Bob Writer"])
        self.assertEqual(s2[0]["metadata"]["archiveID"], "2001.00001")
        self.assertEqual(s2[0]["metadata"]["url"], "https://www.semanticscholar.org/paper/paper-1")

    def test_resolution_preserves_local_order_and_uses_complete_api_core(self):
        entries = [
            {"entry_index": 0, "raw": "[1] Smith. A Useful Paper. 2020.", "metadata": {}},
            {"entry_index": 1, "raw": "[2] Doe. Unresolved Work. 2021.", "metadata": {}},
        ]
        parsed = [
            {
                "entry_index": 0,
                "candidate_index": 0,
                "pattern": "author_title_year",
                "title_candidate": "A Useful Paper",
                "year_candidate": 2020,
                "confidence": 0.9,
                "metadata": {},
            },
            {
                "entry_index": 1,
                "candidate_index": 0,
                "pattern": "author_title_year",
                "title_candidate": "Unresolved Work",
                "year_candidate": 2021,
                "confidence": 0.9,
                "metadata": {},
            },
        ]
        api = [
            {
                "providers": ["semantic_scholar"],
                "provider_record_ids": ["p1"],
                "identifiers": {},
                "title": "A useful paper",
                "authors": ["Smith, Jane"],
                "year": 2020,
                "metadata": {"publicationTitle": "Journal"},
                "response_positions": {"semantic_scholar": 17},
            },
            {
                "providers": ["semantic_scholar"],
                "provider_record_ids": ["extra"],
                "identifiers": {},
                "title": "An Extra API Record",
                "authors": ["Extra"],
                "year": 2018,
                "metadata": {},
                "response_positions": {"semantic_scholar": 0},
            },
        ]

        decisions = reference_api.resolve_candidates(entries, parsed, api)

        self.assertEqual([item["entry_index"] for item in decisions], [0, 1])
        self.assertEqual(decisions[0]["status"], "accepted")
        self.assertEqual(decisions[0]["item"]["raw"], entries[0]["raw"])
        self.assertEqual(decisions[0]["item"]["metadata"]["resolution_source"], "reference_api")
        self.assertEqual(decisions[1]["status"], "unresolved")

    def test_incomplete_and_ambiguous_provider_rows_are_not_accepted(self):
        entries = [
            {"entry_index": 0, "raw": "Smith. Shared Title. 2020.", "metadata": {}},
            {"entry_index": 1, "raw": "Doe. Shared Title. 2020.", "metadata": {}},
        ]
        parsed = [
            {
                "entry_index": index,
                "candidate_index": 0,
                "pattern": "p",
                "title_candidate": "Shared Title",
                "year_candidate": 2020,
                "confidence": 0.9,
                "metadata": {},
            }
            for index in (0, 1)
        ]
        api = [
            {
                "providers": ["crossref"],
                "provider_record_ids": ["r1"],
                "identifiers": {},
                "title": "Shared Title",
                "authors": ["Someone"],
                "year": 2020,
                "metadata": {},
                "response_positions": {"crossref": 0},
            },
            {
                "providers": ["crossref"],
                "provider_record_ids": ["r2"],
                "identifiers": {"DOI": "10.1000/incomplete"},
                "title": "",
                "authors": [],
                "year": None,
                "metadata": {"DOI": "10.1000/incomplete"},
                "response_positions": {"crossref": 1},
            },
        ]

        decisions = reference_api.resolve_candidates(entries, parsed, api)
        self.assertTrue(all(item["status"] == "unresolved" for item in decisions))

    def test_arxiv_semantic_scholar_title_near_match_does_not_compete_below_095(self):
        local_title = "one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen twenty"
        decision = self.resolution_fixture(
            local_title,
            [
                {
                    "providers": ["crossref"],
                    "provider_record_ids": ["correct"],
                    "identifiers": {},
                    "title": "one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen replacement",
                    "authors": ["Correct Author"],
                    "year": 2020,
                    "metadata": {},
                    "response_positions": {"crossref": 0},
                },
                {
                    "providers": ["semantic_scholar"],
                    "provider_record_ids": ["arxiv-interference"],
                    "identifiers": {"arXiv": "2001.00001"},
                    "title": "one two three four five six seven eight nine ten eleven twelve unrelated",
                    "authors": ["Wrong Author"],
                    "year": 2020,
                    "metadata": {"archiveID": "2001.00001"},
                    "response_positions": {"semantic_scholar": 0},
                },
            ],
        )

        self.assertEqual(decision["status"], "accepted")
        self.assertEqual(decision["provider_record_ids"], ["correct"])
        self.assertAlmostEqual(decision["match_score"], 0.95)

    def test_arxiv_semantic_scholar_title_candidate_is_accepted_at_095_or_above(self):
        decision = self.resolution_fixture(
            "A precise title for a cited research paper",
            [
                {
                    "providers": ["semantic_scholar"],
                    "provider_record_ids": ["arxiv-correct"],
                    "identifiers": {"arXiv": "2001.00001"},
                    "title": "A precise title for a cited research paper",
                    "authors": ["Correct Author"],
                    "year": 2020,
                    "metadata": {"archiveID": "2001.00001"},
                    "response_positions": {"semantic_scholar": 0},
                }
            ],
        )

        self.assertEqual(decision["status"], "accepted")
        self.assertEqual(decision["provider_record_ids"], ["arxiv-correct"])

    def test_non_arxiv_semantic_scholar_title_and_exact_identifier_keep_existing_admission(self):
        local_title = "one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen twenty"
        title_decision = self.resolution_fixture(
            local_title,
            [
                {
                    "providers": ["semantic_scholar"],
                    "provider_record_ids": ["s2-no-arxiv"],
                    "identifiers": {},
                    "title": "one two three four five six seven eight nine ten eleven twelve unrelated",
                    "authors": ["Semantic Author"],
                    "year": 2020,
                    "metadata": {},
                    "response_positions": {"semantic_scholar": 0},
                }
            ],
        )
        identifier_decision = self.resolution_fixture(
            "Completely different local title",
            [
                {
                    "providers": ["semantic_scholar"],
                    "provider_record_ids": ["s2-exact-arxiv"],
                    "identifiers": {"arXiv": "2001.00001"},
                    "title": "Unrelated provider title",
                    "authors": ["Identifier Author"],
                    "year": 2020,
                    "metadata": {"archiveID": "2001.00001"},
                    "response_positions": {"semantic_scholar": 0},
                }
            ],
            raw="Author. Completely different local title. arXiv:2001.00001. 2020.",
        )

        self.assertEqual(title_decision["status"], "accepted")
        self.assertEqual(identifier_decision["status"], "accepted")
        self.assertEqual(identifier_decision["match_basis"], "identifier")

    def test_provider_merge_prefers_crossref_title_independent_of_input_order(self):
        merged = reference_api.merge_provider_candidates(
            [
                {
                    "providers": ["semantic_scholar"],
                    "provider_record_ids": ["s2"],
                    "identifiers": {},
                    "title": "Paper Title",
                    "authors": ["A"],
                    "year": 2020,
                    "metadata": {},
                    "response_positions": {"semantic_scholar": 0},
                },
                {
                    "providers": ["crossref"],
                    "provider_record_ids": ["cr"],
                    "identifiers": {},
                    "title": "Paper: Title",
                    "authors": ["A"],
                    "year": 2020,
                    "metadata": {},
                    "response_positions": {"crossref": 0},
                },
            ]
        )

        self.assertEqual(len(merged), 1)
        self.assertEqual(merged[0]["title"], "Paper: Title")
        self.assertEqual(merged[0]["providers"], ["semantic_scholar", "crossref"])

    def test_provider_fetch_rejects_oversized_json_response(self):
        original_limit = reference_api.HTTP_MAX_RESPONSE_BYTES
        reference_api.HTTP_MAX_RESPONSE_BYTES = 32
        try:
            def fake_get(_url: str, _headers: dict[str, str], _timeout: float) -> reference_api.HttpResponse:
                return reference_api.HttpResponse(200, {}, b"{" + b" " * 32 + b"}")

            identifier = reference_api.normalize_identifier("10.1000/source")
            result = reference_api.fetch_crossref(identifier, http_get=fake_get, sleeper=lambda _seconds: None)
        finally:
            reference_api.HTTP_MAX_RESPONSE_BYTES = original_limit

        self.assertEqual(result.status, "failed")
        self.assertEqual(result.error["kind"], "response_too_large")

    def test_semantic_scholar_fetch_retries_rate_limit_and_paginates(self):
        calls: list[str] = []
        sleeps: list[float] = []

        def fake_get(url: str, _headers: dict[str, str], _timeout: float) -> reference_api.HttpResponse:
            calls.append(url)
            if len(calls) == 1:
                return reference_api.HttpResponse(429, {"retry-after": "1"}, b"rate limited")
            if "offset=0" in url:
                return reference_api.HttpResponse(
                    200,
                    {},
                    b'{"data":[{"citedPaper":{"paperId":"p1","title":"Paper One","authors":[{"name":"A"}],"year":2020,"externalIds":{}}}],"next":100}',
                )
            return reference_api.HttpResponse(200, {}, b'{"data":[]}')

        identifier = reference_api.normalize_identifier("10.1000/source")
        result = reference_api.fetch_semantic_scholar(identifier, http_get=fake_get, sleeper=sleeps.append)

        self.assertEqual(result.status, "succeeded")
        self.assertEqual(len(result.candidates), 1)
        self.assertEqual(len(calls), 3)
        self.assertEqual(sleeps, [1.0])


if __name__ == "__main__":
    unittest.main()
