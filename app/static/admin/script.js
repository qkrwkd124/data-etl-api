// 전역 변수
let currentPage = 1;
let pageSize = 20;
let uploadedFiles = [];
let currentJobType = '주요 경제지표(EIU)'; // 현재 선택된 작업 유형

// 페이지 로드시 초기화
document.addEventListener('DOMContentLoaded', function() {
    initializePage();
});

// 페이지 초기화
async function initializePage() {
    checkConnection();
    setupEventListeners();
    // 기본적으로 첫 번째 작업 유형(EIU 경제지표)의 처리이력 로드
    await loadHistory();
}

// 연결 상태 확인
async function checkConnection() {
    try {
        const response = await fetch('/health');
        const statusDot = document.getElementById('connectionStatus');
        const statusText = document.getElementById('connectionText');
        
        if (response.ok) {
            statusDot.className = 'status-dot connected';
            statusText.textContent = '서버 연결됨';
        } else {
            throw new Error('서버 응답 오류');
        }
    } catch (error) {
        const statusDot = document.getElementById('connectionStatus');
        const statusText = document.getElementById('connectionText');
        statusDot.className = 'status-dot disconnected';
        statusText.textContent = '서버 연결 실패';
    }
}

// 이벤트 리스너 설정
function setupEventListeners() {
    // 파일 업로드 관련
    const fileInput = document.getElementById('fileInput');
    const uploadArea = document.getElementById('uploadArea');
    
    fileInput.addEventListener('change', handleFileSelect);
    
    // 드래그 앤 드롭
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleFileDrop);
    
    // 업로드 영역 클릭
    uploadArea.addEventListener('click', () => {
        fileInput.click();
    });
}

// 드래그 오버 처리
function handleDragOver(e) {
    e.preventDefault();
    e.currentTarget.classList.add('dragover');
}

// 드래그 리브 처리
function handleDragLeave(e) {
    e.preventDefault();
    e.currentTarget.classList.remove('dragover');
}

// 파일 드롭 처리
function handleFileDrop(e) {
    e.preventDefault();
    e.currentTarget.classList.remove('dragover');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        uploadFile(files[0]);
    }
}

// 파일 선택 처리
function handleFileSelect(e) {
    const files = e.target.files;
    if (files.length > 0) {
        uploadFile(files[0]);
    }
}

// 파일 업로드
async function uploadFile(file) {
    const progressContainer = document.getElementById('uploadProgress');
    const progressFill = document.getElementById('progressFill');
    const progressText = document.getElementById('progressText');
    
    try {
        // 파일 크기 체크
        if (file.size > 10 * 1024 * 1024) {
            showMessage('오류', '파일 크기는 10MB를 초과할 수 없습니다.', 'error');
            return;
        }
        
        // 파일 타입 체크
        const allowedTypes = ['text/csv', 'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'];
        if (!allowedTypes.includes(file.type)) {
            showMessage('오류', '지원하지 않는 파일 형식입니다. CSV, Excel 파일만 업로드 가능합니다.', 'error');
            return;
        }
        
        // 진행률 표시
        progressContainer.style.display = 'block';
        progressFill.style.width = '0%';
        progressText.textContent = '업로드 중...';
        
        const formData = new FormData();
        formData.append('file', file);
        formData.append('job_type', currentJobType); // 현재 선택된 작업 유형 사용
        
        const response = await fetch('/admin/api/upload', {
            method: 'POST',
            body: formData
        });
        
        // 가짜 진행률 애니메이션
        let progress = 0;
        const progressInterval = setInterval(() => {
            progress += Math.random() * 30;
            if (progress > 90) progress = 90;
            progressFill.style.width = progress + '%';
        }, 100);
        
        const result = await response.json();
        
        clearInterval(progressInterval);
        progressFill.style.width = '100%';
        progressText.textContent = '업로드 완료!';
        
        if (response.ok) {
            // file_seq 정보도 함께 저장
            showMessage('성공', `파일이 성공적으로 업로드되었습니다: ${result.filename} (파일번호: ${result.file_seq})`, 'success');
            await loadHistory(); // 처리이력 새로고침
        } else {
            throw new Error(result.detail || '업로드 실패');
        }
        
    } catch (error) {
        showMessage('오류', error.message, 'error');
    } finally {
        setTimeout(() => {
            progressContainer.style.display = 'none';
            document.getElementById('fileInput').value = '';
        }, 2000);
    }
}





// 히스토리 로드 (작업 유형별 필터링)
async function loadHistory(page = 1) {
    try {
        const statusFilter = document.getElementById('statusFilter').value;
        let url = `/admin/api/history?page=${page}&size=${pageSize}`;
        
        // 작업 유형별 필터링 추가
        if (currentJobType) {
            url += `&job_type=${encodeURIComponent(currentJobType)}`;
        }
        
        if (statusFilter) {
            url += `&status=${statusFilter}`;
        }
        
        const response = await fetch(url);
        const data = await response.json();
        
        displayHistory(data.items);
        displayPagination(data);
        currentPage = page;
        
    } catch (error) {
        document.getElementById('historyTableBody').innerHTML = 
            '<tr><td colspan="8" class="text-center text-danger">이력을 불러올 수 없습니다.</td></tr>';
    }
}

// 히스토리 표시
function displayHistory(items) {
    const tbody = document.getElementById('historyTableBody');
    
    if (items.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" class="text-center">이력이 없습니다.</td></tr>';
        return;
    }
    
    const historyHtml = items.map(item => `
        <tr>
            <td>${item.file_seq}</td>
            <td>${item.data_wrk_nm}</td>
            <td>${item.file_nm || '-'}</td>
            <td>${formatDate(item.strt_dtm)}</td>
            <td>${item.end_dtm ? formatDate(item.end_dtm) : '-'}</td>
            <td>${item.proc_cnt || '-'}</td>
            <td title="${item.rmk_ctnt || ''}">${truncateText(item.rmk_ctnt, 30)}</td>
            <td>
                ${getStatusButton(item.fin_yn, item.file_seq)}
            </td>
        </tr>
    `).join('');
    
    tbody.innerHTML = historyHtml;
}

