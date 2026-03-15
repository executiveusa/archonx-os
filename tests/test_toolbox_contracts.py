import json
from pathlib import Path


def test_toolbox_index_requires_security_flags():
    data = json.loads(Path('toolbox/toolbox.json').read_text())
    assert data['security']['requires_grant'] is True
    assert data['security']['requires_work_item'] is True


def test_reportback_contract_present():
    data = json.loads(Path('.archonx/reportback.json').read_text())
    assert data['contract'] == 'openclaw-reportback-v1'
