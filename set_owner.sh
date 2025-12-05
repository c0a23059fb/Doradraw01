#!/bin/bash

# 現在のユーザーとディレクトリを取得
CURRENT_USER=$(whoami)
TARGET_DIR=$(pwd)

echo "--- シンプルな権限設定を開始します ---"
echo "対象: $TARGET_DIR"

# 1. 対象ディレクトリ以下の所有者を「実行ユーザー(あなた)」に統一する
echo "所有者を $CURRENT_USER に設定中..."
sudo chown -R "$CURRENT_USER" "$TARGET_DIR"

# 2. 「その他 (Other)」に対して読み書き権限を与える
# ディレクトリには実行権限(x)がないと中に入れないため、ディレクトリは777、ファイルは666になります。
echo "その他ユーザー(Apache含む)への読み書き権限を付与中..."
sudo chmod -R o+rwX "$TARGET_DIR"

echo "--- 設定完了 ---"
echo "これでApacheからも、あなたからも自由に読み書き可能です。"