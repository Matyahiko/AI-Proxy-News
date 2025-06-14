let transcriptSpans = [];
let questionsShown = new Set();
let questionsData = [];

window.addEventListener('DOMContentLoaded', () => {
    fetch('/assets/data/kaiken.json').then(r => r.json()).then(setupDemo);

    document.querySelectorAll('.video-selector').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.video-selector').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            fetch(btn.dataset.src).then(r => r.json()).then(setupDemo);
        });
    });

    document.querySelectorAll('.tab-button').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.tab-button').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
            btn.classList.add('active');
            document.getElementById(btn.dataset.target).classList.add('active');
        });
    });
});

function setupDemo(data) {
    const video = document.getElementById('video-player');
    video.src = data.videoUrl;
    transcriptSpans = [];
    questionsShown.clear();
    questionsData = data.questions;

    const tArea = document.getElementById('transcript-area');
    tArea.innerHTML = '';
    data.transcript.forEach(item => {
        const span = document.createElement('span');
        span.textContent = item.text + ' ';
        span.dataset.start = item.start;
        span.dataset.end = item.end;
        tArea.appendChild(span);
        transcriptSpans.push(span);
    });

    const mArea = document.getElementById('mock-questions-area');
    mArea.innerHTML = '';
    data.questions.forEach(q => {
        const p = document.createElement('p');
        p.textContent = q.question;
        const ta = document.createElement('textarea');
        ta.disabled = true;
        mArea.appendChild(p);
        mArea.appendChild(ta);
    });

    const qList = document.getElementById('questions-list');
    qList.innerHTML = '';

    video.ontimeupdate = () => {
        const current = video.currentTime;
        transcriptSpans.forEach(span => {
            if (current >= parseFloat(span.dataset.start) && current <= parseFloat(span.dataset.end)) {
                span.classList.add('current-transcript');
            } else {
                span.classList.remove('current-transcript');
            }
        });

        data.questions.forEach((q, idx) => {
            if (current >= q.timestamp && !questionsShown.has(idx)) {
                const li = document.createElement('li');
                li.textContent = q.question;
                li.addEventListener('click', () => {
                    video.currentTime = q.timestamp;
                });
                qList.appendChild(li);
                questionsShown.add(idx);
            }
        });
    };
}
