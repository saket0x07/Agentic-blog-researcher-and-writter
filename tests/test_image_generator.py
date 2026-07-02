import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
import tempfile
import shutil
from PIL import Image

from blog_agent import config
from blog_agent.utils.image_generator import generate_image, generate_with_pillow
from blog_agent.utils.huggingface_client import generate_with_huggingface

class TestImageGeneratorPipeline(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for test output files
        self.test_dir = Path(tempfile.mkdtemp())
        self.output_path = self.test_dir / "test_image.png"

    def tearDown(self):
        # Remove temporary directory and files
        shutil.rmtree(self.test_dir)

    @patch("blog_agent.utils.image_generator.generate_blog_image")
    @patch("blog_agent.utils.image_generator.generate_with_huggingface")
    @patch("blog_agent.utils.image_generator.generate_with_pillow")
    def test_gemini_success_path(self, mock_pillow, mock_hf, mock_gemini):
        # Setup mock behavior to touch the path (simulating image creation) and return it
        mock_gemini.side_effect = lambda prompt, path: (path.touch(), path)[1]
        
        # Act
        result = generate_image("A futuristic computer system", self.output_path)
        
        # Assert
        self.assertEqual(result, self.output_path)
        mock_gemini.assert_called_once_with("A futuristic computer system", self.output_path)
        mock_hf.assert_not_called()
        mock_pillow.assert_not_called()

    @patch("blog_agent.utils.image_generator.generate_blog_image")
    @patch("blog_agent.utils.image_generator.generate_with_huggingface")
    @patch("blog_agent.utils.image_generator.generate_with_pillow")
    def test_gemini_fails_huggingface_success(self, mock_pillow, mock_hf, mock_gemini):
        # Setup mock behavior
        mock_gemini.side_effect = Exception("Gemini API error")
        mock_hf.side_effect = lambda prompt, path: (path.touch(), path)[1]
        
        # Act
        result = generate_image("A futuristic computer system", self.output_path)
        
        # Assert
        self.assertEqual(result, self.output_path)
        mock_gemini.assert_called_once_with("A futuristic computer system", self.output_path)
        mock_hf.assert_called_once_with("A futuristic computer system", self.output_path)
        mock_pillow.assert_not_called()

    @patch("blog_agent.utils.image_generator.generate_blog_image")
    @patch("blog_agent.utils.image_generator.generate_with_huggingface")
    def test_gemini_and_huggingface_fail_pillow_success(self, mock_hf, mock_gemini):
        # Setup mock behavior
        mock_gemini.side_effect = Exception("Gemini API error")
        mock_hf.side_effect = Exception("HF inference API error")
        
        # Act
        # Let's verify that it falls back to the actual generate_with_pillow implementation
        result = generate_image("A futuristic computer system", self.output_path)
        
        # Assert
        self.assertEqual(result, self.output_path)
        self.assertTrue(self.output_path.exists())
        
        # Verify the created image is a valid PNG image and correct size
        with Image.open(self.output_path) as img:
            self.assertEqual(img.size, (800, 450))
            self.assertEqual(img.format, "PNG")

    def test_pillow_fallback_generation_directly(self):
        # Act
        result = generate_with_pillow("Short prompt", self.output_path)
        
        # Assert
        self.assertEqual(result, self.output_path)
        self.assertTrue(self.output_path.exists())
        
        # Verify the created image is a valid PNG image and correct size
        with Image.open(self.output_path) as img:
            self.assertEqual(img.size, (800, 450))
            self.assertEqual(img.format, "PNG")

    @unittest.skipIf(not getattr(config, "HF_TOKEN", None), "HF_TOKEN not configured; skipping real FLUX integration test")
    def test_real_flux_generation(self):
        # Act
        print("\nRunning real FLUX integration test...")
        output_file = self.test_dir / "real_flux_test.png"
        try:
            result = generate_with_huggingface("A futuristic computer network illustration, digital art, high quality", output_file)
            # Assert
            self.assertEqual(result, output_file)
            self.assertTrue(output_file.exists())
            with Image.open(output_file) as img:
                self.assertIsNotNone(img)
            print(f"\n[Real FLUX Test] Success! Image generated and saved at {output_file}")
        except Exception as e:
            self.fail(f"Real FLUX generation failed: {e}")

    @patch("blog_agent.utils.image_generator.search_images_tavily")
    @patch("blog_agent.utils.image_generator.requests.get")
    def test_fetch_web_image_success(self, mock_requests_get, mock_search_images):
        # 1. Setup mock search results
        mock_search_images.return_value = [
            {"url": "https://example.com/image1.png", "source_url": "https://example.com/source1"}
        ]
        
        # 2. Setup mock response from requests (valid dynamically generated PNG bytes)
        from io import BytesIO
        img = Image.new('RGB', (1, 1), color='red')
        buf = BytesIO()
        img.save(buf, format='PNG')
        tiny_png = buf.getvalue()
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "image/png"}
        mock_response.content = tiny_png
        mock_requests_get.return_value = mock_response
        
        # 3. Act
        from blog_agent.utils.image_generator import fetch_web_image
        result = fetch_web_image("A beautiful data visualization diagram", self.output_path)
        
        # 4. Assert
        self.assertEqual(result["image_path"], str(self.output_path))
        self.assertEqual(result["source_url"], "https://example.com/source1")
        self.assertTrue(self.output_path.exists())

if __name__ == "__main__":
    unittest.main()
