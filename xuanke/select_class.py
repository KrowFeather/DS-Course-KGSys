import csv


def select_class(driver, user_id, role, class_id):
    user_id = int(user_id)

    if role != '0':  # 仅允许 role 为 0 的用户加入班级
        print("User does not have permission to join a class.")
        return None

    # 查找班级节点
    query_class = f"MATCH (c:Class {{class_id: '{class_id}'}}) RETURN c"
    result_class = driver.run(query_class).data()

    if not result_class:
        print(f"Class {class_id} does not exist.")
        return None

    # 查找用户节点
    query_user = f"MATCH (u:user {{id: {user_id}}}) RETURN u"
    result_user = driver.run(query_user).data()

    if not result_user:
        print(f"User with id {user_id} does not exist.")
        return None

    # 检查是否已经存在该关系
    query_existing_relationship = (
        f"MATCH (c:Class {{class_id: '{class_id}'}})-[:selection]->(u:user {{id: {user_id}}}) "
        f"RETURN u, c"
    )
    existing_rel = driver.run(query_existing_relationship).data()

    if existing_rel:
        print(f"User {user_id} is already part of class {class_id}.")
        return 'exsist'  # 或者返回其他信息，表示已存在

    # 为用户与班级创建 SELECTION 关系
    query_selection = (
        f"MATCH (u:user {{id: {user_id}}}), (c:Class {{class_id: '{class_id}'}}) "
        f"CREATE (c)-[:selection]->(u)"
    )
    driver.run(query_selection)

    # 记录班级与用户关系
    with open('data/student_class.csv', mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        rel = 'selection'
        writer.writerow([class_id, rel, user_id])  # 记录每个班级与用户的关系

    print(f"User {user_id} has successfully joined class {class_id}.")
    return class_id
