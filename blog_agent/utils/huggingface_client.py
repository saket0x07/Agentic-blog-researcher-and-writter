from pathlib import Path
import logging

from huggingface_hub import InferenceClient
from PIL import Image
from blog_agent import config

logger = logging.getLogger(__name__)
HF_MODEL="black-forest-labs/FLUX.1-schnell"
# HF_MODEL="stabilityai/stable-diffusion-3.5-medium"
def generate_with_huggingface(prompt: str, output_path: Path) -> Path:
    """ 
    Generate sn image using hugging face inference  API.

    Args: 
        prompt: IMAGE GENERATION PROMPT
        output_path: Path where image will be saved.

    Returns: 
        Path to saved image
    
    Raises:
        Exception: if image cannot be generated and Failed.
    """

    if not config.HF_TOKEN:
        raise ValueError("HF_TOKEN is not configured.")
    
    logger.info("[HF] Intializing HF client..... ")

    client = InferenceClient(api_key=config.HF_TOKEN)
    logger.info("[HF] GENERATING IMAGE USONG  {HF_MODEL}")

    try:
        image = client.text_to_image(prompt=prompt,model=HF_MODEL)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        image.save(output_path)

        logger.info(f"[HF] Image saved at {output_path}")
        return output_path
    except Exception as e:
        logger.error(f"[HF] Failed to generate image via Hugging Face : {e}")
        raise e 

