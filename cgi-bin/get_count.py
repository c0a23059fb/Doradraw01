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
    total_parts = 0
    
    # dataフォルダが存在する場合のみ検索
    if os.path.exists(data_dir):
        # dataフォルダ以下（感情フォルダ含む）をすべて探索
        for root, dirs, files in os.walk(data_dir):
            for file in files:
                # _x.csv だけをカウント対象にする（yやaccを含めると重複するため）
                if file.endswith("_x.csv"):
                    full_path = os.path.join(root, file)
                    try:
                        with open(full_path, 'r', encoding='utf-8') as f:
                            reader = csv.reader(f)
                            for row in reader:
                                # 1列目(row[0])がラベル
                                if row and len(row) > 0 and row[0] == target_label:
                                    total_parts += 1
                    except:
                        continue

    # 3パーツ（右目・左目・口）で1枚（1顔）とみなして計算
    faces_count = total_parts // 3
    
    print(json.dumps({
        "status": "success",
        "label": target_label,
        "parts": total_parts,
        "faces": faces_count
    }))

except Exception as e:
    print(json.dumps({"status": "error", "message": str(e)}))