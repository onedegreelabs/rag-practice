### 환경 설정

- Python 버전

```bash
python=3.10.14
```

- 라이브러리 설치

```bash
pip install -r requirements.txt
```

- 환경변수 (`.env` 파일 생성 필요)

```bash
OPENAI_API_KEY=???
OPENAI_EMBEDDING_MODEL=text-embedding-ada-002
OPENAI_CHAT_MODEL=gpt-4o-mini

PINECONE_API_KEY=???
PINECONE_INDEX_NAME=glimpse
PINECONE_NAMESPACE=ns1
```

### 실행

- Retreival 모드

```bash
python main.py          # retreival 모드
```

- DB sync 모드

```bash
python main.py --sync   # DB sync 모드
```

### Profile 스키마

스키마 고정된 것은 아님.

```json
{
    "id": number,
    "name": string,
    "age": number,
    "profession": string,
    "interests": array<string>
  },
```
