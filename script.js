document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('searchInput');
    const searchBtn = document.getElementById('searchBtn');
    const resultContainer = document.getElementById('resultContainer');

    function renderSchedule(teacherName) {
        resultContainer.innerHTML = ''; // Clear previous results
        
        if (!teacherName) {
            return;
        }

        const schedules = scheduleData[teacherName];

        if (!schedules || schedules.length === 0) {
            resultContainer.innerHTML = `
                <div class="empty-state">
                    <h3>'${teacherName}' 선생님의 배정된 시험감독 시간표가 없습니다.</h3>
                    <p>이름을 올바르게 입력했는지 확인해주세요.</p>
                </div>
            `;
            return;
        }

        // Sort schedules by time
        const sortedSchedules = [...schedules].sort((a, b) => {
             return a.time.localeCompare(b.time);
        });

        let html = `<h2 class="teacher-name-heading">${teacherName} 선생님 시간표</h2>`;
        
        sortedSchedules.forEach(item => {
            html += `
                <div class="schedule-card">
                    <div class="schedule-row">
                        <span class="row-label">⏰ 교시 (감독 시간)</span>
                        <span class="row-value"><span class="period-bold">${item.period}</span> <span class="time-sub">(${item.time})</span></span>
                    </div>
                    <div class="schedule-row">
                        <span class="row-label">📍 장소</span>
                        <span class="row-value location-highlight">${item.grade} ${item.class}</span>
                    </div>
                    <div class="schedule-row">
                        <span class="row-label">📝 시험 과목 (시험 시간)</span>
                        <span class="row-value">${item.exam}</span>
                    </div>
                </div>
            `;
        });

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

    // Initial focus
    searchInput.focus();
});
