import os
import requests
import yaml
from pathlib import Path
from urllib.parse import urlparse
from pydantic import BaseModel, HttpUrl, field_validator
from openai import OpenAI

from src.models.jurisdiction import Jurisdiction

OUTPUT_YAML_PATH = "tests/sample_output/jurisdictions/test/tx/local/austin_city_government_oid1-pdna3tgr-bgad-adaf-ybo5-5n2s7knw2sq3-uwritncj-khcn-35ig-xad4-wagfbefifzrs-n7pgulzv-lnkq-swk5-vto6-iplujpdgivzy-66kjtetx-vmjf-mho4-4rqd-cthyeogir5yd-46cb3ny.yaml"

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class AiURLResp(BaseModel):
    url: HttpUrl

    @field_validator("url")
    @classmethod
    def validate_url(cls, v):
        if not v:
            raise ValueError("URL must not be empty")
        if v.scheme not in ["http", "https"]:
            raise ValueError("URL must be a valid HTTP or HTTPS URL")
        parsed = urlparse(str(v))
        if not (parsed.hostname and parsed.hostname.endswith(".gov")):
            raise ValueError("URL must be a .gov domain")

        try:
            response = requests.get(str(v))
            response.raise_for_status()
        except requests.RequestException as e:
            raise ValueError(f"Error fetching URL: {e}")
        return v


def load_jurisdiction_from_yaml(path: str | Path) -> Jurisdiction:
    """Load and normalize a Jurisdiction from a YAML file."""
    path = Path(path)
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
        jurisdiction_data = {
            "name": data.get("name"),
            "ocdid": data.get("ocdid"),
            "url": data.get("url")
        }
    if not jurisdiction_data["name"] or not jurisdiction_data["ocdid"]:
        raise ValueError("Missing required fields: 'name' and 'ocdid' are required")

    return jurisdiction_data

def fetch_ai_jurisdiction_url(jurisdiction: Jurisdiction) -> AiURLResp:
    jurisdiction_name = jurisdiction["name"]
    jurisdiction_ocdid = jurisdiction["ocdid"]
    
    try: 
        prompt = (
            f"Get the website url for {jurisdiction_name} with the OCDID:{jurisdiction_ocdid}. "
            "Return only official government websites. Most will have .gov domains, but not all. "
            "Where available always return the .gov domain.\n\n"
            "Return the url as a dictionary as shown in the examples below.\n\n"
            'Examples:\n'
            '{"url": "https://www.sausalito.gov/"}\n'
            '{"url": "https://www.chicago.gov/city/en.html"}\n'
            '{"url": "https://www.westfieldnj.gov/"}\n'
            '{"url": "PaloAlto.gov"} # not cityofpaloalto.org,\n'
            '{"url": "https://coltsneck.org/"} # No .gov domain exists, use the official .org domain\n'
        ) 
        response = client.responses.create(
            model="gpt-5.2",
            input=prompt,
        )
        content = response.output_text
    except LookupError as e:
        raise ValueError(f"Error fetching AI jurisdiction URL: {e}")

    print(response.output_text)
    content = response.output_text
    
    import json

    data = json.loads(content)
    url = data["url"] 
    try:
        ai_url_resp = AiURLResp(url=url)
    except Exception as e:
        raise ValueError(f"Error checking URL status: {e}")

    return ai_url_resp


def main() -> None:
    jurisdiction = load_jurisdiction_from_yaml(OUTPUT_YAML_PATH)
    print("Loaded jurisdiction:", jurisdiction["name"])

    ai_result = fetch_ai_jurisdiction_url(jurisdiction)
    print("AI result:", ai_result.url)


if __name__ == "__main__":
    main()
