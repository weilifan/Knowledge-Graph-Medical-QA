import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class EntityAlign:
    def __init__(self):
        root_path = "entity"
        files = os.listdir(root_path)
        self.tag_2_embs = {}
        self.tag_2_tfidf_model = {}
        for file in files:
            tag = file.strip(".txt")

            with open(os.path.join(root_path, file), encoding="utf-8") as f:
                entity = f.read().split("\n") if tag != "disease" else [eval(i)['disease_name'] for i in
                                                                        f.read().split("\n") if i != ""]
            tfidf_model = TfidfVectorizer(analyzer="char")
            embs = tfidf_model.fit_transform(entity).toarray()

            self.tag_2_embs[tag] = embs
            self.tag_2_tfidf_model[tag] = tfidf_model

    def align(self, ent_list):
        new_reuslt = []

        for s, e, ent, cls in ent_list:

            ent_emb = self.tag_2_tfidf_model[cls].transform([ent])
            sim_score = cosine_similarity(ent_emb, self.tag_2_embs[cls])
            max_idx = sim_score[0].argmax()
            max_score = sim_score[0][max_idx]

            if max_score >= 0.5:
                new_reuslt.append((s, e, ent, cls))
        return new_reuslt


if __name__ == "__main__":
    ea = EntityAlign()
    new_result = ea.align([[0, 3, "阳痿早泄", "disease"]])
    print(new_result)