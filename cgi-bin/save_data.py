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
        points = data.get('points', [])
        
        # 【追加】感情ラベルの取得（デフォルトは 'unknown'）
        emotion = data.get('emotion', 'unknown')

        if not points:
            print(json.dumps({"status": "error", "message": "No points data"}))
            return

        # ---------------------------------------------------------
        # 論文の手法に基づくデータ処理
        # ---------------------------------------------------------
        
# 45行目付近から修正
        # ---------------------------------------------------------
        # 論文の手法に基づくデータ処理 (時間・加速度対応)
        # ---------------------------------------------------------
        
        x_list = []
        y_list = []
        t_list = []
        x_acc_list = []
        y_acc_list = []

        # 1. 座標・時間リストの作成
        for p in points:
            x_list.append(p['x'])
            y_list.append(p['y'])
            t_list.append(p.get('t', 0)) # index.htmlで追加した時刻を取得

        # 2. 加速度の計算 (物理定義に基づく計算: a = dv / dt)
        # 点が3つ以上ある場合のみ加速度を計算可能
        if len(points) >= 3:
            vx = []
            vy = []
            # 速度 v = dx / dt の計算
            for i in range(len(points) - 1):
                dt = max(1, t_list[i+1] - t_list[i]) # 0除算回避
                vx.append((x_list[i+1] - x_list[i]) / dt)
                vy.append((y_list[i+1] - y_list[i]) / dt)
            
            # 加速度 a = dv / dt の計算
            for i in range(len(vx) - 1):
                dt = max(1, t_list[i+1] - t_list[i])
                x_acc_list.append((vx[i+1] - vx[i]) / dt)
                y_acc_list.append((vy[i+1] - vy[i]) / dt)

        # ---------------------------------------------------------
        # CSVファイルへの保存 (ディレクトリ分け)
        # ---------------------------------------------------------
        
        data_dir = os.path.join("data", emotion)
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

        base_filename = f"{char_name}_{part}"
        
        # 保存するファイル設定に "_t.csv" (時間) を追加
        files_config = [
            ("_x.csv", x_list),
            ("_y.csv", y_list),
            ("_t.csv", t_list),      # 時間データを追加
            ("_x_acc.csv", x_acc_list),
            ("_y_acc.csv", y_acc_list)
        ]

        saved_files = []
        for suffix, val_list in files_config:
            filename = os.path.join(data_dir, base_filename + suffix)
            row_data = [label] + val_list
            with open(filename, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(row_data)
            saved_files.append(filename)

        print(json.dumps({
            "status": "success", 
            "message": "Data saved successfully",
            "files": saved_files
        }))

    except Exception as e:
        import traceback
        error_msg = traceback.format_exc()
        print(json.dumps({"status": "error", "message": str(e), "detail": error_msg}))

if __name__ == "__main__":
    main()