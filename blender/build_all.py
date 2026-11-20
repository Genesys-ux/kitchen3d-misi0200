"""
Master Blender headless prop builder for 3D Dapur Indonesia (Misi 02:00 WIB).

Usage (local or GitHub Actions):
    blender --background --factory-startup --python blender/build_all.py -- --out-dir character-studio/models

Optional flags after `--`:
    --out-dir <path>   Output folder for .glb files & manifest.json (default: character-studio/models)
    --only <a,b,c>     Build only specific comma-separated prop IDs
    --list             Print all registered prop IDs and exit
"""

import json
import os
import sys
import time
import bpy

# Ensure blender/ directory is importable regardless of cwd
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from utils import finalize_and_export_glb
from props_counter import (
    build_lpg_gas_3kg,
    build_rinnai_stove,
    build_teflon_pan,
    build_pan_lid,
    build_bolster_pillow,
    build_condiment_bottles,
    build_dish_rack_set,
    build_egg_tray,
    build_cobek_ulekan,
    build_utensil_rail,
)
from props_room import (
    build_sharp_fridge,
    build_dispenser_galon,
    build_table_kerupuk_jar,
    build_bufet_appliances,
    build_wall_shelf_props,
    build_cicak,
    build_ceiling_lamp,
    build_broom_sapu,
)


PROP_REGISTRY = {
    # Countertop & Under-Counter Hero Props
    'lpg_gas_3kg':       build_lpg_gas_3kg,
    'rinnai_stove':      build_rinnai_stove,
    'teflon_pan':        build_teflon_pan,
    'pan_lid':           build_pan_lid,
    'bolster_pillow_1':  lambda: build_bolster_pillow(1),
    'bolster_pillow_2':  lambda: build_bolster_pillow(2),
    'condiment_bottles': build_condiment_bottles,
    'dish_rack_set':     build_dish_rack_set,
    'egg_tray':          build_egg_tray,
    'cobek_ulekan':      build_cobek_ulekan,
    'utensil_rail':      build_utensil_rail,
    # Room & Midground Props
    'sharp_fridge':      build_sharp_fridge,
    'dispenser_galon':   build_dispenser_galon,
    'table_kerupuk_jar': build_table_kerupuk_jar,
    'bufet_appliances':  build_bufet_appliances,
    'wall_shelf_props':  build_wall_shelf_props,
    'cicak':             build_cicak,
    'ceiling_lamp':      build_ceiling_lamp,
    'broom_sapu':        build_broom_sapu,
}


def parse_args():
    argv = sys.argv
    if '--' in argv:
        argv = argv[argv.index('--') + 1:]
    else:
        argv = []

    out_dir = os.path.join(os.path.dirname(SCRIPT_DIR), 'character-studio', 'models')
    only = None
    list_only = False

    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg == '--out-dir' and i + 1 < len(argv):
            out_dir = argv[i + 1]
            i += 2
        elif arg == '--only' and i + 1 < len(argv):
            only = [x.strip() for x in argv[i + 1].split(',') if x.strip()]
            i += 2
        elif arg == '--list':
            list_only = True
            i += 1
        else:
            i += 1

    return out_dir, only, list_only


def main():
    out_dir, only, list_only = parse_args()

    if list_only:
        print('Registered Blender Props:', ', '.join(PROP_REGISTRY.keys()))
        return

    os.makedirs(out_dir, exist_ok=True)
    targets = only if only else list(PROP_REGISTRY.keys())

    print(f'[Blender {bpy.app.version_string}] Building {len(targets)} kitchen props -> {out_dir}')
    t0 = time.time()

    manifest_path = os.path.join(out_dir, 'manifest.json')
    existing = {}
    if only and os.path.exists(manifest_path):
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for item in data.get('models', []):
                    existing[item['id']] = item
        except Exception:
            pass

    for prop_id in targets:
        if prop_id not in PROP_REGISTRY:
            raise ValueError(f'Unknown prop ID: {prop_id}')
        pt0 = time.time()
        PROP_REGISTRY[prop_id]()
        out_path = os.path.join(out_dir, f'{prop_id}.glb')
        stats = finalize_and_export_glb(out_path)
        stats['id'] = prop_id
        stats['seconds'] = round(time.time() - pt0, 2)
        existing[prop_id] = stats
        print(
            f"  [OK] {prop_id:20s} -> {stats['file']:24s} "
            f"| {stats['triangles']:6d} tris | {stats['bytes'] / 1024:7.1f} KB | {stats['seconds']:.2f}s"
        )

    manifest = {
        'generator': 'blender/build_all.py',
        'blender_version': bpy.app.version_string,
        'models': [existing[k] for k in PROP_REGISTRY.keys() if k in existing],
    }
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)

    total_kb = sum(m['bytes'] for m in manifest['models']) / 1024.0
    print(
        f'Done! Exported {len(targets)} GLB props ({total_kb:.1f} KB total) '
        f'in {time.time() - t0:.2f}s -> {manifest_path}'
    )


if __name__ == '__main__':
    main()
