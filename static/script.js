import { PoseLandmarker, FilesetResolver } from "https://cdn.skypack.dev/@mediapipe/tasks-vision@0.10.0";

// ── CLASS LABELS ──
const YOGA_82_CLASSES = ['Akarna_Dhanurasana','Bharadvajas_Twist_pose_or_Bharadvajasana_I_','Boat_Pose_or_Paripurna_Navasana_','Bound_Angle_Pose_or_Baddha_Konasana_','Bow_Pose_or_Dhanurasana_','Bridge_Pose_or_Setu_Bandha_Sarvangasana_','Camel_Pose_or_Ustrasana_','Cat_Cow_Pose_or_Marjaryasana_','Chair_Pose_or_Utkatasana_','Child_Pose_or_Balasana_','Cobra_Pose_or_Bhujangasana_','Cockerel_Pose','Corpse_Pose_or_Savasana_','Cow_Face_Pose_or_Gomukhasana_','Crane_(Crow)_Pose_or_Bakasana_','Dolphin_Plank_Pose_or_Makara_Adho_Mukha_Svanasana_','Dolphin_Pose_or_Ardha_Pincha_Mayurasana_','Downward-Facing_Dog_pose_or_Adho_Mukha_Svanasana_','Eagle_Pose_or_Garudasana_','Eight-Angle_Pose_or_Astavakrasana_','Extended_Puppy_Pose_or_Uttana_Shishosana_','Extended_Revolved_Side_Angle_Pose_or_Utthita_Parsvakonasana_','Extended_Revolved_Triangle_Pose_or_Utthita_Trikonasana_','Feathered_Peacock_Pose_or_Pincha_Mayurasana_','Firefly_Pose_or_Tittibhasana_','Fish_Pose_or_Matsyasana_','Four-Limbed_Staff_Pose_or_Chaturanga_Dandasana_','Frog_Pose_or_Bhekasana','Garland_Pose_or_Malasana_','Gate_Pose_or_Parighasana_','Half_Lord_of_the_Fishes_Pose_or_Ardha_Matsyendrasana_','Half_Moon_Pose_or_Ardha_Chandrasana_','Handstand_pose_or_Adho_Mukha_Vrksasana_','Happy_Baby_Pose_or_Ananda_Balasana_','Head-to-Knee_Forward_Bend_pose_or_Janu_Sirsasana_','Heron_Pose_or_Krounchasana_','Intense_Side_Stretch_Pose_or_Parsvottanasana_','Legs-Up-the-Wall_Pose_or_Viparita_Karani_','Locust_Pose_or_Salabhasana_','Lord_of_the_Dance_Pose_or_Natarajasana_','Low_Lunge_pose_or_Anjaneyasana_','Noose_Pose_or_Pasasana_','Peacock_Pose_or_Mayurasana_','Pigeon_Pose_or_Kapotasana_','Plank_Pose_or_Kumbhakasana_','Plow_Pose_or_Halasana_','Pose_Dedicated_to_the_Sage_Koundinya_or_Eka_Pada_Koundinyanasana_I_and_II','Rajakapotasana','Reclining_Hand-to-Big-Toe_Pose_or_Supta_Padangusthasana_','Revolved_Head-to-Knee_Pose_or_Parivrtta_Janu_Sirsasana_','Scale_Pose_or_Tolasana_','Scorpion_pose_or_vrischikasana','Seated_Forward_Bend_pose_or_Paschimottanasana_','Shoulder-Pressing_Pose_or_Bhujapidasana_','Side-Reclining_Leg_Lift_pose_or_Anantasana_','Side_Crane_(Crow)_Pose_or_Parsva_Bakasana_','Side_Plank_Pose_or_Vasisthasana_','Sitting pose 1 (normal)','Split pose','Staff_Pose_or_Dandasana_','Standing_Forward_Bend_pose_or_Uttanasana_','Standing_Split_pose_or_Urdhva_Prasarita_Eka_Padasana_','Standing_big_toe_hold_pose_or_Utthita_Padangusthasana','Supported_Headstand_pose_or_Salamba_Sirsasana_','Supported_Shoulderstand_pose_or_Salamba_Sarvangasana_','Supta_Baddha_Konasana_','Supta_Virasana_Vajrasana','Tortoise_Pose','Tree_Pose_or_Vrksasana_','Upward_Bow_(Wheel)_Pose_or_Urdhva_Dhanurasana_','Upward_Facing_Two-Foot_Staff_Pose_or_Dwi_Pada_Viparita_Dandasana_','Upward_Plank_Pose_or_Purvottanasana_','Virasana_or_Vajrasana','Warrior_III_Pose_or_Virabhadrasana_III_','Warrior_II_Pose_or_Virabhadrasana_II_','Warrior_I_Pose_or_Virabhadrasana_I_','Wide-Angle_Seated_Forward_Bend_pose_or_Upavistha_Konasana_','Wide-Legged_Forward_Bend_pose_or_Prasarita_Padottanasana_','Wild_Thing_pose_or_Camatkarasana_','Wind_Relieving_pose_or_Pawanmuktasana','Yogic_sleep_pose','viparita_virabhadrasana_or_reverse_warrior_pose'];

