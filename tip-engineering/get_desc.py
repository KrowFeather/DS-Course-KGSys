import csv
from ChatGPT import ChatGPT

def get_desc(chatgpt, concept):
    prompt = f"""
        假设你现在是一个数据结构与算法课程的老师，我现在需要你帮我介绍一些关于数据结构和算法的概念。
        我会给你一个提示词，这个提示词是一个名词，表示数据结构与算法里面的一个专业名词。
        我需要你根据这个名词给出定义和解释。我大概是需要两个东西，一个是大致、浓缩的解释，另外一个是详细的解释。
        比如如果给你的提示词是链表，那么你应该按照如下格式给回答：
        链表的大致解释是：链表是一种用于存储数据的数据结构，通过如链条一般的指针来连接元素。它的特点是插入与删除数据十分方便，但寻找与读取数据的表现欠佳。
        链表的详细解释是：链表是一种物理存储单元上非连续、非顺序的存储结构，数据元素的逻辑顺序是通过链表中的指针链接次序实现的。链表由一系列结点（链表中每一个元素称为结点）组成，结点可以在运行时动态生成。每个结点包括两个部分：一个是存储数据元素的数据域，另一个是存储下一个结点地址的指针域。 相比于线性表顺序结构，操作复杂。由于不必须按顺序存储，链表在插入的时候可以达到O(1)的复杂度，比另一种线性表顺序表快得多，但是查找一个节点或者访问特定编号的节点则需要O(n)的时间，而线性表和顺序表相应的时间复杂度分别是O(logn)和O(1)。
        以上就是回答的一个实例。那么现在我给你的提示词是“{concept}”，请按照如上要求给我回答，并且请用中文回答。
    """
    try:
        response = chatgpt.chat(prompt)
        return response["content"]
    except Exception as e:
        return f"获取描述失败：{e}"

concepts_list = []
with open('./concepts.csv', 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    for row in reader:
        if row:
            concepts_list.append(row[0])

chatgpt = ChatGPT()

response = get_desc(chatgpt, concepts_list[0])
print(response)
