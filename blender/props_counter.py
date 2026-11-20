"""
Blender procedural builders for Hero Countertop & Under-Counter Indonesian Kitchen Props.
All props are authored in Blender Z-up meters using t2b(tx, ty, tz) so glTF export (+Y up)
matches kitchen3d.html group origins 1:1 to the millimeter.
"""

import math
import random
import bpy
import bmesh
from mathutils import Vector, Euler

from utils import (
    clear_scene,
    t2b,
    hex_rgba,
    make_pbr_mat,
    set_smooth,
    add_subsurf,
    add_bevel,
    add_solidify,
    boolean_diff,
    apply_all_modifiers,
    assign_mat,
    link_obj,
    create_lathe,
    create_curve_tube,
    create_box,
    create_cylinder,
    create_torus,
    create_uv_sphere,
    make_plaid_image,
    make_lpg_stencil_image,
    make_bottle_label_image,
)


# =============================================================================
# 1. TABUNG GAS LPG 3KG MELON SNI 1452 + REGULATOR + SELANG ORANYE
#    Origin: kitchen3d.html gasGroup at (-1.54, 0, -0.35), rot (0, 0, 0)
# =============================================================================

def build_lpg_gas_3kg():
    clear_scene()

    lpg_img = make_lpg_stencil_image()
    mat_body = make_pbr_mat(
        'LPG_Melon_Steel',
        color=hex_rgba('#6ea848'),
        roughness=0.52,
        metallic=0.14,
        coat=0.08,
        coat_roughness=0.50,
        image=lpg_img,
        bump_strength=0.04,
        bump_scale=45.0,
    )
    mat_green_plain = make_pbr_mat(
        'LPG_Green_Collar',
        color=hex_rgba('#75b24f'),
        roughness=0.54,
        metallic=0.14,
        coat=0.06,
        coat_roughness=0.52,
        double_sided=True,
    )
    mat_brass = make_pbr_mat('LPG_Brass', color=hex_rgba('#dfb85a'), roughness=0.36, metallic=0.82)
    mat_reg = make_pbr_mat('LPG_Regulator_Alloy', color=hex_rgba('#8590a0'), roughness=0.42, metallic=0.68)
    mat_knob = make_pbr_mat('LPG_Black_Plastic', color=hex_rgba('#191c22'), roughness=0.52, metallic=0.05)
    mat_dial = make_pbr_mat('LPG_Gauge_Dial', color=hex_rgba('#f3efe2'), roughness=0.30, metallic=0.0)
    mat_glass = make_pbr_mat('LPG_Gauge_Glass', color=(0.9, 0.96, 1.0, 1.0), roughness=0.08, transmission=0.82, alpha=0.35)
    mat_hose = make_pbr_mat('LPG_Orange_Hose', color=hex_rgba('#d96624'), roughness=0.58, metallic=0.0)
    mat_clamp = make_pbr_mat('LPG_Steel_Clamp', color=hex_rgba('#b8c0cc'), roughness=0.30, metallic=0.85)

    # Smooth SNI 1452 Melon cylinder profile (Ø 26cm, H 42cm) with rolled foot ring
    profile = [
        (0.088, 0.000),
        (0.098, 0.002),
        (0.100, 0.010),
        (0.095, 0.040),
        (0.092, 0.052),
        (0.108, 0.072),
        (0.125, 0.104),
        (0.130, 0.140),
        (0.130, 0.212),
        (0.124, 0.250),
        (0.104, 0.284),
        (0.072, 0.304),
        (0.036, 0.313),
        (0.022, 0.316),
        (0.022, 0.336),
        (0.015, 0.336),
    ]
    tank = create_lathe('LPG_Tank_Body', profile, segments=48, mat=mat_body, subsurf=1)
    # Orient stencil face toward kitchen (+X in Three.js = +X in Blender)
    tank.rotation_euler = Euler((0.0, 0.0, math.pi * 0.5), 'XYZ')

    # Center circumferential welded bead seam
    create_torus('LPG_Weld_Seam', major_radius=0.1305, minor_radius=0.0032, major_seg=48, minor_seg=12,
                 location=t2b(0, 0.174, 0), mat=mat_green_plain)

    # Solidified Hand-Guard Collar (Ø 18.2cm) with REAL Boolean rounded hand/hose cutouts!
    collar = create_cylinder('LPG_HandGuard', radius1=0.091, radius2=0.091, depth=0.098, vertices=48,
                             location=t2b(0, 0.352, 0), cap_ends=False, mat=mat_green_plain)
    add_solidify(collar, thickness=0.0045, offset=0.0)
    apply_all_modifiers(collar)

    # Front & Back rounded-slot Boolean cutouts (oriented cleanly toward kitchen +X & -X)
    cut1 = create_box('Cut1', size=(0.24, 0.092, 0.062), location=t2b(0.0, 0.354, 0.0), bevel=0.018, bevel_segments=4)
    apply_all_modifiers(cut1)
    boolean_diff(collar, cut1)
    set_smooth(collar, 45.0)

    # Thick rolled top & bottom collar rims
    create_torus('LPG_Guard_TopRim', major_radius=0.091, minor_radius=0.0072, major_seg=48, minor_seg=14,
                 location=t2b(0, 0.401, 0), mat=mat_green_plain)
    create_torus('LPG_Guard_BotRim', major_radius=0.091, minor_radius=0.0050, major_seg=48, minor_seg=12,
                 location=t2b(0, 0.304, 0), mat=mat_green_plain)

    # Brass Spindle Valve + Hex Nut Collar
    create_cylinder('LPG_Valve_Stem', radius1=0.018, radius2=0.016, depth=0.044, vertices=16,
                    location=t2b(0, 0.336, 0), mat=mat_brass)
    create_cylinder('LPG_Valve_Hex', radius1=0.022, radius2=0.022, depth=0.012, vertices=6,
                    location=t2b(0, 0.326, 0), bevel=0.0015, mat=mat_brass)

    # Sculpted L-Shaped Pressure Regulator + Locking Lever + Pressure Gauge Dial
    create_cylinder('LPG_Reg_Body', radius1=0.032, radius2=0.029, depth=0.030, vertices=28,
                    location=t2b(0, 0.368, 0), bevel=0.003, mat=mat_reg)
    # Outlet nozzle barb facing kitchen-front (+X, +Z)
    create_cylinder('LPG_Reg_Barb', radius1=0.010, radius2=0.0085, depth=0.038, vertices=16,
                    location=t2b(0.032, 0.367, 0.018), rotation=(0.0, math.pi / 2, -0.52), mat=mat_brass)
    # Black locking switch handle
    create_box('LPG_Reg_Switch', size=(0.052, 0.016, 0.014), location=t2b(-0.024, 0.372, -0.008),
               rotation=(0.0, 0.0, 0.35), bevel=0.003, mat=mat_knob)
    # Pressure Gauge (recessed bezel + cream dial + glass cover)
    create_cylinder('LPG_Gauge_Bezel', radius1=0.018, radius2=0.018, depth=0.014, vertices=24,
                    location=t2b(-0.010, 0.390, 0.016), bevel=0.002, mat=mat_knob)
    create_cylinder('LPG_Gauge_Face', radius1=0.0155, radius2=0.0155, depth=0.002, vertices=24,
                    location=t2b(-0.010, 0.397, 0.016), mat=mat_dial)
    create_cylinder('LPG_Gauge_Glass', radius1=0.016, radius2=0.016, depth=0.002, vertices=24,
                    location=t2b(-0.010, 0.399, 0.016), mat=mat_glass)
    # Hose clamp ring
    create_torus('LPG_Hose_Clamp', major_radius=0.0115, minor_radius=0.0022, major_seg=20, minor_seg=8,
                 location=t2b(0.044, 0.367, 0.024), rotation=(0.0, math.pi / 2, -0.52), mat=mat_clamp)

    # Smooth NURBS Orange Flexible LPG Hose exiting cleanly through the open cutout up to stove!
    hose_pts = [
        t2b(0.038, 0.367, 0.022),
        t2b(0.094, 0.368, 0.068),
        t2b(0.146, 0.468, 0.138),
        t2b(0.122, 0.675, 0.218),
        t2b(-0.010, 0.845, 0.250),
    ]
    create_curve_tube('LPG_Orange_Hose', hose_pts, radius=0.0095, resolution_u=28, bevel_res=10, mat=mat_hose)


