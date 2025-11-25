import base64
from typing import List, Optional
from typing import List, Dict, Any
from helpers.datamodel import ChatAgentMessage
from helpers.secret import AWSSecretManager
from helpers.config import AppConfig

app_conf = AppConfig()
aws_secret_manager = AWSSecretManager()

class Utils:
    def __init__(self):
        pass
    
    def decode_base64_data(encoded_data: Optional[str]) -> Optional[bytes]:
        """Decode base64 string to raw bytes if available."""
        if not encoded_data:
            return None
        try:
            return base64.b64decode(encoded_data)
        except Exception:
            return None
        
    def format_agent_messages(messages: List[ChatAgentMessage]) -> List[Dict[str, Any]]:
        """
        Ensure message structure is Claude-compatible.
        - If message content is str, wrap into [{"type": "text", "text": ...}]
        - If message content is already a list of content blocks, pass through.
        """
        formatted = []

        for msg in messages:
            # Case 1: plain string
            if isinstance(msg.content, str):
                # plain text message
                formatted.append({
                    "role": msg.role,
                    "content": [{"type": "text", "text": msg.content.strip()}]
                })
                continue

            if isinstance(msg.content, list):
                content_blocks = []
                for block in msg.content:
                    block_dict = block if isinstance(block, dict) else block.model_dump(exclude_none=True)

                    # 🖼️ Image block (base64 data remains string)
                    if block_dict.get("type") == "image" and "source" in block_dict:
                        content_blocks.append(block_dict)

                    # 📄 Document block (decode base64 -> raw bytes)
                    elif "document" in block_dict:
                        doc = block_dict["document"]
                        if "source" in doc and "bytes" in doc["source"]:
                            decoded_bytes = Utils.decode_base64_data(doc["source"]["bytes"])
                            doc["source"]["bytes"] = decoded_bytes
                        content_blocks.append({"document": doc})

                    # 🧾 Text block
                    elif block_dict.get("type") == "text":
                        content_blocks.append(block_dict)

                formatted.append({
                    "role": msg.role,
                    "content": content_blocks
                })
                
        return formatted