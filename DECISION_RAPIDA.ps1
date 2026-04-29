Write-Host "`n" -NoNewline
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  ⚡ DECISIÓN RÁPIDA - ¿QUÉ HACER AHORA?" -ForegroundColor White
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "🎯 SITUACIÓN ACTUAL:" -ForegroundColor Yellow
Write-Host "  ✅ Llama-3-Groq-70B está funcionando" -ForegroundColor Green
Write-Host "  ⚠️  Pero es LENTO (100 seg/job → 5 horas total)" -ForegroundColor Yellow
Write-Host "  ✅ Fixes aplicados (timeout + temperatura)" -ForegroundColor Green
Write-Host "  ⏱️  Nuevo tiempo esperado: 40-50 seg/job (2 horas)" -ForegroundColor Cyan
Write-Host ""

Write-Host "📊 TRES OPCIONES:" -ForegroundColor Cyan
Write-Host ""

Write-Host "OPCIÓN A: Ejecutar Pipeline con Llama-3-Groq AHORA" -ForegroundColor White
Write-Host "  ⏱️  Tiempo: 2 horas (182 jobs)" -ForegroundColor Gray
Write-Host "  ✅ Accuracy: 95%" -ForegroundColor Green
Write-Host "  ✅ No hallucinations" -ForegroundColor Green
Write-Host "  💡 Recomendado si: No tienes prisa, quieres máxima calidad" -ForegroundColor Gray
Write-Host ""
Write-Host "  Comando:" -ForegroundColor Yellow
Write-Host "    .\START_CONTROL_CENTER.bat" -ForegroundColor White
Write-Host "    # Opción 1 (Pipeline Completo)" -ForegroundColor Gray
Write-Host "    # Déjalo corriendo y ve a hacer otra cosa" -ForegroundColor Gray
Write-Host ""

Write-Host "OPCIÓN B: Probar Velocidad Primero" -ForegroundColor White
Write-Host "  ⏱️  Tiempo: 2 minutos (test)" -ForegroundColor Gray
Write-Host "  💡 Sabrás si está optimizado o no" -ForegroundColor Gray
Write-Host "  💡 Recomendado si: Quieres verificar antes de commit" -ForegroundColor Gray
Write-Host ""
Write-Host "  Comando:" -ForegroundColor Yellow
Write-Host "    py scripts\tests\test_lm_studio_speed.py" -ForegroundColor White
Write-Host "    # Te dirá: EXCELLENT / GOOD / SLOW / VERY SLOW" -ForegroundColor Gray
Write-Host "    # Luego decides si ejecutar pipeline o cambiar a Qwen" -ForegroundColor Gray
Write-Host ""

Write-Host "OPCIÓN C: Cambiar a Qwen Temporalmente" -ForegroundColor White
Write-Host "  ⏱️  Tiempo: 15 minutos (182 jobs)" -ForegroundColor Gray
Write-Host "  ⚠️  Accuracy: 75%" -ForegroundColor Yellow
Write-Host "  ❌ Algunas hallucinations" -ForegroundColor Red
Write-Host "  💡 Recomendado si: Necesitas resultados YA" -ForegroundColor Gray
Write-Host ""
Write-Host "  Comandos:" -ForegroundColor Yellow
Write-Host "    notepad .env" -ForegroundColor White
Write-Host "    # Cambiar: LLM_MODEL=qwen2.5-14b-instruct" -ForegroundColor Gray
Write-Host "    .\START_CONTROL_CENTER.bat" -ForegroundColor White
Write-Host "    # Opción 1 (Pipeline Completo)" -ForegroundColor Gray
Write-Host ""

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  💡 MI RECOMENDACIÓN:" -ForegroundColor Yellow
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  1️⃣  Ejecuta OPCIÓN B (test de velocidad)" -ForegroundColor White
Write-Host "       → Toma 2 minutos" -ForegroundColor Gray
Write-Host ""
Write-Host "  2️⃣  Si dice 'GOOD' o mejor:" -ForegroundColor White
Write-Host "       → Ejecuta pipeline con Llama (2 horas)" -ForegroundColor Gray
Write-Host ""
Write-Host "  3️⃣  Si dice 'SLOW' o 'VERY SLOW':" -ForegroundColor White
Write-Host "       → Cambia a Qwen por hoy (15 min)" -ForegroundColor Gray
Write-Host "       → Mañana optimiza LM Studio" -ForegroundColor Gray
Write-Host ""

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  📝 COMANDO PARA EMPEZAR:" -ForegroundColor White
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  py scripts\tests\test_lm_studio_speed.py" -ForegroundColor Yellow
Write-Host ""
Write-Host "  (Te dará diagnóstico en 2 minutos)" -ForegroundColor Gray
Write-Host ""

Write-Host "Press Enter to continue..." -ForegroundColor Gray -NoNewline
Read-Host
