from blog_agent.graph.nodes import research
from blog_agent.graph.nodes import research
import os
import logging
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from blog_agent import config
import io

logger = logging.getLogger(__name__)

def generate_blog_image(prompt: str, output_path: Path) -> Path:
    """
    Generate an image using Google GenAI (Imagen 3) and save it to output_path.
    If API key is missing or generation fails, falls back to Pillow placeholder generation.
    """
    api_key = config.GEMINI_API_KEY
    
    # Try calling Google GenAI SDK
    if api_key:
        try:
            from google import genai
            from google.genai import types
            
            logger.info(f"Generating image via Gemini Imagen for prompt: {prompt}")
            client = genai.Client(api_key=api_key)
            # for model in client.models.list():
            #     print(model.name)
            
            # Using Imagen 3.0 model
            result = client.models.generate_content(
                model='gemini-2.5-flash-image',
                contents=prompt,
                # config=types.GenerateImagesConfig(
                #     number_of_images=1,
                #     output_mime_type="image/png",
                #     aspect_ratio="16:9",
                # )
            )
            print(result)
            print("="*80)
            print(result.candidates[0])
            print(result.candidates[0].content.parts)
            print("="*80)
            
            saved = False
            for part in result.candidates[0].content.parts:
                if hasattr(part, 'inline_data') and part.inline_data is not None:
                    image = Image.open(io.BytesIO(part.inline_data.data))
                    image.save(output_path)
                    logger.info(f"Successfully saved Gemini generated image to {output_path}")
                    saved = True
                    break
            if saved:    
                return output_path
            
            # for generated_image in result.generated_images:
            #     # Save the image bytes to path
            #     import io
            #     image = Image.open(io.BytesIO(generated_image.image.image_bytes))
            #     image.save(output_path)
            #     logger.info(f"Successfully saved Gemini generated image to {output_path}")
            #     return output_path
                
        except Exception as e:
            logger.error(f"Failed to generate image via Gemini API: {e}. Falling back to Pillow.")
    else:
        logger.warning("GEMINI_API_KEY not found. Creating Pillow placeholder image.")

    # # Fallback: Create placeholder image using Pillow
    # try:
    #     # Create a nice 16:9 placeholder (800x450)
    #     img = Image.new('RGB', (800, 450), color=(73, 109, 137))
    #     d = ImageDraw.Draw(img)
        
    #     # Write text
    #     text = f"Visual Enrichment Placeholder\nPrompt: {prompt[:60]}..."
    #     # Draw text at center
    #     d.text((40, 200), text, fill=(255, 255, 255))
        
    #     # Save placeholder
    #     output_path.parent.mkdir(parents=True, exist_ok=True)
    #     img.save(output_path)
    #     logger.info(f"Successfully created Pillow placeholder image at {output_path}")
    #     return output_path
    # except Exception as e:
    #     logger.error(f"Failed to create Pillow placeholder: {e}")
    #     raise e
