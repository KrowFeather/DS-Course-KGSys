import re
import csv


def parse_questions(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    questions = []
    current_question = []
    current_answer = ''

    for line_num, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            continue  # 跳过空行

        # 检查是否是答案行（仅一个大写字母）
        if re.fullmatch(r'[A-D]', stripped):
            current_answer = stripped
            # 将当前题目加入列表
            question_text = ' '.join(current_question).replace('\t', ' ').replace('\n', ' ').strip()
            # 清理多余的空白字符
            question_text = re.sub(r'\s+', ' ', question_text)
            questions.append([question_text, current_answer])
            # 重置当前题目
            current_question = []
            current_answer = ''
        else:
            current_question.append(stripped)

    # 处理最后一道题（如果没有答案行）
    if current_question and not current_answer:
        question_text = ' '.join(current_question).replace('\t', ' ').replace('\n', ' ').strip()
        question_text = re.sub(r'\s+', ' ', question_text)
        questions.append([question_text, ''])

    return questions


def write_to_csv(questions, output_path):
    with open(output_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.writer(csvfile)
        # 写入表头
        writer.writerow(['题目', '答案'])
        # 写入每一道题
        for q in questions:
            writer.writerow(q)


if __name__ == "__main__":
    input_txt = './0923choice-question.txt'
    output_csv = './QA2.csv'
    questions = parse_questions(input_txt)
    write_to_csv(questions, output_csv)
    print(f"已将 '{input_txt}' 转换为 '{output_csv}'")
