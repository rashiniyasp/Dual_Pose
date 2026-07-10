const YOGA_82_CLASSES = ['Akarna_Dhanurasana', 'Bharadvajas_Twist_pose_or_Bharadvajasana_I_', 'Boat_Pose_or_Paripurna_Navasana_', 'Bound_Angle_Pose_or_Baddha_Konasana_', 'Bow_Pose_or_Dhanurasana_', 'Bridge_Pose_or_Setu_Bandha_Sarvangasana_', 'Camel_Pose_or_Ustrasana_', 'Cat_Cow_Pose_or_Marjaryasana_', 'Chair_Pose_or_Utkatasana_', 'Child_Pose_or_Balasana_', 'Cobra_Pose_or_Bhujangasana_', 'Cockerel_Pose', 'Corpse_Pose_or_Savasana_', 'Cow_Face_Pose_or_Gomukhasana_', 'Crane_(Crow)_Pose_or_Bakasana_', 'Dolphin_Plank_Pose_or_Makara_Adho_Mukha_Svanasana_', 'Dolphin_Pose_or_Ardha_Pincha_Mayurasana_', 'Downward-Facing_Dog_pose_or_Adho_Mukha_Svanasana_', 'Eagle_Pose_or_Garudasana_', 'Eight-Angle_Pose_or_Astavakrasana_', 'Extended_Puppy_Pose_or_Uttana_Shishosana_', 'Extended_Revolved_Side_Angle_Pose_or_Utthita_Parsvakonasana_', 'Extended_Revolved_Triangle_Pose_or_Utthita_Trikonasana_', 'Feathered_Peacock_Pose_or_Pincha_Mayurasana_', 'Firefly_Pose_or_Tittibhasana_', 'Fish_Pose_or_Matsyasana_', 'Four-Limbed_Staff_Pose_or_Chaturanga_Dandasana_', 'Frog_Pose_or_Bhekasana', 'Garland_Pose_or_Malasana_', 'Gate_Pose_or_Parighasana_', 'Half_Lord_of_the_Fishes_Pose_or_Ardha_Matsyendrasana_', 'Half_Moon_Pose_or_Ardha_Chandrasana_', 'Handstand_pose_or_Adho_Mukha_Vrksasana_', 'Happy_Baby_Pose_or_Ananda_Balasana_', 'Head-to-Knee_Forward_Bend_pose_or_Janu_Sirsasana_', 'Heron_Pose_or_Krounchasana_', 'Intense_Side_Stretch_Pose_or_Parsvottanasana_', 'Legs-Up-the-Wall_Pose_or_Viparita_Karani_', 'Locust_Pose_or_Salabhasana_', 'Lord_of_the_Dance_Pose_or_Natarajasana_', 'Low_Lunge_pose_or_Anjaneyasana_', 'Noose_Pose_or_Pasasana_', 'Peacock_Pose_or_Mayurasana_', 'Pigeon_Pose_or_Kapotasana_', 'Plank_Pose_or_Kumbhakasana_', 'Plow_Pose_or_Halasana_', 'Pose_Dedicated_to_the_Sage_Koundinya_or_Eka_Pada_Koundinyanasana_I_and_II', 'Rajakapotasana', 'Reclining_Hand-to-Big-Toe_Pose_or_Supta_Padangusthasana_', 'Revolved_Head-to-Knee_Pose_or_Parivrtta_Janu_Sirsasana_', 'Scale_Pose_or_Tolasana_', 'Scorpion_pose_or_vrischikasana', 'Seated_Forward_Bend_pose_or_Paschimottanasana_', 'Shoulder-Pressing_Pose_or_Bhujapidasana_', 'Side-Reclining_Leg_Lift_pose_or_Anantasana_', 'Side_Crane_(Crow)_Pose_or_Parsva_Bakasana_', 'Side_Plank_Pose_or_Vasisthasana_', 'Sitting pose 1 (normal)', 'Split pose', 'Staff_Pose_or_Dandasana_', 'Standing_Forward_Bend_pose_or_Uttanasana_', 'Standing_Split_pose_or_Urdhva_Prasarita_Eka_Padasana_', 'Standing_big_toe_hold_pose_or_Utthita_Padangusthasana', 'Supported_Headstand_pose_or_Salamba_Sirsasana_', 'Supported_Shoulderstand_pose_or_Salamba_Sarvangasana_', 'Supta_Baddha_Konasana_', 'Supta_Virasana_Vajrasana', 'Tortoise_Pose', 'Tree_Pose_or_Vrksasana_', 'Upward_Bow_(Wheel)_Pose_or_Urdhva_Dhanurasana_', 'Upward_Facing_Two-Foot_Staff_Pose_or_Dwi_Pada_Viparita_Dandasana_', 'Upward_Plank_Pose_or_Purvottanasana_', 'Virasana_or_Vajrasana', 'Warrior_III_Pose_or_Virabhadrasana_III_', 'Warrior_II_Pose_or_Virabhadrasana_II_', 'Warrior_I_Pose_or_Virabhadrasana_I_', 'Wide-Angle_Seated_Forward_Bend_pose_or_Upavistha_Konasana_', 'Wide-Legged_Forward_Bend_pose_or_Prasarita_Padottanasana_', 'Wild_Thing_pose_or_Camatkarasana_', 'Wind_Relieving_pose_or_Pawanmuktasana', 'Yogic_sleep_pose', 'viparita_virabhadrasana_or_reverse_warrior_pose'];
const YOGA_16_CLASSES = ['chair_pose', 'dolphin_plank_pose', 'downward-facing_dog_pose', 'fish_pose', 'goddess_pose', 'locust_pose', 'lord_of_the_dance_pose', 'low_lunge_pose', 'seated_forward_bend_pose', 'side_plank_pose', 'staff_pose', 'tree_pose', 'warrior_1_pose', 'warrior_2_pose', 'warrior_3_pose', 'wide-angle_seated_forward_bend_pose'];

