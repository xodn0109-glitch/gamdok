document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('searchInput');
    const searchBtn = document.getElementById('searchBtn');
    const resultContainer = document.getElementById('resultContainer');

    // 6월 4일: 1·2·3학년 전학년이 동일한 전국연합 시정표로 동시 시험
    const examSchedule = [
        { name: '학급담임', start: '08:00', end: '08:30', type: 'class' },
        { name: '1교시', start: '08:30', end: '09:30', type: 'class', id: '08:30~09:30', exam: '국어' },
        { name: '2교시', start: '09:30', end: '10:00', type: 'class', id: '09:30~10:00', exam: '국어' },
        { name: '쉬는시간', start: '10:00', end: '10:10', type: 'break' },
        { name: '2교시', start: '10:10', end: '10:30', type: 'class', id: '10:10~10:30', exam: '수학' },
        { name: '3교시', start: '10:30', end: '11:30', type: 'class', id: '10:30~11:30', exam: '수학' },
        { name: '4교시', start: '11:30', end: '12:00', type: 'class', id: '11:30~12:00', exam: '수학' },
        { name: '점심시간', start: '12:00', end: '13:00', type: 'lunch' },
        { name: '4교시', start: '13:00', end: '13:35', type: 'class', id: '13:00~13:35', exam: '영어' },
        { name: '5교시', start: '13:35', end: '14:20', type: 'class', id: '13:35~14:20', exam: '영어' },
        { name: '쉬는시간', start: '14:20', end: '14:40', type: 'break' },
        { name: '6교시', start: '14:40', end: '15:35', type: 'class', id: '14:40~15:35', exam: '한국사' },
        { name: '7교시', start: '15:35', end: '16:37', type: 'class', id: '15:35~16:37', exam: '탐구' },
        { name: '부담임', start: '16:37', end: '17:10', type: 'class', id: '16:37~17:10', exam: '탐구' }
    ];

    function timeToMinutes(timeStr) {
        const [h, m] = timeStr.split(':').map(Number);
        return h * 60 + m;
    }

    function renderTimeline(teacherSchedules) {
        const startMins = timeToMinutes('07:50');
        const endMins = timeToMinutes('17:25');
        const totalMins = endMins - startMins;

        let html = `
            <div class="timeline-wrapper">
                <div class="timeline-header">
                    <div class="th-time">시간</div>
                    <div class="th-col th-primary">전국연합 시정표 · 내 감독 강조</div>
                </div>
                <div class="timeline-container">
        `;

        // 정시 눈금 (08:00 ~ 17:00)
        for (let h = 8; h <= 17; h++) {
            const min = h * 60;
            if (min >= startMins && min <= endMins) {
                const top = (min - startMins) / totalMins * 100;
                html += `<div class="time-marker" style="top: ${top}%"><span>${h}:00</span></div>`;
            }
        }

        examSchedule.forEach(block => {
            const start = timeToMinutes(block.start);
            const end = timeToMinutes(block.end);
            const duration = end - start;
            const top = (start - startMins) / totalMins * 100;
            const height = duration / totalMins * 100;
            const isShort = duration <= 12;

            const mine = block.id ? teacherSchedules.filter(s => s.time === block.id) : [];
            const isMine = mine.length > 0;
            const activeClass = isMine ? 'active-supervision' : '';
            const places = [...new Set(mine.map(d => `${d.grade} ${d.class}`))].join(' / ');
            const detailStr = isMine ? `<div class="tl-detail">${places}</div>` : '';
            const nameStr = block.exam ? `${block.name} · ${block.exam}` : block.name;

            html += `<div class="tl-block tl-single ${block.type} ${activeClass} ${isShort && !isMine ? 'short-block' : ''}" style="top: ${top}%; height: ${height}%">
                <div class="tl-name">${nameStr}</div>
                ${(isShort && !isMine) ? '' : `<div class="tl-time">${block.start}~${block.end}</div>`}
                ${detailStr}
            </div>`;
        });

        html += `</div></div>`;
        return html;
    }

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

        // 타임라인 추가
        html += renderTimeline(sortedSchedules);

        // 상세 정보(카드) 추가
        html += `<h3 style="margin-top: 1rem; margin-bottom: 1rem; font-size: 1.2rem; color: var(--text-main);">📋 상세 배정 내역</h3>`;
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
