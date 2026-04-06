"""
bot.py
Telegram bot que actúa como Media Buyer AI.
Recibe instrucciones en lenguaje natural y ejecuta el pipeline de Meta Ads.
"""

import asyncio
import concurrent.futures
import functools
import os
import subprocess
import sys
import tempfile
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import anthropic

load_dotenv(override=False)  # No override env vars already set (e.g. Railway)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "").strip()
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
VENV_PYTHON = sys.executable  # Uses whatever Python is running this bot (works locally and on Railway)

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)

SYSTEM_PROMPT = f"""Sos un AI Media Buyer especializado en Meta Ads. Tu trabajo es ejecutar campañas publicitarias en Meta (Facebook/Instagram) a partir de instrucciones en lenguaje natural.

## Contexto del proyecto
- Directorio: {PROJECT_DIR}
- Python ejecutable: {VENV_PYTHON}
- Credenciales en .env (ya cargadas)

## Cuentas publicitarias
- **CREMA** (default): Ad Account `1402894801163186`, Página Alpha For Men `552919854574913`
- **Stolar**: Ad Account `345055025230307` (fanpage a confirmar)
- **Shampoo**: Ad Account `495744695407533`

## Configuración estándar de adsets en [CREMA]
- bid_strategy: COST_CAP
- billing_event: IMPRESSIONS
- optimization_goal: OFFSITE_CONVERSIONS
- pixel_id: `9394963073898135`, evento: PURCHASE
- targeting: AR, 18-65, Advantage Audience ON, brand_safety RELAXED
- Status siempre PAUSED al crear

## Copy base de CREMA
- message: "Tu piel pierde colágeno cada año, a menos que hagas algo al respecto. 👇\\n\\n🇦🇷 Probá ALPHA, la primera Marca de Skin Care Masculino en Argentina.\\n\\n⭐Apoya la firmeza y elasticidad de la piel.\\n⭐Ayuda a reducir las líneas finas y las arrugas.\\n⭐Defiende contra la descomposición del colágeno y el envejecimiento.\\n\\n🔬 Respaldado por la ciencia. \\n\\nConsigue el tuyo ahora con envío sin costo y 3 cuotas sin interés"
- title: "🇦🇷 #1 Skincare para hombres en Argentina"
- description: "Poco Stock Disponible"
- link: "https://alphamencare.com.ar/productos/crema-anti-age-luci-mas-joven-eliminando-lineas-finas-y-arrugas/"
- CTA: LEARN_MORE

## Tokens
- META_ACCESS_TOKEN: user token de larga duración (60 días desde abril 2026)
- META_PAGE_ACCESS_TOKEN: page token de Alpha For Men (usar para crear creatives)

## Tu flujo cuando recibís un brief
Escribí UN SOLO script Python que haga todo de una vez:
1. Autenticarse con META_ACCESS_TOKEN del .env
2. Buscar la campaña por nombre
3. Obtener config del adset de referencia
4. Descargar todos los creativos del Drive con gdown
5. Crear los adsets y ads de una sola vez
6. Imprimir los IDs creados

**IMPORTANTE: Usá run_python UNA o DOS veces máximo. No explores paso a paso — escribí el script completo desde el principio.**

## Reglas
- Siempre creá adsets en estado PAUSED
- Si el token expiró (error 190), avisale al usuario que genere uno nuevo
- Respondé siempre en español, de forma concisa
- No hagas llamadas exploratorias previas — resolvé todo en un script

Usá la herramienta run_python para ejecutar código Python contra la API de Meta."""

TOOLS = [
    {
        "name": "run_python",
        "description": "Ejecuta código Python en el contexto del proyecto Meta Ads. Tiene acceso a facebook_business SDK, gdown, las credenciales del .env, y todos los módulos del proyecto.",
        "input_schema": {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "Código Python a ejecutar. El .env ya está cargado. Importá lo que necesites."
                }
            },
            "required": ["code"]
        }
    }
]


