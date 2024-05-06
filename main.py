import torch
import py2neo
import gradio as gr

from ner.entity_align import EntityAlign
from ner.trie_ner import TrieNer
from ner.ner import NerModel
from question_classification import QuestionCls


class Search:
    def __init__(self, model_ner, trie_ner, ent_align, question_cls, idx_2_tag, dev):
        self.model_ner = model_ner
        self.trie_ner = trie_ner
        self.ent_align = ent_align
        self.question_cls = question_cls
        self.index_2_tag = idx_2_tag
        self.device = dev

    def ans(self, input_text, his):
        model_result = self.model_ner.find_entities(input_text, self.index_2_tag,
                                                    self.device)  # find_entities(input_text, pre)
        re_result = self.trie_ner.check_tag(self.trie_ner.find_entity(input_text))

        r = list(set(model_result + re_result))
        r = sorted(r, key=lambda x: (x[0], x[1]))

        result = self.trie_ner.check_tag(r)

        # result = merge(model_result, re_result)

        new_result = self.ent_align.align(result)  # 请问布洛芬颗粒可以治疗什么病

        answer = self.question_cls.text_2_query(input_text, new_result)
        return his + [[input_text, answer]]


if __name__ == "__main__":
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    model = torch.load("ner/best_model.pt", map_location=device)

    with open("index_2_tag.txt", encoding="utf-8") as f:
        index_2_tag = f.read().split("\n")
        tag_2_index = {k: i for i, k in enumerate(index_2_tag)}

    ea = EntityAlign()
    tner = TrieNer()
    max_len = 50

    client = py2neo.Graph("http://127.0.0.1:7474", user="neo4j", password="123456")
    qu = QuestionCls(client)

    search = Search(model, tner, ea, qu, index_2_tag, device)

    with gr.Blocks() as Robot:
        chatbot = gr.Chatbot([[None, "this is😎医疗知识图谱机器人"]], show_label=False, height=650)

        query = gr.Textbox(show_label=False, placeholder="输入问题，回车提问😎", container=False)
        query.submit(search.ans, inputs=[query, chatbot], outputs=[chatbot])
        with gr.Row():
            with gr.Column():
                button1 = gr.Button(value="生成回答")
            with gr.Column():
                button2 = gr.Button(value="清空历史")
        button1.click(search.ans, inputs=[query, chatbot], outputs=[chatbot])
        button2.click(lambda a, b: [[None, "this is😎医疗知识图谱机器人"]], inputs=[query, chatbot], outputs=[chatbot])

    Robot.queue(concurrency_count=3).launch(server_name="127.0.0.1", server_port=9999, share=False)