const YOGA_16_CLASSES = ['chair_pose','dolphin_plank_pose','downward-facing_dog_pose','fish_pose','goddess_pose','locust_pose','lord_of_the_dance_pose','low_lunge_pose','seated_forward_bend_pose','side_plank_pose','staff_pose','tree_pose','warrior_1_pose','warrior_2_pose','warrior_3_pose','wide-angle_seated_forward_bend_pose'];

const YOGA_16_REFS = [
    { name: 'chair_pose',          emoji: '🪑', desc: 'Sit as if in a chair, arms up' },
    { name: 'dolphin_plank_pose',  emoji: '🐬', desc: 'Forearms on floor, body straight' },
    { name: 'downward-facing_dog_pose', emoji: '🐕', desc: 'V-shape, hips high' },
    { name: 'fish_pose',           emoji: '🐟', desc: 'Back arched, chest open' },
    { name: 'goddess_pose',        emoji: '✨', desc: 'Wide squat, arms open' },
    { name: 'locust_pose',         emoji: '🦗', desc: 'Prone, lift chest & legs' },
    { name: 'lord_of_the_dance_pose', emoji: '💃', desc: 'One leg kicked back' },
    { name: 'low_lunge_pose',      emoji: '🏃', desc: 'One knee down, lunge forward' },
    { name: 'seated_forward_bend_pose', emoji: '🧘', desc: 'Legs forward, reach toes' },
    { name: 'side_plank_pose',     emoji: '🏋️', desc: 'One arm, body sideways' },
    { name: 'staff_pose',          emoji: '🎋', desc: 'Sit upright, legs straight' },
    { name: 'tree_pose',           emoji: '🌳', desc: 'Stand on one leg, arms up' },
    { name: 'warrior_1_pose',      emoji: '⚔️', desc: 'Lunge forward, arms up' },
    { name: 'warrior_2_pose',      emoji: '🏹', desc: 'Arms out wide, lunge side' },
    { name: 'warrior_3_pose',      emoji: '🦅', desc: 'Balance on one leg, fly' },
    { name: 'wide-angle_seated_forward_bend_pose', emoji: '🦵', desc: 'Legs wide open, lean forward' },
];

const CONNECTIONS = [
    [0,1],[1,2],[2,3],[3,7],[0,4],[4,5],[5,6],[6,8],
    [9,10],[11,12],[11,13],[13,15],[15,17],[15,19],[15,21],
    [17,19],[12,14],[14,16],[16,18],[16,20],[16,22],[18,20],
    [11,23],[12,24],[23,24],[23,25],[25,27],[27,29],[27,31],
    [29,31],[24,26],[26,28],[28,30],[28,32],[30,32]
];

const ANGLE_TRIPLETS = [
    [12,14,16],[24,12,14],[11,13,15],[23,11,13],
    [24,26,28],[12,24,26],[23,25,27],[11,23,25]
];

const HIGHLIGHT_JOINTS = [11, 12, 23, 24, 25, 26];

