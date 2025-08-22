# streamlit run app.py --server.address 0.0.0.0 --server.port 8501
import streamlit as st
import subprocess
import yaml
from PIL import Image
import os
import re
import time

st.set_page_config(page_title="Avatar Generator", page_icon="🤖", layout="wide")

# --- Helper Functions ---

def get_ip_address_from_yaml(file_path):
    """Extracts the IP address from the glut.yaml file."""
    try:
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)
        urls = data.get('default', {}).get('chat_engine', {}).get('handler_configs', {}).get('LamClient', {}).get('turn_config', {}).get('urls', [])
        for url in urls:
            match = re.search(r'turn:([^:]+):', url)
            if match:
                return match.group(1)
    except (FileNotFoundError, yaml.YAMLError, AttributeError):
        return None

def update_yaml_file(asset_path, api_key, voice, model_name, system_prompt):
    """Updates the glut.yaml file with user configurations."""
    try:
        with open('glut.yaml', 'r') as f:
            data = yaml.safe_load(f)

        # Update paths and keys
        data['default']['chat_engine']['handler_configs']['LamClient']['asset_path'] = f"lam_samples/{asset_path}"
        data['default']['chat_engine']['handler_configs']['CosyVoice']['api_key'] = api_key
        data['default']['chat_engine']['handler_configs']['LLM_Bailian']['api_key'] = api_key
        data['default']['chat_engine']['handler_configs']['CosyVoice']['voice'] = voice
        data['default']['chat_engine']['handler_configs']['LLM_Bailian']['model_name'] = model_name
        if system_prompt:
            data['default']['chat_engine']['handler_configs']['LLM_Bailian']['system_prompt'] = system_prompt

        with open('glut.yaml', 'w') as f:
            yaml.dump(data, f, default_flow_style=False)
        return True
    except (FileNotFoundError, yaml.YAMLError, KeyError) as e:
        st.error(f"Error updating YAML file: {e}")
        return False

# --- Page 1: Upload Image ---
def page_one():
    # import webbrowser
    # ip_address = get_ip_address_from_yaml('glut.yaml')
    # if ip_address:
    #     import sys
    #     port = "8501"  # 默认端口
    #     if len(sys.argv) > 1:
    #         for arg in sys.argv:
    #             if arg.startswith("--server.port="):
    #                 port = arg.split("=")[1]
    #                 break
    #             elif arg == "--server.port" and len(sys.argv) > sys.argv.index(arg) + 1:
    #                 port = sys.argv[sys.argv.index(arg) + 1]
    #                 break
    #     url = f"http://{ip_address}:{port}"
    #     webbrowser.open(url)
    st.title("Upload an image to create a real-time digital avatar in just three steps!")
    st.header("🤖 Step 1: Bring Your Image to Life")

    col1, col2 = st.columns(2)

    with col1:
        uploaded_file = st.file_uploader("Upload your image", type=["jpg", "png", "jpeg"])
        st.info("""
        - The platform accepts full-body, half-body, and images with various backgrounds.
        - Images must have normal facial proportions (realistic anime/game characters are okay).
        - Cartoon-style images with exaggerated features (e.g., large eyes, tiny noses) are not supported.
        """)
        if os.path.exists("g.png"):
            st.image("g.png", caption="Examples")

    with col2:
        if uploaded_file is not None:
            st.session_state.uploaded_image = uploaded_file
            image = Image.open(uploaded_file)
            st.image(image, caption='Uploaded Image', use_container_width=True)

            prompt_text = st.text_input("Edit prompt:", "Describe this image.")

            if st.button("Analyze Image"):
                with st.spinner('Analyzing image...'):
                    from transformers import pipeline
                    pipe = pipeline("image-text-to-text", model="llava-hf/llava-interleave-qwen-0.5b-hf", use_fast=True)
                    messages = [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "image",
                                    "image": Image.open(st.session_state.uploaded_image),
                                },
                                {"type": "text", "text": prompt_text},
                            ],
                        }
                    ]
                    outputs = pipe(text=messages, max_new_tokens=200, return_full_text=False)
                    st.session_state.vlm_output = outputs[0]['generated_text']

            if 'vlm_output' in st.session_state:
                st.text_area("VLM Text Output", st.session_state.vlm_output, height=100)
            st.success("For further customization, consider using Stable Diffusion or ComfyUI to adjust expressions, poses, backgrounds, and styles.")

            if st.button("Confirm and Proceed to Step 2 →"):
                st.session_state.page = 'two'
                st.rerun()

# --- Page 2: Download Model ---
def page_two():
    st.title("📥 Step 2: Download the Avatar Model")
    st.markdown("Go to the [LAM ModelScope Studio](https://www.modelscope.cn/studios/Damo_XR_Lab/LAM_Large_Avatar_Model), follow the instructions, and make sure to check **'Export ZIP file for Chatting Avatar'**.")
    st.markdown("Once generated, copy the `wget` command from the **'Download ZIP file for Chatting Avatar'** section and paste it below.")

    wget_command = st.text_input("Paste the `wget` command here:")

    if st.button("Download Model"):
        if wget_command and wget_command.strip().startswith("wget"):
            st.session_state.wget_command = wget_command.strip()
            # Extract filename for later use
            try:
                filename = wget_command.split('/')[-1].split('?')[0] # Basic parsing
                st.session_state.asset_path = filename
                
                # Define target directory
                target_dir = "/workspace/OpenAvatarChat/src/handlers/client/h5_rendering_client/lam_samples"
                os.makedirs(target_dir, exist_ok=True)

                with st.spinner(f"Executing download command in {target_dir}..."):
                    process = subprocess.run(st.session_state.wget_command, shell=True, check=True, cwd=target_dir, capture_output=True, text=True)
                    st.success("Model downloaded successfully!")
                    st.code(process.stderr)  # wget outputs progress to stderr
                    st.session_state.page = 'three'
                    st.rerun()
            except subprocess.CalledProcessError as e:
                st.error(f"Command execution failed: {e}")
                st.code(e.stderr)
            except (IndexError, AttributeError):
                st.error("Could not extract a valid filename from the wget command. Please ensure it's correct.")
        else:
            st.warning("Please enter a valid `wget` command.")

