### Environment Setup

- Python Version

```bash
python=3.10.14
```

- Installing Dependencies

```bash
pip install -r requirements.txt
```

- Environment Variables (Requires a `.env` file)

```bash
OPENAI_API_KEY=???
OPENAI_EMBEDDING_MODEL=text-embedding-ada-002
OPENAI_CHAT_MODEL=gpt-4o-mini

PINECONE_API_KEY=???
PINECONE_INDEX_NAME=glimpse
PINECONE_NAMESPACE=ns1
```

### Execution

- Retrieval Mode

```bash
python main.py          # retreival mode
```

- DB Sync Mode

```bash
python main.py --sync   # DB sync mode
```

### Profile Schema

The schema is not fixed.

```json
{
    "id": number,
    "name": string,
    "age": number,
    "profession": string,
    "interests": array<string>
  },
```
