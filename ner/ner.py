from transformers import BertModel, BertTokenizer
import torch
import torch.nn as nn
import os
from sklearn.model_selection import train_test_split
from torch.utils.data import Dataset,DataLoader
from seqeval.metrics import f1_score
from tqdm import tqdm
import random
import numpy as np


def read_data(file):
    with open(file,"r",encoding="utf-8") as f:
        all_data = f.read().split("\n")

    all_text = []
    all_label = []

    text = []
    label = []
    for data in all_data:
        if data == "":
            all_text.append(text)
            all_label.append(label)
            text = []
            label = []
        else:

            data_s = data.split(" ")
            if len(data_s) != 2:
                continue

            text.append(data_s[0])
            label.append(data_s[1])

    new_text = []
    new_label = []

    for text,tag in zip(all_text,all_label):
        if tag.count("O") != len(tag):
            new_text.append(text)
            new_label.append(tag)
    return new_text,new_label


def find_entities(text,tag_list):
    result = [] # [ (0,2,食品") ,(4,10,"药品") ]
    b_idx = -1
    e_idx = -1
    type = ""

    is_O = True
    for idx, tag in enumerate(tag_list):
        if tag == "O":

            if is_O == True:
                continue
            else:
                e_idx = idx
                result.append((b_idx,idx,text[b_idx:idx],type))

                b_idx = -1
                e_idx = -1
                type = ""
            is_O = True
        else:

            if "B-" in tag:

                if is_O == False:
                    e_idx = idx
                    result.append((b_idx, idx,text[b_idx:idx], type))

                    b_idx = -1
                    e_idx = -1
                    type = ""


                b_idx = idx
                type = tag.strip("B-")




            is_O = False
    if b_idx != -1:
        result.append((b_idx,idx+1,text[b_idx:idx+1],type))
    return result


def check_tag(ents):
    new_ents = [ents[0]]
    s, e = ents[0][:2]
    for sidx, eidx, ent, type in ents[1:]:
        if s >= sidx and e <= eidx:
            new_ents.pop()
        new_ents.append((sidx, eidx, ent, type))
        s, e = sidx, eidx
    return new_ents


class Entity_Extend:
    def __init__(self):
        root_path = "../entity"
        files = os.listdir(root_path)
        self.type_2_entites = {}
        for file in files:
            type_ = file.strip(".txt")

            with open(os.path.join(root_path,file),encoding="utf-8") as f:
                entities = f.read().split("\n")
            if type_ != "disease":
                self.type_2_entites[type_] = entities
            else:
                d_n = []
                for i in entities:
                    if i != "":
                        d = eval(i)
                        d_n.append(d['disease_name'])
                self.type_2_entites[type_] = d_n

    def entity_replace(self,entity,type):
        entity = "".join(entity)
        while True:
            other_entity = random.choice(self.type_2_entites[type])
            if entity != other_entity:

                new_entity = [i for i in other_entity]
                new_tag =  ["B-"+type] + ["I-"+type]*(len(other_entity)-1)

                try:
                    assert len(new_entity) == len(new_tag),"entity_replace  长度不一致！"
                except:
                    print("entity_replace  长度不一致！")

                return  new_entity,new_tag

    def entity_mask(self,entity,type):
        if len(entity)<2:
            return entity,["B-" + type] + ["I-" + type] * (len(entity) - 1)

        new_entity = entity.copy()

        if len(entity) <=5 :
            new_entity.pop(random.randint(0,len(new_entity)-1))
            new_tag = ["B-"+type] + ["I-"+type]*(len(new_entity)-1)

        else:

            new_entity.pop(random.randint(0, len(new_entity) - 1))
            new_entity.pop(random.randint(0, len(new_entity) - 1))

            new_tag = ["B-" + type] + ["I-" + type] * (len(new_entity) - 1)

        try:
            assert len(new_entity) == len(new_tag),"entity_mask 长度不一致"
        except:
            print("entity_mask")
        return new_entity, new_tag

    def entity_merge(self,entity,type):
        join_word = ["和","与","还有","、"]
        entity = "".join(entity)
        while True:
            other_entity = random.choice(self.type_2_entites[type])
            if entity != other_entity:
                jw = random.choice(join_word)
                new_entity = entity + jw + other_entity
                new_tag = ["B-"+type] + ["I-"+type]*(len(entity)-1) + ["O"] * len(jw) + ["B-"+type] + ["I-"+type]*(len(other_entity)-1)

                try:
                    assert len(new_entity) == len(new_tag),"entity_merge 长度不一致"
                except:
                    print("entity_merge  长度不一致！")
                return new_entity,new_tag

    def entites_extend(self,text,tag,ents):
        new_text = text.copy()
        new_tag = tag.copy()

        # 1. 实体替换

        ps = [self.entity_merge,self.entity_replace,self.entity_replace]

        sign = 0
        for ent in ents:



            p = random.choice(ps)
            temp_ent,temp_tag = p(text[ent[0]:ent[1]],ent[-1])

            new_text[ent[0]+sign:ent[1]+sign] = temp_ent
            new_tag[ent[0]+sign:ent[1]+sign] = temp_tag

            sign += (len(temp_tag)-(ent[1]-ent[0]))


        return  new_text,new_tag


