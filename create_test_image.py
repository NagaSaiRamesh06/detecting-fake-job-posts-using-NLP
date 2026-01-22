from PIL import Image, ImageDraw, ImageFont
import os

def create_test_image():
    # Create white image
    img = Image.new('RGB', (800, 600), color=(255, 255, 255))
    d = ImageDraw.Draw(img)
    
    # Text content designed to trigger "Fake" detection (keywords)
    text = """
    URGENT HIRING: Data Entry Clerk
    
    No experience required. 
    Immediate start available.
    
    Earn $50 per hour. Weekly pay.
    Work from the comfort of your home.
    
    Contact us via Telegram for details.
    """
    
    try:
        # Try to use Arial font
        font = ImageFont.truetype("arial.ttf", 32)
    except IOError:
        # Fallback to default if arial not found
        font = ImageFont.load_default()
        print("Using default font")

    # Draw text
    d.text((50, 50), text, fill=(0, 0, 0), font=font)
    
    # Save
    output_path = os.path.abspath("test_ocr_job.png")
    img.save(output_path)
    print(f"Test image created at: {output_path}")

if __name__ == "__main__":
    create_test_image()
