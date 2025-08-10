# A Digital Human Interaction System: A Three-Step Construction from a Single Image to Real-time Conversation Avatar

Simply upload a portrait or personified image of characters from famous games or animations (e.g., a personified child toy), and it can come to life. In just three steps, you can build a customizable digital avatar from scratch and have real-time intelligent and emotional interactions.

The first step is to upload the image and use Vision Language Models (VLM) to analyze the descriptive text. Then, you can optimize the prompts in the [Stable Diffusion web UI](https://github.com/AUTOMATIC1111/stable-diffusion-webui) or [ComfyUI](https://github.com/comfyanonymous/ComfyUI) and their plugins to customize your preferred expressions, poses, backgrounds, and styles using image-to-image or [Low-Rank Adaptation (LoRA) fine-tuning](https://github.com/Akegarasu/lora-scripts).

The second step involves using the official [LAM (Large Avatar Model for One-shot Animatable Gaussian Head) platform](https://www.modelscope.cn/studios/Damo_XR_Lab/LAM_Large_Avatar_Model) to generate a chatting avatar corresponding to the uploaded image.

Finally, import the avatar into the [Open Avatar Chat platform](https://github.com/HumanAIGC-Engineering/OpenAvatarChat) and you can interact with your digital avatar in real time.

This project uses Streamlit to build a user-friendly, aesthetically pleasing GUI that links the entire process while ensuring adequate legality checks.

Workflow
![Workflow](https://github.com/WillongWang/Single-Image-to-Real-time-Conversation-Avatar-powered-by-LAM-and-Cosyvoice-v2/blob/main/workflow.png)

## GUI examples


