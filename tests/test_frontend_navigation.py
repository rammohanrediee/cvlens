import unittest

from frontend.components.navigation import NAV_LABELS, NAV_OPTIONS
from frontend.components.styles import DARK_THEME, LIGHT_THEME


class FrontendNavigationTestCase(unittest.TestCase):
    def test_primary_workflow_has_separate_views(self):
        self.assertEqual(NAV_OPTIONS[:3], ["Analyze", "Results", "Feedback"])
        self.assertEqual(NAV_LABELS["Analyze"], "Analyze")

    def test_palette_uses_named_primary_colors(self):
        for palette in (LIGHT_THEME, DARK_THEME):
            self.assertIn("primary", palette)
            self.assertIn("primary_soft", palette)
            self.assertNotIn("amber", palette)
            self.assertNotIn("orange", palette)


if __name__ == "__main__":
    unittest.main()