// ── UI ELEMENTS ──
const videoEl          = document.getElementById('input-video');
const imageEl          = document.getElementById('input-image');
const canvasEl         = document.getElementById('output-canvas');
const ctx              = canvasEl.getContext('2d');
const overlayEl        = document.getElementById('status-overlay');
const overlayIcon      = document.getElementById('overlay-icon');
const overlayText      = document.getElementById('overlay-text');
const badgeEl          = document.getElementById('prediction-badge');
const downloadBtn      = document.getElementById('download-btn');
const mainActionBtn    = document.getElementById('main-action-btn');
const galleryEl        = document.getElementById('reference-gallery');
const imageUploadEl    = document.getElementById('image-upload');
const framingAlert     = document.getElementById('framing-alert');
const countdownOverlay = document.getElementById('countdown-overlay');
const countdownNumber  = document.getElementById('countdown-number');
const confidenceBar    = document.getElementById('confidence-bar');
const confidenceVal    = document.getElementById('confidence-val');

// ── STATE ──
let poseLandmarkerImage = null;
let poseLandmarkerVideo = null;
let onnxSession82  = null;
let onnxSession16  = null;
let currentModel   = 'yoga16';
let currentSource  = 'camera';
let activeStream   = null;
let animationId    = null;
let countdownTimer = null;
let isPreviewing   = false;

// ── INIT ──
async function init() {
    setOverlay('🔧', 'Loading ONNX Models...', true);

    try {
        const u82 = base64ToUint8Array(YOGA_82_ONNX_BASE64);
        const u16 = base64ToUint8Array(YOGA_16_ONNX_BASE64);
        onnxSession82 = await ort.InferenceSession.create(u82);
        onnxSession16 = await ort.InferenceSession.create(u16);

        setOverlay('🧠', 'Loading MediaPipe AI...', true);
        const vision = await FilesetResolver.forVisionTasks("https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.0/wasm");

        // Need two modes: VIDEO (for the 5s preview countdown) and IMAGE (for final uploaded photo inference)
        poseLandmarkerVideo = await PoseLandmarker.createFromOptions(vision, {
            baseOptions: { modelAssetPath: "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/1/pose_landmarker_lite.task", delegate: "CPU" },
            runningMode: "VIDEO", numPoses: 1
        });
        
        poseLandmarkerImage = await PoseLandmarker.createFromOptions(vision, {
            baseOptions: { modelAssetPath: "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/1/pose_landmarker_lite.task", delegate: "CPU" },
            runningMode: "IMAGE", numPoses: 1
        });

        setOverlay('🧘', 'Ready! Select an option on the left.', false);
        overlayIcon.style.animation = 'float 3s ease-in-out infinite';

        setupEvents();
        populateGallery();

    } catch (err) {
        setOverlay('❌', `Error: ${err.message}`, false);
        console.error(err);
    }
}

function setOverlay(icon, text, showLoading) {
    overlayEl.style.display = 'flex';
    overlayIcon.textContent = icon;
    overlayText.textContent = text;
    document.getElementById('loading-bar').style.display = showLoading ? 'block' : 'none';
}

function hideOverlay() { overlayEl.style.display = 'none'; }

// ── FEATURE COMPUTATION ──
function computeAngle3D(a, b, c) {
    const ba = [a.x-b.x, a.y-b.y, a.z-b.z];
    const bc = [c.x-b.x, c.y-b.y, c.z-b.z];
    const dot = ba[0]*bc[0]+ba[1]*bc[1]+ba[2]*bc[2];
    const nBA = Math.sqrt(ba[0]**2+ba[1]**2+ba[2]**2);
    const nBC = Math.sqrt(bc[0]**2+bc[1]**2+bc[2]**2);
    if (nBA < 1e-6 || nBC < 1e-6) return 0.0;
    return Math.acos(Math.max(-1, Math.min(1, dot/(nBA*nBC)))) * 180/Math.PI / 180.0;
}

function getPoseFeatures(landmarks) {
    const f = new Float32Array(212);
    let i = 0;
    for (let j=0; j<33; j++) { f[i++]=landmarks[j].x; f[i++]=landmarks[j].y; f[i++]=landmarks[j].z; }
    for (const [a,b,c] of ANGLE_TRIPLETS) f[i++] = computeAngle3D(landmarks[a], landmarks[b], landmarks[c]);
    for (const [u,v] of CONNECTIONS) { f[i++]=landmarks[v].x-landmarks[u].x; f[i++]=landmarks[v].y-landmarks[u].y; f[i++]=landmarks[v].z-landmarks[u].z; }
    return f;
}

