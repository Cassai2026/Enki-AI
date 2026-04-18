# This file has been consolidated into enki_ai/core/ingest_mission_data.py.
# Re-exported here for backwards compatibility.
from enki_ai.core.ingest_mission_data import (  # noqa: F401
    ingest,
    search_forensic_entry,
    extract_text,
    init_db,
    insert_entry,
    THE_14_PILLARS,
)

if __name__ == "__main__":
    import runpy
    runpy.run_module("enki_ai.core.ingest_mission_data", run_name="__main__")
