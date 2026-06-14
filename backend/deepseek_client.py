import httpx

from config import get_settings

_settings = get_settings()


def chat(prompt: str, *, temperature: float = 0.4, timeout: float = 60.0) -> str:
    if not _settings.deepseek_api_key:
        raise RuntimeError("DEEPSEEK_API_KEY belum di-set di .env")

    url = f"{_settings.deepseek_base_url.rstrip('/')}/chat/completions"
    headers = {
        "Authorization": f"Bearer {_settings.deepseek_api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": _settings.deepseek_model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "stream": False,
    }
    with httpx.Client(timeout=timeout) as client:
        r = client.post(url, headers=headers, json=payload)
        r.raise_for_status()
        data = r.json()
    return data["choices"][0]["message"]["content"].strip()
