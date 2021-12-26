# -*- coding: utf-8 -*-

"""
Copyright (C) 2021 Mitchell Isaac Parker <mitch.isaac.parker@gmail.com>

This file is part of the pdbcore project.

The pdbcore project can not be copied, edited, and/or distributed without the express
permission of Mitchell Isaac Parker <mitch.isaac.parker@gmail.com>.
"""

from util.path import get_file_name
from util.lig import lig_col_lst
from util.path import (
    append_file_path,
    get_eds_map_path,
    get_eds_diff_path,
    modify_coord_path,
    map_str,
    diff_str,
)
from util.lst import type_lst, lst_to_str, str_to_lst
from util.color import get_lst_colors, get_rgb
from util.data import lst_col
from util.download import download_file
from util.url import eds_url
from util.col import (
    core_path_col,
    pdb_id_col,
    pdb_code_col,
    modelid_col,
    chainid_col,
    interf_col,
    bound_prot_chainid_col,
    bound_interf_chainid_col,
    bio_lig_col,
    ion_lig_col,
    pharm_lig_col,
    chem_lig_col,
)

polymer_color = "gray80"

bio_color = "gray90"
ion_color = "chartreuse"
pharm_color = "salmon"
chem_color = "cyan"
prot_color = "slate"
hb_color = "tv_yellow"
wmhb_color = "tv_blue"

symbol_lst = [" ", "/", "_"]


def init_pymol(pymol_file, color_dict=None):

    pymol_file.write("bg_color white\n")
    pymol_file.write("set antialias, 2\n")
    pymol_file.write("set orthoscopic, off\n")
    pymol_file.write("set depth_cue, 0\n")
    pymol_file.write("set sphere_scale, 0.4\n")
    pymol_file.write("set stick_radius, 0.2\n")
    pymol_file.write("set hash_max, 300\n")

    if color_dict is not None:
        for group, color in color_dict.items():
            pymol_file.write(f"set_color {group}_color, {color}\n")


def load_obj(pymol_file, path, obj, chainids=None):

    chainid_lst = type_lst(chainids)

    load_cmd = f"load {path}, {obj}"

    if chainid_lst is not None:
        chainids = lst_to_str(chainid_lst, join_txt="+")
        load_cmd += f"; remove model {obj} and not {chainids}//"

    pymol_file.write(f"{load_cmd}\n")


def init_obj(pymol_file, obj=None, ribbon=True, color_chainbow=False):

    color = polymer_color

    if ribbon:
        show = "ribbon"
        hide = "cartoon"
    else:
        show = "cartoon"
        hide = "ribbon"

    pymol_file.write("hide wire, solvent\n")

    if obj is None:
        pymol_file.write(f"show {show}\n")
        pymol_file.write(f"hide {hide}\n")
        pymol_file.write("hide lines\n")
        pymol_file.write("hide sticks\n")
        pymol_file.write("hide spheres\n")
        pymol_file.write(f"color {color}\n")
    else:
        pymol_file.write(f"show {show}, model {obj}\n")
        pymol_file.write(f"hide {hide}, model {obj}\n")
        pymol_file.write(f"hide lines, model {obj}\n")
        pymol_file.write(f"hide sticks, model {obj}\n")
        pymol_file.write(f"hide spheres, model {obj}\n")
        pymol_file.write(f"color {color}, model {obj}\n")

    if color_chainbow:
        pymol_file.write("util.chainbow\n")


def set_color(pymol_file, show_color, color, color_str, return_color=True):

    if show_color == True:
        color_str = color
    elif show_color is not None and show_color != False:
        color_rgb = get_rgb(show_color)
        pymol_file.write(f"set_color {color_str}, {color_rgb}\n")

    if return_color:
        return color_str


def color_sticks(pymol_file, stick_sele, stick_color=None, color_atomic=True):

    if stick_color is not None:
        pymol_file.write(f"color {stick_color}_color, {stick_sele}\n")
    if color_atomic:
        pymol_file.write(f"color atomic, {stick_sele} and (not elem C)\n")


