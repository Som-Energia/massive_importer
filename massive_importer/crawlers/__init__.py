import os, yaml, logging

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
try:
    with open(os.path.join(BASE_DIR, 'massive_importer/crawlers/crawlers/conf/credentials.yaml')) as f:
        all_creds = yaml.load(f.read())
except Exception as e:
    raise Exception(str(e))
