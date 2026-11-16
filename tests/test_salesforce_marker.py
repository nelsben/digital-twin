"""Checks for the Salesforce marker field: starter-kit/connectors/salesforce.

The field Last_Updated_By_Twin__c on Opportunity is source-format (SFDX)
metadata the CRM admin deploys with the Salesforce CLI. These tests parse the
XML and check the facts that matter: the object and API name, the type, that
Field History tracking is on, that the field has a description, and the
permission sets.

Standard library only. Run with: python3 -m unittest tests.test_salesforce_marker
(or: python3 -m unittest discover -s tests)

Metadata shapes: https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/customfield.htm
(CustomField) and .../meta_permissionset.htm (PermissionSet).
"""

import json
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SF_DIR = ROOT / "starter-kit" / "connectors" / "salesforce"
DEFAULT_DIR = SF_DIR / "force-app" / "main" / "default"
FIELD_DIR = DEFAULT_DIR / "objects" / "Opportunity" / "fields"
FIELD_FILE = FIELD_DIR / "Last_Updated_By_Twin__c.field-meta.xml"
PERMSET_DIR = DEFAULT_DIR / "permissionsets"
READ_PERMSET_FILE = PERMSET_DIR / "Twin_Marker_Read.permissionset-meta.xml"
EDIT_PERMSET_FILE = PERMSET_DIR / "Twin_Marker_Edit.permissionset-meta.xml"
README = SF_DIR / "README.md"
PROJECT_FILE = SF_DIR / "sfdx-project.json"

NS = {"m": "http://soap.sforce.com/2006/04/metadata"}
FIELD_API_NAME = "Last_Updated_By_Twin__c"
FIELD_FULL_NAME = "Opportunity." + FIELD_API_NAME


def parse(path):
    """Parse an XML file and return its root element."""
    return ET.parse(path).getroot()


def text_of(root, tag):
    """Return the stripped text of the first direct child with this tag, or None."""
    node = root.find("m:" + tag, NS)
    if node is None or node.text is None:
        return None
    return node.text.strip()


def field_permission(root):
    """Return the fieldPermissions element for the marker field, or None."""
    for fp in root.findall("m:fieldPermissions", NS):
        if text_of(fp, "field") == FIELD_FULL_NAME:
            return fp
    return None


class TestFieldMetadata(unittest.TestCase):
    def setUp(self):
        self.root = parse(FIELD_FILE)

    def test_file_name_is_the_api_name(self):
        self.assertTrue(FIELD_FILE.name.startswith(FIELD_API_NAME + "."))

    def test_root_is_custom_field_in_metadata_namespace(self):
        self.assertEqual(self.root.tag, "{%s}CustomField" % NS["m"])

    def test_api_name_is_right(self):
        self.assertEqual(text_of(self.root, "fullName"), FIELD_API_NAME)

    def test_object_is_opportunity(self):
        # In source format the owning object is the folder the field sits in.
        self.assertEqual(FIELD_FILE.parent.parent.name, "Opportunity")

    def test_type_is_datetime(self):
        self.assertEqual(text_of(self.root, "type"), "DateTime")

    def test_history_tracking_is_on(self):
        self.assertEqual(text_of(self.root, "trackHistory"), "true")

    def test_has_a_description(self):
        description = text_of(self.root, "description")
        self.assertTrue(description, "description must not be empty")
        self.assertIn("twin", description.lower())

    def test_has_a_label(self):
        self.assertTrue(text_of(self.root, "label"))

    def test_field_is_not_required(self):
        # A required field would break every human edit that does not set it.
        self.assertEqual(text_of(self.root, "required"), "false")


class TestPermissionSets(unittest.TestCase):
    def test_read_set_gives_read_only(self):
        root = parse(READ_PERMSET_FILE)
        self.assertEqual(root.tag, "{%s}PermissionSet" % NS["m"])
        fp = field_permission(root)
        self.assertIsNotNone(fp, "read set must name the marker field")
        self.assertEqual(text_of(fp, "readable"), "true")
        self.assertEqual(text_of(fp, "editable"), "false")

    def test_edit_set_gives_edit(self):
        root = parse(EDIT_PERMSET_FILE)
        self.assertEqual(root.tag, "{%s}PermissionSet" % NS["m"])
        fp = field_permission(root)
        self.assertIsNotNone(fp, "edit set must name the marker field")
        self.assertEqual(text_of(fp, "readable"), "true")
        self.assertEqual(text_of(fp, "editable"), "true")

    def test_permission_set_descriptions_fit_salesforce_limit(self):
        # Salesforce caps a PermissionSet description at 255 characters. The OPS-13
        # scratch-org deploy failed on a 338-character one ("max length=255"), and
        # the all-or-nothing deploy then lost the field too. See the wall-test README.
        limit = 255
        paths = sorted(PERMSET_DIR.glob("*.permissionset-meta.xml"))
        self.assertTrue(paths, "no permission set files found")
        for path in paths:
            description = text_of(parse(path), "description") or ""
            self.assertLessEqual(len(description), limit, path.name)

    def test_permission_sets_touch_only_the_marker_field(self):
        for path in (READ_PERMSET_FILE, EDIT_PERMSET_FILE):
            root = parse(path)
            fields = [text_of(fp, "field") for fp in root.findall("m:fieldPermissions", NS)]
            self.assertEqual(fields, [FIELD_FULL_NAME], path.name)
            self.assertTrue(text_of(root, "label"), path.name)
            self.assertTrue(text_of(root, "description"), path.name)


class TestProjectAndReadme(unittest.TestCase):
    def test_sfdx_project_points_at_force_app(self):
        project = json.loads(PROJECT_FILE.read_text(encoding="utf-8"))
        paths = [d["path"] for d in project["packageDirectories"]]
        self.assertIn("force-app", paths)
        self.assertTrue((SF_DIR / "force-app").is_dir())
        self.assertTrue(project.get("sourceApiVersion"))

    def test_readme_covers_deploy_skill_and_reporting(self):
        text = README.read_text(encoding="utf-8")
        for needle in (
            "sf project deploy start",
            FIELD_API_NAME,
            "per-user OAuth",
            "Field History",
            "OpportunityFieldHistory",
            "CRM-update",
        ):
            self.assertIn(needle, text)


if __name__ == "__main__":
    unittest.main()