# =============================================================================
# 2. KOMPOR GAS 2 TUNGKU RINNAI RI-522 (70.0 × 37.8 × 14.9 cm)
#    Origin: kitchen3d.html stoveGroup at (-1.54, 0.86, -0.06), rot (0, 0, 0)
# =============================================================================

def build_rinnai_stove():
    clear_scene()

    mat_steel = make_pbr_mat('Rinnai_Brushed_Steel', color=hex_rgba('#cfd8e4'), roughness=0.28, metallic=0.86, coat=0.25)
    mat_black = make_pbr_mat('Rinnai_CastIron', color=hex_rgba('#171a20'), roughness=0.56, metallic=0.72)
    mat_enamel = make_pbr_mat('Rinnai_Enamel_Bowl', color=hex_rgba('#1d212a'), roughness=0.24, metallic=0.45, coat=0.65)
    mat_brass = make_pbr_mat('Rinnai_Burner_Brass', color=hex_rgba('#e2b858'), roughness=0.26, metallic=0.90)
    mat_fascia = make_pbr_mat('Rinnai_Front_Fascia', color=hex_rgba('#141822'), roughness=0.32, metallic=0.40, coat=0.35)
    mat_knob = make_pbr_mat('Rinnai_Knob', color=hex_rgba('#242934'), roughness=0.34, metallic=0.12)
    mat_red = make_pbr_mat('Rinnai_Knob_Accent', color=hex_rgba('#e63c2e'), roughness=0.30, metallic=0.0)
    mat_rubber = make_pbr_mat('Rinnai_Rubber_Foot', color=hex_rgba('#121318'), roughness=0.88, metallic=0.0)

    # 4 Tapered rubber anti-slip feet
    for fx, fz in [(-0.15, -0.30), (0.15, -0.30), (-0.15, 0.30), (0.15, 0.30)]:
        create_cylinder(f'Foot_{fx}_{fz}', radius1=0.022, radius2=0.017, depth=0.018, vertices=18,
                        location=t2b(fx, 0.009, fz), bevel=0.002, mat=mat_rubber)

    # Main beveled stainless chassis (0.378m D × 0.108m H × 0.700m W)
    # In Blender: sx=0.378 (X), sy=0.700 (Z in Three.js), sz=0.106 (Y up)
    body = create_box('Rinnai_Chassis', size=(0.378, 0.700, 0.106), location=t2b(0, 0.071, 0),
                      bevel=0.010, bevel_segments=4, mat=mat_steel)

    # Stamped overhanging top stainless deck w/ curved lip & Boolean burner wells!
    deck = create_box('Rinnai_TopDeck', size=(0.388, 0.710, 0.016), location=t2b(0, 0.124, 0),
                      bevel=0.005, bevel_segments=3, mat=mat_steel)
    apply_all_modifiers(deck)
    for bi, bz in enumerate([-0.175, 0.175]):
        well_cut = create_cylinder(f'WellCut_{bi}', radius1=0.095, radius2=0.102, depth=0.036, vertices=32,
                                   location=t2b(0, 0.126, bz))
        boolean_diff(deck, well_cut)
    set_smooth(deck, 38.0)

    # Sleek beveled dark front control fascia facing +X (toward kitchen)
    create_box('Rinnai_Fascia', size=(0.012, 0.660, 0.088), location=t2b(0.189, 0.072, 0),
               bevel=0.003, bevel_segments=2, mat=mat_fascia)

    # Sculpted Ergonomic Rotary Control Knobs (both burners; front burner turned ON!)
    for ki, kz in enumerate([-0.175, 0.175]):
        create_cylinder(f'KnobBase_{ki}', radius1=0.025, radius2=0.023, depth=0.022, vertices=28,
                        location=t2b(0.203, 0.070, kz), rotation=(0.0, math.pi / 2, 0.0), bevel=0.003, mat=mat_black)
        # Sculpted tapered finger-grip bar
        rot_x = 0.58 if kz > 0 else 0.0
        create_box(f'KnobGrip_{ki}', size=(0.022, 0.012, 0.044), location=t2b(0.216, 0.070, kz),
                   rotation=(rot_x, 0.0, 0.0), bevel=0.0035, bevel_segments=3, mat=mat_knob)
        create_box(f'KnobMark_{ki}', size=(0.024, 0.004, 0.010), location=t2b(0.217, 0.084, kz),
                   rotation=(rot_x, 0.0, 0.0), bevel=0.001, mat=mat_red)

    # Dual Concave Enamel Drip Bowls + Slotted Brass Burner Crowns + Curved 5-Prong Cast-Iron Spider Grates!
    for bi, bz in enumerate([-0.175, 0.175]):
        bowl_prof = [
            (0.040, 0.116),
            (0.078, 0.118),
            (0.098, 0.128),
            (0.106, 0.134),
            (0.102, 0.136),
            (0.074, 0.123),
            (0.040, 0.121),
        ]
        create_lathe(f'DripBowl_{bi}', bowl_prof, segments=36, mat=mat_enamel, location=t2b(0, 0, bz), subsurf=1)

        # Brass burner head w/ flared crown lip
        crown_prof = [
            (0.026, 0.120),
            (0.032, 0.132),
            (0.045, 0.138),
            (0.047, 0.147),
            (0.041, 0.150),
            (0.024, 0.148),
            (0.014, 0.144),
        ]
        create_lathe(f'BrassCrown_{bi}', crown_prof, segments=32, mat=mat_brass, location=t2b(0, 0, bz), cap_top=True)

        # Outer cast-iron spider support ring
        create_torus(f'GrateRing_{bi}', major_radius=0.104, minor_radius=0.0065, major_seg=36, minor_seg=10,
                     location=t2b(0, 0.146, bz), mat=mat_black)

        # 5 Curved upward-sweeping spider pan-support prongs
        for g in range(5):
            ang = (g / 5.0) * math.tau
            ca, sa = math.cos(ang), math.sin(ang)
            prong_pts = [
                t2b(ca * 0.104, 0.146, bz + sa * 0.104),
                t2b(ca * 0.088, 0.158, bz + sa * 0.088),
                t2b(ca * 0.064, 0.156, bz + sa * 0.064),
                t2b(ca * 0.050, 0.144, bz + sa * 0.050),
            ]
            create_curve_tube(f'Prong_{bi}_{g}', prong_pts, radius=0.0052, radii=[1.0, 1.15, 0.95, 0.78],
                              resolution_u=10, bevel_res=6, mat=mat_black)


