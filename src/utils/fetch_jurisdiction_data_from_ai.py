import os
from pathlib import Path
import yaml
from src.models.jurisdiction import Jurisdiction
from openai import OpenAI

OUTPUT_YAML_PATH = "tests/sample_output/jurisdictions/test/tx/local/austin_city_government_oid1-pdna3tgr-bgad-adaf-ybo5-5n2s7knw2sq3-uwritncj-khcn-35ig-xad4-wagfbefifzrs-n7pgulzv-lnkq-swk5-vto6-iplujpdgivzy-66kjtetx-vmjf-mho4-4rqd-cthyeogir5yd-46cb3ny.yaml"


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def fetch_jurisdiction_data(jurisdiction_name: str, jurisdiction_ocdid: str, output_yaml_path: str = OUTPUT_YAML_PATH) -> dict:
    """
    Fetch website data for a jurisdiction using OpenAI's API.
    """
    prompt = f"Get the website url for {jurisdiction_name} with the OCDID:{jurisdiction_ocdid}"
    import pdb; pdb.set_trace()
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )

    # Assuming the AI returns a YAML or JSON string in message.content
    content = response.choices[0].message.content
    # parse content for the url
    try:
        content_dict = yaml.safe_load(content)
    except Exception:
        import json
        content_dict = json.loads(content)
    url = content_dict.get("url")
    # validate the url format
    if not is_valid_url(url):
        raise ValueError(f"Invalid URL format: {url}")

    def is_valid_url(url: str) -> bool:
        """
        Simple URL validation.
        """
        from urllib.parse import urlparse
        try:
            result = urlparse(url)
            return all([result.scheme in ("http", "https"), result.netloc])
        except Exception:
            return False

    # update the yaml record with the new url
    content_dict["url"] = url
    # save the yaml
    with open(output_yaml_path, 'w') as file:
        yaml.dump(content_dict, file)

def main():
    with open(OUTPUT_YAML_PATH, 'r') as file:
        sample_yaml_file = yaml.safe_load(file)

    # get the ocdid and name from the sample YAML
    jurisdiction_ocdid = sample_yaml_file.get("ocdid")
    jurisdiction_name = sample_yaml_file.get("name")

    # Fetch data from AI
    jurisdiction_data = fetch_jurisdiction_data(jurisdiction_name, jurisdiction_ocdid, OUTPUT_YAML_PATH)

if __name__ == "__main__":
    main()
    # Fetch data from AI
    fetch_jurisdiction_data(jurisdiction_name, jurisdiction_ocdid)


def is_valid_url(url: str) -> bool:
    """
    Validate the URL format.
    """
    from urllib.parse import urlparse
    try:
        result = urlparse(url)
        return all([result.scheme in ("http", "https"), result.netloc])
    except Exception:
        return False