// DUAL-Pose Configuration
const CONNECTIONS = [
    [0, 1], [1, 2], [2, 3], [3, 7], [0, 4], [4, 5], [5, 6], [6, 8],
    [9, 10], [11, 12], [11, 13], [13, 15], [15, 17], [15, 19], [15, 21],
    [17, 19], [12, 14], [14, 16], [16, 18], [16, 20], [16, 22], [18, 20],
    [11, 23], [12, 24], [23, 24], [23, 25], [25, 27], [27, 29], [27, 31],
    [29, 31], [24, 26], [26, 28], [28, 30], [28, 32], [30, 32]
];

const ANGLE_TRIPLETS = [
    [12, 14, 16], [24, 12, 14], [11, 13, 15], [23, 11, 13],
    [24, 26, 28], [12, 24, 26], [23, 25, 27], [11, 23, 25]
];

// UI Elements
const videoEl = document.getElementById('input-video');
const canvasEl = document.getElementById('output-canvas');
const ctx = canvasEl.getContext('2d');
const overlayEl = document.getElementById('status-overlay');
const badgeEl = document.getElementById('prediction-badge');
const recordBtn = document.getElementById('record-btn');
const galleryEl = document.getElementById('reference-gallery');
const videoUploadEl = document.getElementById('video-upload');

// Global State
let poseLandmarker;
let onnxSession82;
let onnxSession16;
let currentModel = 'yoga16';
let featureBuffer = [];
let isRecording = false;
let mediaRecorder;
let recordedChunks = [];
let lastVideoTime = -1;
let animationId;

// Initialize System
async function init() {
    overlayEl.innerHTML = '<p>Loading ONNX Models...</p>';
    
    // Load ONNX Sessions from Base64
    const u82 = base64ToUint8Array(YOGA_82_ONNX_BASE64);
    const u16 = base64ToUint8Array(YOGA_16_ONNX_BASE64);
    onnxSession82 = await ort.InferenceSession.create(u82);
    onnxSession16 = await ort.InferenceSession.create(u16);
    
    overlayEl.innerHTML = '<p>Loading MediaPipe Tasks...</p>';
    const vision = await FilesetResolver.forVisionTasks(
        "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision/wasm"
    );
    
    poseLandmarker = await PoseLandmarker.createFromOptions(vision, {
        baseOptions: {
            modelAssetPath: "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/1/pose_landmarker_lite.task",
            delegate: "GPU"
        },
        runningMode: "VIDEO",
        numPoses: 1
    });

    overlayEl.style.display = 'none';
    setupEvents();
    populateGallery();
    startWebcam(); // default to webcam
}