# =============================================================================
# 3. WAJAN TEFLON 24CM + GAGANG BAKELITE ERGONOMIS
#    Origin: kitchen3d.html teflonGroup at (-1.54, 1.018, 0.115)
#    (Oil pool & dropping egg remain dynamic in kitchen3d.html!)
# =============================================================================

def build_teflon_pan():
    clear_scene()

    mat_teflon = make_pbr_mat('Teflon_Coating', color=hex_rgba('#16181e'), roughness=0.34, metallic=0.42, coat=0.32, bump_strength=0.06, bump_scale=85.0)
    mat_rim = make_pbr_mat('Teflon_Steel_Rim', color=hex_rgba('#d4dce8'), roughness=0.18, metallic=0.92)
    mat_bakelite = make_pbr_mat('Teflon_Bakelite', color=hex_rgba('#1b1a22'), roughness=0.30, metallic=0.06, coat=0.35)

    # Smooth spun-aluminum 24cm shallow flared pan with thick induction bottom & rolled top lip
    pan_prof = [
        (0.001, 0.000),
        (0.096, 0.000),
        (0.104, 0.003),
        (0.118, 0.014),
        (0.132, 0.036),
        (0.137, 0.047),
        (0.134, 0.050),
        (0.129, 0.047),
        (0.114, 0.019),
        (0.098, 0.008),
        (0.001, 0.007),
    ]
    create_lathe('Teflon_Pan_Body', pan_prof, segments=56, mat=mat_teflon, subsurf=1)
    create_torus('Teflon_Silver_Rim', major_radius=0.1345, minor_radius=0.0026, major_seg=56, minor_seg=10,
                 location=t2b(0, 0.048, 0), mat=mat_rim)

    # Ergonomically curved Bakelite handle angled at Three.js rotY = -1.25 rad
    # Helper to rotate handle local (+X outward) around Y_up by -1.25 rad
    yaw = -1.25
    cy, sy = math.cos(yaw), math.sin(yaw)

    def hpt(lx, ly, lz=0.0):
        tx = lx * cy + lz * sy
        tz = -lx * sy + lz * cy
        return t2b(tx, ly, tz)

    # Stainless flame-guard bolster neck
    bolster_pts = [hpt(0.129, 0.040), hpt(0.146, 0.046), hpt(0.165, 0.052)]
    create_curve_tube('Handle_FlameGuard', bolster_pts, radius=0.0135, radii=[1.05, 0.96, 1.02],
                      resolution_u=12, bevel_res=10, mat=mat_rim)

    # Twin interior stainless rivet heads
    for rz in [-0.012, 0.012]:
        create_uv_sphere(f'Rivet_{rz}', radius=0.0045, segments=12, ring_count=8,
                         location=hpt(0.124, 0.036, rz), mat=mat_rim)

    # Ergonomic contoured curved Bakelite grip (gentle S-curve rise + palm swell + tapered hanging end)
    grip_pts = [
        hpt(0.160, 0.051),
        hpt(0.195, 0.060),
        hpt(0.245, 0.072),
        hpt(0.295, 0.080),
        hpt(0.335, 0.082),
    ]
    grip = create_curve_tube('Handle_Bakelite_Grip', grip_pts, radius=0.0155,
                             radii=[0.82, 0.96, 1.12, 1.02, 0.72],
                             resolution_u=20, bevel_res=12, mat=mat_bakelite)
    # Slightly flatten grip vertically for authentic ergonomic hand contour
    grip.scale = Vector((1.0, 1.0, 0.82))

    # Metal hanging loop at end of handle
    create_torus('Handle_HangLoop', major_radius=0.010, minor_radius=0.0022, major_seg=20, minor_seg=8,
                 location=hpt(0.342, 0.082), mat=mat_rim)


