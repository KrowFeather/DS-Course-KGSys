import wikipediaapi
from opencc import OpenCC


# 创建 Wikipedia API 的实例并设置用户代理
def trans(text):
    cc = OpenCC('tw2sp')
    ans = cc.convert(text)
    return ans

def getWiki(concept):
    wiki_wiki = wikipediaapi.Wikipedia(user_agent='MyProjectName (merlin@example.com)',language='zh')
    page_py = wiki_wiki.page(concept)
    if page_py.exists():
        text = page_py.text
        text = trans(text)
        return text
    else:
        return None


def parse_description(concepts):
    mp = {}
    for concept in concepts:
        description = getWiki(concept)
        if description is not None:
            mp[concept] = description
    return mp

ans = parse_description(['二进制'])
print(ans)