# --- Page 3: Configuration ---
def page_three():
    st.title("⚙️ Step 3: Configure and Launch")

    # --- Mappings for display text to actual values ---
    voice_options = {
        "浪漫风情女": "longqiang_v2",
        "温暖春风女": "longyan_v2",
        "甜美娇气女": "longfeifei_v2",
        "知性粤语女": "longjiayi_v2",
        "知性英文女": "loongeva_v2",
        "豪放可爱童女": "longxian_v2",
        "元气甜美童女": "longhua_v2"
    }
    model_options = {
        "qwen-plus (balanced response speed and reasoning abilities)": "qwen-plus",
        "qwen-turbo (fastest speed and very low cost)": "qwen-turbo",
        "qwen-max (strongest reasoning abilities)": "qwen-max"
    }

    api_key = st.text_input("Aliyun Bailian API Key", type="password", help="Your API key is required to power the LLM and TTS services.")

    col1, col2 = st.columns(2)
    with col1:
        selected_voice_display = st.selectbox("Voice Tone", list(voice_options.keys()), help="Select the voice for your avatar.")
    with col2:
        selected_model_display = st.selectbox("LLM Model", list(model_options.keys()), help="Select the language model for conversation.")

    system_prompt = st.text_area("System Prompt (Optional)", placeholder="e.g., You are a helpful assistant.")

    if st.button("🚀 Confirm and Launch Avatar"):
        if api_key:
            # Map display names to actual values before updating
            actual_voice = voice_options[selected_voice_display]
            actual_model = model_options[selected_model_display]

            with st.spinner("Updating configuration..."):
                success = update_yaml_file(st.session_state.asset_path, api_key, actual_voice, actual_model, system_prompt)
            if success:
                st.success("Configuration saved!")
                st.session_state.page = 'running'
                st.rerun()
        else:
            st.warning("Please enter your API key.")

# --- Page 4: Running ---
def page_four():
    st.title("🚀 Launching Your Avatar...")
    log_placeholder = st.empty()
    
    if 'link_shown' not in st.session_state:
        st.session_state.link_shown = False

    with st.spinner('Starting application... This may take a moment.'):
        log_output = ""
        
        try:
            # Set environment variables
            env = os.environ.copy()
            env["PATH"] = "/usr/local/nvidia/bin:/usr/local/cuda/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/local/miniconda3/envs/glut/bin"
            env["MODELSCOPE_CACHE"] = "/workspace/OpenAvatarChat"
            env["TORCH_HOME"] = "/workspace/OpenAvatarChat/models"
            env["HF_ENDPOINT"] = "https://hf-mirror.com"
            
            cwd = "/workspace/OpenAvatarChat"

            log_output += f"[INFO] Setting up environment in {cwd}...\n"
            log_placeholder.code(log_output, language='log')

            # Check disk space
            try:
                df_process = subprocess.run(["df", "-hl"], cwd=cwd, env=env, capture_output=True, text=True, check=True)
                log_output += "[INFO] Disk space check:\n"
                log_output += df_process.stdout
                log_output += "\n"
                log_placeholder.code(log_output, language='log')
            except (subprocess.CalledProcessError, FileNotFoundError) as e:
                log_output += f"[WARNING] Could not check disk space: {e}\n"
                log_placeholder.code(log_output, language='log')
            
            subprocess.run(["sh", "scripts/setup_coturn.sh"], cwd=cwd, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            log_output += "[INFO] Starting avatar... Logs will stream below.\n"
            log_placeholder.code(log_output, language='log')

            cmd = ["python", "src/demo.py", "--config", "/workspace/glut.yaml"]
            process = subprocess.Popen(cmd, cwd=cwd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)

            for line in iter(process.stdout.readline, ''):
                log_output += line
                if "Uvicorn running on" in line and not st.session_state.link_shown:
                    st.success("Your avatar is now live!")
                    ip_address = get_ip_address_from_yaml('glut.yaml')
                    port = "8282"  # default
                    with open('glut.yaml', 'r') as f:
                        data = yaml.safe_load(f)
                        port = data.get('default', {}).get('service', {}).get('port', [])
                    if ip_address and port:
                        url = f"https://{ip_address}:{port}"
                        st.markdown(f"### 👉 [Click here to start chatting with your digital human!]({url})")
                        st.session_state.link_shown = True
                    else:
                        st.error("Could not extract a valid IP address or port from the configuration file.")
                log_placeholder.code(log_output, language='log')
            
            process.stdout.close()
            process.wait()

        except FileNotFoundError as e:
            st.error(f"Error: {e}. Ensure 'python' and 'sh' are in the system's PATH.")
        except Exception as e:
            st.error(f"An exception occurred: {e}")

# --- Main App Logic ---
if 'page' not in st.session_state:
    st.session_state.page = 'one'

if st.session_state.page == 'one':
    page_one()
elif st.session_state.page == 'two':
    page_two()
elif st.session_state.page == 'three':
    page_three()
elif st.session_state.page == 'running':
    page_four()