# =============================================================================
# 4. TUTUP PANCI STAINLESS STEEL 24CM (DOMED REFLECTIVE LID)
#    Origin: kitchen3d.html lidGroup
# =============================================================================

def build_pan_lid():
    clear_scene()

    mat_steel = make_pbr_mat('Lid_Mirror_Steel', color=hex_rgba('#dde6f2'), roughness=0.10, metallic=0.94, coat=0.75, coat_roughness=0.06)
    mat_knob = make_pbr_mat('Lid_Bakelite_Knob', color=hex_rgba('#1b1b22'), roughness=0.28, metallic=0.05, coat=0.35)

    # Stepped domed lid profile with curled rim bead
    lid_prof = [
        (0.001, 0.042),
        (0.035, 0.040),
        (0.072, 0.032),
        (0.104, 0.019),
        (0.118, 0.008),
        (0.123, 0.002),
        (0.129, 0.000),
        (0.129, -0.004),
        (0.122, -0.004),
        (0.116, 0.005),
        (0.098, 0.018),
        (0.065, 0.030),
        (0.001, 0.038),
    ]
    create_lathe('Lid_Dome', lid_prof, segments=56, mat=mat_steel, subsurf=1)

    # Sculpted waisted Bakelite dome knob (classic Indonesian pan lid knob!)
    knob_prof = [
        (0.001, 0.040),
        (0.025, 0.040),
        (0.024, 0.045),
        (0.014, 0.048),
        (0.013, 0.055),
        (0.023, 0.064),
        (0.022, 0.070),
        (0.014, 0.074),
        (0.001, 0.075),
    ]
    create_lathe('Lid_Knob', knob_prof, segments=36, mat=mat_knob, subsurf=1)


# =============================================================================
# 5. BANTAL GULING INDONESIA (ORGANIC SCULPTED KAPUK + PLEATED RUMBAI + TALI SERUT)
#    Origin: bolster center, horizontal along local Y (just like kitchen3d.html!)
# =============================================================================

