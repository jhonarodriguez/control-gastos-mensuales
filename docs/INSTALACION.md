# Instalacion

## Requisitos

- Python 3.10 o superior recomendado
- Cuenta de Google (si usaras Drive)

## 1) Clonar e instalar dependencias

```bash
git clone <url-del-repo>
cd control-gastos-mensuales
pip install -r requirements.txt
```

## 2) Crear configuracion local

Usa la plantilla incluida:

```bash
cp config/configuracion.example.json config/configuracion.json
```

En Windows PowerShell:

```powershell
Copy-Item config/configuracion.example.json config/configuracion.json
```

Luego ajusta tus datos en `config/configuracion.json` desde la web.

## 3) Iniciar interfaz web

```bash
python web_server.py
```

Abre: `http://localhost:8080`

## 4) Configurar Google Drive (opcional)

1. Coloca `config/credentials.json` (OAuth desktop app).
2. Usa el boton de sincronizacion en la web.
3. Autoriza la cuenta cuando abra el navegador.
4. Se generara `config/token.pickle` automaticamente.

## 5) Uso diario

- Registra y ajusta configuracion desde la web.
- Presiona Sync en el header para subir cambios a Drive.
- Usa el bot para registrar gastos diarios.

## Problemas comunes

### No sincroniza con Drive

- Verifica que `credentials.json` exista
- Borra `config/token.pickle` y autentica de nuevo
- Revisa salida de `web_server.py`

### El bot no refleja cambios

- Asegura que sincronizaste al menos una vez desde web
- Revisa que el gasto aparezca en `GASTOS VARIABLES DEL MES`
- Reinicia procesos (`web_server.py` y bot)

## Nota de seguridad

`config/configuracion.json`, `credentials.json` y `token.pickle` son archivos sensibles y no deben subirse a GitHub.
