import re
import csv


def parse_questions(text):
    # 正则表达式匹配题目开头，例如 "1 ."
    question_split_pattern = re.compile(r'\n\s*\d+\s*\.\s*')
    # 分割题目
    questions = question_split_pattern.split(text)
    # 移除第一个空字符串（如果存在）
    if questions[0].strip() == '':
        questions = questions[1:]

    parsed = []
    for q in questions:
        # 提取答案
        answer_match = re.search(r'答案\s*：\s*([A-Z，、,]+)', q)
        if answer_match:
            answer = answer_match.group(1).replace('，', ',').replace('、', ',').strip()
        else:
            answer = ''

        # 提取题目和选项（从开始到"答案："前）
        question_part = re.split(r'答案\s*：', q)[0].strip()

        # 去掉可能的"解析："部分
        question_part = re.split(r'解析\s*：', question_part)[0].strip()

        # 替换多余的空白字符
        question_part = ' '.join(question_part.split())

        parsed.append([question_part, answer])

    return parsed


def txt_to_csv(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        text = f.read()

    parsed_questions = parse_questions(text)

    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['题目', '答案'])
        for row in parsed_questions:
            writer.writerow(row)


if __name__ == "__main__":
    input_txt = './multiple-choice-question.txt'
    output_csv = './QA1.csv'
    txt_to_csv(input_txt, output_csv)
    print(f"已将 '{input_txt}' 转换为 '{output_csv}'")