def build_bolster_pillow(variant=1):
    clear_scene()

    if variant == 1:
        tex_img = make_plaid_image('BolsterPlaid_BlueGold', '#dfe9f4', '#3676c8', '#e8b632', size=256)
    else:
        tex_img = make_plaid_image('BolsterPlaid_CoralMint', '#f7ecec', '#d85262', '#38a696', size=256)

    mat_fabric = make_pbr_mat('Bolster_Cotton_Plaid', color=(1.0, 1.0, 1.0, 1.0), roughness=0.92, metallic=0.0,
                              image=tex_img, bump_strength=0.14, bump_scale=60.0)
    mat_cord = make_pbr_mat('Bolster_Drawstring_Cord', color=hex_rgba('#ede6d4'), roughness=0.88, metallic=0.0)

    # Profile along Blender +Z (which becomes Three.js +Y, matching makeRealisticBolster rotation!)
    b_prof = [
        (0.002, -0.392),
        (0.040, -0.388),
        (0.032, -0.370),
        (0.016, -0.352),  # cinched drawstring neck
        (0.068, -0.328),
        (0.094, -0.270),
        (0.100, -0.175),
        (0.096, -0.055),
        (0.101, 0.065),
        (0.097, 0.195),
        (0.087, 0.292),
        (0.060, 0.334),
        (0.016, 0.352),   # top cinched drawstring neck
        (0.032, 0.370),
        (0.040, 0.388),
        (0.002, 0.392),
    ]
    bolster = create_lathe(f'Bolster_Body_{variant}', b_prof, segments=56, mat=mat_fabric, subsurf=1)

    # Sculpt organic kapuk fullness, pleated cotton cloth folds on gathered frills & subtle gravity settle!
    mesh = bolster.data
    seed_off = variant * 1.9
    for v in mesh.vertices:
        vx, vy, vz = v.co.x, v.co.y, v.co.z
        ang = math.atan2(vy, vx)
        if abs(vz) > 0.354:
            # Deep organic pleated cloth ruffles radiating out of cinched tali serut
            pleat = 1.0 + 0.16 * math.sin(ang * 8.0 + seed_off) + 0.08 * math.cos(ang * 13.0 - seed_off)
            v.co.x = vx * pleat
            v.co.y = vy * pleat
            v.co.z = vz + math.sin(ang * 8.0 + seed_off) * 0.006 * (1.0 if vz > 0 else -1.0)
        elif abs(vz) > 0.320:
            # Radial gathering pinch creases radiating into the cinched neck!
            crease = 1.0 + 0.055 * math.sin(ang * 10.0 + seed_off)
            v.co.x = vx * crease
            v.co.y = vy * crease
        else:
            # Soft organic cotton pillow undulation + slight gravity squash along Y
            lump = 1.0 + 0.036 * math.sin(vz * 13.0 + ang * 2.0 + seed_off) + 0.022 * math.cos(ang * 3.0 - vz * 7.0)
            v.co.x = vx * lump
            v.co.y = vy * lump * 0.88
    mesh.update()
    set_smooth(bolster, 65.0)

    # Real tied cotton drawstring cords & curved bow loops at both ends!
    for end_s in [-1.0, 1.0]:
        zc = end_s * 0.352
        create_torus(f'TaliSerut_Ring_{end_s}', major_radius=0.019, minor_radius=0.0042, major_seg=28, minor_seg=10,
                     location=(0.0, 0.0, zc), mat=mat_cord)
        # Two dangling curved cord tails
        for side in [-1.0, 1.0]:
            tail_pts = [
                (0.016, side * 0.005, zc),
                (0.028, side * 0.016, zc + end_s * 0.012),
                (0.034, side * 0.026, zc + end_s * 0.032),
            ]
            create_curve_tube(f'TaliSerut_Tail_{end_s}_{side}', tail_pts, radius=0.0026,
                              resolution_u=10, bevel_res=6, mat=mat_cord)


# =============================================================================
# 6. BOTOL KECAP MANIS, SAUS SAMBAL & MINYAK GORENG (3 CURVED BOTTLES)
#    Origin: (-1.78, 0.86, -1.14) in kitchen3d.html
# =============================================================================

def build_condiment_bottles():
    clear_scene()

    specs = [
        # (name, rel_tx, rel_tz, body_hex, cap_hex, bg_hex, stripe_hex, scale_h, ribbed)
        ('Kecap_Manis', -0.04, 0.10, '#180a05', '#e8b838', '#24120c', '#e0a228', 1.02, False),
        ('Saus_Sambal', 0.12, -0.02, '#b82218', '#d9281e', '#c82018', '#f2c438', 0.90, False),
        ('Minyak_Goreng', -0.10, -0.10, '#dca832', '#227848', '#1e7442', '#f4cc3a', 1.12, True),
    ]

    for name, rx, rz, b_hex, c_hex, bg_hex, st_hex, sh, ribbed in specs:
        mat_glass = make_pbr_mat(f'{name}_Glass', color=hex_rgba(b_hex), roughness=0.08, metallic=0.02,
                                 coat=0.95, coat_roughness=0.05, transmission=0.30 if name != 'Kecap_Manis' else 0.05, ior=1.50)
        mat_cap = make_pbr_mat(f'{name}_Cap', color=hex_rgba(c_hex), roughness=0.30, metallic=0.05, coat=0.35)
        lbl_img = make_bottle_label_image(f'{name}_LabelImg', bg_hex, st_hex)
        mat_lbl = make_pbr_mat(f'{name}_Label', color=(1, 1, 1, 1), roughness=0.36, image=lbl_img)

        if ribbed:
            # Molded PET cooking oil bottle w/ ergonomic pinched waist & horizontal grip ribs
            prof = [
                (0.001, 0.000), (0.032, 0.000), (0.036, 0.012), (0.036, 0.070 * sh),
                (0.032, 0.088 * sh), (0.035, 0.102 * sh), (0.031, 0.118 * sh), (0.035, 0.136 * sh),
                (0.028, 0.168 * sh), (0.015, 0.205 * sh), (0.014, 0.236 * sh), (0.016, 0.242 * sh),
            ]
        else:
            # Classic curved glass Kecap/Sambal bottle w/ smooth ogive shoulder & collar ring
            prof = [
                (0.001, 0.000), (0.030, 0.000), (0.033, 0.010), (0.033, 0.115 * sh),
                (0.029, 0.148 * sh), (0.019, 0.180 * sh), (0.013, 0.206 * sh),
                (0.013, 0.235 * sh), (0.015, 0.240 * sh), (0.013, 0.244 * sh),
            ]

        loc = t2b(rx, 0.0, rz)
        create_lathe(f'{name}_Body', prof, segments=36, mat=mat_glass, location=loc, cap_top=True, subsurf=1)
        # Screw / flip cap with beveled rim
        create_cylinder(f'{name}_Cap', radius1=0.0155, radius2=0.0148, depth=0.024, vertices=24,
                        location=t2b(rx, 0.252 * sh, rz), bevel=0.002, mat=mat_cap)
        # Wrap-around curved paper label sleeve
        lbl = create_cylinder(f'{name}_Label', radius1=0.0342 if not ribbed else 0.0365,
                              radius2=0.0342 if not ribbed else 0.0365,
                              depth=0.082 * sh, vertices=36,
                              location=t2b(rx, 0.065 * sh, rz), cap_ends=False, mat=mat_lbl)
        lbl.rotation_euler = Euler((0.0, 0.0, math.pi * 0.5), 'XYZ')


