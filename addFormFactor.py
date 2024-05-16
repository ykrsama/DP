#!/usr/bin/env python3

from argparse import ArgumentParser
from pathlib import Path
from distutils.dir_util import copy_tree


COLOUR= {
    "FAIL": '\033[91m',
    'OKGREEN': '\033[92m',
    'OKBLUE': '\033[94m',
    'WARNING': '\033[93m',
    'BOLD': '\033[1m',
    'RESET': '\033[0m',
}


def get_args():
    parser = ArgumentParser(description='Add Form Factor to UFO')
    parser.add_argument('UFO', nargs='?', type=Path, help='UFO Model Path')
    parser.add_argument('-f', '--formfactor', type=Path, required=True, help='Form Factor Path')

    return parser.parse_args()


if __name__ == "__main__":
    args = get_args()
    ufo_dir = args.UFO
    ff_dir = args.formfactor
    # Check if UFO directory exists
    if not ufo_dir:
        print(f'{COLOUR["FAIL"]}UFO directory not provided')
        exit(1)
    if not ufo_dir.exists():
        print(f'{COLOUR["FAIL"]}UFO {ufo_file} does not exist')
        exit(1)
    # Check if form factor directory exists
    if not ff_dir.exists():
        print(f'{COLOUR["FAIL"]}Form Factor {ff_dir} does not exist')
        exit(1)
    # Check if Fortran directory already exists in UFO
    fortran_dir = ufo_dir / "Fortran"
    if fortran_dir.exists():
        print(f'{COLOUR["FAIL"]}Fortran directory already exists in UFO')
        exit(1)

    # Copy Fortran/ form factor files to UFO directory
    copy_tree(str(ff_dir / "Fortran"), str(fortran_dir))

    vtx_particle_ff_map = {
            '[ P.nuc__tilde__, P.nuc, P.a ]' : 'mymdl_FormFactor(-P(-1,3)**2)',
            '[ P.nuc__tilde__, P.nuc, P.Z ]' : 'mymdl_FormFactor(-P(-1,3)**2)',
    }

    # open ufo_dir/verticies.py in read mode
    with open(ufo_dir / "vertices.py", "r") as f:
        vertices_lines = f.readlines()
    with open(ufo_dir / "lorentz.py", "r") as f:
        lorentz_lines = f.readlines()

    for particle, formfactor in vtx_particle_ff_map.items():
        print(f'Finding {particle}')
        for i, line in enumerate(vertices_lines):
            if particle in line:
                # get the next line containing "lorentz = ["
                for j in range(i, len(vertices_lines)):
                    if "lorentz = [" in vertices_lines[j]:
                        vtx_names_origin = vertices_lines[j].strip('lorentz = [],\n').split(', ')
                        print('vtx_names_origin:')
                        print(vtx_names_origin)
                        # get the updated vertex name
                        vtx_names_new = [name + 'FF' for name in vtx_names_origin]
                        # replace the line with new vertex name
                        vertices_lines[j] = vertices_lines[j].replace('lorentz =', f'lorentz = {vtx_names_new}, #'.replace('\'',''))
                        break

                # find the vtx_names_origin in lorentz_lines
                for vtx_name_origin in vtx_names_origin:
                    lorentz_name_origin = vtx_name_origin.replace('L.','')
                    lorentz_name_new = lorentz_name_origin + 'FF'
                    for j, line in enumerate(lorentz_lines):
                        if f'{lorentz_name_origin} = Lorentz(' in line:
                            lines_new_lorentz = [lorentz_lines[j]]
                            lines_new_lorentz[0].replace(lorentz_name_origin, lorentz_name_new)
                            for k in range(j+1, len(lorentz_lines)):
                                cur_line=lorentz_lines[k]
                                if 'structure = ' in cur_line:
                                    new_line = cur_line.replace('structure = \'', f'structure = \'{formfactor} * (').replace('\')\n', ')\')\n')
                                    lines_new_lorentz.append(new_line)
                                    lines_new_lorentz.append('\n')
                                    break
                                else:
                                    lines_new_lorentz.append(cur_line)
                            print('lines_new_lorentz:\n', lines_new_lorentz)
                            break

                    # open ufo_dir/lorentz.py in append mode
                    with open(ufo_dir / "lorentz.py", "a") as f:
                        # append the new vertex name
                        f.writelines(lines_new_lorentz)

                break

    with open(ufo_dir / "vertices.py", 'w') as f:
        f.writelines(vertices_lines)
