# CSVDatabase モジュール

## 概要
CSVファイルを手軽にデータベースとして扱えるようにする Python モジュールです。Python 初学者でも理解しやすいよう、ドキュメントコメントやエラー文を日本語で統一しています。

## 特長
- 既存の CSV ファイルをそのままデータベースとして利用可能
- キー（列名）を指定するだけで初期ファイルを自動作成
- `pandas` を活用した柔軟なデータ操作が可能
- 日本語のドキュメントとエラー文で初学者をサポート

## インストール
1. Python 3.13.5 以上の環境を用意します。
2. 依存ライブラリをインストールします。
   ```bash
   pip install -r requirements.txt
   ```

## 基本的な使い方
### 1. コネクタの生成
データベースとして利用する CSV ファイルへのパスを渡して `CSVConnector` を生成します。ファイルが存在しない場合は、`initial_keys` に列名を指定することで新規作成されます。
```python
from connector import CSVConnector

conn = CSVConnector("db/example.csv", initial_keys=("key1", "key2", "key3"))
```
> 既存のファイルを使う場合は `initial_keys` を省略できます。

### 2. 全データの取得
登録されている全レコードを `pandas.DataFrame` として取得します。返されるデータフレームはコピーなので、直接編集しても元のデータベースには影響しません。
```python
df = conn.read()
print(df)
```

### 3. レコードの登録
列名と値のペアをキーワード引数で指定して保存します。データベースに存在しないキーが含まれている場合はエラーになります。
```python
conn.register(key1="value1", key2=2, key3="value3")
```
辞書を展開して渡すことも可能です。
```python
data = {"key1": "value1", "key2": 2, "key3": "value3"}
conn.register(**data)
```

### 4. レコードの削除
削除したい行番号（0 始まり）を指定します。複数指定も可能で、削除後はインデックスが振り直されます。
```python
conn.delete(0)        # 1 行だけ削除
conn.delete(1, 2, 3)  # 複数行をまとめて削除
```
存在しないインデックスを指定すると `IndexError` が発生します。

### 5. レコードの更新
更新対象の行番号とキー、置き換える値を指定します。
```python
conn.update(row_index=0, key="key2", value=99)
```
行番号が範囲外、もしくはキーが存在しない場合には例外が送出されます。

### 6. 条件付きでデータを取得
特定の列が特定の値を持つレコードのみを抽出できます。
```python
filtered = conn.get_filtered_dataframe_with_key(key="key1", value="value1")
print(filtered)
```

## よくある注意点
- `initial_keys` を指定せずに存在しないファイルを読み込むと `FileNotFoundError` になります。
- `register` では全てのキーに対して値を指定する必要があります。
- `delete` の後はインデックスが振り直されるため、連続操作の際は最新のインデックスを確認してください。

## 開発環境
- Python 3.13.5
- 依存ライブラリは `requirements.txt` を参照してください。

---

# CSVDatabase Module

## Overview
A Python module that lets you treat CSV files as a lightweight database. All docstrings and error messages are written in Japanese so that beginners can easily understand them.

## Features
- Use an existing CSV file directly as a database
- Automatically create an initial file by specifying key (column) names
- Flexible data handling powered by `pandas`
- Documentation and error messages in Japanese for beginners

## Installation
1. Prepare Python 3.13.5 or later.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Basic Usage
### 1. Create a connector
Pass the path to the CSV file you want to treat as a database. When the file does not exist, specify `initial_keys` so that a new file is created with those columns.
```python
from connector import CSVConnector

conn = CSVConnector("db/example.csv", initial_keys=("key1", "key2", "key3"))
```
> You can omit `initial_keys` if you already have a CSV file.

### 2. Read all records
Retrieve all stored records as a `pandas.DataFrame`. The returned frame is a copy, so editing it does not modify the database.
```python
df = conn.read()
print(df)
```

### 3. Register records
Pass column names and values as keyword arguments. A `ValueError` is raised when any column is missing or unknown.
```python
conn.register(key1="value1", key2=2, key3="value3")
```
You can also pass a dictionary using the unpacking operator.
```python
data = {"key1": "value1", "key2": 2, "key3": "value3"}
conn.register(**data)
```

### 4. Delete records
Specify the zero-based row indices you want to remove. Multiple indices can be passed at once, and the index will be re-assigned after deletion.
```python
conn.delete(0)        # Delete a single row
conn.delete(1, 2, 3)  # Delete multiple rows
```
An `IndexError` is raised when the index does not exist.

### 5. Update records
Provide the row index, column name, and new value to update a cell.
```python
conn.update(row_index=0, key="key2", value=99)
```
Exceptions are raised when the row index is out of range or the key does not exist.

### 6. Filter records by key/value
Get only the rows whose specific column matches a given value.
```python
filtered = conn.get_filtered_dataframe_with_key(key="key1", value="value1")
print(filtered)
```

## Notes
- A `FileNotFoundError` is raised when the CSV file does not exist and `initial_keys` is not provided.
- `register` requires values for all columns defined in the database.
- After calling `delete`, row indices are reset; be sure to check the current indices before further operations.

## Development Environment
- Python 3.13.5
- See `requirements.txt` for dependent libraries.
