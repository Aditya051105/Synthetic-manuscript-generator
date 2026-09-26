import streamlit as st
import yaml
import zipfile
import io
import os
from PIL import Image

from src.utils import set_seed
from src.dataset import generate_script_images_memory, find_font

st.set_page_config(page_title="Manuscript Generator", page_icon="📜", layout="wide")

st.title("📜 Synthetic Manuscript Generator")
st.markdown("Cloud-synthesized archival data pipelines powered by Streamlit.")

with st.sidebar:
    st.header("Configuration")
    
    script_type = st.selectbox(
        "Select Script",
        ("devanagari", "modi", "sharada")
    )
    
    img_count = st.number_input("Number of Images", min_value=1, max_value=100, value=3)
    
    random_seed = st.number_input("Random Seed", min_value=0, value=42)
    
    use_custom = st.checkbox("Use Custom Corpus Text?")
    custom_text = ""
    if use_custom:
        custom_text = st.text_area("Enter your custom text lines:")

st.write("### Preview Output")
preview_col1, preview_col2 = st.columns(2)

if st.button("Generate Dataset", type="primary"):
    with st.spinner(f"Synthesizing {img_count} images for {script_type}..."):
        # Load logic
        set_seed(random_seed)
        config_path = "config/config.yaml"
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            
        config['generation']['random_seed'] = random_seed
        font_path = find_font(script_type) or ""
        
        try:
            # Native memory generation via backend script
            results = generate_script_images_memory(
                config=config, 
                script_name=script_type, 
                count=img_count, 
                font_path=font_path, 
                custom_text=custom_text if use_custom else None
            )
            
            # Show preview of the first one
            preview_bytes, preview_md = results[0]
            with preview_col1:
                st.image(preview_bytes, caption=f"Sample Image: {script_type}_001.png", use_container_width=True)
            with preview_col2:
                st.markdown("**Sample Ground Truth (.md)**")
                st.code(preview_md, language="markdown")
            
            # Zip all generated files
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for idx, (img_bytes, text_data) in enumerate(results):
                    base_name = f"{script_type}_{idx+1:03d}"
                    zip_file.writestr(f"{base_name}.png", img_bytes.getvalue())
                    zip_file.writestr(f"{base_name}.md", text_data)
                    
            st.success("Generation Complete!")
            
            # Provide zip download capability native to Streamlit
            st.download_button(
                label="📥 Download Complete Dataset (.ZIP)",
                data=zip_buffer.getvalue(),
                file_name=f"{script_type}_dataset.zip",
                mime="application/zip",
                type="primary"
            )
            
        except Exception as e:
            st.error(f"Generation failed: {e}")