// ── SYNTHETIC ROTATION (16 VIEWS) ──
function generateViews(worldLandmarks) {
    const views = [];
    const anglesDeg = [];
    for (let i = 0; i < 16; i++) {
        anglesDeg.push(-180 + i * (360 / 15)); // np.linspace(-180, 180, 16)
    }

    for (let deg of anglesDeg) {
        const theta = deg * Math.PI / 180.0;
        const c = Math.cos(theta);
        const s = Math.sin(theta);

        // Rotate all landmarks around Y-axis
        const rotated = [];
        for (let i=0; i<33; i++) {
            const pt = worldLandmarks[i];
            const rx = pt.x * c + pt.z * s;
            const ry = pt.y;
            const rz = -pt.x * s + pt.z * c;
            rotated.push({x: rx, y: ry, z: rz, visibility: pt.visibility});
        }
        
        views.push(getPoseFeatures(rotated)); // 212 length array
    }
    return views;
}

// ── INFERENCE ──
async function runInference(worldLandmarks) {
    // 1. Generate 16 rotated views from the single image
    const multiViews = generateViews(worldLandmarks);
    
    // 2. Flatten into [1, 16, 212] tensor
    const inputBuf = new Float32Array(16 * 212);
    for (let i=0; i<16; i++) inputBuf.set(multiViews[i], i*212);

    const tensor  = new ort.Tensor('float32', inputBuf, [1, 16, 212]);
    const session = currentModel === 'yoga16' ? onnxSession16 : onnxSession82;
    const results = await session.run({ input: tensor });
    const output  = results.output.data;

    // 3. Softmax for confidence
    const maxLogit = Math.max(...output);
    const exps = Array.from(output).map(v => Math.exp(v - maxLogit));
    const sumExp = exps.reduce((a,b)=>a+b, 0);
    const probs = exps.map(v => v/sumExp);

    let maxIdx = 0;
    for (let i=1; i<probs.length; i++) if (probs[i]>probs[maxIdx]) maxIdx=i;

    const classes   = currentModel === 'yoga16' ? YOGA_16_CLASSES : YOGA_82_CLASSES;
    const className = classes[maxIdx].replace(/_/g,' ').replace(/-/g,' ');
    const conf      = (probs[maxIdx] * 100).toFixed(0);

    badgeEl.textContent = className.toUpperCase();
    badgeEl.classList.add('active');

    confidenceBar.style.width = conf + '%';
    confidenceVal.textContent = conf + '%';
}

// ── DRAWING ──
function drawSkeleton(screenLandmarks, W, H) {
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(0, 0, W, H);

    ctx.lineWidth = Math.max(2, W / 200);
    ctx.strokeStyle = '#dc2626';
    ctx.lineCap = 'round';
    for (const [u, v] of CONNECTIONS) {
        const pu = screenLandmarks[u], pv = screenLandmarks[v];
        if ((pu.visibility||1) < 0.2 || (pv.visibility||1) < 0.2) continue;
        ctx.beginPath();
        ctx.moveTo(pu.x * W, pu.y * H);
        ctx.lineTo(pv.x * W, pv.y * H);
        ctx.stroke();
    }

    const r = Math.max(4, W / 150);
    ctx.fillStyle = '#16a34a';
    for (const p of screenLandmarks) {
        if ((p.visibility||1) < 0.2) continue;
        ctx.beginPath();
        ctx.arc(p.x * W, p.y * H, r, 0, 2*Math.PI);
        ctx.fill();
    }

    ctx.fillStyle = '#ff2244';
    ctx.shadowColor = '#ff2244';
    ctx.shadowBlur = 8;
    for (const j of HIGHLIGHT_JOINTS) {
        const p = screenLandmarks[j];
        if ((p.visibility||1) < 0.2) continue;
        ctx.beginPath();
        ctx.arc(p.x * W, p.y * H, r * 1.8, 0, 2*Math.PI);
        ctx.fill();
    }
    ctx.shadowBlur = 0;
}

