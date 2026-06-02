document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('searchInput');
    const searchBtn = document.getElementById('searchBtn');
    const resultContainer = document.getElementById('resultContainer');

    function renderSchedule(teacherName) {
        resultContainer.innerHTML = ''; // Clear previous results

        if (!teacherName) {
            return;
        }

        const schedules = scheduleData[teacherName] || [];

        if (schedules.length === 0) {
            resultContainer.innerHTML = `
                <div class="empty-state">
                    <h3>'${teacherName}' 선생님의 배정된 시험감독이 없습니다.</h3>
                    <p>이름을 올바르게 입력했는지 확인해주세요.</p>
                </div>
            `;
            return;
        }

        const sortedSchedules = [...schedules].sort((a, b) => a.time.localeCompare(b.time));

        let html = `<h2 class="teacher-name-heading">${teacherName} 선생님 감독 시간표 <span class="count-badge">${sortedSchedules.length}건</span></h2>`;

        // 상세 배정 내역(카드)
        html += `<h3 style="margin-bottom: 1rem; font-size: 1.2rem; color: var(--text-main);">📋 상세 배정 내역</h3>`;
        html += `<div class="card-list">`;
        sortedSchedules.forEach(item => {
            html += `
                <div class="schedule-card">
                    <div class="schedule-row">
                        <span class="row-label">⏰ 감독 시간</span>
                        <span class="row-value"><span class="period-bold">${item.period.split(' ')[0]}</span> <span class="time-sub">(${item.time})</span></span>
                    </div>
                    <div class="schedule-row">
                        <span class="row-label">📍 장소</span>
                        <span class="row-value location-highlight">${item.grade} ${item.class}</span>
                    </div>
                    <div class="schedule-row">
                        <span class="row-label">📝 시험 과목</span>
                        <span class="row-value">${item.exam}</span>
                    </div>
                </div>
            `;
        });
        html += `</div>`;

        resultContainer.innerHTML = html;
    }

    searchBtn.addEventListener('click', () => {
        const query = searchInput.value.trim();
        renderSchedule(query);
    });

    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            const query = searchInput.value.trim();
            renderSchedule(query);
        }
    });

    searchInput.focus();
});
