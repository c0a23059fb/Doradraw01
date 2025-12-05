#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import json
import os
import csv
import cgitb

# エラーをブラウザに表示する設定（デバッグ用）
cgitb.enable()

# Windows等での改行コード問題を防ぐおまじない
if sys.platform == "win32":
    import msvcrt
    msvcrt.setmode(0, os.O_BINARY)
    msvcrt.setmode(1, os.O_BINARY)

def main():
    # ヘッダー出力
    print("Content-Type: application/json; charset=utf-8")
    print()

    try:
        # POSTデータの読み込み
        content_length = int(os.environ.get('CONTENT_LENGTH', 0))
        if content_length == 0:
            print(json.dumps({"status": "error", "message": "No data received"}))
            return

        body = sys.stdin.read(content_length)
        data = json.loads(body)

        # 必要な情報の抽出
        label = data.get('label', '0')
        char_name = data.get('charName', 'unknown')
        part = data.get('part', 'unknown')
        points = data.get('points', []) # [{x:..., y:...}, ...]

        if not points:
            print(json.dumps({"status": "error", "message": "No points data"}))
            return

        # ---------------------------------------------------------
        # 論文の手法に基づくデータ処理
        # ---------------------------------------------------------
        
        # 配列の初期化
        x_list = []
        y_list = []
        x_acc_list = []
        y_acc_list = []

        # 1. 座標リストの作成
        for p in points:
            x_list.append(p['x'])
            y_list.append(p['y'])

        # 2. 加速度の計算
        # 論文式: a_x(i) = x(i+1) - x(i)
        # ※ 加速度データは座標データより1つ少なくなります
        for i in range(len(points) - 1):
            ax = points[i+1]['x'] - points[i]['x']
            ay = points[i+1]['y'] - points[i]['y']
            x_acc_list.append(ax)
            y_acc_list.append(ay)

        # ---------------------------------------------------------
        # CSVファイルへの保存
        # ---------------------------------------------------------
        
        # 保存先ディレクトリ（dataフォルダを作成）
        data_dir = "data"
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

        # ファイル名の定義 (論文: dra_right_eye_x.csv 等)
        base_filename = f"{char_name}_{part}"
        
        files_config = [
            # (suffix, data_list)
            ("_x.csv", x_list),
            ("_y.csv", y_list),
            ("_x_acc.csv", x_acc_list),
            ("_y_acc.csv", y_acc_list)
        ]

        saved_files = []

        for suffix, val_list in files_config:
            filename = os.path.join(data_dir, base_filename + suffix)
            
            # 論文形式: 1列目がラベル、2列目以降がデータ
            # 行 = 1サンプル
            row_data = [label] + val_list
            
            # 追記モードで保存
            with open(filename, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(row_data)
            
            saved_files.append(filename)

        # 成功レスポンス
        print(json.dumps({
            "status": "success", 
            "message": "Data saved successfully",
            "files": saved_files
        }))

    except Exception as e:
        # エラーハンドリング
        import traceback
        error_msg = traceback.format_exc()
        print(json.dumps({"status": "error", "message": str(e), "detail": error_msg}))

if __name__ == "__main__":
    main()