// ── BODY FRAMING CHECK ──
function checkBodyFraming(landmarks) {
    const nose = landmarks[0], leftSho = landmarks[11], rightSho = landmarks[12];
    const leftHip = landmarks[23], rightHip = landmarks[24];
    const leftAnk = landmarks[27], rightAnk = landmarks[28];
    const visThresh = 0.5;

    const faceOnly = nose.visibility > visThresh && (leftSho.visibility < visThresh || rightSho.visibility < visThresh);
    const noLegs = (leftSho.visibility > visThresh || rightSho.visibility > visThresh) && (leftHip.visibility < visThresh || rightHip.visibility < visThresh);
    const noFeet = (leftHip.visibility > visThresh || rightHip.visibility > visThresh) && (leftAnk.visibility < visThresh && rightAnk.visibility < visThresh);

    if (faceOnly) showFramingAlert('📏 Please step back — show your full body');
    else if (noLegs) showFramingAlert('🦵 Please show full body — step further back');
    else if (noFeet) showFramingAlert('👣 Try to show your feet too for better accuracy');
    else hideFramingAlert();
}

function showFramingAlert(msg) { framingAlert.textContent = msg; framingAlert.style.display = 'block'; }
function hideFramingAlert() { framingAlert.style.display = 'none'; }

// ── CAMERA PREVIEW LOOP ──
async function previewLoop() {
    if (!isPreviewing || !poseLandmarkerVideo || !videoEl.readyState) return;

    const W = videoEl.videoWidth, H = videoEl.videoHeight;
    if (W && H) {
        if (canvasEl.width !== W || canvasEl.height !== H) {
            canvasEl.width = W; canvasEl.height = H;
        }

        let results;
        try { results = poseLandmarkerVideo.detectForVideo(videoEl, performance.now()); } catch(e) { return; }

        if (results.landmarks && results.landmarks.length > 0) {
            drawSkeleton(results.landmarks[0], W, H);
            checkBodyFraming(results.landmarks[0]);
        } else {
            ctx.fillStyle = '#ffffff'; ctx.fillRect(0, 0, W, H);
            ctx.fillStyle = '#9ca3af'; ctx.font = 'bold 24px Outfit'; ctx.textAlign = 'center';
            ctx.fillText('👤 No person detected', W/2, H/2);
            hideFramingAlert();
        }
    }
    animationId = requestAnimationFrame(previewLoop);
}

// ── ACTION FLOWS ──
async function initiateCameraCapture() {
    stopStream();
    badgeEl.textContent = 'Previewing...';
    
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: { ideal: 720, facingMode: 'user' } });
        activeStream = stream;
        videoEl.srcObject = stream;
        videoEl.src = '';
        await videoEl.play();
        
        isPreviewing = true;
        hideOverlay();
        mainActionBtn.disabled = true;
        downloadBtn.disabled = true;
        
        if (!animationId) animationId = requestAnimationFrame(previewLoop);

        // Start 5 second countdown
        countdownOverlay.style.display = 'flex';
        let count = 5;
        countdownNumber.textContent = count;
        
        countdownTimer = setInterval(async () => {
            count--;
            if (count > 0) {
                countdownNumber.textContent = count;
            } else {
                // Time's up! Freeze and capture.
                clearInterval(countdownTimer);
                countdownOverlay.style.display = 'none';
                isPreviewing = false;
                cancelAnimationFrame(animationId);
                
                await captureAndProcessWebcamFrame();
            }
        }, 1000);

    } catch(e) {
        setOverlay('🚫', `Camera error: ${e.message}`, false);
    }
}

async function captureAndProcessWebcamFrame() {
    const W = videoEl.videoWidth, H = videoEl.videoHeight;
    const results = poseLandmarkerVideo.detectForVideo(videoEl, performance.now());
    
    // Stop the camera completely
    if (activeStream) { activeStream.getTracks().forEach(t => t.stop()); activeStream = null; }
    videoEl.srcObject = null;
    hideFramingAlert();
    mainActionBtn.disabled = false;

    if (results.landmarks && results.landmarks.length > 0) {
        drawSkeleton(results.landmarks[0], W, H);
        await runInference(results.worldLandmarks[0]);
        downloadBtn.disabled = false;
    } else {
        ctx.fillStyle = '#ffffff'; ctx.fillRect(0, 0, W, H);
        badgeEl.textContent = 'No Pose Found';
        badgeEl.classList.remove('active');
        alert("No person was detected in the final frame. Please try again.");
    }
}

