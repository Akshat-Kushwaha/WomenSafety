// WebSocket client for video streaming
class VideoStreamClient {
    constructor() {
        this.socket = null;
        this.canvas = document.getElementById('videoCanvas');
        this.ctx = this.canvas.getContext('2d');
        this.isConnected = false;
        this.isStreaming = false;
        this.frameCount = 0;
        this.fps = 0;
        this.lastFpsUpdate = Date.now();
        
        this.initializeSocket();
        this.setupEventListeners();
        this.startFpsCounter();
    }

    initializeSocket() {
        // Connect to WebSocket server
        this.socket = io();

        this.socket.on('connect', () => {
            this.updateConnectionStatus('connected', 'Connected to server');
            this.isConnected = true;
        });

        this.socket.on('disconnect', () => {
            this.updateConnectionStatus('disconnected', 'Disconnected from server');
            this.isConnected = false;
            this.isStreaming = false;
            this.updateStreamControls();
        });

        this.socket.on('connection_response', (data) => {
            console.log('Server response:', data);
        });

        this.socket.on('video_frame', (data) => {
            this.displayFrame(data.frame);
            this.frameCount++;
        });

        this.socket.on('stream_status', (data) => {
            this.handleStreamStatus(data);
        });

        this.socket.on('video_info', (data) => {
            this.displayVideoInfo(data);
        });
    }

    setupEventListeners() {
        // Handle page unload
        window.addEventListener('beforeunload', () => {
            if (this.socket) {
                this.socket.disconnect();
            }
        });

        // Handle canvas click for play/pause (placeholder)
        this.canvas.addEventListener('click', () => {
            if (this.isStreaming) {
                // Add play/pause functionality if needed
            }
        });
    }

    displayFrame(frameData) {
        const img = new Image();
        img.onload = () => {
            this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
            this.ctx.drawImage(img, 0, 0, this.canvas.width, this.canvas.height);
        };
        img.src = `data:image/jpeg;base64,${frameData}`;
    }

    startStream() {
        if (!this.isConnected) {
            alert('Not connected to server');
            return;
        }

        const videoSelect = document.getElementById('videoSelect');
        const selectedVideo = videoSelect.value;

        this.socket.emit('start_stream', { video: selectedVideo });
    }

    stopStream() {
        if (this.isConnected) {
            this.socket.emit('stop_stream');
        }
    }

    getVideoInfo() {
        if (!this.isConnected) {
            alert('Not connected to server');
            return;
        }

        const videoSelect = document.getElementById('videoSelect');
        const selectedVideo = videoSelect.value;

        this.socket.emit('get_video_info', { video: selectedVideo });
    }

    handleStreamStatus(data) {
        const statusElement = document.getElementById('streamStatus');
        
        switch (data.status) {
            case 'started':
                this.isStreaming = true;
                statusElement.textContent = `Streaming: ${data.video}`;
                statusElement.className = 'status streaming';
                this.updateStreamControls();
                break;
            case 'stopped':
                this.isStreaming = false;
                statusElement.textContent = 'Stream stopped';
                statusElement.className = 'status';
                this.updateStreamControls();
                // Clear canvas
                this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
                break;
            case 'error':
                this.isStreaming = false;
                statusElement.textContent = `Error: ${data.message || 'Unknown error'}`;
                statusElement.className = 'status disconnected';
                this.updateStreamControls();
                break;
        }
    }

    updateConnectionStatus(status, message) {
        const statusElement = document.getElementById('connectionStatus');
        statusElement.textContent = message;
        statusElement.className = `status ${status}`;
    }

    updateStreamControls() {
        const startBtn = document.getElementById('startBtn');
        const stopBtn = document.getElementById('stopBtn');

        startBtn.disabled = !this.isConnected || this.isStreaming;
        stopBtn.disabled = !this.isConnected || !this.isStreaming;
    }

    displayVideoInfo(info) {
        const infoElement = document.getElementById('videoInfo');
        infoElement.innerHTML = `
            <strong>Video Information:</strong><br>
            FPS: ${info.fps.toFixed(2)}<br>
            Frames: ${Math.round(info.frame_count)}<br>
            Duration: ${info.duration.toFixed(2)} seconds
        `;
    }

    startFpsCounter() {
        setInterval(() => {
            const now = Date.now();
            const delta = (now - this.lastFpsUpdate) / 1000;
            this.fps = this.frameCount / delta;
            
            document.getElementById('fpsCounter').textContent = this.fps.toFixed(1);
            document.getElementById('frameCounter').textContent = this.frameCount;
            
            this.frameCount = 0;
            this.lastFpsUpdate = now;
        }, 1000);
    }
}

// Global functions for HTML buttons
let videoClient;

function startStream() {
    videoClient.startStream();
}

function stopStream() {
    videoClient.stopStream();
}

function getVideoInfo() {
    videoClient.getVideoInfo();
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', () => {
    videoClient = new VideoStreamClient();
});