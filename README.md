
```
streamlit run app.py --server.port 8050
```

Gemini APIを使用する場合は `.env` に `GEMINI_API_KEY` を設定して起動します（省略時のデフォルト）。

```bash
./run.sh --provider gemini
```

OpenAI APIを使用する場合は `.env` に `OPENAI_API_KEY` を設定し、起動引数でプロバイダーを指定します。

```bash
./run.sh --provider openai
```

`run.sh` を使わずに起動する場合:

```bash
streamlit run app.py --server.port 8050 -- --provider openai
```

```
gcloud run deploy meal-app \
  --source . \
  --region asia-northeast1 \
  --port 8501 \
  --allow-unauthenticated \
  --set-env-vars GEMINI_API_KEY=${GEMINI_API_KEY}
```