import json
import os
import subprocess
import tempfile
from functools import lru_cache


base_path = os.path.abspath(os.path.split(__file__)[0])
CS_PROJ_PATH = "kqlextraction/KqlExtraction/KqlExtraction.csproj"
TEST_PATH = "kqlextraction/tests"


@lru_cache(maxsize=1024)
def extract_kql(kql):
    with tempfile.NamedTemporaryFile("w", delete=False) as f:
        f.write(kql)
        temp_path = f.name

    try:
        kql_extraction = subprocess.run(
            [
                "dotnet",
                "run",
                "-c",
                "Release",
                "--project",
                os.path.join(base_path, CS_PROJ_PATH),
                temp_path,
            ],
            capture_output=True,
            check=True,
        )

        kql_extraction.check_returncode()
        return json.loads(kql_extraction.stdout.strip())

    except Exception as ex:
        print("[!] KqlExtraction Failed\n", ex)
    finally:
        os.unlink(temp_path)

    return {}


if __name__ == "__main__":
    for kql_file in os.listdir(os.path.join(base_path, TEST_PATH)):
        kql_file = os.path.join(base_path, TEST_PATH, kql_file)

        with open(kql_file, "r", encoding="utf-8") as f:
            kql = f.read()

        kql_description = extract_kql(kql)
        print(json.dumps(kql_description, indent=2))
