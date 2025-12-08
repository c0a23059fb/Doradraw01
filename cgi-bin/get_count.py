#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cgi
import os
import sys
import json
import csv

# Windows等での改行コード対策
if sys.platform == "win32":
    import msvcrt
    msvcrt.setmode(0, os.O_BINARY)
    msvcrt.setmode(1, os.O_BINARY)

print("Content-Type: application/json; charset=utf-8")
print()

try:
    # URLパラメータから label を取得
    form = cgi.FieldStorage()
    target_label = form.getvalue('label', '0')
    
    data_dir = "data"
    
    # 集計用辞書: counts[char_name][emotion][part] = count
    counts = {}
    
    # パーツ定義
    valid_parts = ['left_eye', 'right_eye', 'mouth']

    if os.path.exists(data_dir):
        # data/{emotion}/{charName}_{part}_x.csv という構造を探索
        for emotion in os.listdir(data_dir):
            emotion_dir = os.path.join(data_dir, emotion)
            if not os.path.isdir(emotion_dir):
                continue
                
            for file in os.listdir(emotion_dir):
                # _x.csv だけを対象にする
                if file.endswith("_x.csv"):
                    # ファイル名からキャラクター名とパーツ名を特定する
                    # ファイル名例: "doraemon_left_eye_x.csv"
                    name_part_base = file.replace("_x.csv", "")
                    
                    detected_part = None
                    char_name = None
                    
                    # パーツ名で終わっているかチェック
                    for vp in valid_parts:
                        suffix = "_" + vp
                        if name_part_base.endswith(suffix):
                            detected_part = vp
                            # パーツ名と区切り文字(_)を除去してキャラ名を取得
                            char_name = name_part_base[:-len(suffix)]
                            break
                    
                    if detected_part and char_name:
                        # 辞書の初期化
                        if char_name not in counts:
                            counts[char_name] = {}
                        if emotion not in counts[char_name]:
                            counts[char_name][emotion] = {p: 0 for p in valid_parts}
                        
                        # 行数をカウント（該当ラベルのみ）
                        full_path = os.path.join(emotion_dir, file)
                        try:
                            with open(full_path, 'r', encoding='utf-8') as f:
                                reader = csv.reader(f)
                                c = 0
                                for row in reader:
                                    if row and len(row) > 0 and row[0] == target_label:
                                        c += 1
                                counts[char_name][emotion][detected_part] = c
                        except:
                            pass

    # "3パーツ揃った数" (faces) を計算して整形
    # 結果構造: result[char_name][emotion] = 枚数
    breakdown = {}
    total_faces = 0

    for char_name, emotion_dict in counts.items():
        if char_name not in breakdown:
            breakdown[char_name] = {}
        
        for emotion, parts_count in emotion_dict.items():
            # 3パーツのうち最小のカウント数を「完成枚数」とする
            completed = min(parts_count.values())
            if completed > 0:
                breakdown[char_name][emotion] = completed
                total_faces += completed

    print(json.dumps({
        "status": "success",
        "label": target_label,
        "total": total_faces,
        "breakdown": breakdown  # { "sample": {"angry": 2, "happy": 1}, ... }
    }))

except Exception as e:
    import traceback
    print(json.dumps({"status": "error", "message": str(e), "detail": traceback.format_exc()}))