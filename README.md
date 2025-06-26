# Auto-Suggest ZSH Plugin

AIを活用してディレクトリコンテキストとコマンド履歴に基づいて次のコマンドを提案するzshプラグインです。

## 必要な依存関係

- `uv` - Python パッケージマネージャー
- `fzf` - ファジーファインダー
- `llm` - Simon Willison の LLM CLI ツール

## インストール

### Sheldon での使用

```toml
# ~/.config/sheldon/plugins.toml に追加
[plugins.auto-suggest]
github = "YusukeShimizu/auto-suggest"
```

## 使用方法

### 基本的な使用

```bash
# 現在のディレクトリでコマンド提案
suggest

# 特定のディレクトリでコマンド提案
suggest /path/to/project

# 履歴の件数を指定
suggest --history 30
```

### ショートカット

- `sg` - `suggest` のエイリアス
- `Ctrl+G` - キーバインドで直接提案を開始

### 設定

環境変数で動作をカスタマイズできます：

```bash
# 履歴の件数（デフォルト: 20）
export AUTO_SUGGEST_HISTORY_LIMIT=30

# fzf の高さ（デフォルト: 40%）
export AUTO_SUGGEST_FZF_HEIGHT=50%
```

## 機能

- **コンテキスト認識**: READMEファイルとディレクトリ名を分析
- **履歴統合**: 最近のzshコマンド履歴を考慮
- **インタラクティブ選択**: fzfを使用した使いやすいインターフェース
- **日本語対応**: コマンドの説明が日本語で表示
- **zsh統合**: 選択したコマンドを直接入力バッファに挿入

## 仕組み

1. 現在のディレクトリのREADMEファイルを読み取り
2. zshの履歴から最近のコマンドを取得
3. LLMを使用してコンテキストに基づいた提案を生成
4. fzfでインタラクティブに選択
5. 選択したコマンドをzshの入力バッファに挿入

## トラブルシューティング

### エラー: uv not found
```bash
# macOS
brew install uv

# その他のプラットフォーム
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### エラー: fzf not found
```bash
# macOS
brew install fzf

# Ubuntu/Debian
sudo apt install fzf
```

### エラー: llm not found
```bash
# pipx を使用してインストール
pipx install llm

# または pip を使用
pip install llm
```

## ライセンス

MIT License