# =============================================================================
# 7. RAK PIRING PLASTIK + 5 PIRING CEKUNG + 2 MUG GAGANG-C + SENDOK MELENGKUNG
#    Origin: kitchen3d.html rackGroup at (-1.64, 0.86, -1.96)
# =============================================================================

def build_dish_rack_set():
    clear_scene()

    mat_teal = make_pbr_mat('Rack_Plastic_Teal', color=hex_rgba('#2f96a6'), roughness=0.36, metallic=0.02, coat=0.25)
    mat_ceramic = make_pbr_mat('Plate_Cream_Ceramic', color=hex_rgba('#fff9ee'), roughness=0.14, metallic=0.0, coat=0.85, coat_roughness=0.08)
    mat_mug1 = make_pbr_mat('Mug_Ochre', color=hex_rgba('#e0c48c'), roughness=0.18, coat=0.72)
    mat_mug2 = make_pbr_mat('Mug_Blue', color=hex_rgba('#5686b2'), roughness=0.18, coat=0.72)
    mat_steel = make_pbr_mat('Cutlery_Steel', color=hex_rgba('#d4dde8'), roughness=0.18, metallic=0.90)

    # Molded beveled drain tray
    create_box('Rack_Tray', size=(0.36, 0.46, 0.022), location=t2b(0, 0.011, 0), bevel=0.005, bevel_segments=3, mat=mat_teal)
    # Front/back curved top rails & rounded vertical cage ribs
    for rz in [-0.215, 0.215]:
        create_box(f'Rack_TopRail_{rz}', size=(0.35, 0.018, 0.020), location=t2b(0, 0.135, rz), bevel=0.004, mat=mat_teal)
        for ri in range(6):
            rx = -0.15 + ri * 0.06
            create_cylinder(f'Rack_Post_{rz}_{ri}', radius1=0.007, radius2=0.007, depth=0.124, vertices=12,
                            location=t2b(rx, 0.073, rz), mat=mat_teal)

    # 5 Smooth Subsurf Concave Ceramic Plates resting cleanly in slots
    plate_prof = [
        (0.001, 0.000), (0.056, 0.000), (0.062, 0.004), (0.104, 0.019),
        (0.110, 0.023), (0.106, 0.025), (0.098, 0.020), (0.056, 0.006), (0.001, 0.006),
    ]
    for pi in range(5):
        pz = -0.15 + pi * 0.065
        plate = create_lathe(f'Plate_{pi}', plate_prof, segments=36, mat=mat_ceramic,
                             location=t2b(-0.05, 0.124, pz), subsurf=1)
        # Tilt plate upright inside rack (around X axis)
        plate.rotation_euler = Euler((math.pi / 2 - 0.16, 0.0, 0.0), 'XYZ')

    # 2 Ceramic Mugs w/ smooth sculpted hollow walls & NURBS-swept ergonomic C-handles!
    mug_prof = [
        (0.001, 0.000), (0.034, 0.000), (0.038, 0.008), (0.040, 0.084),
        (0.038, 0.089), (0.035, 0.086), (0.033, 0.012), (0.001, 0.010),
    ]
    for mi, mmat in enumerate([mat_mug1, mat_mug2]):
        mz = -0.10 + mi * 0.13
        create_lathe(f'Mug_{mi}', mug_prof, segments=32, mat=mmat, location=t2b(0.105, 0.022, mz), subsurf=1)
        # Curved ergonomic C-handle swept smoothly out of mug wall
        hdl_pts = [
            t2b(0.141, 0.088, mz),
            t2b(0.168, 0.086, mz),
            t2b(0.172, 0.062, mz),
            t2b(0.165, 0.042, mz),
            t2b(0.140, 0.040, mz),
        ]
        create_curve_tube(f'Mug_Handle_{mi}', hdl_pts, radius=0.0052, resolution_u=14, bevel_res=8, mat=mmat)

    # Draining cutlery cup + 3 sculpted stainless spoons with curved necks & concave oval bowls!
    cup_prof = [(0.001, 0.0), (0.028, 0.0), (0.033, 0.098), (0.030, 0.100), (0.026, 0.008), (0.001, 0.008)]
    create_lathe('Cutlery_Cup', cup_prof, segments=24, mat=mat_teal, location=t2b(0.11, 0.022, 0.16))
    for si in range(3):
        sx = 0.098 + si * 0.011
        sz = 0.155 + (si % 2) * 0.010
        lean = (si - 1) * 0.018
        sp_pts = [
            t2b(sx, 0.035, sz),
            t2b(sx + lean * 0.5, 0.110, sz),
            t2b(sx + lean, 0.165, sz),
            t2b(sx + lean * 1.2, 0.195, sz),
        ]
        create_curve_tube(f'Spoon_Stem_{si}', sp_pts, radius=0.0030, radii=[1.2, 0.85, 0.75, 1.0],
                          resolution_u=10, bevel_res=6, mat=mat_steel)
        bowl = create_uv_sphere(f'Spoon_Bowl_{si}', radius=0.014, segments=16, ring_count=10,
                                scale=(0.65, 0.35, 1.25), location=t2b(sx + lean * 1.25, 0.205, sz), mat=mat_steel)


