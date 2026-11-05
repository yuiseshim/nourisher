import os
import json
from io import BytesIO

import streamlit as st
from PIL import Image
from dotenv import load_dotenv
from google import genai
from google.genai import types


load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
  st.error("GEMINI_API_KEY が設定されていません. .env を確認してください. ")
  st.stop()

client = genai.Client(api_key=API_KEY)


PROMPT = """
あなたは食事管理アプリの画像解析エンジンです. 
入力された食事写真を解析し, 以下のJSON形式だけで返してください. 

推定値には不確実性があるため, confidenceも付けてください. 
カロリーやPFCは概算で構いません. 

{
  "meal_name": "料理名",
  "items": [
    {
      "name": "食品名",
      "estimated_amount": "推定量",
      "calories_kcal": 0,
      "protein_g": 0,
      "fat_g": 0,
      "carbs_g": 0,
      "confidence": 0.0
    }
  ],
  "total": {
    "calories_kcal": 0,
    "protein_g": 0,
    "fat_g": 0,
    "carbs_g": 0
  },
  "notes": "補足"
}
"""


def analyze_meal(image: Image.Image) -> dict:
  response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=[
      PROMPT,
      image,
    ],
    config=types.GenerateContentConfig(
      response_mime_type="application/json"
    ),
  )

  try:
    return json.loads(response.text)
  except json.JSONDecodeError:
    return {
      "error": "JSONとして解析できませんでした",
      "raw_response": response.text,
    }


st.set_page_config(
  page_title="食事ログAI",
  page_icon="🍽️",
  layout="wide",
)

st.title("🍽️ 食事ログAI")
st.caption("食事写真をアップロードすると, Geminiが料理・カロリー・PFCを推定します. ")

uploaded_file = st.file_uploader(
  "食事写真をアップロードしてください",
  type=["jpg", "jpeg", "png", "webp"],
)

if uploaded_file:
  image = Image.open(BytesIO(uploaded_file.read()))

  col1, col2 = st.columns([1, 1])

  with col1:
    st.subheader("アップロード画像")
    st.image(image, use_container_width=True)

  with col2:
    st.subheader("解析")

    if st.button("Geminiで解析する", type="primary"):
      with st.spinner("解析中..."):
        result = analyze_meal(image)
        st.session_state["analysis_result"] = result

    if "analysis_result" in st.session_state:
      result = st.session_state["analysis_result"]

      st.subheader("Gemini推定結果")
      st.json(result)

      if "total" in result:
        total = result["total"]

        st.subheader("ユーザー補正")

        meal_name = st.text_input(
          "料理名",
          value=result.get("meal_name", ""),
        )

        calories = st.number_input(
          "カロリー kcal",
          value=float(total.get("calories_kcal", 0)),
          step=10.0,
        )

        protein = st.number_input(
          "たんぱく質 g",
          value=float(total.get("protein_g", 0)),
          step=1.0,
        )

        fat = st.number_input(
          "脂質 g",
          value=float(total.get("fat_g", 0)),
          step=1.0,
        )

        carbs = st.number_input(
          "炭水化物 g",
          value=float(total.get("carbs_g", 0)),
          step=1.0,
        )

        memo = st.text_area(
          "メモ",
          value=result.get("notes", ""),
        )

        corrected = {
          "meal_name": meal_name,
          "calories_kcal": calories,
          "protein_g": protein,
          "fat_g": fat,
          "carbs_g": carbs,
          "memo": memo,
        }

        st.subheader("保存予定データ")
        st.json(corrected)

        if st.button("この内容で保存する"):
          st.success("保存しました. ※このサンプルではDB保存は未実装です. ")