def execute_python(code: str) -> str:
    """Ejecuta código Python en el venv del proyecto."""
    wrapper = f"""
import sys
import os
sys.path.insert(0, '{PROJECT_DIR}')
os.chdir('{PROJECT_DIR}')

from dotenv import load_dotenv
load_dotenv(override=False)

import warnings
warnings.filterwarnings('ignore')

{code}
"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(wrapper)
        tmp_path = f.name

    try:
        result = subprocess.run(
            [VENV_PYTHON, tmp_path],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=PROJECT_DIR
        )
        output = result.stdout
        if result.stderr:
            # Filtrar warnings de urllib3
            stderr_lines = [l for l in result.stderr.split('\n')
                          if 'NotOpenSSLWarning' not in l and 'WARNING:root' not in l and l.strip()]
            if stderr_lines:
                output += "\nSTDERR:\n" + '\n'.join(stderr_lines)
        return output or "(sin output)"
    except subprocess.TimeoutExpired:
        return "ERROR: Timeout después de 120 segundos"
    except Exception as e:
        return f"ERROR: {e}"
    finally:
        os.unlink(tmp_path)


async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    import httpx, json
    key = os.getenv("ANTHROPIC_API_KEY", "")
    try:
        r = httpx.post(
            "https://api.anthropic.com/v1/messages",
            headers={"x-api-key": key, "anthropic-version": "2023-06-01", "content-type": "application/json"},
            json={"model": "claude-haiku-4-5-20251001", "max_tokens": 5, "messages": [{"role": "user", "content": "hi"}]},
            timeout=30
        )
        await update.message.reply_text(f"✅ POST directo: {r.status_code}\n{r.text[:200]}")
    except Exception as e:
        await update.message.reply_text(f"❌ POST falló: {type(e).__name__}: {str(e)[:200]}")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    await update.message.reply_text("⏳ Procesando...")

    messages = [{"role": "user", "content": user_message}]

    try:
        max_steps = 20
        steps = 0
        while steps < max_steps:
            # Retry hasta 3 veces si hay connection error
            response = None
            for attempt in range(3):
                try:
                    loop = asyncio.get_event_loop()
                    response = await loop.run_in_executor(
                        executor,
                        functools.partial(
                            client.messages.create,
                            model="claude-haiku-4-5-20251001",
                            max_tokens=4096,
                            system=[{
                                "type": "text",
                                "text": SYSTEM_PROMPT,
                                "cache_control": {"type": "ephemeral"}
                            }],
                            tools=TOOLS,
                            messages=messages
                        )
                    )
                    break
                except Exception as conn_err:
                    if attempt == 2:
                        raise conn_err
                    await asyncio.sleep(3)
            if response is None:
                break

            if response.stop_reason == "end_turn":
                text = next((b.text for b in response.content if hasattr(b, 'text')), "✅ Listo.")
                await update.message.reply_text(text)
                break

            elif response.stop_reason == "tool_use":
                tool_block = next(b for b in response.content if b.type == "tool_use")

                if tool_block.name == "run_python":
                    code = tool_block.input["code"]
                    steps += 1
                    await update.message.reply_text(f"🔧 Ejecutando... ({steps}/{max_steps})")
                    result = execute_python(code)
                    # Truncar resultado si es muy largo para no exceder límite de tokens
                    if len(result) > 4000:
                        result = result[:4000] + "\n...[truncado]"

                    messages.append({"role": "assistant", "content": response.content})
                    messages.append({
                        "role": "user",
                        "content": [{
                            "type": "tool_result",
                            "tool_use_id": tool_block.id,
                            "content": result
                        }]
                    })
            else:
                await update.message.reply_text("⚠️ Respuesta inesperada del modelo.")
                break
        else:
            await update.message.reply_text("⚠️ Se alcanzó el límite de pasos. Intentá con una tarea más simple.")

    except Exception as e:
        await update.message.reply_text(f"❌ Error tipo: {type(e).__name__}\nDetalle: {str(e)[:300]}")


def main():
    print("🤖 AI Media Buyer Bot iniciando...")
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("ping", ping))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("✅ Bot corriendo. Esperando mensajes en Telegram...")
    app.run_polling(drop_pending_updates=True, allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
