# -*- coding: utf-8 -*-
"""
MIT License

Copyright (c) 2022 Mitchell Isaac Parker

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import streamlit as st
from random import randint

from ..functions.col import id_col, core_path_col
from ..functions.path import (
    delete_path,
    get_file_path,
    get_file_name,
    get_neighbor_path,
    load_table,
    get_dir_path,
    pages_str,
    data_str,
    rascore_str,
    classify_str,
)
from ..functions.file import result_table_file
from ..functions.gui import (
    save_st_file,
    show_st_dataframe,
    download_st_df,
    rename_st_cols,
    write_st_end,
)
from ..pipelines.classify_rascore import classify_rascore


def classify_page():

    st.markdown("# Classify Structures")

    st.markdown("---")

    st_file_lst = st.file_uploader(
        "Upload Coordinate Files", accept_multiple_files=True
    )

    table_st_file = None
    with st.expander("Optional Input", expanded=False):

        st.markdown(
            """
        Tab-separated table with columns:
        - **core_path:** coordinate path:
        - **modelid:** model number (*optional*)
        - **chainid:** chain identifier
        - **nucleotide_class:** nucleotide state (*optional*)
        """
        )
        table_st_file = st.file_uploader(
            "Upload Table File", accept_multiple_files=False
        )

    with st.form(key="Classify Form"):
        out_file = st.text_input(
            label="Classify File Name", value="rascore_classify.tsv"
        )
        submit_files = st.form_submit_button(label="Classify Structures")

    if submit_files:
        if len(st_file_lst) > 0:
            with st.spinner(text="Classifying Structures"):

                try:
                    coord_path_lst = list()
                    id_dict = dict()
                    path_dict = dict()
                    for st_file in st_file_lst:
                        coord_path = save_st_file(st_file)
                        coord_path_lst.append(coord_path)
                        id_dict[get_file_name(coord_path)] = st_file.name
                        path_dict[st_file.name] = coord_path

                    classify_path = get_dir_path(
                        dir_str=f"{rascore_str}_{classify_str}_{randint(0,3261994)}",
                        dir_path=get_neighbor_path(__file__, pages_str, data_str),
                    )

                    if table_st_file is None:
                        classify_input = coord_path_lst
                    else:
                        table_path = save_st_file(table_st_file)
                        classify_input = load_table(table_path)
                        classify_input[core_path_col] = classify_input[
                            core_path_col
                        ].map(path_dict)
                        delete_path(table_path)

                    classify_rascore(classify_input, out_path=classify_path)

                    st.success("Classified Structures")

                    result_file_path = get_file_path(
                        result_table_file, dir_path=classify_path
                    )

                    df = load_table(result_file_path)

                    df[id_col] = df[id_col].map(id_dict)

                    df = rename_st_cols(df)

                    show_st_dataframe(df)

                    download_st_df(df, out_file, "Download Classification Table")
                except:
                    st.error("Error Analyzing Uploaded Structures")

                delete_path(classify_path)
                for coord_path in coord_path_lst:
                    delete_path(coord_path)

    write_st_end()
