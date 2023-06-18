from ultralytics import YOLO
from sklearn.cluster import DBSCAN
from pathlib import Path
import streamlit as st

from mahjong.checker import HONORS, BACK, AKA_MAN, AKA_PIN, AKA_SOU, AKA_DORA, NINES


@st.cache_resource
def load_model():
    model_path = Path(__file__).resolve().parent / 'weights' / 'yolov8x.pt'
    model = YOLO(model_path)
    return model


MODEL = load_model()

IDS = {
    0: AKA_MAN, 1: AKA_PIN, 2: AKA_SOU, 3: BACK,
    **{_ // 10 + 35: _ for _ in NINES},
    **{4 * (_ + 1): _ for _ in range(8)},
    **{4 * (_ - 9) + 1: _ for _ in range(10, 18)},
    **{4 * (_ - 19) + 2: _ for _ in range(20, 28)},
    **{4 * (_ - 2) + 3: _ * 10 for _ in range(3, 10)}
}


def vertical_cluster(boxes, eps):
    y_coords = [[_.xyxy.tolist()[0][1]] for _ in boxes]
    # print("boxes".center(50, '-'))
    # print(np.array(y_coords))
    db = DBSCAN(eps=eps, min_samples=1).fit(y_coords)
    current = db.labels_[0]
    groups = [[]]
    for i in range(len(boxes)):
        new_cls = db.labels_[i]
        if new_cls != current:
            groups.append([boxes[i]])
        else:
            groups[-1].append(boxes[i])
        current = new_cls
    # print('clusters'.center(50, '-'))
    # print(db.labels_)
    return groups


def horizontal_split(boxes):
    x_coords = [_.xyxy.tolist()[0][0] for _ in boxes]
    widths = [_.xywh.tolist()[0][2] for _ in boxes]
    groups = [[boxes[0]]]
    for i in range(len(boxes) - 1):
        # print(x_coords[i + 1] - x_coords[i] - widths[i])
        if x_coords[i + 1] - x_coords[i] - widths[i] < 0.1 * widths[i]:
            groups[-1].append(boxes[i + 1])
        else:
            groups.append([boxes[i + 1]])
    return groups


def recognize(file, conf=0.5, to_str=True, display=True):
    output = MODEL.predict(source=file, conf=conf)[0]
    boxes = output.boxes
    res_plotted = None
    if display:
        res_plotted = output.plot()[:, :, ::-1]
    h = sum([_.xywh.tolist()[0][3] for _ in boxes]) / len(boxes)

    boxes = list(sorted(boxes, key=lambda _: _.xyxy.tolist()[0][1]))
    groups = vertical_cluster(boxes, 0.5 * h)

    lines = []
    for group in groups:
        group = list(sorted(group, key=lambda _: _.xyxy.tolist()[0][0]))
        line = horizontal_split(group)
        lines.append(line)
    if to_str:
        m = output.names
    else:
        m = IDS
    if display:
        return [[[m[_.cls.int().item()] for _ in items] for items in line] for line in lines], res_plotted
    else:
        return [[[m[_.cls.int().item()] for _ in items] for items in line] for line in lines]


def _id2str(id_list):
    m = p = s = z = ''
    for id_ in id_list:
        if id_ == -1:
            m += '0'
        elif id_ == 9:
            p += '0'
        elif id_ == 19:
            s += '0'
        elif id_ == -2:
            z += '0'
        elif 0 <= id_ < 9:
            m += str(id_ + 1)
        elif 10 <= id_ < 19:
            p += str(id_ - 9)
        elif 20 <= id_ < 29:
            s += str(id_ - 19)
        elif id_ in HONORS:
            z += str(id_ // 10 - 2)
        else:
            raise ValueError(f'Wrong ID: {id_}!')
    res = ''
    sort_key = lambda x: '5' if x == '0' else x
    if m:
        res += ''.join(sorted(m, key=sort_key)) + 'm'
    if p:
        res += ''.join(sorted(p, key=sort_key)) + 'p'
    if s:
        res += ''.join(sorted(s, key=sort_key)) + 's'
    if z:
        res += ''.join(sorted(z)) + 'z'
    return res


def id2str(id_list, concealed_kong=True):
    if concealed_kong and len(id_list) == 4 and id_list[0] == id_list[-1] == BACK:
        if id_list[1] != id_list[2]:
            if id_list[1] in AKA_DORA and id_list[2] == id_list[1] + 5:
                s = _id2str(id_list[1: -1])
                s = ''.join([s[1], s[0], s[1], s[1], s[1]]) + s[-1]
            elif id_list[2] in AKA_DORA and id_list[1] == id_list[2] + 5:
                s = _id2str(id_list[1: -1])
                s = ''.join([s[0], s[0], s[1], s[0], s[0]]) + s[-1]
            else:
                s = _id2str(id_list)
        else:
            s = _id2str([id_list[1]])
            s = s[0] * 5 + s[1]
    else:
        s = _id2str(id_list)
    return s


def to_string(id_groups):
    first_group = id_groups[0]
    hand_tiles, *others = first_group
    *hand_tiles, hu_tile = hand_tiles
    others = sum(id_groups[1:], others)
    s = [id2str(hand_tiles, concealed_kong=False)]
    for tiles in others:
        s.append(id2str(tiles, concealed_kong=True))
    hu_tile = id2str([hu_tile])
    return ' '.join(s), hu_tile
