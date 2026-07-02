import unittest

import tests  # noqa: F401  (sets up sys.path, see tests/__init__.py)

import metro_config


class TestOverlayConfig(unittest.TestCase):
    """
        metro_config.overlay_config() implements the three-layer precedence
        (hardcoded -> config file -> command line) described in metro_config.py:
        "The command line overwrite the config file. Config file overwrite
        hardcoded value." This tests that merge logic directly, without going
        through the full metro_config.init()/set_default_value() machinery.
    """

    def setUp(self):
        self.dBase = {
            'AT': {'VALUE': 0.0, 'FROM': metro_config.CFG_HARDCODED, 'COMMENTS': "air temp"},
            'LANG': {'VALUE': "en", 'FROM': metro_config.CFG_HARDCODED, 'COMMENTS': "language"},
        }

    def test_new_value_overwrites_existing_key(self):
        metro_config.overlay_config(self.dBase, {'AT': -5.0}, metro_config.CFG_CONFIGFILE)
        self.assertEqual(self.dBase['AT']['VALUE'], -5.0)
        self.assertEqual(self.dBase['AT']['FROM'], metro_config.CFG_CONFIGFILE)

    def test_unrelated_key_is_untouched(self):
        metro_config.overlay_config(self.dBase, {'AT': -5.0}, metro_config.CFG_CONFIGFILE)
        self.assertEqual(self.dBase['LANG']['VALUE'], "en")
        self.assertEqual(self.dBase['LANG']['FROM'], metro_config.CFG_HARDCODED)

    def test_command_line_overwrites_config_file_value(self):
        metro_config.overlay_config(self.dBase, {'AT': -5.0}, metro_config.CFG_CONFIGFILE)
        metro_config.overlay_config(self.dBase, {'AT': -8.0}, metro_config.CFG_COMMANDLINE)
        self.assertEqual(self.dBase['AT']['VALUE'], -8.0)
        self.assertEqual(self.dBase['AT']['FROM'], metro_config.CFG_COMMANDLINE)

    def test_unknown_key_is_added_as_new_entry(self):
        metro_config.overlay_config(self.dBase, {'CUSTOM_KEY': 42}, metro_config.CFG_COMMANDLINE)
        self.assertIn('CUSTOM_KEY', self.dBase)
        self.assertEqual(self.dBase['CUSTOM_KEY']['VALUE'], 42)
        self.assertEqual(self.dBase['CUSTOM_KEY']['FROM'], metro_config.CFG_COMMANDLINE)


if __name__ == '__main__':
    unittest.main()
