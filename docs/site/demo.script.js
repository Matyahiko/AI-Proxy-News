let transcriptSpans = [];
let questionsShown = new Set();
let ws = null;
let recorder = null;

window.addEventListener('DOMContentLoaded', () => {
    const video = document.getElementById('video-player');
    const btnContainer = document.getElementById('video-buttons');
    const themeToggle = document.getElementById('theme-toggle');

    themeToggle.addEventListener('click', () => {
        document.body.classList.toggle('dark');
        themeToggle.textContent =
            document.body.classList.contains('dark') ? 'ライトモード' : 'ダークモード';
    });

    fetch('assets/data/video_list.json')
        .then(r => r.json())
        .then(list => {
            list.forEach((name, idx) => {
                const btn = document.createElement('button');
                btn.textContent = name;
                btn.className = 'video-selector';
                btnContainer.appendChild(btn);
                if (idx === 0) {
                    btn.classList.add('active');
                    setVideo(name);
                }
                btn.addEventListener('click', () => {
                    document.querySelectorAll('.video-selector').forEach(b => b.classList.remove('active'));
                    btn.classList.add('active');
                    setVideo(name);
                });
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

function setVideo(name) {
    const video = document.getElementById('video-player');
    video.src = '/data/' + name;
    setupRealtime(video);
    const base = name.replace(/\.[^.]+$/, '');
    fetch('assets/data/' + base + '.json')
        .then(r => r.ok ? r.json() : null)
        .then(data => {
            if (data) {
                setupDemo(data);
            } else {
                clearPanels();
            }
        });
}

function clearPanels() {
    const video = document.getElementById('video-player');
    video.ontimeupdate = null;
    if (recorder) {
        recorder.stop();
        recorder = null;
    }
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.close();
    }
    transcriptSpans = [];
    questionsShown.clear();
    document.getElementById('transcript-area').innerHTML = '';
    document.getElementById('mock-questions-area').innerHTML = '';
    document.getElementById('questions-list').innerHTML = '';
}

function setupRealtime(video) {
    video.onplay = () => {
        if (ws && ws.readyState === WebSocket.OPEN) return;
        ws = new WebSocket('ws://localhost:7001');
        ws.onmessage = e => {
            if (e.data === 'READY') {
                console.log('ASR server ready');
                startRecorder(video);
            } else {
                addTranscriptLine(e.data);
            }
        };
    };
    video.onpause = stopRecorder;
    video.onended = stopRecorder;
}

function startRecorder(video) {
    const stream = video.captureStream();
    const audioStream = new MediaStream(stream.getAudioTracks());
    // Record directly in WebM/Opus. The server will forward this stream
    // to Google Speech-to-Text.
    recorder = new MediaRecorder(audioStream, {mimeType: 'audio/webm;codecs=opus'});
    recorder.ondataavailable = async e => {
        if (e.data.size > 0 && ws && ws.readyState === WebSocket.OPEN) {
            const buf = await e.data.arrayBuffer();
            ws.send(buf);
        }
    };
    console.log('Recorder started');
    recorder.start(250);
}

function stopRecorder() {
    if (recorder) {
        recorder.stop();
        recorder = null;
    }
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send('EOS');
    }
    console.log('Recorder stopped');
}

function addTranscriptLine(text) {
    const area = document.getElementById('transcript-area');
    const lines = area.textContent.split('\n').filter(l => l);
    lines.push(text.trim());
    while (lines.length > 5) lines.shift();
    area.textContent = lines.join('\n');
}

function setupDemo(data) {
    const video = document.getElementById('video-player');
    transcriptSpans = [];
    questionsShown.clear();

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
                const timeStr = new Date(q.timestamp * 1000).toISOString().substr(14, 5);
                li.textContent = `[${timeStr}] ${q.question}`;
                li.addEventListener('click', () => {
                    video.currentTime = q.timestamp;
                });
                qList.appendChild(li);
                questionsShown.add(idx);
            }
        });
    };
}
