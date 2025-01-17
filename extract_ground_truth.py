### Schema to prompt ChatGPT
JSON_SCHEMA = """
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://example.com/product.schema.json",
  "title": "Insurance Policy",
  "description": "Details of an insurance policy",
  "type": "object",
  "properties": {
    "policyNumber": {
      "description": "The unique identifier of an insurance policy",
      "type": "string"
    },
    "policyStartDate": {
      "description": "The start date of the insurance policy",
      "type": "string"
    },
    "policyEndDate": {
      "description": "The end date of the insurance policy",
      "type": "string",
    },
    "policyPremium": {
      "description": "The premium dollar amount of the insurance policy",
      "type": "float",
    },
    "policyFormsandEndorsements": {
      "description": "All forms and endorsements associated with the policy",
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "description"],
        "properties": {
            "id": {
                "type": "string"
            },
            "description": {
                "type": "string"
            }
          }
        },
      "minItems": 1,
      "uniqueItems": true
    }
  },
  "required": [ "policyNumber", "policyStartDate", "policyEndDate", "policyPremium", "policyFormsandEndorsements" ]
}
"""
