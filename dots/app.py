import streamlit as st
from PIL import Image
import io

# ASCII characters for standard mode
ASCII_CHARS = "@%#*+=-:. "

def scale_image(image, new_width, mode_multiplier=0.5):
    (original_width, original_height) = image.size
    aspect_ratio = original_height / float(original_width)
    new_height = int(aspect_ratio * new_width * mode_multiplier)
    new_image = image.resize((new_width, new_height))
    return new_image

def convert_to_grayscale(image):
    return image.convert("L")

def pixels_to_ascii(image):
    pixels = image.getdata()
    characters = "".join([ASCII_CHARS[pixel // (256 // len(ASCII_CHARS))] for pixel in pixels])
    return characters

def pixels_to_research_dots(image, opaque_char="▣", trans_char="※"):
    if image.mode != 'RGBA':
        image = image.convert('RGBA')
    
    pixels = image.getdata()
    characters = []
    for pixel in pixels:
        if pixel[3] > 0:
            characters.append(opaque_char)
        else:
            characters.append(trans_char)
    return "".join(characters)

def main():
    st.set_page_config(
        page_title="Dot Image Converter",
        page_icon="🖼️",
        layout="centered"
    )
    
    # Custom CSS for better display
    st.markdown("""
        <style>
        .stCode {
            background-color: #f0f2f6;
            padding: 1rem;
            border-radius: 0.5rem;
        }
        .main-header {
            text-align: center;
            padding: 2rem 0;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<div class='main-header'><h1>🖼️ Image to Text Dot Converter</h1><p>사진을 텍스트 도트로 변환하여 연구나 디자인에 활용하세요.</p></div>", unsafe_allow_html=True)

    # Sidebar for controls
    with st.sidebar:
        st.header("⚙️ 설정")
        research_mode = st.toggle("Research Mode (Transparency)", value=True, help="투명 배경 이미지를 위한 전용 모드입니다.")
        
        st.divider()
        
        width = st.slider("너비 조절 (Width)", min_value=10, max_value=120, value=30, help="도트의 해상도를 결정합니다.")
        
        if research_mode:
            st.info("연구용 모드: 투명 배경은 ※, 이미지는 ▣로 표시됩니다.")
            col1, col2 = st.columns(2)
            opaque_char = col1.text_input("Opaque (이미지)", value="▣")
            trans_char = col2.text_input("Trans (투명)", value="※")
        else:
            st.info("표준 모드: 이미지의 명암을 ASCII 문자로 표현합니다.")
            
        st.divider()
        st.markdown("")

    uploaded_file = st.file_uploader("사진 파일을 업로드하세요 (JPG, PNG, GIF 등)", type=["jpg", "jpeg", "png", "bmp", "gif"])

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        
        col_img, col_info = st.columns([1, 1])
        with col_img:
            st.image(image, caption="원본 이미지 미리보기", use_container_width=True)
        with col_info:
            st.success("이미지가 성공적으로 로드되었습니다!")
            st.write(f"**파일명:** {uploaded_file.name}")
            st.write(f"**해상도:** {image.width}x{image.height}")
            if st.button("🚀 도트로 변환하기", use_container_width=True):
                st.session_state.converted = True

        if st.session_state.get('converted', False):
            with st.spinner("변환 중입니다..."):
                if research_mode:
                    scaled_image = scale_image(image, width, mode_multiplier=1.0)
                    dots = pixels_to_research_dots(scaled_image, opaque_char, trans_char)
                else:
                    scaled_image = scale_image(image, width, mode_multiplier=0.5)
                    gray_image = convert_to_grayscale(scaled_image)
                    dots = pixels_to_ascii(gray_image)
                
                # Format dots into lines
                pixel_count = len(dots)
                ascii_image = "\n".join([dots[index:(index + width)] for index in range(0, pixel_count, width)])
                
                st.divider()
                st.subheader("📋 변환 결과")
                st.code(ascii_image, language=None)
                
                # Download button
                st.download_button(
                    label="💾 텍스트 파일로 저장하기",
                    data=ascii_image,
                    file_name=f"{uploaded_file.name}_dots.txt",
                    mime="text/plain",
                    use_container_width=True
                )

if __name__ == "__main__":
    main()
