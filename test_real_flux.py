import sys
import os
from pathlib import Path

# Add project root to python path
sys.path.append(str(Path(__file__).resolve().parent))

from blog_agent import config
from blog_agent.utils.huggingface_client import generate_with_huggingface

def main():
    print("=" * 60)
    print("HUGGING FACE FLUX IMAGE GENERATOR TEST SCRIPT")
    print("=" * 60)

    # 1. Check token configuration
    token = config.HF_TOKEN
    if not token:
        print("[ERROR] HF_TOKEN is not configured in your environment or .env file.")
        print("Please add the following to your d:\\Fxis.ai\\FX_LangGraph\\.env file:")
        print("HF_TOKEN=your_huggingface_inference_api_token_here")
        print("\nYou can get a free token from https://huggingface.co/settings/tokens")
        sys.exit(1)

    print(f"[INFO] Using Hugging Face token: {token[:4]}...{token[-4:] if len(token) > 8 else ''}")

    # 2. Setup prompt and output path
    prompt = """A minimalist flat vector flowchart of a cloud platform, top-to-bottom layout, solid dark blue background. Four clean light-grey rectangular nodes connected by single straight white downward arrows.
The first node contains only the text "User Request".
The second node contains only the text "LangChain".
The third node contains only the text "LangSmith".
The fourth node contains only the text "Dashboard".
All text is perfectly spelled, sharp, clean sans-serif font. Minimalist line icons next to nodes. Flat design."""
    output_path = Path(__file__).resolve().parent / "blog_agent" / "output" / "test_flux_image.png"

    print(f"[INFO] Prompt: '{prompt}'")
    print(f"[INFO] Output Path: {output_path}")
    print("[INFO] Attempting to generate image using FLUX model...")

    try:
        # 3. Generate image
        saved_path = generate_with_huggingface(prompt, output_path)
        print("=" * 60)
        print(f"[SUCCESS] Image successfully generated and saved!")
        print(f"File location: {saved_path}")
        print("=" * 60)
    except Exception as e:
        print("=" * 60)
        print(f"[FAILURE] Failed to generate image via Hugging Face: {e}")
        print("=" * 60)
        sys.exit(1)

if __name__ == "__main__":
    main()
