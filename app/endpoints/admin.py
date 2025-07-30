"""
관리자 페이지 API 엔드포인트 (HTTP 요청 방식)
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
import httpx
import asyncio

from app.db.base import get_main_db
from app.services.history_service import HistoryService
from app.services.file_service import FileService
from app.schemas.admin_schemas import HistoryListResponse, FileUploadResponse
from app.core.setting import get_settings

router = APIRouter(prefix="/admin")
templates = Jinja2Templates(directory="app/templates")
settings = get_settings()

# 기본 API 서버 URL (같은 서버지만 명시적으로)
BASE_API_URL = "http://localhost:8090"

@router.get("/", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    """관리자 대시보드 페이지"""
    return templates.TemplateResponse("admin/dashboard.html", {"request": request})

@router.get("/api/history", response_model=HistoryListResponse)
async def get_history_list(
    page: int = 1,
    size: int = 20,
    db: AsyncSession = Depends(get_main_db)
):
    """히스토리 목록 API"""
    try:
        service = HistoryService(db)
        return await service.get_history_list(page=page, size=size)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"히스토리 조회 실패: {str(e)}")

@router.post("/api/upload", response_model=FileUploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """파일 업로드 API"""
    try:
        # 파일 타입 검증
        allowed_types = ["text/csv", "application/vnd.ms-excel", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"]
        if file.content_type not in allowed_types:
            raise HTTPException(status_code=400, detail="지원하지 않는 파일 형식입니다.")
        
        # 파일 크기 검증 (10MB 제한)
        content = await file.read()
        if len(content) > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="파일 크기는 10MB를 초과할 수 없습니다.")
        
        await file.seek(0)
        
        file_service = FileService()
        file_info = await file_service.save_uploaded_file(file)
        
        return FileUploadResponse(
            filename=file_info["filename"],
            size=file_info["size"],
            content_type=file_info["content_type"],
            upload_path=file_info["relative_path"]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"파일 업로드 실패: {str(e)}")

@router.get("/api/files")
async def get_uploaded_files():
    """업로드된 파일 목록 API"""
    try:
        file_service = FileService()
        files = await file_service.get_uploaded_files()
        return {"files": files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"파일 목록 조회 실패: {str(e)}")

@router.post("/api/process")
async def process_data(
    job_type: str,
    file_path: str
):
    """데이터 처리 요청 (기존 API 호출)"""
    try:
        # 파일 존재 확인
        file_service = FileService()
        file_info = file_service.get_file_info(file_path.replace('/static/uploads/', 'app/static/uploads/'))
        if not file_info:
            raise HTTPException(status_code=404, detail="파일을 찾을 수 없습니다.")
        
        # 작업 유형에 따라 적절한 API 엔드포인트 결정
        api_endpoint = get_api_endpoint(job_type)
        if not api_endpoint:
            raise HTTPException(status_code=400, detail="지원하지 않는 작업 유형입니다.")
        
        # HTTP 요청으로 기존 API 호출
        async with httpx.AsyncClient(timeout=300.0) as client:  # 5분 타임아웃
            # 파일 업로드 형태로 요청
            with open(file_info["path"], 'rb') as f:
                files = {"file": (file_info["filename"], f, "application/octet-stream")}
                
                response = await client.post(
                    f"{BASE_API_URL}{api_endpoint}",
                    files=files,
                    timeout=300.0
                )
        
        # 응답 처리
        if response.status_code == 200:
            try:
                result_data = response.json()
                return {
                    "success": True,
                    "message": f"{job_type} 처리가 성공적으로 완료되었습니다.",
                    "data": result_data
                }
            except:
                return {
                    "success": True, 
                    "message": f"{job_type} 처리가 완료되었습니다."
                }
        else:
            try:
                error_data = response.json()
                error_message = error_data.get("detail", "알 수 없는 오류가 발생했습니다.")
            except:
                error_message = f"HTTP {response.status_code} 오류가 발생했습니다."
            
            return {
                "success": False,
                "message": f"처리 실패: {error_message}"
            }
        
    except httpx.TimeoutException:
        return {
            "success": False,
            "message": "요청 시간이 초과되었습니다. 처리 시간이 오래 걸리는 작업입니다."
        }
    except httpx.RequestError as e:
        return {
            "success": False,
            "message": f"네트워크 오류가 발생했습니다: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"처리 중 오류가 발생했습니다: {str(e)}"
        }

def get_api_endpoint(job_type: str) -> str:
    """작업 유형에 따른 API 엔드포인트 반환"""
    endpoint_map = {
        "국가별 수출입규모(관세청)": "/customs/country-data",
        "주요 수출/수입품(관세청) - 수출실적": "/customs/export-items", 
        "주요 수출/수입품(관세청) - 수입실적": "/customs/import-items",
        "주요 경제지표(EIU)": "/eiu/economic-indicators",
        "주요 수출/수입국(EIU)": "/eiu/trade-partners"
    }
    
    return endpoint_map.get(job_type)

@router.delete("/api/files/{filename}")
async def delete_file(filename: str):
    """파일 삭제 API"""
    try:
        file_service = FileService()
        success = await file_service.delete_file(filename)
        
        if not success:
            raise HTTPException(status_code=404, detail="삭제할 파일을 찾을 수 없습니다.")
        
        return {"message": "파일이 성공적으로 삭제되었습니다."}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"파일 삭제 실패: {str(e)}")

@router.delete("/api/history/{file_seq}/{data_wrk_nm}")
async def delete_history(
    file_seq: int,
    data_wrk_nm: str,
    db: AsyncSession = Depends(get_main_db)
):
    """히스토리 삭제 API"""
    try:
        service = HistoryService(db)
        success = await service.delete_history(file_seq, data_wrk_nm)
        
        if not success:
            raise HTTPException(status_code=404, detail="삭제할 히스토리를 찾을 수 없습니다.")
        
        return {"message": "히스토리가 성공적으로 삭제되었습니다."}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"히스토리 삭제 실패: {str(e)}") 