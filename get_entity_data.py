import re
import os


if __name__ == "__main__":
    with open(os.path.join("data","medical.json"),encoding="utf-8") as f:
        all_data = f.read().split("\n")

    # client = py2neo.Graph("http://127.0.0.1:7474", user="neo4j", password="123456")
    # client.run("match (n) detach delete (n)")

    all_entity = {
        "disease": [],  # 疾病
        "common_drug": [],  # 常用药品
        "food": [],  # 食物
        "check": [],  # 检查项目
        "cure_department": [],  # 科目
        "drug_manufacturers": [],  # 药品商
        "symptom": [],  # 疾病症状
        "cure_way": [],  # 治疗方法
    }

    for data in all_data:
        if len(data) < 3:
            continue
        data = eval(data)

        disease_name = data.get("name","")
        all_entity["disease"].append({                   # 添加 疾病实体
            "disease_name": disease_name,
            "desc": data.get("desc", ""),
            "cause": data.get("cause", ""),
            "prevent": data.get("prevent", ""),
            "cure_lasttime": data.get("cure_lasttime", ""),
            "cured_prob": data.get("cured_prob", ""),
            "easy_get": data.get("easy_get", ""),
        })

        drugs = data.get("common_drug", []) + data.get("recommand_drug", [])
        all_entity["common_drug"].extend(drugs)  # 添加药品实体

        do_eat = data.get("do_eat", [])
        rec_eat = data.get("recommand_eat", [])
        not_eat = data.get("not_eat",[])
        all_entity["food"].extend(do_eat + not_eat + rec_eat)  # 添加药品实体

        check = data.get("check", [])
        all_entity["check"].extend(check)

        cure_department = data.get("cure_department", [])
        all_entity["cure_department"].extend(cure_department)

        sympom = data.get("symptom", [])
        all_entity["symptom"].extend(sympom)

        cure_way = data.get("cure_way", [])
        all_entity["cure_way"].extend(cure_way)

        drug_detail = data.get("drug_detail", [])
        pattern = r"(.*?)\((.*?)\)"
        for drug_str in drug_detail:
            dp = re.findall(pattern,drug_str)
            if len(dp) != 0:
                pr, p = dp[0]
                pr = pr.strip(p)
                all_entity["drug_manufacturers"].append(pr)
                all_entity["common_drug"].append(p)

    all_entity = {k: list(set(v)) if k != "disease" else v for k, v in all_entity.items()}

    with open(os.path.join("entity", "disease.txt"), "w", encoding="utf-8") as f:
        for e in all_entity["disease"]:
            f.write(str(e))
            f.write("\n")

    for name, entities in all_entity.items():
        if name != "disease":
            with open(os.path.join("entity", f"{name}.txt"), "w", encoding="utf-8") as f:
                for e in entities:
                    f.write(str(e))
                    f.write("\n")
