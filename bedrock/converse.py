import boto3
from langchain_aws import ChatBedrockConverse
from helpers.config import AppConfig, AWSConfig

class Converse():
    def __init__(self):
        self.aws_conf = AWSConfig()
    
    def build_converse(self, llm):
        guardrails = None
        if llm.guardrail_id and llm.guardrail_version:
            guardrails = {
                "guardrailIdentifier": llm.guardrail_id,
                "guardrailVersion": llm.guardrail_version
            }

        converse = ChatBedrockConverse(
            client=boto3.client("bedrock-runtime", region_name=llm.region),
            model=llm.model_id,
            temperature=float(llm.model_temperature),
            max_tokens=int(llm.model_max_tokens),
            guardrails=guardrails
        )

        return converse