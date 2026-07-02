import os
import re
from pathlib import Path
from typing import List
from pydantic import BaseModel, Field
from blog_agent.graph.state import OverallState
from blog_agent.graph.llm import get_llm
from blog_agent.utils.image_generator import generate_image, fetch_web_image
from blog_agent import config

class ImagePlanItem(BaseModel):
    section_id: str = Field(description="The ID of the section (e.g., 'sec_1', 'sec_2') where the image should be placed.")
    prompt: str = Field(description="A descriptive, high-quality prompt for Google's Imagen model, focusing on modern vector art, system architecture, tech illustrations, or data flows related to the section's contents.")
    caption: str = Field(description="A brief caption to display under the image.")

class ImagePlan(BaseModel):
    images: List[ImagePlanItem] = Field(description="A list of up to 3 image plans. Do not plan more than 3 images.")

def reducer_node(state: OverallState):
    """
    Reducer Node.
    1. Stitches sections together in correct sequence.
    2. Plans optimal image locations and prompts.
    3. Calls Gemini image generation, saves files locally.
    4. Integrates image paths and writes final markdown.
    """
    plan = state["plan"]
    drafts = state["section_drafts"]
    llm = get_llm()
    
    print(f"[Reducer Node] Stitching {len(drafts)} sections...")
    
    # 1. Stitching in the correct order defined in the plan tasks
    task_order = [t["id"] for t in plan["tasks"]]
    drafts_by_id = {d["task_id"]: d for d in drafts}
    
    stitched_sections = []
    for task_id in task_order:
        if task_id in drafts_by_id:
            stitched_sections.append(drafts_by_id[task_id])
        else:
            print(f"[Reducer Node] Warning: draft for {task_id} not found.")
            
    # Assemble raw content for review
    raw_markdown_list = []
    for idx, sec in enumerate(stitched_sections):
        raw_markdown_list.append(sec["content"])
    
    raw_blog_text = "\n\n".join(raw_markdown_list)
    
    # 2. Image Planning
    print("[Reducer Node] Planning visual placements...")
    
    image_choices = state.get("image_choices")
    if image_choices:
        print(f"[Reducer Node] Using user-provided image choices (Count: {len(image_choices)})")
        class PlannedImageChoice(BaseModel):
            section_id: str
            prompt: str
            caption: str
            mode: str = "generate"
        planned_images = [PlannedImageChoice(**choice) for choice in image_choices]
    else:
        structured_llm = llm.with_structured_output(ImagePlan)
        system_prompt = (
            "You are a technical editor. Your job is to review a compiled technical blog post "
            "and determine up to 3 ideal sections to embed visuals. You will output a list of image items, "
            "each specifying the section_id where the visual fits best, a detailed Imagen 3 generation prompt "
            "describing the style (use professional, clean tech vector illustrations, avoid realistic photos), "
            "and a caption for the graphic."
        )
        user_prompt = (
            f"Blog Title: {plan['title']}\n"
            f"Blog Structure (Tasks):\n"
            f"{[{'id': t['id'], 'title': t['title'], 'goal': t['goal']} for t in plan['tasks']]}\n\n"
            f"Stitched Content Preview:\n{raw_blog_text[:2000]}..."
        )
        try:
            image_plan = structured_llm.invoke([
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ])
            planned_images = image_plan.images
        except Exception as e:
            print(f"[Reducer Node] Error during image planning: {e}. Proceeding without images.")
            planned_images = []
        
    print(f"[Reducer Node] Planned {len(planned_images)} images.")
    
    #  file naming
    title_slug = re.sub(r'[^a-zA-Z0-9]', '_', plan["title"].lower())[:30]
    
    #  Generate Images and reconstruct markdown
    local_images = []
    local_image_prompts = []
    blog_final_markdown = ""
    
    # final markdown section-by-section
    for sec in stitched_sections:
        sec_id = sec["task_id"]
        sec_content = sec["content"]
        
        # Append the section draft
        blog_final_markdown += sec_content + "\n\n"
        
        # Check if there is an image planned for this section
        for i, img_item in enumerate(planned_images):
            if img_item.section_id == sec_id:
                # Generate unique filename
                image_filename = f"{title_slug}_img_{sec_id}_{i}.png"
                image_path = config.IMAGE_DIR / image_filename
                
                # Clean prompt of any weird control/non-breaking space characters
                clean_prompt = img_item.prompt.replace('\xa0', ' ').replace('\u200b', '').replace('\r', '').strip()
                
                mode = getattr(img_item, "mode", "generate")
                img_meta = {
                    "section_id": img_item.section_id,
                    "prompt": clean_prompt,
                    "caption": img_item.caption,
                    "image_path": str(image_path),
                    "success": False,
                    "mode": mode
                }
                
                try:
                    if mode == "fetch":
                        # Fetch web image
                        print(f"[Reducer Node] Fetching web image for section {sec_id}...")
                        fetch_res = fetch_web_image(clean_prompt, image_path)
                        saved_path = fetch_res["image_path"]
                        source_url = fetch_res["source_url"]
                        
                        img_meta["image_path"] = str(saved_path)
                        img_meta["success"] = True
                        img_meta["source_url"] = source_url
                        
                        relative_path = f"output/images/{image_filename}"
                        local_images.append(str(saved_path))
                        
                        # Add to markdown with original source page link
                        image_markdown = f"\n![{img_item.caption}]({relative_path})\n*Figure: {img_item.caption}. [Source Link]({source_url})*\n\n"
                    else:
                        # Run normal image generator fallbacks
                        saved_path = generate_image(clean_prompt, image_path)
                        img_meta["image_path"] = str(saved_path)
                        img_meta["success"] = True
                        
                        relative_path = f"output/images/{image_filename}"
                        local_images.append(str(saved_path))
                        
                        # Add to markdown
                        image_markdown = f"\n![{img_item.caption}]({relative_path})\n*Figure: {img_item.caption}*\n\n"
                    
                    blog_final_markdown += image_markdown
                    print(f"[Reducer Node] Embedded image for section {sec_id} (mode={mode}): {relative_path}")
                except Exception as ex:
                    print(f"[Reducer Node] Failed to process image for {sec_id} (mode={mode}): {ex}")
                
                local_image_prompts.append(img_meta)
                
                # Sleep briefly to avoid rate limits on sequential image generations
                import time
                time.sleep(3)
                    
    # Write final markdown to output
    final_blog_path = config.OUTPUT_DIR / f"{title_slug}_blog.md"
    try:
        # Prepend main title to the blog if it doesn't already have one
        if not blog_final_markdown.strip().startswith("# "):
            title_header = f"# {plan['title']}\n\n*Target Audience: {plan['audience']} | Tone: {plan['tone']}*\n\n---\n\n"
            blog_final_markdown = title_header + blog_final_markdown
            
        with open(final_blog_path, "w", encoding="utf-8") as f:
            f.write(blog_final_markdown)
        print(f"[Reducer Node] Successfully saved final blog to: {final_blog_path}")
    except Exception as e:
        print(f"[Reducer Node] Error saving final blog: {e}")
        
    return {
        "final_blog": blog_final_markdown,
        "images": local_images,
        "image_prompts": local_image_prompts
    }
