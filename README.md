# lareferencia-usage-stats-db

Paquete de dominio y utilidades de base de datos para toda la plataforma de estadísticas.

## Rol en la arquitectura

Este módulo define el contrato de datos común:

- modelos `Source` y `Country`.
- funciones de normalización de identificadores OAI.
- `UsageStatsDatabaseHelper` para resoluciones de negocio (source -> índices OpenSearch).

Todos los demás submódulos dependen de este paquete.

## Estructura principal

- `src/lareferenciastatsdb/models.py`
  - Modelos SQLAlchemy/Flask-AppBuilder.
  - Constantes de tipo: `R` (repositorio), `N` (nacional), `L` (regional).
- `src/lareferenciastatsdb/normalize.py`
  - `normalize_oai_identifier(...)`
  - `extract_oai_identifier_prefix(...)`
  - `normalize_oai_identifier_prefix(...)`
- `src/lareferenciastatsdb/helper.py`
  - `UsageStatsDatabaseHelper`
  - `IdentifierPrefixNotFoundException`
  - funciones lookup (`get_source_by_id`, etc.)

## Modelo de datos

### `Source`
Campos relevantes:
- identificación: `source_id`, `name`, `type`.
- indexación: `site_id`, `national_site_id`, `regional_site_id`.
- autenticación: `auth_token`.
- clasificación: `country_iso`.
- mapeo de identificadores: `identifier_prefix`, `identifier_map_regex`, `identifier_map_replace`, `identifier_map_filename`, `identifier_map_type`.

### `Country`
- `country_iso`, `site_id`, `auth_token`.

## Helper de negocio (`UsageStatsDatabaseHelper`)

Cachea en memoria datos de `Source` para resolver rápido:

- fuente por `source_id` o `site_id`.
- fuente por prefijo de identificador OAI.
- fuentes nacionales/repositorios por país.
- índices OpenSearch de consulta:
  - por identificador (`get_indices_from_identifier`)
  - por source (`get_indices_from_source`)
  - por source nacional (`get_indices_from_national_source`)
  - por source regional (`get_indices_from_regional_source`)

Convención de nombre de índice:

- `get_index_name(prefix, idsite)` -> `<prefix>-<idsite>`

## Scripts de mantenimiento

- `migrate.py`: carga/actualiza `Source` desde Excel legacy.
- `load_countries_data.py`: carga/actualiza `Country` desde Excel.
- `update_regional_siteids.py`: recalcula `national_site_id`/`site_id` según país.
- `obtain_identifiers.py`: exploración puntual de prefijos desde Matomo.

## Empaquetado e instalación

- `setup.py`, `setup.cfg`, `pyproject.toml`, `tox.ini`.

Instalación local:

```bash
pip install -r requirements.txt
pip install -e .
```

## Integración con otros módulos

- `service`: usa helper para resolver índices de consulta.
- `processor`: usa helper para contexto de source y reglas de identificación.
- `admin`: usa `Source/Country` en vistas CRUD.
- `config`: lookup de `Source` para generar archivo de colector.

## Notas técnicas

- Existe un `__init__.py` adicional en raíz del repo que no corresponde al paquete `src/`; mantener atención al `PYTHONPATH` para evitar import ambiguo.
- Tests actuales son parciales y varios tienen patrones legacy no representativos del flujo actual de producción.
