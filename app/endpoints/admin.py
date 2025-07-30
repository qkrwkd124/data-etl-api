"""
관리자 페이지 API 엔드포인트 (HTTP 요청 방식)
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
import httpx
import asyncio

from app.db.base import get_main_db
from app.services.history_service import HistoryService
from app.services.file_service import FileService
from app.schemas.admin_schemas import HistoryListResponse, FileUploadResponse, WORK_TYPE_MAPPING
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
    status: str = None,
    job_type: str = None,  # 작업 유형별 필터링 추가
    db: AsyncSession = Depends(get_main_db)
):
    """히스토리 목록 API (작업 유형별 필터링 지원)"""
    try:
        service = HistoryService(db)
        return await service.get_history_list(page=page, size=size, status=status, job_type=job_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"히스토리 조회 실패: {str(e)}")

@router.post("/api/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    job_type: str = Form(...),  # 작업 유형 추가
    db: AsyncSession = Depends(get_main_db)
):
    """파일 업로드 + 작업 유형과 함께 History 테이블 등록"""
    try:
        # 파일 검증
        allowed_types = ["text/csv", "application/vnd.ms-excel", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"]
        if file.content_type not in allowed_types:
            raise HTTPException(status_code=400, detail="지원하지 않는 파일 형식입니다.")
        
        content = await file.read()
        if len(content) > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="파일 크기는 10MB를 초과할 수 없습니다.")
        
        await file.seek(0)
        
        # 작업 유형 확인
        work_config = WORK_TYPE_MAPPING.get(job_type)
        if not work_config:
            raise HTTPException(status_code=400, detail="지원하지 않는 작업 유형입니다.")
        
        # 1. 파일 저장
        file_service = FileService()
        file_info = await file_service.save_uploaded_file(file)
        
        # 2. History 테이블에 작업 유형과 함께 등록  
        history_service = HistoryService(db)
        file_seq = await history_service.create_with_job_type(file_info, job_type, work_config["data_wrk_no"])
        
        return FileUploadResponse(
            filename=file_info["filename"],
            size=file_info["size"],
            content_type=file_info["content_type"],
            upload_path=file_info["relative_path"],
            file_seq=file_seq  # 추가
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"파일 업로드 실패: {str(e)}")

@router.get("/api/files")
async def get_uploaded_files(
    job_type: str = None, 
    db: AsyncSession = Depends(get_main_db)
):
    """업로드된 파일 목록 API (작업 유형별 필터링)"""
    try:
        history_service = HistoryService(db)
        
        if job_type and job_type != 'all':
            # 히스토리에서 해당 작업 유형의 파일만 가져오기
            histories = await history_service.get_history_list(page=1, size=100)
            
            # 작업 유형에 맞는 파일만 필터링
            filtered_files = [
                {
                    "filename": h.file_nm,
                    "size": int(h.file_size) if h.file_size else 0,
                    "file_seq": h.file_seq,
                    "created_at": h.reg_dtm,
                    "job_type": h.data_wrk_nm
                }
                for h in histories.items 
                if h.data_wrk_nm == job_type and h.file_nm
            ]
            return {"files": filtered_files, "job_type": job_type}
        else:
            # 전체 파일 목록
            file_service = FileService()
            files = await file_service.get_uploaded_files()
            return {"files": files, "job_type": job_type}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"파일 목록 조회 실패: {str(e)}")

@router.post("/api/execute/{file_seq}")
async def execute_job_by_file_seq(
    file_seq: int,
    db: AsyncSession = Depends(get_main_db)
):
    """file_seq로 작업 실행 (작업 유형은 히스토리에서 가져옴)"""
    try:
        # 1. file_seq로 히스토리 정보 조회
        history_service = HistoryService(db)
        history = await history_service.get_history_by_seq(file_seq)
        
        if not history:
            raise HTTPException(status_code=404, detail="파일 정보를 찾을 수 없습니다.")
        
        # 2. 히스토리에서 작업 유형 정보 가져오기
        job_type = history.data_wrk_nm
        work_config = WORK_TYPE_MAPPING.get(job_type)
        
        if not work_config:
            raise HTTPException(status_code=400, detail="지원하지 않는 작업 유형입니다.")
        
        # 3. 해당 작업 유형의 가공 서비스 호출
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(
                f"{BASE_API_URL}{work_config['endpoint']}",
                json={"file_seq": file_seq},
                timeout=300.0
            )
        
        if response.status_code == 200:

            response_data = response.json()
            if response_data.get("success"):
                return {
                    "success": True,
                    "message": response_data.get("message", "처리 성공"),
                    "file_seq": file_seq
                }
            else:
                return {
                    "success": False,
                    "message": response_data.get("message", "처리 실패")
                }
        else:
            return {
                "success": False,
                "message": response_data.get("message", "처리 실패")
            }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"처리 중 오류가 발생했습니다: {str(e)}"
        }

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