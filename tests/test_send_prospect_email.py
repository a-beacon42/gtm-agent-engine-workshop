import os
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import patch

os.environ.setdefault("OPENAI_API_KEY", "sk-test")

from gtm_agent.gtm_agent import send_prospect_email


class SendProspectEmailTest(TestCase):
    def setUp(self):
        self.runtime = SimpleNamespace(config={"metadata": {}})
        self.prospect = {
            "prospect_id": "LEAD-12345",
            "name": "Alex Smith",
            "email": "alex@example.com",
        }

    @patch("gtm_agent.gtm_agent.data_service.get_prospect_record")
    def test_disqualified_prospect_is_blocked(self, get_prospect_record):
        get_prospect_record.return_value = {
            "email": "alex@example.com",
            "disqualified": True,
        }

        result = send_prospect_email.func(
            self.prospect,
            "Following up",
            "Hello",
            self.runtime,
            from_rep={"email": "rep@example.com", "name": "Rep"},
        )

        self.assertEqual(result["status"], "blocked")
        self.assertEqual(result["prospect_id"], "LEAD-12345")
        self.assertEqual(
            result["error"],
            "Prospect is disqualified; outbound email suppressed.",
        )

    @patch("gtm_agent.gtm_agent.data_service.get_prospect_record")
    def test_qualified_prospect_is_sent(self, get_prospect_record):
        get_prospect_record.return_value = {
            "email": "alex@example.com",
            "disqualified": False,
        }

        result = send_prospect_email.func(
            self.prospect,
            "Following up",
            "Hello",
            self.runtime,
            from_rep={"email": "rep@example.com", "name": "Rep"},
        )

        self.assertEqual(result["status"], "sent")
        self.assertEqual(result["to"], "alex@example.com")
