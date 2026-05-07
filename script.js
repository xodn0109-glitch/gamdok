document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('searchInput');
    const searchBtn = document.getElementById('searchBtn');
    const resultContainer = document.getElementById('resultContainer');

    const grade12Schedule = [
        { name: '조회', start: '08:30', end: '08:40', type: 'class' },
        { name: '1교시', start: '08:40', end: '09:25', type: 'class' },
        { name: '쉬는시간', start: '09:25', end: '09:35', type: 'break' },
        { name: '2교시', start: '09:35', end: '10:20', type: 'class' },
        { name: '쉬는시간', start: '10:20', end: '10:35', type: 'break' },
        { name: '3교시', start: '10:35', end: '11:20', type: 'class' },
        { name: '쉬는시간', start: '11:20', end: '11:35', type: 'break' },
        { name: '4교시', start: '11:35', end: '12:25', type: 'class' },
        { name: '점심시간', start: '12:25', end: '13:40', type: 'lunch' },
        { name: '5교시', start: '13:40', end: '14:25', type: 'class' },
        { name: '쉬는시간', start: '14:25', end: '14:40', type: 'break' },
        { name: '6교시', start: '14:40', end: '15:25', type: 'class' },
        { name: '쉬는시간', start: '15:25', end: '15:40', type: 'break' },
        { name: '7교시', start: '15:40', end: '16:30', type: 'class' },
        { name: '종례', start: '16:30', end: '16:40', type: 'class' }
    ];

    const grade3Schedule = [
        { name: '1교시', start: '08:30', end: '09:30', type: 'class', id: '08:30~09:30' },
        { name: '2교시', start: '09:30', end: '10:00', type: 'class', id: '09:30~10:00' },
        { name: '쉬는시간', start: '10:00', end: '10:10', type: 'break' },
        { name: '2교시(계속)', start: '10:10', end: '10:30', type: 'class', id: '10:10~10:30' },
        { name: '3교시', start: '10:30', end: '11:30', type: 'class', id: '10:30~11:30' },
        { name: '4교시', start: '11:30', end: '12:00', type: 'class', id: '11:30~12:00' },
        { name: '점심시간', start: '12:00', end: '13:00', type: 'lunch' },
        { name: '4교시(계속)', start: '13:00', end: '13:35', type: 'class', id: '13:00~13:35' },
        { name: '5교시', start: '13:35', end: '14:20', type: 'class', id: '13:35~14:20' },
        { name: '쉬는시간', start: '14:20', end: '14:40', type: 'break' },
        { name: '6교시', start: '14:40', end: '15:35', type: 'class', id: '14:40~15:35' },
        { name: '화1교시', start: '15:35', end: '16:37', type: 'class', id: '15:35~16:37' }
    ];

    function timeToMinutes(timeStr) {
        const [h, m] = timeStr.split(':').map(Number);
        return h * 60 + m;
    }

    function renderTimeline(teacherSchedules, regularClasses) {
        const startMins = timeToMinutes('08:10'); // 조금 일찍 시작해서 여백 확보
        const endMins = timeToMinutes('16:50');
        const totalMins = endMins - startMins;
        
        let html = `
            <div class="timeline-wrapper">
                <div class="timeline-header">
                    <div class="th-col">1, 2학년 시정표</div>
                    <div class="th-time">시간</div>
                    <div class="th-col th-primary">3학년(내 감독)</div>
                </div>
                <div class="timeline-container">
        `;

        // Add time markers (e.g. 08:30, 09:00, 10:00, ...)
        for(let h=8; h<=16; h++) {
            const min = h * 60;
            if (min >= startMins && min <= endMins) {
                const top = (min - startMins) / totalMins * 100;
                html += `<div class="time-marker" style="top: ${top}%"><span>${h}:00</span></div>`;
            }
        }
        
        // Render 1,2 grade blocks
        grade12Schedule.forEach(block => {
            const start = timeToMinutes(block.start);
            const end = timeToMinutes(block.end);
            const duration = end - start;
            const top = (start - startMins) / totalMins * 100;
            const height = duration / totalMins * 100;
            const isShort = duration <= 15;
            
            const myClasses = regularClasses ? regularClasses.filter(c => c.period === block.name) : [];
            const activeClass = myClasses.length > 0 ? 'active-regular' : '';
            const detailStr = myClasses.length > 0 ? `<div class="tl-detail" style="font-size: 0.75rem; line-height: 1.2;">${myClasses.map(c => `${c.grade} ${c.class}(${c.subject})`).join('<br>')}</div>` : '';
            
            html += `<div class="tl-block tl-12 ${block.type} ${activeClass} ${(isShort && myClasses.length === 0) ? 'short-block' : ''}" style="top: ${top}%; height: ${height}%">
                <div class="tl-name">${block.name}</div>
                ${(isShort && myClasses.length === 0) ? '' : `<div class="tl-time">${block.start}~${block.end}</div>`}
                ${detailStr}
            </div>`;
        });

        // Render 3 grade blocks
        const mySchedules = teacherSchedules.map(s => s.time);
        
        grade3Schedule.forEach(block => {
            const start = timeToMinutes(block.start);
            const end = timeToMinutes(block.end);
            const duration = end - start;
            const top = (start - startMins) / totalMins * 100;
            const height = duration / totalMins * 100;
            const isShort = duration <= 15;
            
            const isMySupervision = mySchedules.includes(block.id);
            const activeClass = isMySupervision ? 'active-supervision' : '';
            const myData = isMySupervision ? teacherSchedules.find(s => s.time === block.id) : null;
            const detailStr = myData ? `<div class="tl-detail">${myData.grade} ${myData.class}</div>` : '';

            html += `<div class="tl-block tl-3 ${block.type} ${activeClass} ${isShort && !isMySupervision ? 'short-block' : ''}" style="top: ${top}%; height: ${height}%">
                <div class="tl-name">${block.name}</div>
                ${(isShort && !isMySupervision) ? '' : `<div class="tl-time">${block.start}~${block.end}</div>`}
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
        const regularClasses = (typeof thursdayData !== 'undefined' && thursdayData[teacherName]) ? thursdayData[teacherName] : [];

        if (schedules.length === 0 && regularClasses.length === 0) {
            resultContainer.innerHTML = `
                <div class="empty-state">
                    <h3>'${teacherName}' 선생님의 배정된 시험감독 또는 정규수업이 없습니다.</h3>
                    <p>이름을 올바르게 입력했는지 확인해주세요.</p>
                </div>
            `;
            return;
        }

        const sortedSchedules = [...schedules].sort((a, b) => a.time.localeCompare(b.time));

        let html = `<h2 class="teacher-name-heading">${teacherName} 선생님 시간표 비교</h2>`;
        
        // 타임라인 추가
        html += renderTimeline(sortedSchedules, regularClasses);

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