# =============================================================================
# 8. RAK TELUR + 5 TELUR AYAM OVOID HALUS
#    Origin: kitchen3d.html trayGroup at (-1.38, 0.86, 1.06)
# =============================================================================

def build_egg_tray():
    clear_scene()

    mat_tray = make_pbr_mat('EggTray_Yellow', color=hex_rgba('#f0bc30'), roughness=0.42, metallic=0.0, coat=0.22)
    mat_egg = make_pbr_mat('Egg_Brown_Shell', color=hex_rgba('#d89c66'), roughness=0.40, metallic=0.0, coat=0.18, bump_strength=0.05, bump_scale=120.0)

    tray = create_box('EggTray_Base', size=(0.18, 0.26, 0.026), location=t2b(0, 0.013, 0), bevel=0.006, bevel_segments=3, mat=mat_tray)
    apply_all_modifiers(tray)

    # Molded egg cup indentations via Boolean spheres!
    cup_coords = [(-0.045, -0.07), (0.045, -0.07), (-0.045, 0.0), (0.045, 0.0), (-0.045, 0.07), (0.045, 0.07)]
    for ci, (ex, ez) in enumerate(cup_coords):
        cut = create_uv_sphere(f'CupCut_{ci}', radius=0.026, segments=16, ring_count=10, location=t2b(ex, 0.032, ez))
        boolean_diff(tray, cut)
    set_smooth(tray, 40.0)

    # 5 True asymmetric ovoid eggs (broader base, gently pointed apex!)
    egg_prof = [
        (0.001, 0.000), (0.015, 0.003), (0.023, 0.014), (0.024, 0.026),
        (0.021, 0.040), (0.015, 0.052), (0.007, 0.059), (0.001, 0.061),
    ]
    for ei, (ex, ez) in enumerate(cup_coords[:5]):
        eg = create_lathe(f'Egg_{ei}', egg_prof, segments=28, mat=mat_egg, location=t2b(ex, 0.011, ez), subsurf=1)
        eg.rotation_euler = Euler((0.05 * ((ei % 3) - 1), 0.04 * ((ei % 2) * 2 - 1), 0.0), 'XYZ')


# =============================================================================
# 9. COBEK BATU VOLKANIK + ULEKAN LENGKUNG + CABAI RAWIT MERAH
#    Origin: kitchen3d.html cobekGroup at (-1.58, 0.86, -1.48)
# =============================================================================

def build_cobek_ulekan():
    clear_scene()

    mat_stone = make_pbr_mat('Volcanic_Stone', color=hex_rgba('#454a54'), roughness=0.88, metallic=0.02, bump_strength=0.22, bump_scale=65.0)
    mat_chili = make_pbr_mat('Red_Chili', color=hex_rgba('#e2241a'), roughness=0.22, metallic=0.0, coat=0.65)
    mat_stem = make_pbr_mat('Chili_Stem', color=hex_rgba('#3e7c2e'), roughness=0.55)

    # Deep concave hand-carved volcanic andesite mortar (Cobek)
    cobek_prof = [
        (0.001, 0.000), (0.076, 0.000), (0.088, 0.008), (0.104, 0.030),
        (0.108, 0.042), (0.100, 0.045), (0.090, 0.036), (0.068, 0.018),
        (0.036, 0.012), (0.001, 0.011),
    ]
    cobek = create_lathe('Cobek_Mortar', cobek_prof, segments=36, mat=mat_stone, subsurf=1)
    # Subtle organic hand-chiseled irregularity
    rng = random.Random(42)
    for v in cobek.data.vertices:
        v.co.x *= 1.0 + (rng.random() - 0.5) * 0.028
        v.co.y *= 1.0 + (rng.random() - 0.5) * 0.028
    cobek.data.update()

    # Authentic curved Indonesian L-shaped stone pestle (Ulekan!)
    ulek_pts = [
        t2b(-0.042, 0.028, -0.012),
        t2b(-0.008, 0.028, 0.006),
        t2b(0.036, 0.046, 0.022),
        t2b(0.072, 0.074, 0.030),
    ]
    create_curve_tube('Ulekan_Pestle', ulek_pts, radius=0.024, radii=[1.12, 0.96, 0.78, 0.72],
                      resolution_u=16, bevel_res=10, mat=mat_stone)

    # 3 Curved organic red chilies + curved green stems resting inside the cobek!
    chili_specs = [
        [t2b(-0.045, 0.018, 0.032), t2b(-0.024, 0.021, 0.040), t2b(-0.005, 0.019, 0.035), t2b(0.008, 0.018, 0.022)],
        [t2b(-0.052, 0.020, 0.008), t2b(-0.032, 0.024, 0.020), t2b(-0.010, 0.022, 0.024)],
        [t2b(0.012, 0.018, -0.030), t2b(0.032, 0.022, -0.022), t2b(0.048, 0.020, -0.008)],
    ]
    for ci, pts in enumerate(chili_specs):
        create_curve_tube(f'Chili_{ci}', pts, radius=0.0068, radii=[0.95, 1.05, 0.65, 0.18][:len(pts)],
                          resolution_u=12, bevel_res=8, mat=mat_chili)
        stem_pts = [pts[0], pts[0] + Vector((-0.010, 0.006, 0.008)), pts[0] + Vector((-0.016, 0.009, 0.014))]
        create_curve_tube(f'ChiliStem_{ci}', stem_pts, radius=0.0018, radii=[1.2, 0.7, 0.5],
                          resolution_u=8, bevel_res=5, mat=mat_stem)


