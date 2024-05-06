import py2neo
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
    client = py2neo.Graph("http://127.0.0.1:7474", user="neo4j", password="123456")
    client.run("match (n) detach delete (n)")

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

    with open(os.path.join("relationship", "all_relationship.txt"), encoding="utf-8") as f:
        all_data = f.read().split("\n")
        create_relationship(client, all_data)
