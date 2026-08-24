from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from backend.services.import_service import ImportService

router = APIRouter(prefix="/api/import", tags=["Bulk Import"])


class PreviewImportRequest(BaseModel):
    client_id: str = Field(..., description="Target Client ID")
    raw_text: str = Field(..., description="Pasted CSV or TSV tabular data")


class CommitImportRequest(BaseModel):
    client_id: str = Field(..., description="Target Client ID")
    target_date: Optional[str] = Field(None, description="Snapshot date YYYY-MM-DD (defaults to today)")
    rows: List[Dict[str, Any]] = Field(..., description="Validated mapped rows from preview")


@router.post("/preview")
async def preview_bulk_import(payload: PreviewImportRequest):
    """
    Parses pasted CSV or TSV data and returns a structured preview with validated fields and computed statuses.
    """
    service = ImportService()
    result = await service.preview_import(
        raw_text=payload.raw_text,
        client_id=payload.client_id
    )
    if not result.get("valid"):
        raise HTTPException(status_code=400, detail=result.get("error", "Unable to parse table data"))
    return result


@router.post("/bulk-paste")
async def commit_bulk_import(payload: CommitImportRequest):
    """
    Commits validated bulk rows into MongoDB, upserting Creatives and creating DailySnapshots.
    """
    service = ImportService()
    try:
        result = await service.commit_import(
            client_id=payload.client_id,
            rows=payload.rows,
            target_date=payload.target_date
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to import records: {str(e)}")
