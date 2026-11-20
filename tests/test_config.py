import json, tempfile, unittest
from pathlib import Path
from config_loader import load_config

class ConfigTests(unittest.TestCase):
    def test_local_defaults_and_modes(self):
        cfg=load_config(Path(__file__).resolve().parents[1])
        self.assertEqual(cfg["runtime"]["max_heavy_engines_active"],1)
        self.assertEqual(set(cfg["modes"]),{"sora","shadow","jarvis"})
        self.assertEqual(cfg["modes"]["sora"]["backend"],"local")
        self.assertEqual(cfg["modes"]["jarvis"]["engine"],"stable_diffusion_cpp")
