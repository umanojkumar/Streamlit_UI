# -*- coding: utf-8 -*-

"""
Copyright (C) 2021 Mitchell Isaac Parker <mitch.isaac.parker@gmail.com>

This file is part of the rascore project.

The rascore project can not be copied, edited, and/or distributed without the express
permission of Mitchell Isaac Parker <mitch.isaac.parker@gmail.com>.
"""

import cairosvg

from rdkit import Chem
from rdkit.Chem import (
    Draw,
    rdFMCS,
    AllChem,
    PyMol,
)
from rdkit.Chem.EnumerateHeterocycles import EnumerateHeterocycles

from tqdm import tqdm

from .lst import type_lst
from .color import get_lst_colors, get_rgb, change_hex_alpha
from .download import download_file
from .path import path_exists, get_lig_path, append_file_path, lig_str
from .url import lig_expo_url


def download_lig(lig, lig_dir=None):

    lig_path = get_lig_path(lig, dir_path=lig_dir)

    download_file(
        f"{lig_expo_url}{lig[0]}/{lig}/{lig}_model.sdf",
        lig_path,
    )

    return lig_path


def load_lig(lig, lig_dir=None):

    lig_path = get_lig_path(lig, dir_path=lig_dir)

    if not path_exists(lig_path):
        lig_path = download_lig(lig, lig_dir=None)

    return Chem.MolFromMolFile(lig_path)


def get_lig_smiles(lig, lig_dir=None):

    mol = lig
    if type(lig) == str:
        smiles = mol
        if len(lig) <= 3:
            mol = load_lig(lig, lig_dir=lig_dir)
    if type(mol) != str:
        smiles = Chem.MolToSmiles(mol)

    return smiles


def get_lig_mol(lig, lig_dir=None, stereo=True):

    mol = lig
    if type(lig) == str:
        smiles = mol
        if len(lig) <= 3:
            smiles = get_lig_smiles(lig, lig_dir=lig_dir)
        mol = Chem.MolFromSmiles(smiles)

    if not stereo:
        AllChem.Compute2DCoords(mol)

    return mol


def get_lig_simi(lig_1, lig_2, lig_dir=None):

    mol_1 = Chem.RDKFingerprint(get_lig_mol(lig_1, lig_dir=lig_dir))
    mol_2 = Chem.RDKFingerprint(get_lig_mol(lig_2, lig_dir=lig_dir))

    return Chem.DataStructs.FingerprintSimilarity(mol_1, mol_2)


def is_lig_match(lig, matches, lig_dir=None):

    mol = get_lig_mol(lig, lig_dir=lig_dir)

    match_lst = type_lst(matches)

    if True in [
        mol.HasSubstructMatch(get_lig_mol(x, lig_dir=lig_dir)) for x in match_lst
    ]:
        return True
    else:
        return False


def get_lig_mcs(
    lig_lst,
    lig_dir=None,
    min_simi=0.9,
    compare_bonds=False,
    compare_exact=False,
    match_valence=False,
    match_rings=False,
    complete_rings=False,
):

    mol_lst = list()
    for lig in tqdm(
        lig_lst,
        desc="Loading ligands",
        position=0,
        leave=True,
    ):

        mol_lst.append(get_lig_mol(lig, lig_dir=lig_dir))

    if compare_bonds:
        if compare_exact:
            bond_compare = rdFMCS.BondCompare.CompareOrderExact
        else:
            bond_compare = rdFMCS.BondCompare.CompareOrder
    else:
        bond_compare = rdFMCS.BondCompare.CompareAny

    return Chem.MolFromSmarts(
        rdFMCS.FindMCS(
            mol_lst,
            threshold=min_simi,
            bondCompare=bond_compare,
            matchValences=match_valence,
            ringMatchesRingOnly=match_rings,
            completeRingsOnly=complete_rings,
        ).smartsString
    )


