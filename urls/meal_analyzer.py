import base64
import json
from io import BytesIO

from google.genai import types
from PIL import Image

from prompts.meal_analysis_prompt import MEAL_ANALYSIS_PROMPT


def analyze_meal(image: Image.Image, provider: str, client) -> dict:
  if provider == "gemini":
    response = client.models.generate_content(
      model="gemini-2.5-flash",
      contents=[
        MEAL_ANALYSIS_PROMPT,
        image,
      ],
      config=types.GenerateContentConfig(
        response_mime_type="application/json"
      ),
    )
    response_text = response.text
  else:
    image_buffer = BytesIO()
    image.convert("RGB").save(image_buffer, format="JPEG")
    image_data = base64.b64encode(image_buffer.getvalue()).decode("ascii")
    response = client.chat.completions.create(
      model="gpt-4o-mini",
      messages=[
        {
          "role": "user",
          "content": [
            {"type": "text", "text": MEAL_ANALYSIS_PROMPT},
            {
              "type": "image_url",
              "image_url": {
                "url": f"data:image/jpeg;base64,{image_data}",
              },
            },
          ],
        },
      ],
      response_format={"type": "json_object"},
    )
    response_text = response.choices[0].message.content

  try:
    return json.loads(response_text)
  except json.JSONDecodeError:
    return {
      "error": "JSONとして解析できませんでした",
      "raw_response": response_text,
    }
