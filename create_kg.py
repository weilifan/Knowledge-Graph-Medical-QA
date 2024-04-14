import py2neo
import re
import os
from tqdm import tqdm


def create_node(client, type, entity_list):
    print(f"正在导入{type}类型节点")
    for entity in tqdm(entity_list):
        cmd = """ create (a:%s {name:"%s"})  """ % (type, entity)

        client.run(cmd)


def create_disease_node(client, disease_list):
    print(f"正在导入疾病类型的节点")

    for disease in tqdm(disease_list):
        try:
            disease = eval(disease)
            node = py2neo.Node("disease",
                               name=disease["disease_name"],
                               desc=disease["desc"],
                               cause=disease["cause"],
                               prevent=disease["prevent"],
                               cure_lasttime=disease["cure_lasttime"],
                               cured_prob=disease["cured_prob"],
                               easy_get=disease['easy_get'])
            client.create(node)
        except:
            continue


def create_relationship(client, relationship_list):
    print("正在导入所有关系...")
    for data in tqdm(relationship_list):
        try:
            name1, type1, relation_ship, name2, type2 = data.split(" ")
            # clinet.run("match (a:老师 {姓名:'王小明'}),(b:学生 {姓名:'小明'}) create (a)-[rel:学生]->(b) ")
            cmd = f""" match (a:{type1} {{name:"{name1}"}}),(b:{type2} {{name:"{name2}"}})  create (a)-[rel:{relation_ship}]->(b) """
            client.run(cmd)
        except:
            print(data.split(" "))
            continue


if __name__ == "__main__":
    # with open(os.path.join("data","medical.json"),encoding="utf-8") as f:
    #     all_data = f.read().split("\n")

    client = py2neo.Graph("http://127.0.0.1:7474", user="neo4j", password="123456")
    client.run("match (n) detach delete (n)")

    # all_entity = {
    #     "disease": [],  # 疾病
    #     "common_drug": [],  # 常用药品
    #     "food": [],  # 食物
    #     "check": [],  # 检查项目
    #     "cure_department": [],  # 科目
    #     "drug_manufacturers": [],  # 药品商
    #     "symptom": [],  # 疾病症状
    #     "cure_way": [],  # 治疗方法
    # }
    #
    # all_relationship = []
    #
    # for data in all_data:
    #     if len(data) < 3:
    #         continue
    #     data = eval(data)
    #
    #     disease_name = data.get("name","")
    #     all_entity["disease"].append({                   # 添加 疾病实体
    #         "disease_name": disease_name,
    #         "desc": data.get("desc", ""),
    #         "cause": data.get("cause", ""),
    #         "prevent": data.get("prevent", ""),
    #         "cure_lasttime": data.get("cure_lasttime", ""),
    #         "cured_prob": data.get("cured_prob", ""),
    #         "easy_get": data.get("easy_get", ""),
    #     })
    #
    #     drugs = data.get("common_drug", []) + data.get("recommand_drug", [])
    #     all_entity["common_drug"].extend(drugs)  # 添加药品实体
    #     if drugs:
    #         all_relationship.extend([(disease_name, "disease", "recommend_drug", d, "common_drug") for d in drugs])  # 疾病使用药品
    #
    #     do_eat = data.get("do_eat", [])
    #     rec_eat = data.get("recommand_eat", [])
    #     not_eat = data.get("not_eat",[])
    #     all_entity["food"].extend(do_eat + not_eat + rec_eat)  # 添加药品实体
    #     if do_eat + rec_eat:
    #         all_relationship.extend([(disease_name, "disease", "do_eat", f, "food") for f in do_eat + rec_eat])
    #     if not_eat:
    #         all_relationship.extend([(disease_name, "disease", "not_eat", f, "food") for f in not_eat])
    #
    #     check = data.get("check", [])
    #     all_entity["check"].extend(check)
    #     if check:
    #         all_relationship.extend([(disease_name, "disease", "do_check", c, "check") for c in check])
    #
    #     cure_department = data.get("cure_department", [])
    #     all_entity["cure_department"].extend(cure_department)
    #     if cure_department:
    #         all_relationship.append((disease_name, "disease", "belong_to", cure_department[-1],"cure_department"))
    #
    #     sympom = data.get("symptom", [])
    #     all_entity["symptom"].extend(sympom)
    #     if sympom:
    #         all_relationship.extend([(disease_name, "disease", "has_symptom", sy, "symptom") for sy in sympom])
    #
    #     cure_way = data.get("cure_way", [])
    #     all_entity["cure_way"].extend(cure_way)
    #     if cure_way:
    #         all_relationship.extend([(disease_name, "disease", "cured_by", cw, "cure_way") for cw in cure_way])
    #
    #     acompany_with = data.get("acompany", [])
    #     if acompany_with:
    #         all_relationship.extend([(disease_name, "disease", "accompany_by", aw, "disease") for aw in acompany_with])
    #
    #     drug_detail = data.get("drug_detail", [])
    #     pattern = r"(.*?)\((.*?)\)"
    #     for drug_str in drug_detail:
    #         dp = re.findall(pattern,drug_str)
    #         if len(dp) != 0:
    #             pr, p = dp[0]
    #             pr = pr.strip(p)
    #             all_entity["drug_manufacturers"].append(pr)
    #             all_entity["common_drug"].append(p)
    #
    #             if pr:
    #                 all_relationship.append((pr, "drug_manufacturers", "produce", p, "common_drug"))
    #
    # all_entity = {k: list(set(v)) if k != "disease" else v for k, v in all_entity.items()}
    # all_relationship = list(set(all_relationship))
    #
    # with open("disease.txt", "w", encoding="utf-8") as f:
    #     for e in all_entity["disease"]:
    #         f.write(str(e))
    #         f.write("\n")
    #
    # for name, entities in all_entity.items():
    #     if name != "disease":
    #         with open(f"{name}.txt", "w", encoding="utf-8") as f:
    #             for e in entities:
    #                 f.write(str(e))
    #                 f.write("\n")
    #
    # with open("all_relation_ship.txt", "w", encoding="utf-8") as f:
    #     for r in all_relationship:
    #         f.write(" ".join(r))
    #         f.write("\n")
    #
    # with open(os.path.join("data","medical.json"),encoding="utf-8") as f:
    #     all_data = f.read().split("\n")

    for file_name in os.listdir("entity"):
        k = file_name.split(".txt")[0]
        if k != "disease":
            with open(os.path.join("entity", file_name), encoding="utf-8") as f:
                all_data = f.read().split("\n")
                create_node(client, k, all_data)
        else:
            with open(os.path.join("entity", file_name), encoding="utf-8") as f:
                all_data = f.read().split("\n")
                create_disease_node(client, all_data)

    # for k in all_entity:
    #     if k != "疾病":
    #         create_node(client,k,all_entity[k])
    #     else:
    #         create_disease_node(client,all_entity["疾病"])

    # with open("all_relation_ship.txt","w",encoding="utf-8") as f:
    #     for r in all_relationship:
    #         f.write(" ".join(r))
    #         f.write("\n")
    with open(os.path.join("relationship", "all_relationship.txt"), encoding="utf-8") as f:
        all_data = f.read().split("\n")
        create_relationship(client, all_data)