def show_lig(
    pymol_file,
    lig_col,
    lig_dict,
    show_lig,
    lig_color,
    spheres=False,
):

    if show_lig is not None and show_lig != False:

        lig_str = lst_to_str(lig_dict[lig_col], join_txt="+")

        if lig_str is not None:

            lig_sele = f"{lig_col}_lig"

            pymol_file.write(f"select {lig_sele}, resn {lig_str}\n")

            pymol_file.write(f"color {lig_color}, {lig_sele}\n")

            if spheres:
                pymol_file.write(f"show spheres, {lig_sele}\n")
            else:
                pymol_file.write(f"show sticks, {lig_sele}\n")
                color_sticks(pymol_file, lig_sele)


def get_sup_sele(obj, chainid, sup_resids=None):

    sup_sele_lst = [f"model {obj} and chain {chainid}"]

    if sup_resids is not None:
        sup_resids = str(sup_resids)
        sele_resid_lst = sup_resids.replace(":", "+")
        sup_sele_lst.append(f"resi {lst_to_str(sele_resid_lst,join_txt='+')}")

    sup_sele_lst.append("bb.")
    sup_sele = lst_to_str(sup_sele_lst, join_txt=" and ")

    return sup_sele


def get_hb_sele(
    x_hb_resname, y_hb_resname, obj=None, x_hb_atomid_str=None, y_hb_atomid_str=None
):
    sele_lst = list()

    if obj is not None:
        sele_lst.append(obj)

    sele_lst.append(x_hb_resname)

    if x_hb_atomid_str is not None:
        sele_lst.append(x_hb_atomid_str.replace("+", "_"))

    sele_lst.append(y_hb_resname)

    if y_hb_atomid_str is not None:
        sele_lst.append(y_hb_atomid_str.replace("+", "_"))

    hb_sele_lst = sele_lst.copy()
    wmhb_sele_lst = sele_lst.copy()
    angle_sele_lst = sele_lst.copy()

    hb_sele_lst.append("hb")
    wmhb_sele_lst.append("wmhb")
    angle_sele_lst.append("angle")

    hb_sele = lst_to_str(hb_sele_lst, join_txt="_")
    wmhb_sele = lst_to_str(wmhb_sele_lst, join_txt="_")
    angle_sele = lst_to_str(angle_sele_lst, join_txt="_")

    return hb_sele, wmhb_sele, angle_sele