// -----------------------------
// Core DUAL-Pose Math logic
// -----------------------------
function computeAngle3D(a, b, c) {
    const ba = [a.x - b.x, a.y - b.y, a.z - b.z];
    const bc = [c.x - b.x, c.y - b.y, c.z - b.z];
    
    const dot = ba[0]*bc[0] + ba[1]*bc[1] + ba[2]*bc[2];
    const normBA = Math.sqrt(ba[0]*ba[0] + ba[1]*ba[1] + ba[2]*ba[2]);
    const normBC = Math.sqrt(bc[0]*bc[0] + bc[1]*bc[1] + bc[2]*bc[2]);
    
    if (normBA < 1e-6 || normBC < 1e-6) return 0.0;
    
    let cosAngle = dot / (normBA * normBC);
    cosAngle = Math.max(-1.0, Math.min(1.0, cosAngle));
    return (Math.acos(cosAngle) * 180 / Math.PI) / 180.0;
}

function getPoseFeaturesDynamic(landmarks) {
    const features = new Float32Array(212);
    let idx = 0;
    
    // 1. Coords (99)
    for (let i = 0; i < 33; i++) {
        features[idx++] = landmarks[i].x;
        features[idx++] = landmarks[i].y;
        features[idx++] = landmarks[i].z;
    }
    
    // 2. Angles (8)
    for (let i = 0; i < ANGLE_TRIPLETS.length; i++) {
        const [a, b, c] = ANGLE_TRIPLETS[i];
        features[idx++] = computeAngle3D(landmarks[a], landmarks[b], landmarks[c]);
    }
    
    // 3. Bones (105)
    for (let i = 0; i < CONNECTIONS.length; i++) {
        const [u, v] = CONNECTIONS[i];
        features[idx++] = landmarks[v].x - landmarks[u].x;
        features[idx++] = landmarks[v].y - landmarks[u].y;
        features[idx++] = landmarks[v].z - landmarks[u].z;
    }
    
    return features;
}

// -----------------------------
// Inference Pipeline
// -----------------------------
async function runInference(landmarks) {
    const features = getPoseFeaturesDynamic(landmarks);
    
    // Buffer last 16 frames
    featureBuffer.push(features);
    if (featureBuffer.length > 16) {
        featureBuffer.shift();
    }
    
    if (featureBuffer.length === 16) {
        // Flatten into [1, 16, 212]
        const inputBuffer = new Float32Array(16 * 212);
        for(let i=0; i<16; i++) {
            inputBuffer.set(featureBuffer[i], i * 212);
        }
        
        const tensor = new ort.Tensor('float32', inputBuffer, [1, 16, 212]);
        const session = currentModel === 'yoga16' ? onnxSession16 : onnxSession82;
        const results = await session.run({ input: tensor });
        const output = results.output.data; // Float32Array
        
        // Argmax
        let maxIdx = 0;
        let maxVal = output[0];
        for(let i=1; i<output.length; i++) {
            if(output[i] > maxVal) { maxVal = output[i]; maxIdx = i; }
        }
        
        const className = currentModel === 'yoga16' ? YOGA_16_CLASSES[maxIdx] : YOGA_82_CLASSES[maxIdx];
        badgeEl.innerText = className.replace(/_/g, ' ').toUpperCase();
    }
}

// -----------------------------
// Main Video Loop
// -----------------------------
async function renderLoop() {
    if (!videoEl.videoWidth) {
        animationId = requestAnimationFrame(renderLoop);
        return;
    }
    
    canvasEl.width = videoEl.videoWidth;
    canvasEl.height = videoEl.videoHeight;
    
    let startTimeMs = performance.now();
    if (lastVideoTime !== videoEl.currentTime) {
        lastVideoTime = videoEl.currentTime;
        const results = poseLandmarker.detectForVideo(videoEl, startTimeMs);
        
        // Draw White Canvas
        ctx.fillStyle = '#ffffff';
        ctx.fillRect(0, 0, canvasEl.width, canvasEl.height);
        
        if (results.landmarks && results.landmarks.length > 0) {
            const screenMarks = results.landmarks[0]; // For drawing (x, y normalized)
            const worldMarks = results.worldLandmarks[0]; // For AI model
            
            // Draw skeleton (Red connections, Green nodes)
            ctx.lineWidth = 4;
            ctx.strokeStyle = '#ef4444'; // Red bones
            for (const [u, v] of CONNECTIONS) {
                const pu = screenMarks[u];
                const pv = screenMarks[v];
                ctx.beginPath();
                ctx.moveTo(pu.x * canvasEl.width, pu.y * canvasEl.height);
                ctx.lineTo(pv.x * canvasEl.width, pv.y * canvasEl.height);
                ctx.stroke();
            }
            
            ctx.fillStyle = '#10b981'; // Green joints
            for (const p of screenMarks) {
                ctx.beginPath();
                ctx.arc(p.x * canvasEl.width, p.y * canvasEl.height, 6, 0, 2*Math.PI);
                ctx.fill();
            }
            
            // Highlight explainability joints (Shoulders, Hips, Knees)
            ctx.fillStyle = '#ff3366';
            const highlightJoints = [11, 12, 23, 24, 25, 26]; 
            for(let j of highlightJoints) {
                const p = screenMarks[j];
                ctx.beginPath();
                ctx.arc(p.x * canvasEl.width, p.y * canvasEl.height, 10, 0, 2*Math.PI);
                ctx.fill();
            }
            
            await runInference(worldMarks);
        }
    }
    
    animationId = requestAnimationFrame(renderLoop);
}

