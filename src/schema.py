# JSON schema for all telemetry payloads
payload_schema = {
    "type": "object",
    "properties": {
        "ts":    {"type": "number"},   # unix seconds
        "value": {"type": "number"}    # numeric reading
    },
    "required": ["ts", "value"],
    "additionalProperties": False
}
