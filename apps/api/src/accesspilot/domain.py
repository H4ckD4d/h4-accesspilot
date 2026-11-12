"""Deterministic HTML-only heuristic. Does not fetch websites or certify WCAG."""
import json
from html.parser import HTMLParser
from fastapi import APIRouter,Depends,Query
from pydantic import BaseModel,Field
from sqlalchemy import select
from sqlalchemy.orm import Session
from .app_helpers import session_dep,require_record
from .auth import actor,writer
from .db import Resource,record_event

router=APIRouter(prefix='/v1/audits',tags=['accessibility'])

class AuditCreate(BaseModel):
    label:str=Field(min_length=2,max_length=100)
    html_source:str=Field(min_length=5,max_length=200000)

class AuditParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.lang=False;self.title=False;self.title_text='';self.in_title=False
        self.images=[];self.inputs=[];self.anchors=[];self.active_links=[]
        self.label_for=set();self.label_depth=0;self.first_h1=False
    def handle_starttag(self,tag,attrs):
        d=dict(attrs);line=self.getpos()[0]
        if tag=='html':self.lang=bool((d.get('lang') or '').strip())
        if tag=='title':self.in_title=True;self.title=True
        if tag=='h1':self.first_h1=True
        if tag=='img' and 'alt' not in d:self.images.append(line)
        if tag=='label':
            self.label_depth+=1
            if d.get('for'):self.label_for.add(d['for'])
        if tag in ('input','select','textarea') and d.get('type','').lower() not in ('hidden','submit','button','reset','image'):
            self.inputs.append((line,d.get('id'),bool(d.get('aria-label') or d.get('aria-labelledby') or self.label_depth)))
        if tag=='a' and 'href' in d:
            self.active_links.append({'line':line,'accessible':bool(d.get('aria-label') or d.get('aria-labelledby') or d.get('title')),'text':''})
    def handle_data(self,data):
        if self.in_title:self.title_text+=data
        for a in self.active_links:a['text']+=data
    def handle_endtag(self,tag):
        if tag=='title':self.in_title=False
        if tag=='label':self.label_depth=max(0,self.label_depth-1)
        if tag=='a' and self.active_links:
            self.anchors.append(self.active_links.pop())

def analyze_html(source):
    parser=AuditParser();parser.feed(source);parser.close()
    findings=[]
    def flag(rule,line,details,wcag):
        findings.append({'rule':rule,'line':line,'severity':'review','detail':details,'wcag_reference':wcag})
    if not parser.lang:flag('document-language',1,'Declare a document language (html lang).','3.1.1')
    if not parser.title or not parser.title_text.strip():flag('page-title',1,'Add a meaningful title.','2.4.2')
    if not parser.first_h1:flag('missing-h1',1,'Review page heading structure (heuristic).','1.3.1')
    for line in parser.images:flag('image-alt-missing',line,'Review alternative text for image.','1.1.1')
    for line,id,accessible in parser.inputs:
        if not accessible and not (id and id in parser.label_for):flag('form-label-missing',line,'Provide an explicit accessible label.','1.3.1')
    for link in parser.anchors:
        if not (link['accessible'] or link['text'].strip()):flag('empty-link-name',link['line'],'Provide meaningful link text.','2.4.4')
    return {'findings':findings,'finding_count':len(findings),'heuristic_score':max(0,100-10*len(findings)),
            'scope':'Static supplied HTML only. Not comprehensive WCAG compliance or accessibility certification.'}

@router.post('',status_code=201)
def submit_audit(payload:AuditCreate,auth=Depends(writer),session:Session=Depends(session_dep)):
    result=analyze_html(payload.html_source)
    safe_record={'label':payload.label,**result}
    # Only findings and counts, NOT raw HTML: avoid accidental storage of private source.
    item=Resource(tenant_id=auth['tenant_id'],kind='audit',status='completed',data_json=json.dumps(safe_record))
    session.add(item);session.flush();record_event(session,auth,'audit.created',item.id);session.commit()
    return {'id':item.id,**safe_record}

@router.get('')
def audits(limit:int=Query(default=25,ge=1,le=100),offset:int=Query(default=0,ge=0,le=10000),
           auth=Depends(actor),session:Session=Depends(session_dep)):
    rows=session.scalars(select(Resource).where(Resource.tenant_id==auth['tenant_id'],Resource.kind=='audit')
          .order_by(Resource.created_at.desc(),Resource.id.desc()).offset(offset).limit(limit)).all()
    return {'audits':[{'id':x.id,**json.loads(x.data_json)} for x in rows],'limit':limit,'offset':offset}

@router.get('/{audit_id}')
def audit_detail(audit_id:str,auth=Depends(actor),session:Session=Depends(session_dep)):
    x=require_record(session,audit_id,auth['tenant_id'],'audit')
    return {'id':x.id,**json.loads(x.data_json)}
