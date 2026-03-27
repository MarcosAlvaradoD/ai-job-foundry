#!/usr/bin/env python3
"""
form_filler.py — Rellena formularios de empleo con datos del perfil (CHALAN).
Compatible con: LinkedIn Easy Apply, Indeed Quick Apply, Computrabajo, Adzuna, Glassdoor.
"""
import asyncio
import re
from typing import Optional
from playwright.async_api import Page, Locator
from core.automation.apply_profile import get_profile


async def get_field_label(field: Locator, page: Page) -> str:
    """Extrae la etiqueta de un campo de formulario."""
    label = ""
    try:
        # Intentar aria-label
        label = await field.get_attribute("aria-label") or ""
        if label:
            return label.strip()
        # Intentar placeholder
        label = await field.get_attribute("placeholder") or ""
        if label:
            return label.strip()
        # Intentar name
        label = await field.get_attribute("name") or ""
        if label:
            return label.strip()
        # Buscar <label> asociado
        field_id = await field.get_attribute("id")
        if field_id:
            lbl = page.locator(f'label[for="{field_id}"]')
            if await lbl.count() > 0:
                label = (await lbl.first.inner_text()).strip()
    except Exception:
        pass
    return label


async def fill_form_fields(page: Page, job: dict, site: str, ask_missing: bool = True) -> dict:
    """
    Detecta y rellena todos los campos de texto/select visibles en la página actual.

    Args:
        page: Playwright page
        job: dict con 'Role', 'Company', 'ApplyURL'
        site: nombre del sitio ('linkedin', 'indeed', 'computrabajo', etc.)
        ask_missing: si True, pregunta por Telegram los campos desconocidos

    Returns:
        dict con {'filled': [...], 'skipped': [...], 'asked': [...]}
    """
    profile = get_profile()
    job_title = job.get("Role", "?")
    company = job.get("Company", "?")

    result = {"filled": [], "skipped": [], "asked": []}

    # ── Text inputs y textareas ──────────────────────────────────────────────
    text_fields = page.locator('input[type="text"], input[type="tel"], input[type="email"], input[type="number"], textarea')
    count = await text_fields.count()

    for i in range(count):
        field = text_fields.nth(i)
        try:
            if not await field.is_visible():
                continue
            if await field.is_disabled():
                continue

            current_val = await field.input_value()
            if current_val.strip():
                continue  # Ya tiene valor, no sobreescribir

            label = await get_field_label(field, page)
            if not label:
                continue

            field_name = profile.match_field(label)

            if field_name:
                value = profile.get(field_name)
                if value:
                    await field.fill(str(value))
                    await asyncio.sleep(0.3)
                    result["filled"].append({"label": label, "field": field_name, "value": value})
                elif ask_missing:
                    qid = profile.ask_question(field_name, label, job_title, company, site)
                    result["asked"].append({"label": label, "field": field_name, "question_id": qid})
                    # Esperar respuesta (hasta 2 min)
                    if qid:
                        answer = profile.wait_for_answer(qid, timeout=120)
                        if answer:
                            await field.fill(str(answer))
                            result["filled"].append({"label": label, "field": field_name, "value": answer})
            else:
                result["skipped"].append({"label": label, "reason": "no match"})
        except Exception as e:
            result["skipped"].append({"label": "?", "reason": str(e)})

    # ── Selects (dropdowns) ───────────────────────────────────────────────────
    selects = page.locator("select")
    sel_count = await selects.count()

    for i in range(sel_count):
        sel = selects.nth(i)
        try:
            if not await sel.is_visible():
                continue
            label = await get_field_label(sel, page)
            field_name = profile.match_field(label)
            if field_name:
                value = profile.get(field_name)
                if value:
                    # Intentar seleccionar por label exacto o parcial
                    options = await sel.locator("option").all_text_contents()
                    best = next((o for o in options if value.lower() in o.lower()), None)
                    if best:
                        await sel.select_option(label=best)
                        result["filled"].append({"label": label, "field": field_name, "value": best})
        except Exception:
            pass

    return result


async def handle_linkedin_easy_apply_steps(page: Page, job: dict) -> bool:
    """
    Maneja el formulario multi-paso de LinkedIn Easy Apply.
    Retorna True si llegó al submit final.
    """
    profile = get_profile()
    max_steps = 10

    for step in range(max_steps):
        await asyncio.sleep(1.5)

        # Rellenar campos del paso actual
        await fill_form_fields(page, job, "linkedin", ask_missing=True)

        # Buscar botón Next / Review / Submit
        for btn_text in ["Submit application", "Review", "Next", "Continue"]:
            btn = page.locator(f'button:has-text("{btn_text}")').first
            if await btn.is_visible():
                if "Submit" in btn_text:
                    await btn.click()
                    return True
                await btn.click()
                break
        else:
            # No encontró ningún botón conocido
            break

    return False
