"""
파일 처리 서비스
"""
import os
import aiofiles
from typing import List, Dict, Any
from fastapi import UploadFile
from datetime import datetime

class FileService:
    """파일 업로드 및 관리 서비스"""
    
    def __init__(self, upload_dir: str = "app/static/uploads"):
        self.upload_dir = upload_dir
        os.makedirs(upload_dir, exist_ok=True)
    
    async def save_uploaded_file(self, file: UploadFile) -> Dict[str, Any]:
        """업로드된 파일 저장"""
        # 파일명에 타임스탬프 추가하여 중복 방지
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{file.filename}"
        file_path = os.path.join(self.upload_dir, filename)
        
        # 파일 저장
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        return {
            "filename": filename,
            "original_filename": file.filename,
            "size": len(content),
            "content_type": file.content_type,
            "upload_path": file_path,
            "relative_path": f"/static/uploads/{filename}"
        }
    
    async def get_uploaded_files(self) -> List[Dict[str, Any]]:
        """업로드된 파일 목록 조회"""
        files = []
        
        if not os.path.exists(self.upload_dir):
            return files
        
        for filename in os.listdir(self.upload_dir):
            file_path = os.path.join(self.upload_dir, filename)
            if os.path.isfile(file_path):
                stat = os.stat(file_path)
                files.append({
                    "filename": filename,
                    "size": stat.st_size,
                    "created_at": datetime.fromtimestamp(stat.st_ctime),
                    "modified_at": datetime.fromtimestamp(stat.st_mtime),
                    "path": file_path,
                    "relative_path": f"/static/uploads/{filename}"
                })
        
        # 최신 파일 순으로 정렬
        files.sort(key=lambda x: x["created_at"], reverse=True)
        return files
    
    async def delete_file(self, filename: str) -> bool:
        """파일 삭제"""
        file_path = os.path.join(self.upload_dir, filename)
        
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """파일 정보 조회"""
        if not os.path.exists(file_path):
            return None
        
        stat = os.stat(file_path)
        filename = os.path.basename(file_path)
        
        return {
            "filename": filename,
            "size": stat.st_size,
            "created_at": datetime.fromtimestamp(stat.st_ctime),
            "modified_at": datetime.fromtimestamp(stat.st_mtime),
            "path": file_path
        }