async function handleImageUpload(file) {
    stopStream();
    hideOverlay();
    badgeEl.textContent = 'Analyzing...';
    downloadBtn.disabled = true;

    const url = URL.createObjectURL(file);
    imageEl.src = url;
    
    imageEl.onload = async () => {
        const W = imageEl.naturalWidth, H = imageEl.naturalHeight;
        canvasEl.width = W; canvasEl.height = H;

        // Process image directly
        const results = poseLandmarkerImage.detect(imageEl);
        
        if (results.landmarks && results.landmarks.length > 0) {
            drawSkeleton(results.landmarks[0], W, H);
            await runInference(results.worldLandmarks[0]);
            downloadBtn.disabled = false;
        } else {
            ctx.fillStyle = '#ffffff'; ctx.fillRect(0, 0, W, H);
            badgeEl.textContent = 'No Pose Found';
            badgeEl.classList.remove('active');
            alert("No person was detected in the uploaded image.");
        }
    };
}

function stopStream() {
    isPreviewing = false;
    cancelAnimationFrame(animationId);
    clearInterval(countdownTimer);
    countdownOverlay.style.display = 'none';
    hideFramingAlert();
    
    if (activeStream) { activeStream.getTracks().forEach(t => t.stop()); activeStream = null; }
    videoEl.srcObject = null;
    
    badgeEl.textContent = 'Waiting for input...';
    badgeEl.classList.remove('active');
    confidenceBar.style.width = '0%';
    confidenceVal.textContent = '--';
    downloadBtn.disabled = true;
    mainActionBtn.disabled = false;
}

// ── EVENTS ──
function setupEvents() {
    document.querySelectorAll('input[name="model"]').forEach(r => {
        r.addEventListener('change', e => {
            document.querySelectorAll('input[name="model"]').forEach(i => i.closest('.radio-card').classList.remove('active'));
            e.target.closest('.radio-card').classList.add('active');
            currentModel = e.target.value;
            populateGallery();
            stopStream();
            ctx.clearRect(0,0, canvasEl.width, canvasEl.height);
        });
    });

    document.querySelectorAll('input[name="input-source"]').forEach(r => {
        r.addEventListener('change', e => {
            document.querySelectorAll('input[name="input-source"]').forEach(i => i.closest('.radio-card').classList.remove('active'));
            e.target.closest('.radio-card').classList.add('active');
            currentSource = e.target.value;
            stopStream();
            ctx.clearRect(0,0, canvasEl.width, canvasEl.height);
            
            if (currentSource === 'camera') {
                mainActionBtn.innerHTML = '<span>📸</span> Start Camera (5s Delay)';
                mainActionBtn.classList.remove('uploading');
            } else {
                mainActionBtn.innerHTML = '<span>🖼️</span> Select Photo to Upload';
                mainActionBtn.classList.add('uploading');
            }
        });
    });

    mainActionBtn.addEventListener('click', () => {
        if (currentSource === 'camera') {
            initiateCameraCapture();
        } else {
            imageUploadEl.click();
        }
    });

    imageUploadEl.addEventListener('change', e => {
        if (e.target.files.length > 0) handleImageUpload(e.target.files[0]);
    });

    downloadBtn.addEventListener('click', () => {
        const link = document.createElement('a');
        link.download = `skeleton_result_${currentModel}.png`;
        link.href = canvasEl.toDataURL('image/png');
        link.click();
    });
}

// ── GALLERY ──
function populateGallery() {
    galleryEl.innerHTML = '';
    if (currentModel === 'yoga16') {
        document.getElementById('gallery-container').style.display = 'block';
        YOGA_16_REFS.forEach(ref => {
            const card = document.createElement('div');
            card.className = 'pose-card';
            card.innerHTML = `<span class="pose-emoji">${ref.emoji}</span><span class="pose-name">${ref.name.replace(/_/g,' ')}</span>`;
            card.title = ref.desc;
            galleryEl.appendChild(card);
        });
    } else {
        document.getElementById('gallery-container').style.display = 'none';
    }
}

function base64ToUint8Array(b64) {
    const bin = atob(b64);
    const buf = new Uint8Array(bin.length);
    for (let i=0; i<bin.length; i++) buf[i] = bin.charCodeAt(i);
    return buf;
}

window.addEventListener('load', init);
