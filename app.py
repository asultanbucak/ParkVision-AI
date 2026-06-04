import streamlit as st
from ultralytics import YOLO
from PIL import Image
import numpy as np
import cv2

st.set_page_config(page_title="ParkVision AI", page_icon="🚗", layout="wide")

st.markdown("""
<style>
.stApp { background: #0B1020; color: #E5E7EB; }
[data-testid="stHeader"] { background: transparent; }

.hero {
    padding: 35px;
    border-radius: 28px;
    background: radial-gradient(circle at top left, #2563EB 0%, #111827 45%, #020617 100%);
    border: 1px solid rgba(255,255,255,.12);
    margin-bottom: 24px;
}
.hero h1 {
    font-size: 58px;
    margin: 0;
    font-weight: 900;
}
.hero p {
    font-size: 19px;
    color: #CBD5E1;
    max-width: 850px;
}

.panel {
    background: rgba(255,255,255,.06);
    border: 1px solid rgba(255,255,255,.12);
    border-radius: 24px;
    padding: 24px;
    height: 100%;
}

.big-number {
    font-size: 46px;
    font-weight: 900;
    margin: 0;
}

.label {
    color: #94A3B8;
    font-size: 15px;
}

.status {
    padding: 18px;
    border-radius: 18px;
    background: rgba(37,99,235,.18);
    border: 1px solid rgba(96,165,250,.25);
    font-size: 20px;
    font-weight: 700;
}

.upload-box {
    padding: 25px;
    border-radius: 22px;
    background: rgba(15,23,42,.9);
    border: 1px dashed rgba(148,163,184,.6);
}
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_model():
    return YOLO("best.pt")

model = load_model()

st.markdown("""
<div class="hero">
    <h1>ParkVision AI</h1>
    <p>
        YOLO tabanlı akıllı otopark doluluk analiz sistemi.
        Görüntüden araçları ve boş park alanlarını tespit eder, doluluk oranını anlık olarak hesaplar.
    </p>
</div>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "📸 Analiz edilecek otopark görselini seç",
    type=["jpg", "jpeg", "png"]
)

if uploaded_file is None:
    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("""
        <div class="panel">
            <p class="big-number">01</p>
            <p class="label">Görsel yükle</p>
            <p>Otopark alanına ait bir fotoğraf seç.</p>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown("""
        <div class="panel">
            <p class="big-number">02</p>
            <p class="label">Model analiz etsin</p>
            <p>YOLO modeli dolu ve boş alanları tespit eder.</p>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown("""
        <div class="panel">
            <p class="big-number">03</p>
            <p class="label">Sonucu görüntüle</p>
            <p>Doluluk oranı ve işaretlenmiş görsel ekranda gösterilir.</p>
        </div>
        """, unsafe_allow_html=True)

else:
    image = Image.open(uploaded_file).convert("RGB")
    img = np.array(image)

    with st.spinner("Park alanı analiz ediliyor..."):
        results = model(img, conf=0.2 , imgsz=640)

    annotated = results[0].plot()
    annotated = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)

    car_count = 0
    empty_count = 0

    for box in results[0].boxes:
        cls = int(box.cls[0])
        if cls == 0:
            car_count += 1
        elif cls == 1:
            empty_count += 1

    total = car_count + empty_count
    occupancy = (car_count / total) * 100 if total > 0 else 0

    if occupancy >= 80:
        status = "Yoğun Doluluk"
    elif occupancy >= 50:
        status = "Orta Doluluk"
    else:
        status = "Uygun Kapasite"

    top1, top2, top3, top4 = st.columns(4)

    with top1:
        st.markdown(f"""
        <div class="panel">
            <p class="label">Doluluk Oranı</p>
            <p class="big-number">%{occupancy:.1f}</p>
        </div>
        """, unsafe_allow_html=True)

    with top2:
        st.markdown(f"""
        <div class="panel">
            <p class="label">Dolu Alan</p>
            <p class="big-number">{car_count}</p>
        </div>
        """, unsafe_allow_html=True)

    with top3:
        st.markdown(f"""
        <div class="panel">
            <p class="label">Boş Alan</p>
            <p class="big-number">{empty_count}</p>
        </div>
        """, unsafe_allow_html=True)

    with top4:
        st.markdown(f"""
        <div class="panel">
            <p class="label">Toplam Tespit</p>
            <p class="big-number">{total}</p>
        </div>
        """, unsafe_allow_html=True)

    st.progress(int(occupancy))

    st.markdown(f"""
    <div class="status">
        Genel Durum: {status}
    </div>
    """, unsafe_allow_html=True)

    st.write("")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Orijinal Görsel")
        st.image(image, use_container_width=True)

    with col2:
        st.markdown("### Yapay Zeka Analizi")
        st.image(annotated, use_container_width=True)