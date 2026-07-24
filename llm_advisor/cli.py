"""LLM advisor CLI (F4, shadow mode).

Kullanım:
  python3 -m llm_advisor.cli veto --input sinyal.json          # gerçek çağrı (ANTHROPIC_API_KEY gerekir)
  python3 -m llm_advisor.cli veto --input sinyal.json --mock   # ağsız duman testi
  python3 -m llm_advisor.cli brief --input durum.json

Girdi formatı için: llm_advisor/examples/sinyal_ornek.json
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

from llm_advisor.advisor import run_brief, run_veto


def _load(path: str) -> dict:
    if path == "-":
        return json.load(sys.stdin)
    return json.loads(pathlib.Path(path).read_text(encoding="utf-8"))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("mode", choices=["veto", "brief"])
    ap.add_argument("--input", required=True, help="JSON dosyası veya '-' (stdin)")
    ap.add_argument("--model", default=None)
    ap.add_argument("--mock", action="store_true", help="LLM çağrısı yapmadan test et")
    args = ap.parse_args()

    data = _load(args.input)

    try:
        if args.mode == "veto":
            result = run_veto(
                signal=data.get("signal", data),
                headlines=data.get("headlines", []),
                model=args.model,
                mock=args.mock,
            )
            print(json.dumps(result, ensure_ascii=False, indent=1))
        else:
            print(run_brief(data, model=args.model, mock=args.mock))
        return 0
    except Exception as exc:  # tip zinciri: anthropic kuruluysa özelleştir
        try:
            import anthropic

            if isinstance(exc, anthropic.RateLimitError):
                print("HATA: rate limit — bekleyip tekrar dene", file=sys.stderr)
                return 2
            if isinstance(exc, anthropic.AuthenticationError):
                print("HATA: ANTHROPIC_API_KEY geçersiz/eksik (.env kontrol et)", file=sys.stderr)
                return 3
            if isinstance(exc, anthropic.APIStatusError):
                print(f"HATA: API {exc.status_code}: {exc.message}", file=sys.stderr)
                return 4
            if isinstance(exc, anthropic.APIConnectionError):
                print("HATA: ağ bağlantısı kurulamadı", file=sys.stderr)
                return 5
        except ImportError:
            pass
        raise


if __name__ == "__main__":
    sys.exit(main())
