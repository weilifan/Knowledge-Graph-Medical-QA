import os
import ahocorasick  # 字符串匹配AC自动机，其实就是在Trie树上实现KMP，可以完成多模式串的匹配


class TrieNer:
    def __init__(self):
        self.tag_2_entity = {}
        self.tag_2_tree = {}

        root_path = "entity"
        files = os.listdir(root_path)
        self.type_2_entites = {}
        for file in files:
            tag = file.strip(".txt")

            with open(os.path.join(root_path, file), encoding="utf-8") as f:
                entity = f.read().split("\n") if tag != "disease" else [eval(i)['disease_name'] for i in f.read().split("\n") if i != ""]

                self.tag_2_tree[tag] = ahocorasick.Automaton()
                for ent in entity:
                    self.tag_2_tree[tag].add_word(ent, ent)
                self.tag_2_tree[tag].make_automaton()

    def find_entity(self, text):
        result = []
        result_ = []

        for type, tree in self.tag_2_tree.items():
            r = list(tree.iter(text))
            if r:
                for i in r:
                    s, e = i[0]-len(i[1])+1, i[0]+1
                    if (s, e) not in result_:
                        result.append((s, e, i[1], type))
                        result_.append((s, e))
        return result

    def check_tag(self, ents):
        new_ents = [ents[0]]
        s, e = ents[0][:2]
        for sidx, eidx, ent, type in ents[1:]:
            if s >= sidx and e <= eidx:
                new_ents.pop()
            new_ents.append((sidx, eidx, ent, type))
            s, e = sidx, eidx
        return new_ents


if __name__ == "__main__":
    rener = TrieNer()
    while True:
        input_text = input("请输入：")
        input_text = input_text[:510]

        re_result = rener.check_tag(rener.find_entity(input_text))

        print(re_result)
