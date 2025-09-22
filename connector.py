from pathlib import Path
import os
from typing import Literal
from datetime import datetime

import pandas as pd


class CSVConnector:

    def __init__(self, csv_file: str | Path, initial_keys: tuple[str] | list[str] | None = None):
        """コンストラクタ  
        
        Args:
            csv_file(str | Path): 作成するCSVファイルのパス
            initial_keys(tuple[str] | list[str] | None, optional):
                ファイルが存在しなかった場合に作成するCSVのキー.  
                これらの値がCSVファイルの列名となる.  
                指定されない場合は初期ファイルが作成されず, ファイルが見つからない  
                場合にはエラーを投げる.  
                Default to None.
        
        Raises:
            FileNotFoundError:
            `initial_keys` が指定されず, ファイルが見つからない場合に生じる.
        """

        self.__csv = csv_file

        # CSVファイルが見つからなかった場合の処理
        if not os.path.exists(csv_file):
            
            if not initial_keys:
                raise FileNotFoundError(f"{csv_file} にファイルが見つかりません.")
            
            initial_dataframe = pd.DataFrame([], columns=initial_keys)
            initial_dataframe.to_csv(csv_file, index=False)
        
        self.__df = self.__read_csv()
    
    def __read_csv(self) -> pd.DataFrame:
        """CSVファイルからデータフレームを作成して返すメソッド"""
        return pd.read_csv(self.__csv)
    
    def __write_csv(self, mode: Literal["w", "a"] = "w") -> pd.DataFrame:
        """CSVファイルへの書き込みを行うためのメソッド"""
        self.__df.to_csv(self.__csv, mode=mode, index=False)
        return self.__df
    
    def __reset_index(self):
        """行インデックスを振り直すためのメソッド"""
        self.__df.reset_index(drop=True, inplace=True)
        return self.__df
    
    def read(self):
        """データベースからデータ全体を取得するためのメソッド.  
        
        負荷軽減のため, あらかじめ読み込んで保持しているデータフレームを返す.  
        渡したデータフレームはコピーであるため, 変更されてもデータベースは変更されない.  
        
        Returns:
            pandas.DataFrame: データベース全体の情報を保持するデータフレーム"""
        return self.__df.copy()

    def get_filtered_dataframe_with_key(self, key: str, value: str | int | float | bool | datetime) -> pd.DataFrame:
        """特定のキーの値を持つデータのデータフレームを取得するためのメソッド.  
        
        `key` 列の値が `value` であるレコードで構成された `DataFrame` を返す.  
        戻り値のデータフレームはコピーされたものであるため, 変更されてもデータベースは  
        変更されない.  

        Args:
            key(str): 参照するキー(列名)
            value: 条件となる値
        
        Returns:
            pandas.DataFrame: 
                条件に一致するレコードで構成された `DataFrame` オブジェクトのコピー
        """
        return self.__df[(self.__df[key] == value)].copy()
    
    def register(self, **key_and_values) -> pd.DataFrame:
        """データ(レコード)を追加するためのメソッド.
        
        キーとその値をキーワード引数の形で指定し, データベースへ登録する.  
        既存のデータベースのキーを参照し, 引数で指定されていないキーがあればエラーを投げる.  
        
        Args:
            key_and_values: キーと値を `key=value` の形で指定する.
        
        Returns:
            pd.DataFrame: 更新後のデータフレームのコピー
        
        Raises:
            ValueError: 正しく引数を受け取れなかった場合に生じる
        
        Examples:
            キーが `"key1", "key2", "key3"` であるとき, 以下のように記述して新しい  
            データを保存する.  

            ```
            conn = CSVConnector("db/example.csv", ["key1", "key2", "key3"])

            conn.register(key1="value1", key=2, key3="value3")
            ```
            
            または辞書オブジェクトを用いて以下のように記述できる. これは上記のコード  
            と等価である.  
            
            ```
            conn = CSVConnector("db/example.csv", ["key1", "key2", "key3"])

            kv = {key1: "value1", key: 2, key3: "value3"}
            conn.register(**kv)
            ```
        """

        # エラーチェック
        if set(key_and_values.keys()) != set(self.__df.columns.to_list()):
            raise ValueError("指定されていない値があります.")
        
        for k, v in key_and_values.items():
            key_and_values[k] = [v]
        new_row = pd.DataFrame(key_and_values, columns=tuple(key_and_values.keys()))
        self.__df = pd.concat([self.__df, new_row], ignore_index=True)
        self.__write_csv()
        return self.read()
    
    def delete(self, *row_index: int) -> pd.DataFrame:
        """データベースからアイテムを削除するためのメソッド.  
        
        指定された行インデックスのレコードを削除して, 削除後のデータフレームのコピーを返す.  
        **削除後はデータフレームの行インデックスが振り直される**.  
        
        Args:
            *row_index(int): 削除する行インデックス
        
        Returns:
            pandas.DataFrame: 変更後のデータフレームのコピー
        
        Raises:
            IndexError: 存在しない行番号が指定された場合に生じる"""
        try:
            for idx in row_index:
                self.__df.drop(idx, inplace=True)
            self.__reset_index()
            self.__write_csv()
        except KeyError as e:
            raise IndexError("指定の行番号がデータフレームの範囲外です. index: {}".format(idx))
        return self.read()
    
    def update(self, row_index: int, key: str, value: str | int | float | bool | datetime) -> pd.DataFrame:
        """データベースの値を更新するためのメソッド.  
        
        更新したい値を行インデックスとキーで検索して, 新しい値と交換し, データベースに  
        保存する.  
        
        Args:
            row_index(int): 行インデックス
            key(str): キー(列名)
            value: 新しい値
        
        Returns:
            pandas.DataFrame: 更新後のデータフレーム
        
        Raises:
            ValueError:
                データベースに登録された値がないにも関わらず呼び出された場合に生じる.  
            
            IndexError:
                範囲外の行インデックスが指定された場合に生じる.
            
            KeyError:
                キーの指定が不正な場合に生じる."""
        
        # エラーチェック
        idx = self.__df.index.to_list()
        cols = self.__df.columns.to_list()
        if len(idx) == 0:
            raise ValueError("データベースにはなにも値が保存されていません.")
        if not(min(idx) <= row_index and row_index <= max(idx)):
            raise IndexError(f"指定の行番号がデータフレームの範囲外です. index: {row_index}")
        if key not in cols:
            raise KeyError(f"指定のキーはこのデータベースで使用できません. Key: {key}")
        
        self.__df.loc[row_index, key] = value
        self.__write_csv()
        return self.read()