// 상태 버튼 생성
function getStatusButton(status, fileSeq) {
    if (status === 'Y') {
        // 완료된 작업
        return `<button class="status-btn completed" disabled>완료</button>`;
    } else {
        // 대기 상태는 실행 가능
        return `<button class="status-btn execute" onclick="executeJobByFileSeq(${fileSeq})">실행</button>`;
    }
}

// 페이지네이션 표시
function displayPagination(data) {
    const pagination = document.getElementById('pagination');
    
    if (data.total_pages <= 1) {
        pagination.innerHTML = '';
        return;
    }
    
    let paginationHtml = '';
    
    // 이전 페이지
    if (data.page > 1) {
        paginationHtml += `<button onclick="loadHistory(${data.page - 1})">이전</button>`;
    }
    
    // 페이지 번호들
    const startPage = Math.max(1, data.page - 2);
    const endPage = Math.min(data.total_pages, data.page + 2);
    
    for (let i = startPage; i <= endPage; i++) {
        const activeClass = i === data.page ? 'active' : '';
        paginationHtml += `<button class="${activeClass}" onclick="loadHistory(${i})">${i}</button>`;
    }
    
    // 다음 페이지
    if (data.page < data.total_pages) {
        paginationHtml += `<button onclick="loadHistory(${data.page + 1})">다음</button>`;
    }
    
    pagination.innerHTML = paginationHtml;
}

// 상태 필터
function filterHistory() {
    loadHistory(1);
}

// 히스토리 새로고침
function refreshHistory() {
    loadHistory(currentPage);
}



// 히스토리 삭제
async function deleteHistory(fileSeq, dataWrkNm) {
    if (!confirm('정말로 이 이력을 삭제하시겠습니까?')) {
        return;
    }
    
    try {
        const response = await fetch(`/admin/api/history/${fileSeq}/${encodeURIComponent(dataWrkNm)}`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showMessage('성공', '이력이 삭제되었습니다.', 'success');
            await loadHistory(currentPage);
        } else {
            throw new Error(result.detail || '삭제 실패');
        }
    } catch (error) {
        showMessage('오류', error.message, 'error');
    }
}



// 유틸리티 함수들
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// 날짜/시간 포맷 함수 수정
function formatDate(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    
    // 날짜와 시간을 분리해서 표시
    const dateStr = date.toLocaleDateString('ko-KR', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
    });
    const timeStr = date.toLocaleTimeString('ko-KR', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
    
    return `<div class="datetime-display">
                <div class="date-part">${dateStr}</div>
                <div class="time-part">${timeStr}</div>
            </div>`;
}

function getStatusBadge(status) {
    const statusMap = {
        'Y': { text: '완료', class: 'status-completed' },
        'N': { text: '진행중', class: 'status-processing' },
        'E': { text: '에러', class: 'status-error' }
    };
    
    const statusInfo = statusMap[status] || { text: '-', class: '' };
    return `<span class="status-badge ${statusInfo.class}">${statusInfo.text}</span>`;
}

function truncateText(text, maxLength) {
    if (!text) return '-';
    return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
}

function showMessage(title, message, type = 'info') {
    document.getElementById('modalTitle').textContent = title;
    document.getElementById('modalMessage').textContent = message;
    document.getElementById('messageModal').style.display = 'block';
}

function closeModal() {
    document.getElementById('messageModal').style.display = 'none';
}

function showLoading(text = '처리 중...') {
    document.getElementById('loadingText').textContent = text;
    document.getElementById('loadingOverlay').style.display = 'block';
}

function hideLoading() {
    document.getElementById('loadingOverlay').style.display = 'none';
}

// 모달 외부 클릭시 닫기
window.onclick = function(event) {
    const modal = document.getElementById('messageModal');
    if (event.target === modal) {
        closeModal();
    }
}

// 파일 선택 함수 수정
function selectFile() {
    if (!currentJobType) {
        showMessage('오류', '작업 유형을 먼저 선택해주세요.', 'error');
        return;
    }
    document.getElementById('fileInput').click();
}

// 작업 유형 선택 함수 (새로 추가)
function selectJobType(jobType) {
    // 이전 선택 해제
    document.querySelectorAll('.menu-item').forEach(item => {
        item.classList.remove('active');
    });
    
    // 새로운 선택 활성화
    const selectedItem = document.querySelector(`[data-job-type="${jobType}"]`);
    if (selectedItem) {
        selectedItem.classList.add('active');
    }
    
    // 전역 변수 업데이트
    currentJobType = jobType;
    
    // 화면 업데이트
    document.getElementById('currentJobTypeName').textContent = jobType;
    
    // 해당 작업 유형의 파일 목록과 처리이력 로드
    loadHistory();
}



// file_seq로 작업 실행
async function executeJobByFileSeq(fileSeq) {
    if (!confirm('이 파일로 데이터 처리를 시작하시겠습니까?')) {
        return;
    }
    
    try {
        showLoading('데이터 처리를 시작하고 있습니다...');
        
        const response = await fetch(`/admin/api/execute/${fileSeq}`, {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (result.success) {
            showMessage('성공', result.message, 'success');
            await loadHistory(); // 히스토리 새로고침
        } else {
            showMessage('실패', result.message, 'error');
        }
        
    } catch (error) {
        showMessage('오류', `처리 중 오류가 발생했습니다: ${error.message}`, 'error');
    } finally {
        hideLoading();
    }
}