# =============================================================================
# 10. REL GANTUNGAN ALAT MASAK (CENTONG SAYUR + SODET + SEROK)
#     Origin: (-1.98, 1.42, -1.65) in kitchen3d.html
# =============================================================================

def build_utensil_rail():
    clear_scene()

    mat_iron = make_pbr_mat('Rail_Iron', color=hex_rgba('#1c2028'), roughness=0.38, metallic=0.80)
    mat_steel = make_pbr_mat('Utensil_Steel', color=hex_rgba('#d4dde8'), roughness=0.20, metallic=0.90, double_sided=True)
    mat_handle = make_pbr_mat('Utensil_Handle', color=hex_rgba('#1c1e26'), roughness=0.40, metallic=0.05)

    # Horizontal iron bar (along Z in Three.js = Y in Blender) + 2 wall standoff mounts
    create_cylinder('Rail_Bar', radius1=0.008, radius2=0.008, depth=1.15, vertices=16,
                    location=t2b(0, 0, 0), rotation=(math.pi / 2, 0.0, 0.0), mat=mat_iron)
    for bz in [-0.52, 0.52]:
        create_cylinder(f'Rail_Mount_{bz}', radius1=0.008, radius2=0.014, depth=0.06, vertices=14,
                        location=t2b(-0.03, 0, bz), rotation=(0.0, math.pi / 2, 0.0), mat=mat_iron)

    # 3 Utensils hanging at local Z = -0.31, -0.07, +0.17 (world Z = -1.96, -1.72, -1.48)
    for idx, uz in enumerate([-0.31, -0.07, 0.17]):
        # S-hook wrapping cleanly over rail
        s_pts = [
            t2b(0.008, 0.012, uz), t2b(0.014, 0.002, uz), t2b(0.008, -0.012, uz),
            t2b(0.014, -0.024, uz), t2b(0.010, -0.034, uz),
        ]
        create_curve_tube(f'SHook_{idx}', s_pts, radius=0.0028, resolution_u=12, bevel_res=6, mat=mat_iron)

        # Ergonomic tapered handle grip
        grip_pts = [t2b(0.012, -0.032, uz), t2b(0.012, -0.075, uz), t2b(0.012, -0.125, uz)]
        create_curve_tube(f'UGrip_{idx}', grip_pts, radius=0.009, radii=[0.85, 1.05, 0.80],
                          resolution_u=10, bevel_res=8, mat=mat_handle)

        if idx == 0:
            # Sculpted Soup Ladle (Centong Sayur) with curved J-neck & deep hemispherical bowl!
            neck_pts = [t2b(0.012, -0.125, uz), t2b(0.012, -0.235, uz), t2b(0.022, -0.275, uz)]
            create_curve_tube('Ladle_Neck', neck_pts, radius=0.0042, resolution_u=12, bevel_res=6, mat=mat_steel)
            bowl_prof = [
                (0.001, 0.000), (0.018, 0.003), (0.032, 0.014), (0.039, 0.030),
                (0.036, 0.032), (0.028, 0.016), (0.015, 0.006), (0.001, 0.004),
            ]
            bowl = create_lathe('Ladle_Bowl', bowl_prof, segments=28, mat=mat_steel, location=t2b(0.038, -0.295, uz), subsurf=1)
            bowl.rotation_euler = Euler((0.0, -math.pi / 2 + 0.18, 0.0), 'XYZ')
        else:
            # Bent-neck Slotted Turner Spatula (Sodet) w/ real Boolean vent slots!
            neck_pts = [t2b(0.012, -0.125, uz), t2b(0.012, -0.240, uz), t2b(0.024, -0.268, uz)]
            create_curve_tube(f'Spatula_Neck_{idx}', neck_pts, radius=0.0038, resolution_u=10, bevel_res=6, mat=mat_steel)
            blade = create_box(f'Spatula_Blade_{idx}', size=(0.0035, 0.064, 0.095),
                               location=t2b(0.026, -0.312, uz), rotation=(0.0, 0.10, 0.0), bevel=0.0015, mat=mat_steel)
            apply_all_modifiers(blade)
            for sz in [-0.017, 0.0, 0.017]:
                slot_cut = create_box(f'Slot_{idx}_{sz}', size=(0.020, 0.007, 0.056),
                                      location=t2b(0.026, -0.312, uz + sz))
                boolean_diff(blade, slot_cut)
            set_smooth(blade, 35.0)
