"""Translation store helpers: split unit text into (prefix, body, suffix), keyed by body."""
import re, json, os
PFX=re.compile(r'^(?:[　 ]|%W\d+)*')
SFX=re.compile(r'(?:[　 ]|%W\d+)*$')
def split_unit(s):
    m=PFX.match(s); pre=m.group(0)
    rest=s[len(pre):]
    m2=SFX.search(rest); suf=m2.group(0) if m2 else ''
    body=rest[:len(rest)-len(suf)] if suf else rest
    return pre,body,suf
WORK=os.environ.get('THERESIA_WORK','/tmp/claude-0/-home-user-KRPTCH/4b976868-e8ad-5cd2-9a29-b1ffff23f1f0/scratchpad/work')
REPO=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','translations','theresia')
