import random
import string


def generate_class_id():
    # 生成一个随机的八位班级号，包含大写字母和数字
    existing_class_ids = set()
    # with open('data/class.csv', 'r', encoding='utf-8') as f:
    #     reader = csv.reader(f)
    #     next(reader)  # 跳过表头
    #     for row in reader:
    #         class_id = row[0].strip()  # 获取第一列的班级号并去掉空白字符
    #         existing_class_ids.add(class_id)  # 将班级号添加到集合中

    # 生成一个随机的八位班级号，包含大写字母和数字
    new_class_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

    # 如果生成的班级号已经存在，则重新生成
    while new_class_id in existing_class_ids:
        new_class_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

    return new_class_id


def create_class(driver, user_id, class_id, capacity, course_name):
    # 查询是否已存在具有指定 user_id 的用户节点
    query_user = f"MATCH (u:user) WHERE u.id = {user_id} RETURN u"
    result_user = driver.run(query_user).data()

    if not result_user:
        print(f"User with id {user_id} does not exist.")
        return None  # 用户不存在，返回 None 或者可以选择创建新用户

    # 用户存在，创建班级节点的 Cypher 查询
    query_class = (
        f"CREATE (c:Class {{class_id: '{class_id}', capacity: {capacity}, course_name: '{course_name}'}}) "
        f"WITH c "
        f"MATCH (u:user) WHERE u.id = {user_id} "
        f"CREATE (u)-[:own]->(c)"  # 与现有的 User 节点建立 OWN 关系
    )

    # 使用 py2neo 的 driver 来运行查询
    driver.run(query_class)  # 直接使用 run 来执行 Cypher 查询
    print(f"Class {class_id} created with capacity {capacity} and OWN relationship established.")

    # 将用户与班级的关系记录到 CSV 文件
    # with open('data/teacher_class.csv', mode='a', newline='', encoding='utf-8') as file:
    #     writer = csv.writer(file)
    #     rel = 'own'
    #     writer.writerow([user_id,rel, class_id])  # 记录每个班级与用户的关系
    #
    # with open('data/class.csv', mode='a', newline='', encoding='utf-8') as file:
    #     writer = csv.writer(file)
    #     writer.writerow([class_id, course_name, capacity])  # 记录每个班级与用户的关系

    return class_id

def create_class_for_user(driver, user_id, role, capacity, course_name):
    role = str(role)  # 确保 role 是字符串类型
    if role != '1':  # 只有管理员角色（role == '1'）可以创建班级
        print("User does not have permission to create a class.")
        return None

    class_id = generate_class_id()  # 生成班级ID
    class_id = create_class(driver, user_id, class_id, capacity, course_name)  # 创建班级
    return class_id
