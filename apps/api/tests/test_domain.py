from .conftest import headers,OWNER,VIEWER,OTHER
BAD='<!doctype html><html><head></head><body><img src="a.png"><input id="email"><a href="/x"></a></body></html>'
GOOD='<!doctype html><html lang="pt-BR"><head><title>Example</title></head><body><h1>Welcome</h1><label for="mail">Email</label><input id="mail"><img src="a.png" alt="Test graphic"><a href="/x">More</a></body></html>'

def test_accessibility_heuristics(client):
    out=client.post('/v1/audits',json={'label':'Synthetic audit','html_source':BAD},headers=headers())
    assert out.status_code==201,out.text
    rules={f['rule'] for f in out.json()['findings']}
    assert {'document-language','page-title','image-alt-missing','form-label-missing','empty-link-name'}.issubset(rules)
    assert 'html_source' not in str(out.json())
    assert client.get('/v1/audits/'+out.json()['id'],headers=headers(OTHER)).status_code==404

def test_good_html_has_no_findings(client):
    out=client.post('/v1/audits',json={'label':'Synthetic valid','html_source':GOOD},headers=headers())
    assert out.json()['finding_count']==0

def test_access_control_and_limit(client):
    assert client.post('/v1/audits',json={'label':'Synthetic','html_source':BAD},headers=headers(VIEWER)).status_code==403
    assert client.get('/v1/audits',headers=headers(VIEWER)).status_code==200
    assert client.get('/v1/audits?limit=101',headers=headers()).status_code==422

def test_tenant_visibility(client):
    client.post('/v1/audits',json={'label':'Private source','html_source':BAD},headers=headers())
    assert client.get('/v1/audits',headers=headers(OTHER)).json()['audits']==[]
    assert len(client.get('/v1/audits',headers=headers()).json()['audits'])==1
