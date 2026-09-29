import unittest
import os

os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ["LANGSMITH_TRACING"] = "false"

from gtm_agent import data_service
from gtm_agent.gtm_agent import SAFE_PROSPECT_FIELDS, build_prospect_profile, get_prospect


class ProspectToolPrivacyTests(unittest.TestCase):
    def setUp(self):
        data_service._PROFILES.clear()

    def test_prospect_tools_only_expose_safe_fields(self):
        prospect_id = next(iter(data_service.PROSPECTS))
        safe_fields = {"prospect_id", *SAFE_PROSPECT_FIELDS}
        billing_fields = {
            "billing_qualification",
            "tax_id",
            "date_of_birth",
            "card_on_file",
            "credit_check_ref",
        }

        prospect = get_prospect.invoke({"prospect_id": prospect_id})["prospect"]
        profile = build_prospect_profile.invoke({"prospect_id": prospect_id})["prospect_profile"]
        saved_profile = data_service.get_profile_from_db(prospect_id)["prospect_profile"]

        self.assertEqual(set(prospect), safe_fields)
        self.assertTrue(safe_fields.issubset(profile))
        self.assertTrue({"engagement_history", "account_details", "tech_stack"}.issubset(profile))
        self.assertEqual(profile, saved_profile)
        self.assertTrue(billing_fields.isdisjoint(prospect))
        self.assertTrue(billing_fields.isdisjoint(profile))
        self.assertTrue(billing_fields.isdisjoint(saved_profile))


if __name__ == "__main__":
    unittest.main()
