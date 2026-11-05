
```
streamlit run app.py  --server.port 8050
```

```
gcloud run deploy meal-app \
  --source . \
  --region asia-northeast1 \
  --port 8501 \
  --allow-unauthenticated \
  --set-env-vars GEMINI_API_KEY=${GEMINI_API_KEY}
```