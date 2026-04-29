# ⚡ PLAN DE PRUEBAS RÁPIDO - CIERRE DE SESIÓN

## ✅ 4 PROBLEMAS RESUELTOS

1. ✅ **BulletinProcessor** - Fix import error
2. ✅ **EXPIRE_LIFECYCLE** - Fix subprocess (python → py)
3. ✅ **Indeed URLs** - Filtrar onboarding redirects
4. ✅ **LinkedIn UNKNOWNs** - +12 patrones detección

---

## 🧪 PRUEBA ÚNICA PARA VALIDAR TODO

### Ejecuta Pipeline Completo
```powershell
py control_center.py
# Selecciona: 1
```

### ✅ Resultados Esperados

**Pipeline Summary (al final):**
```
Email Processing     ✅ PASS
Bulletin Processing  ✅ PASS  ← Era ❌ FAIL antes
AI Analysis          ✅ PASS
Auto-Apply           ✅ PASS
Expire Check         ✅ PASS  ← Sin warning ahora
Report               ✅ PASS
```

**Durante Expire Check:**
```
[1/4] Deleting previously marked EXPIRED jobs...
  ✅ Deleted X EXPIRED jobs  ← Sin traceback warning

[2/4] Verifying Glassdoor...
  ✅ Glassdoor: X expired, Y active

[3/4] Verifying LinkedIn...
  ✅ LinkedIn: X expired, Y active  ← Menos UNKNOWNs

[4/4] Verifying Indeed...
  ✅ Indeed: X expired, Y active  ← URLs correctas ahora
```

---

## ⏱️ DURACIÓN: ~10-15 minutos

### Si TODO pasa ✅:
- **Sistema 100% funcional**
- **Puedes cerrar sesión**
- **Ejecutar diariamente con confianza**

### Si algo falla ❌:
- Revisar: `logs/powershell/session_*.log`
- Compartir error específico para debug

---

## 📋 CHECKLIST POST-PRUEBA

Después del pipeline, verifica en Google Sheets:
- [ ] Tab **LinkedIn**: Jobs tienen Status actualizado
- [ ] Tab **Glassdoor**: EXPIRED marcados correctamente
- [ ] Tab **Indeed**: URLs NO tienen `profOnboarding`
- [ ] Tab **Registry**: Nuevos emails procesados

---

## 🎯 SI QUIERES PROBAR MÁS (Opcional)

### Opción A: Solo verificar LinkedIn (3 min)
```powershell
py control_center.py
# Opción 7 → LinkedIn → 10 jobs
```

### Opción B: Procesar emails nuevos (2 min)
```powershell
py control_center.py
# Opción 3
```

---

## 📞 ARCHIVOS CLAVE

- 📄 **FIXES_SESION_2025-12-07.md** - Detalle técnico completo
- 📊 **Google Sheets** - https://docs.google.com/spreadsheets/d/1EqWPiHdcYyMr5trEuiT_-lzPVEr0owOoDEtTsCIBxdg

---

**¡Listo para cerrar sesión!** 🚀