class NerDataset(Dataset):
    def __init__(self,all_text,all_tag,tokenizer,max_len,tag_2_index,is_train=True):
        self.all_text = all_text
        self.all_tag = all_tag
        self.tokenizer = tokenizer
        self.max_len = max_len
        self.tag_2_index = tag_2_index
        self.extend = Entity_Extend()
        self.is_train = is_train
        print("")

    def __getitem__(self, index):
        text = self.all_text[index]
        tag = self.all_tag[index]

        if self.is_train == True:
            ents = find_entities(text, tag)

            new_text,new_tag = self.extend.entites_extend(text,tag,ents)

            if len(new_text) == len(new_tag):
                text = new_text
                tag = new_tag

        text = text[:(max_len-2)]
        tag = tag[:(max_len-2)]

        text_len = len(text)

        text_idx = self.tokenizer.encode(text,padding="max_length",max_length=self.max_len,truncation=True)
        tag_idx = [self.tag_2_index["<PAD>"]] +  [self.tag_2_index[i] for i in tag] + [self.tag_2_index["<PAD>"]]  + [self.tag_2_index["<PAD>"]]*(self.max_len-text_len-2)

        # try:
        assert len(text_idx) == len(tag_idx) == self.max_len,"text和tag长度都不一样，Ner个求啊！"
        # except e:
        #     return None

        return torch.tensor(text_idx),torch.tensor(tag_idx),text_len

    def __len__(self):
        return len(self.all_text)


def build_index2tag(all_tag):
    tag_2_index = {"<PAD>":0}
    for tags in all_tag:
        for tag in tags:
            tag_2_index[tag] = tag_2_index.get(tag,len(tag_2_index))
    return tag_2_index,list(tag_2_index)


class NerModel(nn.Module):
    def __init__(self,lstm_hidden_num,tag_num):
        super(NerModel, self).__init__()
        self.bert = BertModel.from_pretrained("bert-base-chinese")
        for name,param in self.bert.named_parameters():
            # if pooler not in name:
                param.requires_grad =  True

            # if "7" in name:
            #     param.requires_grad = True

        self.lstm = nn.LSTM(768,lstm_hidden_num,batch_first=True,bidirectional=False)

        self.classifier = nn.Linear(lstm_hidden_num,tag_num)
        self.loss_fun = nn.CrossEntropyLoss(ignore_index=0)

    def forward(self,batch_text_idx,batch_tag_idx=None):
        bert_out0,bert_out1 = self.bert(batch_text_idx,attention_mask=batch_text_idx>0,return_dict=False)

        lstm_out0,list_out1 = self.lstm(bert_out0)
        pre  = self.classifier(lstm_out0)

        if batch_tag_idx != None:
            loss = self.loss_fun(pre.reshape(-1,pre.shape[-1]),batch_tag_idx.reshape(-1))
            return loss
        else:
            return torch.argmax(pre,-1)


def seed_torch(seed=24):
    random.seed(seed)
    os.environ['PYTHONHASHSEED'] = str(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)  # if you are using multi-GPU.
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.enabled = False


if __name__ == "__main__":
    seed_torch()
    all_text, all_tag = read_data("all_ner.txt")
    train_text, dev_text, train_tag, dev_tag = train_test_split(all_text, all_tag, test_size = 0.18, random_state = 42)

    tag_2_index, index_2_tag = build_index2tag(all_tag)

    batch_size = 50
    epoch = 1  # 10
    max_len = 50
    lstm_hidden_num = 128
    lr = 0.00001

    best_f1 = -1

    device = "cuda:0" if torch.cuda.is_available() else "cpu"

    tokenizer = BertTokenizer.from_pretrained("bert-base-chinese")

    train_dataset = NerDataset(train_text,train_tag,tokenizer,max_len,tag_2_index,True)
    train_dataloader = DataLoader(train_dataset,batch_size,shuffle=False)

    dev_dataset = NerDataset(dev_text, dev_tag, tokenizer, max_len, tag_2_index,False)
    dev_dataloader = DataLoader(dev_dataset, batch_size, shuffle=False)

    model = NerModel(lstm_hidden_num, len(tag_2_index)).to(device)
    opt = torch.optim.Adam(model.parameters(), lr=lr)

    for e in range(epoch):
        model.train()
        for batch_text_idx, batch_tag_idx, batch_len in tqdm(train_dataloader):
            batch_text_idx = batch_text_idx.to(device)
            batch_tag_idx = batch_tag_idx.to(device)
            loss = model.forward(batch_text_idx, batch_tag_idx)
            loss.backward()
            opt.step()
            opt.zero_grad()

            # print(loss)
            break

        model.eval()

        all_pre = []
        all_dev = []
        for batch_text_idx,batch_tag_idx,batch_len in dev_dataloader:
            batch_text_idx = batch_text_idx.to(device)
            batch_tag_idx = batch_tag_idx.to(device)
            pre = model.forward(batch_text_idx)

            for t, p, l in zip(batch_tag_idx,pre,batch_len):
                l = int(l)
                all_dev.append([index_2_tag[int(i)] for i in t[1:l+1]])
                all_pre.append([index_2_tag[int(i)] for i in p[1:l+1]])
            break

        f1 = f1_score(all_dev, all_pre)

        # if f1 > best_f1 and f1 > 0.75:
        if f1 > best_f1:
            torch.save(model, "best_model.pt")

        print(f"epoch:{e},f1:{f1:.4f}")

