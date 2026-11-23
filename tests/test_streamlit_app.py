import os
import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest

from src.examples import IDE_TEST_EXAMPLE, LONG_METHOD, SHORT_METHOD


APP_PATH = Path(__file__).resolve().parents[1] / "app.py"
os.environ["CODESCOPE_DISABLE_RETRAIN"] = "1"


class StreamlitAppTest(unittest.TestCase):
    def test_app_loads_and_renders_short_analysis(self):
        app = AppTest.from_file(str(APP_PATH), default_timeout=90).run()
        self.assertEqual(len(app.exception), 0)
        app.text_area(key="code_input").set_value(SHORT_METHOD)
        app.button(key="analyze_button").click().run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(len(app.dataframe), 3)

    def test_app_renders_flagged_long_method(self):
        app = AppTest.from_file(str(APP_PATH), default_timeout=90).run()
        app.text_area(key="code_input").set_value(LONG_METHOD)
        app.button(key="analyze_button").click().run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(app.toast[0].value, "Analisis selesai.")
        rendered = "\n".join(
            [str(item.value) for item in app.markdown]
            + [str(item.value) for item in app.caption]
        )
        self.assertIn("Hasil prediksi input IDE", rendered)
        self.assertIn("Perbandingan data latih dan data uji", rendered)
        self.assertIn("Data latih", rendered)
        self.assertIn("Perbandingan versi model", rendered)
        self.assertIn("V2", rendered)
        self.assertIn(
            "Data uji baru harus berisi minimal satu fungsi Long Method",
            rendered,
        )
        self.assertIn("78.6%", rendered)
        self.assertIn("89.3%", rendered)
        self.assertIn("83.6%", rendered)
        self.assertIn("Label pembanding R0915 ditambahkan otomatis", rendered)

    def test_small_ide_sample_shows_metrics_with_sample_warning(self):
        app = AppTest.from_file(str(APP_PATH), default_timeout=90).run()
        app.text_area(key="code_input").set_value(IDE_TEST_EXAMPLE)
        app.button(key="analyze_button").click().run()
        rendered = "\n".join(str(item.value) for item in app.markdown)
        self.assertEqual(len(app.exception), 0)
        self.assertIn("Data uji IDE", rendered)
        self.assertIn("100.0%", rendered)
        self.assertIn("Sampel relatif kecil", rendered)

    def test_internal_test_data_can_be_loaded_without_upload(self):
        app = AppTest.from_file(str(APP_PATH), default_timeout=90).run()
        app.button(key="load_internal_test").click().run()
        rendered = "\n".join(str(item.value) for item in app.markdown)
        self.assertEqual(len(app.exception), 0)
        self.assertIn("Data uji internal", rendered)
        self.assertIn("61.8%", rendered)
        self.assertIn("83.9%", rendered)
        self.assertIn("71.2%", rendered)



if __name__ == "__main__":
    unittest.main()
