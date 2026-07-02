import logging
import requests
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

from blog_agent.utils.gemini_client import generate_blog_image
from blog_agent.utils.huggingface_client import generate_with_huggingface
from blog_agent.utils.tavily_client import search_images_tavily

logger = logging.getLogger(__name__)

def generate_with_pillow(prompt: str, output_path: Path) -> Path:
    """
    Fallback: Create a visually appealing placeholder image using Pillow.
    """
    logger.info(f"Generating Pillow placeholder for prompt: {prompt}")
    try:
        # Create a nice 16:9 placeholder (800x450) with a modern slate-blue background
        img = Image.new('RGB', (800, 450), color=(30, 41, 59)) # Slate 800
        d = ImageDraw.Draw(img)
        
        # Draw a subtle border accent
        d.rectangle([(10, 10), (790, 440)], outline=(71, 85, 105), width=3) # Slate 600
        
        # Load a default font or standard system font if available
        font = None
        title_font = None
        for font_name in ["arial.ttf", "calibri.ttf", "DejaVuSans.ttf"]:
            try:
                font = ImageFont.truetype(font_name, 16)
                title_font = ImageFont.truetype(font_name, 24)
                break
            except Exception:
                continue
        
        if font is None:
            font = ImageFont.load_default()
            title_font = ImageFont.load_default()
            
        # Draw a stylized card header
        d.text((40, 40), "FX_LangGraph Blog Agent", fill=(96, 165, 250), font=title_font) # Light Blue 400
        
        # Wrap prompt text if it's too long
        max_width = 720
        words = prompt.split()
        lines = []
        current_line = []
        for word in words:
            test_line = " ".join(current_line + [word])
            estimated_width = len(test_line) * 8
            if estimated_width < max_width:
                current_line.append(word)
            else:
                lines.append(" ".join(current_line))
                current_line = [word]
        if current_line:
            lines.append(" ".join(current_line))
        
        wrapped_prompt = "\n".join(lines[:6]) # Max 6 lines
        if len(lines) > 6:
            wrapped_prompt += "\n..."
            
        # Draw Prompt Details
        d.text((40, 120), "IMAGE GENERATION PROMPT:", fill=(148, 163, 184), font=font) # Slate 400
        d.text((40, 150), wrapped_prompt, fill=(241, 245, 249), font=font) # Slate 100
        
        # Draw fallback status badge in bottom right
        d.rectangle([(550, 390), (760, 420)], fill=(239, 68, 68)) # Red 500
        d.text((565, 395), "PILLOW FALLBACK", fill=(255, 255, 255), font=font)
        
        # Ensure target directory exists and save
        output_path.parent.mkdir(parents=True, exist_ok=True)
        img.save(output_path)
        logger.info(f"Successfully created Pillow placeholder image at {output_path}")
        return output_path
    except Exception as e:
        logger.error(f"Failed to create Pillow placeholder: {e}")
        raise e

def generate_image(prompt: str, output_path: Path) -> Path:
    """
    Generate an image by trying Gemini Imagen first.
    If Gemini fails (raises exception or returns None/non-existent path), fallback to Hugging Face FLUX.
    If Hugging Face fails, fallback to Pillow placeholder generation.
    """
    # 1. Try Gemini
    try:
        logger.info("Attempting image generation using Gemini...")
        result = generate_blog_image(prompt, output_path)
        if result and Path(result).exists():
            return Path(result)
        logger.warning("Gemini did not return a valid image path. Trying Hugging Face fallback...")
    except Exception as e:
        logger.warning(f"Gemini image generation failed: {e}. Trying Hugging Face fallback...")

    # 2. Try Hugging Face
    try:
        logger.info("Attempting image generation using Hugging Face...")
        result = generate_with_huggingface(prompt, output_path)
        if result and Path(result).exists():
            return Path(result)
        logger.warning("Hugging Face did not return a valid image path. Trying Pillow fallback...")
    except Exception as e:
        logger.warning(f"Hugging Face image generation failed: {e}. Trying Pillow fallback...")

    # 3. Fallback to Pillow
    try:
        logger.info("Attempting image generation using Pillow placeholder...")
        return generate_with_pillow(prompt, output_path)
    except Exception as e:
        logger.error(f"All image generation methods failed: {e}")
        raise e

def fetch_web_image(prompt: str, output_path: Path) -> dict:
    """
    Search for a matching image on the web using Tavily image search,
    download the first successfully fetched image, and save it locally.
    
    Returns:
        dict with keys: 'image_path' (str) and 'source_url' (str for credit).
    Raises:
        Exception: if search returns no images or download fails.
    """
    logger.info(f"Searching web for image matching prompt: {prompt}")
    # Run image search
    results = search_images_tavily(prompt, max_results=5)
    if not results:
        raise ValueError(f"No web images found for prompt: '{prompt}'")
    
    # Try downloading the retrieved images in order of relevance
    last_error = None
    for res in results:
        img_url = res.get("url")
        source_url = res.get("source_url")
        if not img_url:
            continue
        
        try:
            logger.info(f"Attempting to download image: {img_url}")
            response = requests.get(
                img_url, 
                timeout=10, 
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
            )
            if response.status_code == 200:
                content_type = response.headers.get("Content-Type", "")
                if "image" in content_type or any(img_url.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.webp', '.gif']):
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(output_path, "wb") as f:
                        f.write(response.content)
                    
                    # Verify it's a valid image that PIL can open
                    with Image.open(output_path) as test_img:
                        test_img.verify()
                        
                    logger.info(f"Successfully downloaded and verified web image from {img_url}")
                    return {
                        "image_path": str(output_path),
                        "source_url": source_url
                    }
                else:
                    logger.warning(f"Downloaded content from {img_url} is not a valid image content type: {content_type}")
            else:
                logger.warning(f"Failed to download image from {img_url} (HTTP status code {response.status_code})")
        except Exception as e:
            logger.warning(f"Failed to download or verify image from {img_url}: {e}")
            last_error = e
            
    raise last_error or RuntimeError(f"Failed to download any of the {len(results)} found web images for prompt: '{prompt}'")

    
    
