class QuestionCls:
    def __init__(self, client):
        self.client = client
        self.dis_sym_kw = ["症状", "现象", "会怎样", "会怎么样", "表征"]
        self.dis_drug_kw = ["吃什么药", "服用"]
        self.dis_food_kw = ["吃什么东西", "饮食", "膳食", "伙食", "食用", "补品", "食品", "菜谱", "食谱"]
        self.drug_dis_kw = ["可以治", "治疗啥", "主治什么", "治什么病"]

        self.dis_cure_kw = ["怎么办", "该怎么办", "如何治疗", "怎么治疗", "咋治", "咋办"]

    def text_2_query(self, text, entity_list):
        # entity_list = [(0,4,"XXX","疾病"),(5,9,"XXX","疾病症状")]

        _, _, ents, clss = zip(*entity_list)

        query = ""

        try:
            dis_idx = clss.index("disease")
        except:
            dis_idx = -1

        try:
            drug_idx = clss.index("common_drug")
        except:
            drug_idx = -1

        if dis_idx != -1 and self.keyword_in(text, self.dis_sym_kw):
            query = """ match (a:disease {name:"%s"})-[r:has_symptom]->(b:symptom) return b.name""" % (ents[dis_idx])

            result = self.client.run(query)
            result_text = result.data()
            result_text = [list(i.values())[0] for i in result_text]

            answer = f"症状有：{'、'.join(result_text)}"

        elif dis_idx != -1 and self.keyword_in(text, self.dis_drug_kw):
            query = """ match (a:disease {name:"%s"})-[r:recommend_drug]->(b:common_drug) return b.name""" % (
            ents[dis_idx])
            result = self.client.run(query)
            result_text = result.data()
            result_text = [list(i.values())[0] for i in result_text]

            answer = f"可以服用以下药物：{'、'.join(result_text)}"

        elif dis_idx != -1 and self.keyword_in(text, self.dis_food_kw):
            query = """ match (a:disease {name:"%s"})-[r:do_eat]->(b:food) return b.name""" % (ents[dis_idx])
            result = self.client.run(query)
            result_text = result.data()
            result_text = [list(i.values())[0] for i in result_text]

            answer = f"可以食用：{'、'.join(result_text)}"

        elif drug_idx != -1 and self.keyword_in(text, self.drug_dis_kw):
            query = """ match (a:disease)-[r:recommend_drug]->(b:common_drug  {name:"%s"}) return a.name""" % (
            ents[drug_idx])
            result = self.client.run(query)
            result_text = result.data()
            result_text = [list(i.values())[0] for i in result_text]

            answer = f"该药主要治疗：{'、'.join(result_text)}"

        elif dis_idx != -1 and self.keyword_in(text, self.dis_cure_kw):
            query = """ match (a:disease {name:"%s"})-[r:cured_by]->(b:cure_way) return b.name""" % (ents[dis_idx])
            result = self.client.run(query)
            result_text = result.data()
            result_text = [list(i.values())[0] for i in result_text]

            answer = f"可以通过一下方式进行治疗：{'、'.join(result_text)}"

        else:
            answer = "不好意思，没听懂！请重新问。"

        return answer

    def keyword_in(self, text, keyword_lst):
        for word in keyword_lst:
            if word in text:
                return True
        return False
