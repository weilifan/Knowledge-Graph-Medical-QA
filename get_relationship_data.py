import re
import os


if __name__ == "__main__":
    with open(os.path.join("data","medical.json"),encoding="utf-8") as f:
        all_data = f.read().split("\n")

    all_relationship = []

    for data in all_data:
        if len(data) < 3:
            continue
        data = eval(data)

        disease_name = data.get("name","")

        drugs = data.get("common_drug", []) + data.get("recommand_drug", [])
        if drugs:
            all_relationship.extend([(disease_name, "disease", "recommend_drug", d, "common_drug") for d in drugs])  # 疾病使用药品

        do_eat = data.get("do_eat", [])
        rec_eat = data.get("recommand_eat", [])
        not_eat = data.get("not_eat",[])
        if do_eat + rec_eat:
            all_relationship.extend([(disease_name, "disease", "do_eat", f, "food") for f in do_eat + rec_eat])
        if not_eat:
            all_relationship.extend([(disease_name, "disease", "not_eat", f, "food") for f in not_eat])

        check = data.get("check", [])
        if check:
            all_relationship.extend([(disease_name, "disease", "do_check", c, "check") for c in check])

        cure_department = data.get("cure_department", [])
        if cure_department:
            all_relationship.append((disease_name, "disease", "belong_to", cure_department[-1],"cure_department"))

        sympom = data.get("symptom", [])
        if sympom:
            all_relationship.extend([(disease_name, "disease", "has_symptom", sy, "symptom") for sy in sympom])

        cure_way = data.get("cure_way", [])
        if cure_way:
            all_relationship.extend([(disease_name, "disease", "cured_by", cw, "cure_way") for cw in cure_way])

        acompany_with = data.get("acompany", [])
        if acompany_with:
            all_relationship.extend([(disease_name, "disease", "accompany_by", aw, "disease") for aw in acompany_with])

        drug_detail = data.get("drug_detail", [])
        pattern = r"(.*?)\((.*?)\)"
        for drug_str in drug_detail:
            dp = re.findall(pattern,drug_str)
            if len(dp) != 0:
                pr, p = dp[0]
                pr = pr.strip(p)

                if pr:
                    all_relationship.append((pr, "drug_manufacturers", "produce", p, "common_drug"))

    all_relationship = list(set(all_relationship))

    with open(os.path.join("relationship", "all_relationship.txt"), "w", encoding="utf-8") as f:
        for r in all_relationship:
            f.write(" ".join(r))
            f.write("\n")
