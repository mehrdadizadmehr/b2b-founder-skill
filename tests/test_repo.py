import json
import os
import re
import unittest

from _load import ROOT, SKILLS_DIR

SKILLS = ["b2b-board", "b2b-competitors", "b2b-committee", "b2b-pricing", "b2b-offer", "b2b-cfo",
          "b2b-gtm", "b2b-brand", "b2b-ops", "b2b-launch", "b2b-plan"]
TOOLS = {"b2b-committee": "committee.py", "b2b-cfo": "b2b_economics.py", "b2b-pricing": "pricing.py", "b2b-plan": "compile.py"}


def frontmatter(path):
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    return (m.group(1) if m else ""), text


class Repo(unittest.TestCase):
    def test_eleven_skill_folders(self):
        found = sorted(d for d in os.listdir(SKILLS_DIR) if os.path.isfile(os.path.join(SKILLS_DIR, d, "SKILL.md")))
        self.assertEqual(found, sorted(SKILLS))

    def test_frontmatter_name_and_description(self):
        for s in SKILLS:
            fm, text = frontmatter(os.path.join(SKILLS_DIR, s, "SKILL.md"))
            self.assertIn("name: %s\n" % s, fm + "\n", s)
            self.assertIn("description:", fm, s)
            self.assertIn("## Output", text, s)

    def test_skills_reference_the_b2b_folder_not_founder(self):
        for s in SKILLS:
            _, text = frontmatter(os.path.join(SKILLS_DIR, s, "SKILL.md"))
            self.assertIn("b2b/", text, s)
            self.assertNotIn("founder/", text, s)
            self.assertNotIn("/founder-", text, s)

    def test_tools_present_and_stdlib_only(self):
        for folder, tool in TOOLS.items():
            path = os.path.join(SKILLS_DIR, folder, tool)
            self.assertTrue(os.path.isfile(path), path)
            with open(path, encoding="utf-8") as fh:
                src = fh.read()
            for bad in ("import requests", "import urllib", "import socket", "import subprocess", "eval(", "exec("):
                self.assertNotIn(bad, src, "%s uses %s" % (tool, bad))

    def test_lenses_and_examples(self):
        with open(os.path.join(SKILLS_DIR, "b2b-board", "lenses.md"), encoding="utf-8") as fh:
            lenses = fh.read()
        for h in ("## The Positioning lens", "## The Chasm lens", "## The Monopoly lens"):
            self.assertIn(h, lenses)
        for f in ("example-deal.json", "example-distribution.json", "example-manufacturing.json"):
            with open(os.path.join(SKILLS_DIR, "b2b-cfo", f), encoding="utf-8") as fh:
                self.assertIn(json.load(fh)["model"], ("deal", "distribution", "manufacturing"))
        with open(os.path.join(SKILLS_DIR, "b2b-committee", "customer.example.json"), encoding="utf-8") as fh:
            c = json.load(fh)
        self.assertGreaterEqual(len(c["roles"]), 2)

    def test_plugin_manifests(self):
        for f in ("plugin.json", "marketplace.json"):
            with open(os.path.join(ROOT, ".claude-plugin", f), encoding="utf-8") as fh:
                m = json.load(fh)
            self.assertEqual(m["name"], "b2b-founder-skill")

    def test_readme_names_every_skill(self):
        with open(os.path.join(ROOT, "README.md"), encoding="utf-8") as fh:
            readme = fh.read()
        for s in SKILLS:
            self.assertIn("/%s" % s, readme)


if __name__ == "__main__":
    unittest.main()
