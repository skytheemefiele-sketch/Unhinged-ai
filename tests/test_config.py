import os, tempfile, unittest
from pathlib import Path
from config_loader import load_config

ROOT=Path(__file__).resolve().parents[1]

class ConfigTests(unittest.TestCase):
    def _isolated_root(self):
        tmp=tempfile.TemporaryDirectory()
        root=Path(tmp.name)
        (root/"config.json").write_text((ROOT/"config.json").read_text(encoding="utf-8"),encoding="utf-8")
        return tmp,root

    def test_local_defaults_and_modes(self):
        tmp,root=self._isolated_root()
        try:
            cfg=load_config(root)
            self.assertEqual(cfg["runtime"]["max_heavy_engines_active"],1)
            self.assertEqual(set(cfg["modes"]),{"sora","shadow","jarvis"})
            self.assertEqual(cfg["modes"]["sora"]["backend"],"local")
            self.assertEqual(cfg["modes"]["jarvis"]["engine"],"stable_diffusion_cpp")
        finally: tmp.cleanup()

    def test_env_override_enables_remote(self):
        tmp,root=self._isolated_root()
        names=("CUSTOM_BASE_URL","CUSTOM_API_KEY","CUSTOM_MODEL","UNHINGED_SORA_BACKEND")
        old={k:os.environ.get(k) for k in names}
        try:
            os.environ.update({"CUSTOM_BASE_URL":"https://example.test/v1","CUSTOM_API_KEY":"test-key","CUSTOM_MODEL":"test-model","UNHINGED_SORA_BACKEND":"remote"})
            cfg=load_config(root)
            self.assertTrue(cfg["remote"]["enabled"])
            self.assertEqual(cfg["modes"]["sora"]["backend"],"remote")
        finally:
            for k,v in old.items():
                if v is None: os.environ.pop(k,None)
                else: os.environ[k]=v
            tmp.cleanup()
