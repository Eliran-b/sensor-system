from typing import Literal
from pydantic import BaseModel
from common.enums.message_source_enum import MessageSourceEnum


class MessageAttributes(BaseModel):
    message_source: Literal[tuple(message_source_enum.value for message_source_enum in MessageSourceEnum)]
