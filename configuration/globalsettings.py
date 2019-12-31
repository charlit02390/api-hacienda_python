import yaml

cfg = None
with open("config.yaml", 'r') as ymlfile:
    cfg = yaml.safe_load(ymlfile)

