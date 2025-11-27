# filesystem-frontmatter-mcp

Markdown ファイルの frontmatter を DuckDB SQL でクエリできる MCP サーバー。

## 機能

- **inspect_frontmatter**: glob パターンにマッチするファイルの frontmatter スキーマを取得
- **query_frontmatter**: DuckDB SQL で frontmatter データをクエリ

## インストール

```bash
uv tool install git+https://github.com/kzmshx/filesystem-frontmatter-mcp.git
```

## 使い方

### Claude Desktop / Claude Code での設定

```json
{
  "mcpServers": {
    "frontmatter": {
      "command": "filesystem-frontmatter-mcp",
      "args": ["--base-dir", "/path/to/markdown/directory"]
    }
  }
}
```

### ツールの使用例

#### スキーマの確認

```
inspect_frontmatter("**/*.md")
```

出力例:

```json
{
  "file_count": 186,
  "schema": {
    "date": {
      "type": "string",
      "count": 180,
      "nullable": true,
      "sample_values": ["2025-11-01", "2025-11-02"]
    },
    "tags": {
      "type": "array",
      "count": 150,
      "nullable": true,
      "sample_values": [["ai", "claude"], ["python"]]
    }
  }
}
```

#### SQL クエリ

```sql
-- 今月のファイル一覧
SELECT path, date, tags
FROM files
WHERE date LIKE '2025-11-%'
ORDER BY date DESC

-- タグの集計（配列を展開）
SELECT tag, COUNT(*) as count
FROM files, UNNEST(from_json(tags, '[""]')) AS t(tag)
WHERE date LIKE '2025-11-%'
GROUP BY tag
ORDER BY count DESC
```

## 技術的な注意点

### すべての値は文字列

frontmatter の値はすべて文字列として DuckDB に渡される。型変換が必要な場合は SQL 側で `TRY_CAST` を使用する。

```sql
-- 日付での比較
SELECT * FROM files
WHERE TRY_CAST(date AS DATE) >= '2025-11-01'
```

### 配列は JSON 文字列

`tags: [ai, python]` のような配列は JSON 文字列 `'["ai", "python"]'` として格納される。展開には `from_json()` と `UNNEST` を使用する。

```sql
SELECT path, tag
FROM files, UNNEST(from_json(tags, '[""]')) AS t(tag)
WHERE tag = 'ai'
```

### Templater 式への対応

Obsidian Templater プラグインの式（`<% tp.date.now("YYYY-MM-DD") %>`）がそのまま含まれるファイルも処理できる。これらは文字列として扱われ、日付フィルタリングで自動的に除外される。

## ライセンス

MIT