def get_lig_query_match(lig, query, lig_dir=None):

    mol = get_lig_mol(lig, lig_dir=lig_dir)
    query = get_lig_mol(query, lig_dir=lig_dir)

    atom_lst = list(mol.GetSubstructMatch(query))
    bond_lst = list()

    if len(atom_lst) > 0:

        bond_lst += [
            mol.GetBondBetweenAtoms(
                atom_lst[x.GetBeginAtomIdx()], atom_lst[x.GetEndAtomIdx()]
            ).GetIdx()
            for x in query.GetBonds()
        ]

    return atom_lst, bond_lst


def draw_lig_plot(
    ligs,
    plot_path,
    lig_dir=None,
    lig_labels=None,
    highlight_querys=None,
    highlight_alpha=0.75,
    color_palette=None,
    n_cols=None,
    mol_pad=0.1,
    plot_height=3,
    plot_width=3,
    font_size=2,
):

    lig_lst = type_lst(ligs)
    highlight_query_lst = type_lst(highlight_querys)

    if type(lig_labels) == dict:
        label_lst = [lig_labels[x] for x in lig_lst]
    else:
        label_lst = type_lst(lig_labels)
    if len(label_lst) != len(lig_lst):
        label_lst = None

    mol_lst = [get_lig_mol(x, lig_dir=lig_dir) for x in lig_lst]

    final_atom_lst = list()
    final_bond_lst = list()
    final_atom_color_lst = list()
    final_bond_color_lst = list()

    if highlight_querys is not None:
        if type(color_palette) == dict:
            color_dict = color_palette
            for key, val in color_dict.items():
                color_dict[key] = get_rgb(change_hex_alpha(val, highlight_alpha))
        else:
            color_dict = get_lst_colors(
                highlight_query_lst,
                palette=color_palette,
                return_rgb=True,
                return_dict=True,
                alpha=highlight_alpha,
            )

    for mol in mol_lst:

        mol_atom_lst = list()
        mol_bond_lst = list()
        mol_atom_color_dict = dict()
        mol_bond_color_dict = dict()

        if highlight_querys is not None:
            for i, highlight_query in enumerate(highlight_query_lst):

                atom_lst, bond_lst = get_lig_query_match(mol, highlight_query)

                if len(atom_lst) > 0:

                    mol_atom_lst += atom_lst
                    mol_bond_lst += bond_lst

                    for atom in atom_lst:
                        mol_atom_color_dict[atom] = color_dict[highlight_query]

                    for bond in bond_lst:
                        mol_bond_color_dict[bond] = color_dict[highlight_query]

        final_atom_lst.append(mol_atom_lst)
        final_bond_lst.append(mol_bond_lst)
        final_atom_color_lst.append(mol_atom_color_dict)
        final_bond_color_lst.append(mol_bond_color_dict)

    total_mols = len(mol_lst)
    if n_cols is None:
        n_cols = total_mols
    plot_size = (plot_width * 72, plot_height * 72)
    n_rows = total_mols // n_cols
    if total_mols % n_cols:
        n_rows += 1

    total_size = (n_cols * plot_size[0], n_rows * plot_size[1])
    draw = Draw.rdMolDraw2D.MolDraw2DSVG(
        total_size[0], total_size[1], plot_size[0], plot_size[1]
    )

    if n_cols is None:
        n_cols = len(mol_lst)

    draw.drawOptions().legendFontSize = font_size
    draw.drawOptions().padding = mol_pad
    draw.SetFontSize(1)
    draw.SetLineWidth(1)
    draw.DrawMolecules(
        mol_lst,
        legends=label_lst,
        highlightAtoms=final_atom_lst,
        highlightBonds=final_bond_lst,
        highlightAtomColors=final_atom_color_lst,
        highlightBondColors=final_bond_color_lst,
    )
    draw.FinishDrawing()
    img = draw.GetDrawingText()
    append_file_path(plot_path)
    cairosvg.svg2pdf(bytestring=img.encode("utf-8"), write_to=plot_path)


def show_pymol_lig(
    lig,
    lig_dir=None,
):

    lig_path = download_lig(lig, lig_dir=lig_dir)

    mv = PyMol.MolViewer()

    mv.LoadFile(lig_path, lig_str)

    mv.Zoom(lig_str)