def write_pymol_script(
    pymol_df,
    pymol_pml_path,
    group_col=None,
    stick_resids=None,
    loop_resids=None,
    sup_resids=None,
    sup_coord_path=None,
    sup_chainid=None,
    sup_all=True,
    sup_group=False,
    group_order=None,
    style_ribbon=True,
    thick_bb=True,
    color_atomic=True,
    show_resids=None,
    cartoon_transp=0,
    show_bio=None,
    show_ion=None,
    show_pharm=None,
    show_chem=None,
    show_prot=None,
    color_palette=None,
    color_group=True,
    color_chainbow=False,
    coord_path_col=None,
    prot_chainid_col=None,
    set_view=None,
    eds_dir=None,
    eds_resids=None,
    map_cutoff=1.0,
    diff_cutoff=3.0,
    carve_value=1.6,
    mesh_width=0.5,
    x_hb_resids=None,
    x_hb_atomids=None,
    y_hb_resids=None,
    y_hb_atomids=None,
    max_hb_dist=3.2,
    max_wmhb_dist=3.0,
    show_hb=True,
    show_wmhb=True,
    show_angle=False,
    add_h=False,
):

    df = pymol_df.reset_index(drop=True)

    if coord_path_col is None:
        coord_path_col = core_path_col

    if prot_chainid_col is None:
        prot_chainid_col = bound_prot_chainid_col

    stick_resid_lst = type_lst(stick_resids)
    loop_resid_lst = type_lst(loop_resids)

    x_hb_resid_lst = type_lst(x_hb_resids)
    x_hb_atomid_lst = type_lst(x_hb_atomids)
    y_hb_resid_lst = type_lst(y_hb_resids)
    y_hb_atomid_lst = type_lst(y_hb_atomids)

    if max_wmhb_dist is None:
        max_wmhb_dist = max_hb_dist

    index_lst = list(df.index.values)
    df_col_lst = list(df.columns)

    add_modelid = False
    if len(lst_col(df, modelid_col, unique=True)) > 1:
        add_modelid = True

    label_pdb = False
    if pdb_id_col in df_col_lst:
        label_pdb = True

    if group_col is None:
        group_lst = index_lst
    else:
        for symbol in symbol_lst:
            df[group_col] = df[group_col].str.replace(symbol, "_")
        if group_order is not None:
            for symbol in symbol_lst:
                group_order = [x.replace(symbol, "_") for x in group_order]
            group_lst = group_order
        else:
            group_lst = lst_col(df, group_col, unique=True, return_str=True)

        group_dict = dict()
        for group in group_lst:
            group_dict[group] = list()

    if (group_col is None or color_group is False) and loop_resids is not None:
        label_lst = loop_resid_lst.copy()
    else:
        label_lst = group_lst.copy()

    if type(color_palette) == dict:
        color_dict = dict()
        for key, val in color_palette.items():
            for symbol in symbol_lst:
                key = key.replace(symbol, "_")
            color_dict[key] = get_rgb(val)
    else:
        color_dict = get_lst_colors(
            label_lst, palette=color_palette, return_rgb=True, return_dict=True
        )

    append_file_path(pymol_pml_path)

    pymol_file = open(pymol_pml_path, "w")

    init_pymol(pymol_file, color_dict=color_dict)

    bio_color_str = set_color(pymol_file, show_bio, bio_color, "bio_color")
    ion_color_str = set_color(pymol_file, show_ion, ion_color, "ion_color")
    pharm_color_str = set_color(pymol_file, show_pharm, pharm_color, "pharm_color")
    chem_color_str = set_color(pymol_file, show_chem, chem_color, "chem_color")
    prot_color_str = set_color(pymol_file, show_prot, prot_color, "prot_color")

    if type(show_hb) == list:
        hb_color_lst = list()
        for i, color in enumerate(show_hb):
            hb_color_lst.append(set_color(pymol_file, color, hb_color, f"{i}_hb"))

    if type(show_wmhb) == list:
        wmhb_color_lst = list()
        for i, color in enumerate(show_wmhb):
            wmhb_color_lst.append(set_color(pymol_file, color, wmhb_color, f"{i}_wmhb"))

    lig_dict = dict()

    for lig_col in lig_col_lst:
        lig_dict[lig_col] = list()

    for index in index_lst:

        coord_path = df.at[index, coord_path_col]
        modelid = df.at[index, modelid_col]
        chainid = df.at[index, chainid_col]

        if add_h:
            coord_path = modify_coord_path(coord_path, return_pdb=True, add_h=True)

        for lig_col in lig_col_lst:
            if lig_col in df_col_lst:
                ligs = df.at[index, lig_col]
                if ligs != "None":
                    for lig in str_to_lst(ligs):
                        if lig != "GLY":
                            if lig not in lig_dict[lig_col]:
                                lig_dict[lig_col].append(lig)

        obj_lst = list()

        if label_pdb:
            obj_lst.append(df.at[index, pdb_id_col])
            if add_modelid:
                obj_lst.append(modelid)
            if interf_col in df_col_lst:
                obj_lst.append(df.at[index, interf_col])
        else:
            obj_lst.append(get_file_name(coord_path))

        group = index
        if group_col is not None:
            group = df.at[index, group_col]
            obj_lst.append(group)

        obj = lst_to_str(obj_lst, join_txt="_")

        if group_col is not None:
            group_dict[str(group)].append([obj, coord_path, chainid])

        chainid_lst = type_lst(chainid)
        if show_prot is not None and show_prot != False:
            prot_chainid = df.at[index, prot_chainid_col]
            if prot_chainid != "None":
                prot_chainid_lst = str_to_lst(prot_chainid)
                chainid_lst += prot_chainid_lst

        load_obj(pymol_file, coord_path, obj, chainids=chainid_lst)

        chain_sele = f"model {obj} and chain {chainid}"

        if show_prot is not None and show_prot != False:
            if prot_chainid_col != bound_interf_chainid_col:
                if prot_chainid != "None":
                    prot_chainid_str = lst_to_str(prot_chainid_lst, join_txt="+")

                    prot_sele = f"{obj}_{prot_chainid_str}_{prot_chainid_col}"

                    pymol_file.write(
                        f"select {prot_sele}, model {obj} and chain {prot_chainid_str}\n"
                    )

    init_obj(pymol_file, ribbon=style_ribbon, color_chainbow=color_chainbow)

    if show_resids:
        hide_style = "cartoon"
        if style_ribbon:
            hide_style = "ribbon"
        pymol_file.write(f"hide {hide_style}, not resi {show_resids}\n")

    if stick_resids is not None:
        for stick_resid in stick_resid_lst:
            stick_sele = f"{stick_resid}_stick"
            if group_col is None or color_group is False:
                pymol_file.write(
                    f"select {stick_sele}, resi {stick_resid} and not name O+N+C\n"
                )
                color_sticks(
                    pymol_file,
                    stick_sele,
                    color_atomic=color_atomic,
                )
            else:
                for group in group_lst:
                    group_stick_sele = f"{group}_{stick_sele}"
                    pymol_file.write(
                        f"select {group_stick_sele}, *_{group} and resi {stick_resid} and not name O+N+C\n"
                    )

                    color_sticks(
                        pymol_file,
                        group_stick_sele,
                        stick_color=group,
                        color_atomic=color_atomic,
                    )

                pymol_file.write(f"group {stick_sele}, *_{stick_sele}\n")

            pymol_file.write(f"show sticks, {stick_sele}\n")

    if loop_resids is not None:
        for loop_range in loop_resid_lst:

            loop_range = str(loop_range)

            resid_str = loop_range.replace(":", "+")
            loop_range = loop_range.replace(":", "_")

            loop_sele = f"{loop_range}_loop"

            if group_col is None or color_group is False:
                pymol_file.write(f"select {loop_sele}, resi {resid_str}\n")
                color_sticks(
                    pymol_file,
                    loop_sele,
                    stick_color=loop_range,
                    color_atomic=color_atomic,
                )

                if style_ribbon:
                    pymol_file.write(f"hide cartoon,{loop_sele}\n")
                    if thick_bb:
                        pymol_file.write(f"show sticks, bb. and {loop_sele}\n")
            else:
                for group in group_lst:
                    group_loop_sele = f"{group}_{loop_sele}"
                    pymol_file.write(
                        f"select {group_loop_sele}, *_{group} and resi {resid_str}\n"
                    )
                    color_sticks(
                        pymol_file,
                        group_loop_sele,
                        stick_color=group,
                        color_atomic=color_atomic,
                    )

                    if style_ribbon:
                        pymol_file.write(f"hide cartoon,{group_loop_sele}\n")
                        if thick_bb:
                            pymol_file.write(
                                f"show sticks, bb. and {group_loop_sele}\n"
                            )

                pymol_file.write(f"group {loop_sele}, *_{loop_sele}\n")

    show_lig(
        pymol_file,
        bio_lig_col,
        lig_dict,
        show_bio,
        bio_color_str,
        spheres=False,
    )

    show_lig(
        pymol_file,
        ion_lig_col,
        lig_dict,
        show_ion,
        ion_color_str,
        spheres=True,
    )

    show_lig(
        pymol_file,
        pharm_lig_col,
        lig_dict,
        show_pharm,
        pharm_color_str,
        spheres=False,
    )

    show_lig(
        pymol_file,
        chem_lig_col,
        lig_dict,
        show_chem,
        chem_color_str,
        spheres=False,
    )

    if show_prot is not None and show_prot != False:
        if prot_chainid_col != bound_interf_chainid_col:
            prot_style = "cartoon"
            if style_ribbon:
                prot_style = "ribbon"
            pymol_file.write(f"group {prot_chainid_col}, *_{prot_chainid_col}\n")
            pymol_file.write(f"show {prot_style}, {prot_chainid_col}\n")
            pymol_file.write(f"hide sticks, {prot_chainid_col}\n")
            pymol_file.write(f"color {prot_color_str}, {prot_chainid_col}\n")

    if len(df) > 1:
        if sup_all:
            if sup_coord_path is None:
                sup_coord_path = df.at[0, coord_path_col]
                if sup_chainid is None:
                    sup_chainid = df.at[0, chainid_col]

            if sup_coord_path is not None and sup_chainid is not None:

                sup_obj = "sup_obj"

                load_obj(
                    pymol_file,
                    sup_coord_path,
                    sup_obj,
                    chainids=sup_chainid,
                )

                sup_sele = get_sup_sele(
                    sup_obj,
                    sup_chainid,
                    sup_resids=sup_resids,
                )

                pymol_file.write(f"alignto {sup_sele}\n")
                pymol_file.write(f"center {sup_obj}\n")
                pymol_file.write(f"delete {sup_obj}\n")

    if group_col is not None:
        for group in group_lst:
            if sup_group:
                obj_val_lst = group_dict[group]

                if len(obj_val_lst) > 1:

                    sup_val_lst = obj_val_lst[0]

                    sup_obj = sup_val_lst[0]
                    sup_chainid = sup_val_lst[2]

                    sup_sele = get_sup_sele(
                        sup_obj,
                        sup_chainid,
                        sup_resids=sup_resids,
                    )

                    for val_lst in obj_val_lst:
                        group_obj = val_lst[0]
                        if group_obj != sup_obj:
                            pymol_file.write(f"align {group_obj}, {sup_sele}\n")

            pymol_file.write(f"group {group}, *_{group}\n")

    if x_hb_resid_lst is not None and y_hb_resid_lst is not None:

        pymol_file.write(f"set h_bond_cutoff_edge, {max_hb_dist}\n")

        for index in index_lst:

            coord_path = df.at[index, coord_path_col]
            modelid = df.at[index, modelid_col]
            chainid = df.at[index, chainid_col]

            obj_lst = list()

            if label_pdb:
                obj_lst.append(df.at[index, pdb_id_col])
                if add_modelid:
                    obj_lst.append(modelid)
                if interf_col in df_col_lst:
                    obj_lst.append(df.at[index, interf_col])
            else:
                obj_lst.append(get_file_name(coord_path))

            group = index
            if group_col is not None:
                group = df.at[index, group_col]
                obj_lst.append(group)

            obj = lst_to_str(obj_lst, join_txt="_")

            chain_sele = f"model {obj} and chain {chainid}"

            for i, (x_hb_resname, y_hb_resname) in enumerate(
                zip(x_hb_resid_lst, y_hb_resid_lst)
            ):

                if x_hb_atomid_lst is not None:
                    x_hb_atomid_str = lst_to_str(
                        type_lst(x_hb_atomid_lst[i]), join_txt="+"
                    )
                if y_hb_atomid_lst is not None:
                    y_hb_atomid_str = lst_to_str(
                        type_lst(y_hb_atomid_lst[i]), join_txt="+"
                    )

                hb_sele, wmhb_sele, angle_sele = get_hb_sele(
                    x_hb_resname,
                    y_hb_resname,
                    x_hb_atomid_str=x_hb_atomid_str,
                    y_hb_atomid_str=y_hb_atomid_str,
                    obj=obj,
                )

                x_res_str = "resi"
                y_res_str = "resi"

                if type(x_hb_resname) == str:
                    x_hb_resid = df.at[index, x_hb_resname]
                    x_res_str = "resname"
                else:
                    x_hb_resid = x_hb_resname

                if type(y_hb_resname) == str:
                    y_hb_resid = df.at[index, y_hb_resname]
                    y_res_str = "resname"
                else:
                    y_hb_resid = y_hb_resname

                if x_hb_resid is not None and y_hb_resid is not None:

                    x_hb_resid_sele = f"{chain_sele} and {x_res_str} {x_hb_resid}"
                    y_hb_resid_sele = f"{chain_sele} and {y_res_str} {y_hb_resid}"

                    if x_hb_atomid_lst[i] is not None:
                        x_hb_resid_sele += f" and name {x_hb_atomid_str}"

                    if y_hb_atomid_lst[i] is not None:
                        y_hb_resid_sele += f" and name {y_hb_atomid_str}"

                    write_hb = show_hb
                    if type(show_hb) == list:
                        write_hb = show_hb[i]

                    if write_hb is not False:
                        pymol_file.write(
                            f"dist {hb_sele}, {x_hb_resid_sele}, {y_hb_resid_sele}, cutoff={max_hb_dist}\n"
                        )

                    write_wmhb = show_wmhb
                    if type(show_wmhb) == list:
                        write_wmhb = show_wmhb[i]

                    if write_wmhb is not False:
                        wat_sele_1 = f"byres {chain_sele} and resname HOH within {max_wmhb_dist} of {x_hb_resid_sele}"
                        wat_sele_2 = f"byres {chain_sele} and resname HOH within {max_wmhb_dist} of {y_hb_resid_sele}"

                        wat_sele = f"({wat_sele_1}) in ({wat_sele_2})"

                        pymol_file.write(
                            f"dist {wmhb_sele}, {wat_sele}, ({x_hb_resid_sele})+({y_hb_resid_sele}), cutoff={max_wmhb_dist}\n"
                        )

                        if show_angle:
                            pymol_file.write(
                                f"angle {angle_sele},{x_hb_resid_sele}, {wat_sele}, {y_hb_resid_sele}\n"
                            )

                        pymol_file.write(f"sele HOH, {wat_sele}, merge=1\n")

    if x_hb_resids is not None and y_hb_resids is not None:

        pymol_file.write(f"set sphere_scale, 0.3, HOH\n")

        for i, (x_hb_resname, y_hb_resname) in enumerate(
            zip(x_hb_resid_lst, y_hb_resid_lst)
        ):

            if x_hb_atomid_lst is not None:
                x_hb_atomid_str = lst_to_str(type_lst(x_hb_atomid_lst[i]), join_txt="+")
            if y_hb_atomid_lst is not None:
                y_hb_atomid_str = lst_to_str(type_lst(y_hb_atomid_lst[i]), join_txt="+")

            hb_sele, wmhb_sele, angle_sele = get_hb_sele(
                x_hb_resname,
                y_hb_resname,
                x_hb_atomid_str=x_hb_atomid_str,
                y_hb_atomid_str=y_hb_atomid_str,
            )

            write_hb_status = show_hb
            write_hb_color = hb_color
            if type(show_hb) == list:
                write_hb_status = show_hb[i]
                write_hb_color = hb_color_lst[i]

            write_wmhb_status = show_hb
            write_wmhb_color = wmhb_color
            if type(show_wmhb) == list:
                write_wmhb_status = show_wmhb[i]
                write_wmhb_color = wmhb_color_lst[i]

            if group_col is None or color_group is False:
                if write_hb_status is not False:
                    pymol_file.write(f"group {hb_sele}, *_{hb_sele}\n")
                    pymol_file.write(f"color {write_hb_color}, {hb_sele}\n")
                if write_wmhb_status is not False:
                    pymol_file.write(f"group {wmhb_sele}, *_{wmhb_sele}\n")
                    pymol_file.write(f"color {write_wmhb_color}, {wmhb_sele}\n")
                    if show_angle:
                        pymol_file.write(f"group {angle_sele}, *_{angle_sele}\n")
                        pymol_file.write(f"color {write_wmhb_color}, {angle_sele}\n")
            else:
                for group in group_lst:
                    if write_hb_status is not False:
                        group_hb_sele = f"{group}_{hb_sele}"
                        pymol_file.write(f"group {group_hb_sele}, *_{group_hb_sele}\n")
                        if type(write_hb_status) == str:
                            group_hb_color = write_hb_color
                        else:
                            group_hb_color = f"{group}_color"
                        pymol_file.write(f"color {group_hb_color}, {group_hb_sele}\n")
                    if write_wmhb_status is not False:
                        group_wmhb_sele = f"{group}_{wmhb_sele}"
                        pymol_file.write(
                            f"group {group_wmhb_sele}, *_{group_wmhb_sele}\n"
                        )
                        if type(write_wmhb_status) == str:
                            group_wmhb_color = write_wmhb_color
                        else:
                            group_wmhb_color = f"{group}_color"
                        pymol_file.write(
                            f"color {group_wmhb_color}, {group_wmhb_sele}\n"
                        )
                        if show_angle:
                            group_angle_sele = f"{group}_{angle_sele}"
                            pymol_file.write(
                                f"group {group_angle_sele}, *_{group_angle_sele}\n"
                            )
                            pymol_file.write(
                                f"color {group_wmhb_color}, {group_angle_sele}\n"
                            )

            pymol_file.write(f"set dash_width, 3\n")

            if show_angle:
                pymol_file.write(f"hide angles\n")

            pymol_file.write(f"show spheres, HOH\n")
            pymol_file.write(f"color red, HOH\n")

    if set_view is not None:
        pymol_file.write(f"set_view {set_view}\n")

    if eds_dir is not None and eds_resids is not None:
        if len(df) == 1:
            if pdb_code_col in df_col_lst:
                pdb_code = df.at[0, pdb_code_col]
                chainid = df.at[0, chainid_col]

                map_eds_url = f"{eds_url}{pdb_code}.ccp4"
                diff_eds_url = f"{eds_url}{pdb_code}_diff.ccp4"

                map_path = get_eds_map_path(pdb_code, dir_path=eds_dir)
                diff_path = get_eds_diff_path(pdb_code, dir_path=eds_dir)

                download_file(map_eds_url, map_path)
                download_file(diff_eds_url, diff_path)

                pymol_file.write(f"load {map_path}, {map_str}\n")
                pymol_file.write(f"load {diff_path}, {diff_str}\n")

                mesh_map_sele = f"mesh_{map_str}"
                mesh_diff_sele = f"mesh_{diff_str}"

                eds_resids = str(eds_resids)

                eds_str = eds_resids.replace(":", "+")

                eds_sele = f"{obj} and chain and resi {eds_str}"

                pymol_file.write(
                    f"isomesh {mesh_map_sele}, {map_str}, {map_cutoff}, {eds_sele}, carve={carve_value}\n"
                )
                pymol_file.write(
                    f"isomesh {mesh_diff_sele}, {diff_str}, {diff_cutoff}, {eds_sele}\n"
                )

                pymol_file.write(f"color gray50, {mesh_map_sele}\n")
                pymol_file.write(f"color green, {mesh_diff_sele}\n")
                pymol_file.write("set mesh_negative_color, red\n")
                pymol_file.write("set mesh_negative_visible\n")

                pymol_file.write(f"orient {eds_sele}\n")

                pymol_file.write(f"set mesh_width, {mesh_width}\n")

    pymol_file.write(f"set cartoon_transparency, {cartoon_transp}\n")

    pymol_file.write("hide labels\n")

    pymol_file.write("zoom center, 25\n")

    pymol_file.write(f"save {pymol_pml_path.replace('.pml','.pse')}\n")

    pymol_file.close()

    print("Wrote PyMOL script!")