// -----------------------------
// Media Control Helpers
// -----------------------------
async function startWebcam() {
    videoEl.src = '';
    videoEl.srcObject = null;
    const stream = await navigator.mediaDevices.getUserMedia({ video: true });
    videoEl.srcObject = stream;
    if(!animationId) renderLoop();
}

function startVideoFile(file) {
    videoEl.srcObject = null;
    videoEl.src = URL.createObjectURL(file);
    videoEl.play();
    if(!animationId) renderLoop();
}

function toggleRecording() {
    if (isRecording) {
        mediaRecorder.stop();
        recordBtn.innerHTML = '<span class="icon">⏺</span> Record Privacy Video';
        recordBtn.classList.remove('recording');
        isRecording = false;
    } else {
        const stream = canvasEl.captureStream(30);
        mediaRecorder = new MediaRecorder(stream, { mimeType: 'video/webm' });
        
        mediaRecorder.ondataavailable = e => {
            if (e.data.size > 0) recordedChunks.push(e.data);
        };
        
        mediaRecorder.onstop = () => {
            const blob = new Blob(recordedChunks, { type: 'video/webm' });
            recordedChunks = [];
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `skeleton_privacy_yoga_${currentModel}.webm`;
            a.click();
        };
        
        mediaRecorder.start();
        recordBtn.innerHTML = '<span class="icon">⏹</span> Stop & Save Video';
        recordBtn.classList.add('recording');
        isRecording = true;
    }
}

// -----------------------------
// UI Events
// -----------------------------
function setupEvents() {
    document.querySelectorAll('input[name="model"]').forEach(rad => {
        rad.addEventListener('change', (e) => {
            document.querySelectorAll('input[name="model"]').forEach(r => r.parentElement.classList.remove('active'));
            e.target.parentElement.classList.add('active');
            currentModel = e.target.value;
            featureBuffer = []; // reset buffer on model swap
            populateGallery();
        });
    });

    document.querySelectorAll('input[name="input-source"]').forEach(rad => {
        rad.addEventListener('change', (e) => {
            document.querySelectorAll('input[name="input-source"]').forEach(r => r.parentElement.classList.remove('active'));
            e.target.parentElement.classList.add('active');
            
            if (e.target.value === 'live') {
                startWebcam();
            } else {
                videoUploadEl.click();
            }
        });
    });

    videoUploadEl.addEventListener('change', (e) => {
        if(e.target.files.length > 0) {
            startVideoFile(e.target.files[0]);
        }
    });

    recordBtn.addEventListener('click', toggleRecording);
}

// -----------------------------
// Gallery Population
// -----------------------------
function populateGallery() {
    galleryEl.innerHTML = '';
    if (currentModel === 'yoga16') {
        document.getElementById('gallery-container').style.display = 'block';
        // Display a subset of Yoga 16 references
        const sampleClasses = ['chair_pose', 'tree_pose', 'goddess_pose', 'warrior_2_pose'];
        sampleClasses.forEach(cls => {
            const img = document.createElement('img');
            // Look for any image in the local assets folder for that class
            // Note: Since we are running on file:// without a server to list directories,
            // we will attempt to load a generic 1.jpg if it exists, or handle fallback.
            img.src = `../../assets/${cls}/1.jpg`; // Assuming standard naming, adjust if needed
            img.onerror = () => img.style.display = 'none';
            img.title = cls.replace(/_/g, ' ');
            galleryEl.appendChild(img);
        });
    } else {
        document.getElementById('gallery-container').style.display = 'none';
    }
}

const { FilesetResolver, PoseLandmarker } = window;
window.onload = init;
