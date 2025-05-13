from fastapi import APIRouter, HTTPException
from app.schemas.data_schemas import DataRequest, DataResponse, DataSource
from app.utils.excel_utils import read_excel_file, process_excel_data
from typing import Dict, Any

router = APIRouter()

@router.post("/process-data", response_model=DataResponse)
async def process_data(request: DataRequest) -> Dict[str, Any]:
    """
    엑셀 파일을 처리하는 엔드포인트
    
    Args:
        request (DataRequest): 처리할 파일 정보
        
    Returns:
        Dict[str, Any]: 처리 결과
    """
    try:
        # 파일 읽기
        df = await read_excel_file(request.file_path, request.file_name)
        if df is None:
            raise HTTPException(status_code=404, detail="파일을 읽을 수 없습니다.")
            
        # 데이터 처리
        result = await process_excel_data(
            df,
            request.data_source.value,
            request.process_date.isoformat() if request.process_date else None
        )
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
            
        return DataResponse(
            success=True,
            message="데이터 처리 완료",
            processed_rows=result["processed_rows"]
        )
        
    except Exception as e:
        return DataResponse(
            success=False,
            message="데이터 처리 실패",
            error=str(e)
        ) 