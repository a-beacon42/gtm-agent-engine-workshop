import os
import unittest

os.environ.setdefault("OPENAI_API_KEY", "test-api-key")

from gtm_agent import data_service
from gtm_agent.gtm_agent import build_prospect_profile


class UpdateProspectInfoTest(unittest.TestCase):
    prospect_id = "LEAD-39002"

    def setUp(self):
        self.record = data_service.PROSPECTS[self.prospect_id]
        self.original_tech_stack = list(self.record["tech_stack"])
        self.original_profile = data_service._PROFILES.pop(self.prospect_id, None)

    def tearDown(self):
        self.record["tech_stack"] = self.original_tech_stack
        if self.original_profile is None:
            data_service._PROFILES.pop(self.prospect_id, None)
        else:
            data_service._PROFILES[self.prospect_id] = self.original_profile

    def test_update_persists_technology_and_invalidates_profile(self):
        build_prospect_profile.invoke({"prospect_id": self.prospect_id})

        result = data_service.update_prospect_info(self.prospect_id, "Terraform")

        self.assertTrue(result["updated"])
        self.assertIn("Terraform", data_service.fetch_tech_stack(self.prospect_id))
        profile = build_prospect_profile.invoke({"prospect_id": self.prospect_id})
        self.assertIn("Terraform", profile["prospect_profile"]["tech_stack"])


if __name__ == "__main__":
    unittest.main()
