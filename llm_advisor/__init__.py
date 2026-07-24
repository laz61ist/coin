"""F4 LLM karar destek katmanı — SHADOW MODE.

Tasarım kuralı (docs/03 §2 + kaynakça §5 sentezi): bu katmanın EMİR YETKİSİ
YOKTUR. Çıktısı jsonl log'a yazılır; F4 kabulünde katkısı backtest'le ölçülür,
ölçülmeden hiçbir girişi engellemez. Bu tercih değil, literatür bulgusudur
(FINSABER, Profit Mirage).
"""
