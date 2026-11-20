"""
Blender procedural builders for Room & Midground Indonesian Kitchen Props:
Sharp 2-Door Fridge, Miyako Dispenser + 19L Aqua Gallon, Wooden Table + 16L Kerupuk Jar,
Bufet + Magic Com + Thermos, Wall Shelf + Khong Guan Tin + Teko Blirik + Potted Sirih Gading,
Sculpted Cicak Gecko, Enamel Ceiling Lamp, and Sapu Ijuk Broom.
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
)


# =============================================================================
# 1. KULKAS 2 PINTU SHARP 156cm (W 56 × D 58 × H 156 cm)
#    Origin: kitchen3d.html fridgeGroup at (1.50, 0, -2.08), rotY = -PI/2 - 0.10
# =============================================================================

def build_sharp_fridge():
    clear_scene()

    mat_silver = make_pbr_mat('Fridge_Brushed_Silver', color=hex_rgba('#dce6f2'), roughness=0.28, metallic=0.32, coat=0.52, coat_roughness=0.14)
    mat_back = make_pbr_mat('Fridge_Rear_Galvanized', color=hex_rgba('#2d3440'), roughness=0.66, metallic=0.35)
    mat_gasket = make_pbr_mat('Fridge_Rubber_Gasket', color=hex_rgba('#252934'), roughness=0.84)
    mat_handle = make_pbr_mat('Fridge_Dark_Handle', color=hex_rgba('#242a36'), roughness=0.26, metallic=0.72)
    mat_int = make_pbr_mat('Fridge_Glowing_Liner', color=hex_rgba('#e2f6ff'), roughness=0.30,
                           emission=hex_rgba('#9cdfff'), emission_strength=0.65)
    mat_glass = make_pbr_mat('Fridge_Glass_Shelf', color=hex_rgba('#bce8f8'), roughness=0.08, transmission=0.75, alpha=0.58)
    mat_crisper = make_pbr_mat('Fridge_Crisper', color=hex_rgba('#9ed4ea'), roughness=0.18, transmission=0.55, alpha=0.66)
    mat_milk = make_pbr_mat('Milk_Carton', color=hex_rgba('#3b72c8'), roughness=0.36)
    mat_soda = make_pbr_mat('Soda_Bottle_Green', color=hex_rgba('#2aa64c'), roughness=0.10, coat=0.90, transmission=0.42)
    mat_pitcher = make_pbr_mat('Water_Pitcher_Glass', color=hex_rgba('#d4f0ff'), roughness=0.08, transmission=0.80, alpha=0.52)

    # Strictly non-overlapping beveled cabinet shell (ZERO z-fighting!)
    # Outer rear back panel (full width 0.56 × height 1.56 × depth 0.06, Z_three in [-0.29, -0.23])
    create_box('Fridge_BackPanel', size=(0.56, 0.06, 1.56), location=t2b(0, 0.78, -0.26),
               bevel=0.006, bevel_segments=2, mat=mat_back)
    # Left & Right side walls starting cleanly in front of back panel (depth 0.52, Z_three in [-0.23, +0.29])
    create_box('Fridge_SideL', size=(0.05, 0.52, 1.56), location=t2b(-0.255, 0.78, 0.03),
               bevel=0.008, bevel_segments=3, mat=mat_silver)
    create_box('Fridge_SideR', size=(0.05, 0.52, 1.56), location=t2b(0.255, 0.78, 0.03),
               bevel=0.008, bevel_segments=3, mat=mat_silver)
    # Top, bottom & mid-divider strictly between SideL and SideR (width 0.46)
    create_box('Fridge_Top', size=(0.46, 0.52, 0.06), location=t2b(0, 1.53, 0.03),
               bevel=0.008, bevel_segments=3, mat=mat_silver)
    create_box('Fridge_Bot', size=(0.46, 0.52, 0.08), location=t2b(0, 0.04, 0.03),
               bevel=0.006, bevel_segments=2, mat=mat_silver)
    create_box('Fridge_MidDiv', size=(0.46, 0.50, 0.05), location=t2b(0, 1.04, 0.02),
               bevel=0.004, bevel_segments=2, mat=mat_silver)
    # Glowing lower interior back liner
    create_box('Fridge_IntLiner', size=(0.452, 0.006, 0.92), location=t2b(0, 0.545, -0.225), mat=mat_int)

    # 3 Framed glass shelves + Crisper drawer w/ curved pull handle
    for sy in [0.34, 0.58, 0.80]:
        create_box(f'Fridge_Shelf_{sy}', size=(0.448, 0.42, 0.012), location=t2b(0, sy, 0.02), bevel=0.002, mat=mat_glass)
    create_box('Fridge_Crisper', size=(0.42, 0.36, 0.19), location=t2b(0, 0.18, 0.02), bevel=0.008, mat=mat_crisper)

    # Interior props: Gable-top Milk Carton, Curved Soda Bottle, Glass Water Pitcher w/ curved C-handle!
    create_box('Milk_Body', size=(0.072, 0.072, 0.17), location=t2b(0.10, 0.67, 0.10), bevel=0.004, mat=mat_milk)
    soda_prof = [
        (0.001, 0.0), (0.034, 0.0), (0.035, 0.12), (0.030, 0.16), (0.014, 0.20), (0.013, 0.22), (0.001, 0.222),
    ]
    create_lathe('Soda_Bottle', soda_prof, segments=24, mat=mat_soda, location=t2b(-0.07, 0.35, 0.12), subsurf=1)
    pitch_prof = [
        (0.001, 0.0), (0.038, 0.0), (0.044, 0.06), (0.042, 0.14), (0.048, 0.18), (0.044, 0.182), (0.036, 0.01), (0.001, 0.01),
    ]
    create_lathe('Water_Pitcher', pitch_prof, segments=24, mat=mat_pitcher, location=t2b(0.06, 0.35, 0.03), subsurf=1)
    p_hdl = [t2b(0.102, 0.50, 0.03), t2b(0.132, 0.49, 0.03), t2b(0.134, 0.43, 0.03), t2b(0.102, 0.40, 0.03)]
    create_curve_tube('Pitcher_Handle', p_hdl, radius=0.005, resolution_u=12, bevel_res=6, mat=mat_pitcher)

    # Upper Freezer Door (closed, softly beveled rounded corners + curved vertical handle)
    create_box('Upper_Gasket', size=(0.54, 0.020, 0.47), location=t2b(0, 1.31, 0.295), bevel=0.003, mat=mat_gasket)
    create_box('Upper_Door', size=(0.556, 0.048, 0.482), location=t2b(0, 1.31, 0.324), bevel=0.012, bevel_segments=4, mat=mat_silver)
    u_hdl = [t2b(0.22, 1.15, 0.348), t2b(0.22, 1.18, 0.376), t2b(0.22, 1.30, 0.376), t2b(0.22, 1.33, 0.348)]
    create_curve_tube('Upper_Handle', u_hdl, radius=0.010, resolution_u=14, bevel_res=8, mat=mat_handle)

    # Lower Fridge Door hinged at (-0.275, 0.54, 0.30) opened 21° (-0.36 rad in Three.js Y-up = -0.36 rad in Blender Z-up!)
    ang = -0.36
    ca, sa = math.cos(ang), math.sin(ang)

    def ldoor_pt(lx, ly, lz):
        # Three.js rotateY(ang): x' = lx*cos + lz*sin, z' = -lx*sin + lz*cos
        tx = -0.275 + lx * ca + lz * sa
        ty = 0.54 + ly
        tz = 0.30 - lx * sa + lz * ca
        return t2b(tx, ty, tz)

    g_lo = create_box('Lower_Gasket', size=(0.54, 0.018, 0.96), location=ldoor_pt(0.275, 0, -0.002),
                      rotation=(0.0, 0.0, ang), bevel=0.003, mat=mat_gasket)
    d_lo = create_box('Lower_Door', size=(0.556, 0.048, 0.982), location=ldoor_pt(0.275, 0, 0.026),
                      rotation=(0.0, 0.0, ang), bevel=0.012, bevel_segments=4, mat=mat_silver)
    l_hdl = [
        ldoor_pt(0.495, 0.12, 0.050),
        ldoor_pt(0.495, 0.16, 0.078),
        ldoor_pt(0.495, 0.36, 0.078),
        ldoor_pt(0.495, 0.40, 0.050),
    ]
    create_curve_tube('Lower_Handle', l_hdl, radius=0.010, resolution_u=14, bevel_res=8, mat=mat_handle)

    # Sticky notes & rounded glossy magnets on upper freezer door
    mat_note1 = make_pbr_mat('Sticky_Yellow', color=hex_rgba('#fff078'), roughness=0.86)
    mat_note2 = make_pbr_mat('Sticky_Pink', color=hex_rgba('#ffb6c1'), roughness=0.86)
    create_box('Note1', size=(0.11, 0.002, 0.11), location=t2b(-0.11, 1.34, 0.350), rotation=(0.0, 0.08, 0.0), mat=mat_note1)
    create_box('Note2', size=(0.105, 0.002, 0.105), location=t2b(0.07, 1.28, 0.350), rotation=(0.0, -0.10, 0.0), mat=mat_note2)
    for mi, (mx, my, mhex) in enumerate([(-0.11, 1.39, '#e84838'), (0.07, 1.33, '#30b868'), (-0.02, 1.44, '#3b86e8'), (-0.18, 1.22, '#f2be32')]):
        mm = make_pbr_mat(f'Magnet_{mi}', color=hex_rgba(mhex), roughness=0.22, coat=0.65)
        create_cylinder(f'Mag_{mi}', radius1=0.017, radius2=0.015, depth=0.010, vertices=20,
                        location=t2b(mx, my, 0.353), rotation=(math.pi / 2, 0.0, 0.0), bevel=0.003, mat=mm)


# =============================================================================
# 2. DISPENSER MIYAKO WD-389HC + GALON AQUA 19L BERULIR HALUS
#    Origin: kitchen3d.html dispGroup at (1.56, 0, -0.68), rotY = -PI/2
#    (Animated rising bubbles stay dynamic in kitchen3d.html!)
# =============================================================================

def build_dispenser_galon():
    clear_scene()

    mat_white = make_pbr_mat('Miyako_White_Plastic', color=hex_rgba('#e4e8ee'), roughness=0.34, metallic=0.04, coat=0.35)
    mat_collar = make_pbr_mat('Miyako_Top_Collar', color=hex_rgba('#cdd4de'), roughness=0.36, metallic=0.04)
    mat_dark = make_pbr_mat('Miyako_Alcove_Dark', color=hex_rgba('#1a202c'), roughness=0.52)
    mat_nozzle = make_pbr_mat('Miyako_Chrome_Spout', color=hex_rgba('#dce2ea'), roughness=0.20, metallic=0.78)
    mat_red = make_pbr_mat('Miyako_Hot_Red', color=hex_rgba('#d92e24'), roughness=0.30, coat=0.35)
    mat_blue = make_pbr_mat('Miyako_Cold_Blue', color=hex_rgba('#2278d8'), roughness=0.30, coat=0.35)
    mat_galon = make_pbr_mat('Aqua_19L_Polycarb', color=hex_rgba('#42adff'), roughness=0.06, metallic=0.02,
                             coat=1.0, coat_roughness=0.04, transmission=0.88, ior=1.36, alpha=0.72)
    mat_water = make_pbr_mat('Aqua_Water_Volume', color=hex_rgba('#64ceff'), roughness=0.04, transmission=0.80, ior=1.33, alpha=0.50)

    # Rounded beveled tower body w/ REAL Boolean recessed pouring alcove!
    body = create_box('Dispenser_Tower', size=(0.31, 0.30, 0.96), location=t2b(0, 0.48, 0),
                      bevel=0.016, bevel_segments=4, mat=mat_white)
    apply_all_modifiers(body)

    alcove_cut = create_box('AlcoveCut', size=(0.22, 0.11, 0.23), location=t2b(0, 0.72, 0.145), bevel=0.014, bevel_segments=3)
    apply_all_modifiers(alcove_cut)
    boolean_diff(body, alcove_cut)
    set_smooth(body, 38.0)

    # Dark interior backing plate & removable slotted drip tray
    create_box('Alcove_Back', size=(0.21, 0.012, 0.22), location=t2b(0, 0.72, 0.095), mat=mat_dark)
    create_box('Drip_Tray', size=(0.23, 0.095, 0.024), location=t2b(0, 0.60, 0.158), bevel=0.005, mat=mat_dark)

    # Sculpted curved Hot & Cold push-paddle faucets + downward spouts!
    for fx, pmat in [(-0.052, mat_red), (0.052, mat_blue)]:
        create_cylinder(f'Spout_{fx}', radius1=0.008, radius2=0.011, depth=0.038, vertices=16,
                        location=t2b(fx, 0.78, 0.155), bevel=0.002, mat=mat_nozzle)
        paddle_pts = [t2b(fx, 0.805, 0.142), t2b(fx, 0.790, 0.175), t2b(fx, 0.748, 0.184)]
        create_curve_tube(f'Paddle_{fx}', paddle_pts, radius=0.012, radii=[0.85, 1.15, 0.90],
                          resolution_u=12, bevel_res=6, mat=pmat)

    # 3 Glowing indicator LEDs (HOT, POWER, COOL)
    for li, (lx, lhex) in enumerate([(-0.052, '#ff3b28'), (0.0, '#ffb830'), (0.052, '#38ff8c')]):
        lmat = make_pbr_mat(f'LED_{li}', color=hex_rgba(lhex), roughness=0.2, emission=hex_rgba(lhex), emission_strength=2.2)
        create_uv_sphere(f'LED_Bulb_{li}', radius=0.0065, segments=12, ring_count=8, location=t2b(lx, 0.875, 0.151), mat=lmat)

    # Conical top water-guard funnel collar
    collar_prof = [(0.045, 0.958), (0.118, 0.958), (0.106, 0.978), (0.086, 0.990), (0.068, 0.985), (0.045, 0.962)]
    create_lathe('Water_Guard_Collar', collar_prof, segments=36, mat=mat_collar, subsurf=1)

    # Smooth Subsurf Multi-Ribbed 19L Aqua Polycarbonate Gallon (Ø 26cm, H 49cm)
    galon_prof = [
        (0.028, 0.000), (0.030, 0.054), (0.045, 0.078), (0.116, 0.138), (0.130, 0.172),
        (0.123, 0.192), (0.130, 0.214), (0.130, 0.272), (0.123, 0.292), (0.130, 0.314),
        (0.130, 0.372), (0.123, 0.392), (0.130, 0.415), (0.126, 0.470), (0.110, 0.486), (0.001, 0.488),
    ]
    create_lathe('Aqua_19L_Gallon', galon_prof, segments=48, mat=mat_galon, location=t2b(0, 0.96, 0), subsurf=1)
    water_prof = [(0.024, 0.050), (0.112, 0.136), (0.120, 0.344), (0.001, 0.350)]
    create_lathe('Aqua_Inner_Water', water_prof, segments=36, mat=mat_water, location=t2b(0, 0.96, 0), subsurf=1)


# =============================================================================
# 3. MEJA KAYU + TOPLES KERUPUK WARUNG 16L + 36 KERUPUK KERITING ORGANIK
#    Origin: kitchen3d.html stoolGroup at (1.48, 0, 0.42)
# =============================================================================

def build_table_kerupuk_jar():
    clear_scene()

    mat_wood = make_pbr_mat('Table_Teak_Wood', color=hex_rgba('#9e6438'), roughness=0.60, metallic=0.02, bump_strength=0.10, bump_scale=28.0)
    mat_jar = make_pbr_mat('Jar_PET_Clear', color=hex_rgba('#eaf5ff'), roughness=0.06, coat=0.95, transmission=0.86, ior=1.48, alpha=0.38)
    mat_lid = make_pbr_mat('Jar_Red_Lid', color=hex_rgba('#c81c18'), roughness=0.20, coat=0.72, coat_roughness=0.12)
    mat_kerupuk = make_pbr_mat('Kerupuk_Putih', color=hex_rgba('#f2ead8'), roughness=0.82, bump_strength=0.16, bump_scale=90.0)

    # Chamfered Solid Teak Kitchen Table
    create_box('Table_Top', size=(0.50, 0.50, 0.038), location=t2b(0, 0.58, 0), bevel=0.007, bevel_segments=3, mat=mat_wood)
    for az in [-0.20, 0.20]:
        create_box(f'Apron_Z_{az}', size=(0.42, 0.026, 0.065), location=t2b(0, 0.53, az), bevel=0.003, mat=mat_wood)
    for ax in [-0.20, 0.20]:
        create_box(f'Apron_X_{ax}', size=(0.026, 0.42, 0.065), location=t2b(ax, 0.53, 0), bevel=0.003, mat=mat_wood)
        create_box(f'Stretcher_{ax}', size=(0.028, 0.40, 0.028), location=t2b(ax, 0.16, 0), bevel=0.003, mat=mat_wood)
    for lx, lz in [(-0.20, -0.20), (0.20, -0.20), (-0.20, 0.20), (0.20, 0.20)]:
        create_box(f'Leg_{lx}_{lz}', size=(0.044, 0.044, 0.57), location=t2b(lx, 0.285, lz), bevel=0.005, mat=mat_wood)

    # Tapered Warung 16L PET Kerupuk Jar w/ smooth molded grip ring & ribbed red screw-on lid!
    jar_y = 0.599
    jar_prof = [
        (0.001, 0.000), (0.118, 0.000), (0.122, 0.010), (0.132, 0.125),
        (0.129, 0.140), (0.135, 0.155), (0.145, 0.252), (0.141, 0.268), (0.135, 0.272),
    ]
    create_lathe('Kerupuk_Jar_Body', jar_prof, segments=44, mat=mat_jar, location=t2b(0, jar_y, 0), subsurf=1)

    lid_prof = [
        (0.146, 0.258), (0.153, 0.262), (0.153, 0.302), (0.148, 0.310),
        (0.132, 0.314), (0.125, 0.306), (0.001, 0.305),
    ]
    create_lathe('Kerupuk_Jar_Lid', lid_prof, segments=44, mat=mat_lid, location=t2b(0, jar_y, 0), subsurf=1)
    # Tactile grip ribs around the red lid rim
    for ri in range(24):
        ra = (ri / 24.0) * math.tau
        create_box(f'LidRib_{ri}', size=(0.004, 0.006, 0.036),
                   location=t2b(math.cos(ra) * 0.153, jar_y + 0.282, math.sin(ra) * 0.153),
                   rotation=(0.0, 0.0, -ra), mat=mat_lid)

    # 36 Organically ruffled curly Indonesian Kerupuk Putih packed naturally across the jar!
    rng = random.Random(333)
    # Build one master ruffled wavy kerupuk torus-rosette curve mesh and duplicate/vary it cleanly
    k_pts = []
    for i in range(48):
        u = (i / 48.0) * math.tau
        rad = 0.023 + 0.014 * math.sin(u * 5.0) + 0.005 * math.cos(u * 9.0)
        k_pts.append((math.cos(u) * rad, math.sin(u) * rad, 0.0075 * math.cos(u * 7.5)))
    master_k = create_curve_tube('Kerupuk_Master', k_pts, radius=0.0082, resolution_u=4, bevel_res=5,
                                 cyclic=True, fill_caps=False, mat=mat_kerupuk)
    master_mesh = master_k.data
    bpy.data.objects.remove(master_k, do_unlink=True)

    for ki in range(36):
        layer = ki / 36.0
        max_r = 0.080 + layer * 0.022
        ka = ki * 2.39996 + rng.random() * 0.4
        kr = math.sqrt(((ki % 7) + 0.5) / 7.0) * max_r
        k_obj = bpy.data.objects.new(f'Kerupuk_{ki}', master_mesh)
        k_obj.location = t2b(math.cos(ka) * kr, jar_y + 0.036 + layer * 0.195, math.sin(ka) * kr)
        k_obj.rotation_euler = Euler((rng.random() * 2.5, rng.random() * 3.1, rng.random() * 2.5), 'XYZ')
        sc = 0.88 + rng.random() * 0.24
        k_obj.scale = Vector((sc, sc, sc * 1.12))
        link_obj(k_obj)


# =============================================================================
# 4. BUFET KAYU + MAGIC COM RICE COOKER + THERMOS AIR PANAS
#    Origin: kitchen3d.html bufetGroup at (0.32, 0, 3.16)
# =============================================================================

def build_bufet_appliances():
    clear_scene()

    mat_wood = make_pbr_mat('Bufet_Wood', color=hex_rgba('#a2683c'), roughness=0.58, bump_strength=0.10, bump_scale=24.0)
    mat_brass = make_pbr_mat('Bufet_Brass_Pull', color=hex_rgba('#e4be64'), roughness=0.24, metallic=0.88)
    mat_mc_white = make_pbr_mat('MagicCom_White', color=hex_rgba('#f4f2ec'), roughness=0.22, coat=0.65)
    mat_mc_pink = make_pbr_mat('MagicCom_Lid_Coral', color=hex_rgba('#e64a62'), roughness=0.20, coat=0.72)
    mat_mc_dark = make_pbr_mat('MagicCom_Trim', color=hex_rgba('#242832'), roughness=0.40)
    mat_led = make_pbr_mat('MagicCom_LED', color=hex_rgba('#ffb830'), emission=hex_rgba('#ffb830'), emission_strength=2.5)
    mat_therm_red = make_pbr_mat('Thermos_Red', color=hex_rgba('#d8322c'), roughness=0.20, coat=0.70)
    mat_therm_cap = make_pbr_mat('Thermos_Cream_Cap', color=hex_rgba('#f2eee4'), roughness=0.30, coat=0.35)

    # Beveled wooden sideboard bufet w/ 3 recessed cabinet doors & brass pulls
    create_box('Bufet_Body', size=(1.38, 0.48, 0.80), location=t2b(0, 0.42, 0), bevel=0.008, bevel_segments=3, mat=mat_wood)
    create_box('Bufet_Top', size=(1.44, 0.52, 0.045), location=t2b(0, 0.84, 0), bevel=0.008, bevel_segments=3, mat=mat_wood)
    for dx in [-0.42, 0.0, 0.42]:
        create_box(f'Bufet_Door_{dx}', size=(0.38, 0.022, 0.66), location=t2b(dx, 0.42, -0.245), bevel=0.005, mat=mat_wood)
        create_uv_sphere(f'Bufet_Knob_{dx}', radius=0.013, segments=14, ring_count=10, location=t2b(dx + 0.13, 0.48, -0.262), mat=mat_brass)

    # Classic Curved Indonesian Magic Com Rice Cooker (domed lid, curved carry bail handle, steam vent!)
    mc_x = -0.34
    mc_y = 0.862
    mc_prof = [
        (0.001, 0.000), (0.132, 0.000), (0.146, 0.020), (0.148, 0.175),
        (0.144, 0.210), (0.138, 0.214),
    ]
    create_lathe('MagicCom_Body', mc_prof, segments=36, mat=mat_mc_white, location=t2b(mc_x, mc_y, 0), subsurf=1)
    lid_prof = [
        (0.144, 0.208), (0.140, 0.228), (0.118, 0.258), (0.072, 0.272), (0.001, 0.275),
    ]
    create_lathe('MagicCom_Lid', lid_prof, segments=36, mat=mat_mc_pink, location=t2b(mc_x, mc_y, 0), subsurf=1)
    # Steam vent cap + curved carry handle + front warm indicator LED
    create_cylinder('MagicCom_Vent', radius1=0.024, radius2=0.022, depth=0.016, vertices=20,
                    location=t2b(mc_x, mc_y + 0.274, 0.045), bevel=0.004, mat=mat_mc_dark)
    bail_pts = [
        t2b(mc_x - 0.146, mc_y + 0.195, 0),
        t2b(mc_x - 0.138, mc_y + 0.295, 0.03),
        t2b(mc_x, mc_y + 0.335, 0.04),
        t2b(mc_x + 0.138, mc_y + 0.295, 0.03),
        t2b(mc_x + 0.146, mc_y + 0.195, 0),
    ]
    create_curve_tube('MagicCom_Handle', bail_pts, radius=0.0075, resolution_u=18, bevel_res=8, mat=mat_mc_white)
    create_uv_sphere('MagicCom_LED', radius=0.010, segments=12, ring_count=8, location=t2b(mc_x, mc_y + 0.095, -0.148), mat=mat_led)

    # Classic Curved Vintage Red Thermos Air Panas w/ curved side handle & domed cup cap!
    th_x, th_z = 0.26, 0.02
    th_prof = [
        (0.001, 0.000), (0.072, 0.000), (0.076, 0.022), (0.074, 0.245),
        (0.068, 0.285), (0.056, 0.305),
    ]
    create_lathe('Thermos_Body', th_prof, segments=32, mat=mat_therm_red, location=t2b(th_x, mc_y, th_z), subsurf=1)
    cap_prof = [
        (0.069, 0.288), (0.068, 0.335), (0.060, 0.372), (0.044, 0.382), (0.001, 0.384),
    ]
    create_lathe('Thermos_Cap', cap_prof, segments=32, mat=mat_therm_cap, location=t2b(th_x, mc_y, th_z), subsurf=1)
    th_hdl = [
        t2b(th_x + 0.072, mc_y + 0.255, th_z),
        t2b(th_x + 0.118, mc_y + 0.245, th_z),
        t2b(th_x + 0.120, mc_y + 0.135, th_z),
        t2b(th_x + 0.074, mc_y + 0.105, th_z),
    ]
    create_curve_tube('Thermos_Handle', th_hdl, radius=0.0085, resolution_u=16, bevel_res=8, mat=mat_therm_cap)


# =============================================================================
# 5. RAK DINDING KANAN + KALENG BISKUIT + MANGKUK + TEKO BLIRIK + POT SIRIH GADING
#    Origin: kitchen3d.html rShelfGroup at (1.74, 1.72, 0.18)
# =============================================================================

def build_wall_shelf_props():
    clear_scene()

    mat_wood = make_pbr_mat('Shelf_Wood', color=hex_rgba('#a66c3e'), roughness=0.60)
    mat_iron = make_pbr_mat('Shelf_Iron', color=hex_rgba('#1b2028'), roughness=0.38, metallic=0.80)
    mat_tin = make_pbr_mat('KhongGuan_Red_Tin', color=hex_rgba('#d82822'), roughness=0.24, metallic=0.34, coat=0.58)
    mat_tin_gold = make_pbr_mat('KhongGuan_Gold_Trim', color=hex_rgba('#e6be58'), roughness=0.22, metallic=0.82)
    mat_teko = make_pbr_mat('Teko_Green_Enamel', color=hex_rgba('#288858'), roughness=0.20, coat=0.72)
    mat_pot = make_pbr_mat('Terracotta_Pot', color=hex_rgba('#c8643c'), roughness=0.78, bump_strength=0.12, bump_scale=55.0)
    mat_soil = make_pbr_mat('Potting_Soil', color=hex_rgba('#2e2018'), roughness=0.95)
    mat_leaf = make_pbr_mat('Sirih_Gading_Leaf', color=hex_rgba('#42a648'), roughness=0.45, coat=0.25, double_sided=True)

    # Beveled floating wooden shelf + curved L-brackets
    create_box('Shelf_Board', size=(0.24, 1.32, 0.036), location=t2b(0, 0, 0), bevel=0.005, mat=mat_wood)
    for bz in [-0.46, 0.46]:
        br_pts = [t2b(0.10, -0.13, bz), t2b(0.08, -0.025, bz), t2b(-0.08, -0.022, bz)]
        create_curve_tube(f'Bracket_{bz}', br_pts, radius=0.011, resolution_u=12, bevel_res=6, mat=mat_iron)

    # Iconic Beveled Indonesian Red Square Biscuit Tin (Kaleng Khong Guan!) w/ stepped gold-trimmed lid
    tin = create_box('Biscuit_Tin_Body', size=(0.17, 0.17, 0.19), location=t2b(0, 0.114, -0.34),
                     rotation=(0.0, 0.0, 0.14), bevel=0.012, bevel_segments=4, mat=mat_tin)
    create_box('Biscuit_Tin_Lid', size=(0.176, 0.176, 0.026), location=t2b(0, 0.214, -0.34),
               rotation=(0.0, 0.0, 0.14), bevel=0.008, bevel_segments=3, mat=mat_tin_gold)

    # 3 Smooth Subsurf Stacked Ceramic Bowls
    bowl_prof = [
        (0.001, 0.000), (0.038, 0.000), (0.046, 0.008), (0.068, 0.032),
        (0.075, 0.048), (0.071, 0.050), (0.062, 0.032), (0.038, 0.008), (0.001, 0.007),
    ]
    for bi, bhex in enumerate(['#f2b838', '#4ca8b8', '#e8685a']):
        bmat = make_pbr_mat(f'Bowl_{bi}', color=hex_rgba(bhex), roughness=0.16, coat=0.78)
        create_lathe(f'Ceramic_Bowl_{bi}', bowl_prof, segments=32, mat=bmat,
                     location=t2b(0, 0.018 + bi * 0.028, 0.02), subsurf=1)

    # Classic Curved Indonesian Enamel Kettle (Teko Blirik!) w/ S-Curved Gooseneck Spout & Arched Bail Handle!
    tz = 0.26
    teko_prof = [
        (0.001, 0.000), (0.070, 0.000), (0.078, 0.016), (0.074, 0.088),
        (0.058, 0.145), (0.062, 0.152), (0.052, 0.154), (0.048, 0.168), (0.024, 0.178), (0.001, 0.180),
    ]
    create_lathe('Teko_Body', teko_prof, segments=36, mat=mat_teko, location=t2b(0, 0.018, tz), subsurf=1)
    create_uv_sphere('Teko_Finial', radius=0.011, segments=14, ring_count=10, location=t2b(0, 0.205, tz), mat=mat_teko)
    # S-curved pouring spout facing kitchen (-X in Three.js)
    spout_pts = [t2b(-0.068, 0.068, tz), t2b(-0.105, 0.095, tz), t2b(-0.118, 0.148, tz), t2b(-0.132, 0.172, tz)]
    create_curve_tube('Teko_Spout', spout_pts, radius=0.011, radii=[1.25, 1.0, 0.78, 0.65],
                      resolution_u=16, bevel_res=8, mat=mat_teko)
    # Arched wire bail handle over kettle top
    bail_pts = [
        t2b(0, 0.148, tz - 0.060), t2b(0, 0.228, tz - 0.052),
        t2b(0, 0.258, tz), t2b(0, 0.228, tz + 0.052), t2b(0, 0.148, tz + 0.060),
    ]
    create_curve_tube('Teko_BailHandle', bail_pts, radius=0.0045, resolution_u=18, bevel_res=6, mat=mat_iron)

    # Terracotta Pot w/ Rolled Rim + Curved Trailing Sirih Gading Vines & Sculpted Heart-Shaped Leaves!
    pz = 0.50
    pot_prof = [
        (0.001, 0.000), (0.042, 0.000), (0.056, 0.082), (0.063, 0.086),
        (0.063, 0.100), (0.054, 0.100), (0.050, 0.084), (0.001, 0.084),
    ]
    create_lathe('Terracotta_Pot', pot_prof, segments=28, mat=mat_pot, location=t2b(0, 0.018, pz), subsurf=1)
    create_cylinder('Pot_Soil', radius1=0.052, radius2=0.052, depth=0.010, vertices=24, location=t2b(0, 0.100, pz), mat=mat_soil)

    # Curved trailing vines + arched heart-shaped leaves
    for li in range(8):
        la = (li / 8.0) * math.tau + 0.25
        ca, sa = math.cos(la), math.sin(la)
        droop = 0.065 if ca < 0 else 0.025  # trail gracefully off the front edge of the shelf!
        vine_pts = [
            t2b(ca * 0.015, 0.105, pz + sa * 0.015),
            t2b(ca * 0.058, 0.142, pz + sa * 0.058),
            t2b(ca * 0.098, 0.132 - droop * 0.5, pz + sa * 0.098),
            t2b(ca * 0.118, 0.112 - droop, pz + sa * 0.118),
        ]
        create_curve_tube(f'Vine_{li}', vine_pts, radius=0.0024, resolution_u=10, bevel_res=5, mat=mat_leaf)
        leaf = create_uv_sphere(f'Leaf_{li}', radius=0.028, segments=14, ring_count=10,
                                scale=(1.25, 0.82, 0.14),
                                location=vine_pts[-1],
                                rotation=(0.35 * sa, -0.45 * ca, -la), mat=mat_leaf)


# =============================================================================
# 6. CICAK DI DINDING (ORGANIC SCULPTED INDONESIAN HOUSE GECKO!)
#    Origin: kitchen3d.html cicakGroup (local +Y up along wall, +Z out of wall)
# =============================================================================

def build_cicak():
    clear_scene()

    mat_skin = make_pbr_mat('Cicak_Translucent_Skin', color=hex_rgba('#e2d2b5'), roughness=0.42, coat=0.35, coat_roughness=0.38)
    mat_eye = make_pbr_mat('Cicak_Glossy_Eye', color=hex_rgba('#0e0f14'), roughness=0.06, coat=1.0)

    # Organic curved gecko spine + torso + head + smoothly tapering S-curved tail (all smooth NURBS tubes!)
    body_pts = [
        t2b(0.0, 0.056, 0.005),   # rounded snout tip
        t2b(0.0, 0.044, 0.006),   # skull / brow
        t2b(0.0, 0.030, 0.0045),  # slender neck
        t2b(0.0, 0.014, 0.0055),  # chest
        t2b(0.0, -0.004, 0.0055), # belly
        t2b(0.0, -0.022, 0.0045), # pelvis
        t2b(0.003, -0.042, 0.0035),
        t2b(-0.005, -0.068, 0.0028),
        t2b(0.004, -0.094, 0.0020), # graceful S-curved tail tip!
    ]
    body_radii = [0.55, 1.08, 0.72, 1.05, 1.12, 0.80, 0.60, 0.36, 0.12]
    body = create_curve_tube('Cicak_BodyTail', body_pts, radius=0.0115, radii=body_radii,
                             resolution_u=24, bevel_res=10, mat=mat_skin)
    # Flatten gecko cleanly against the wall (Blender Y = Three.js -Z depth!)
    body.scale = Vector((1.0, 0.48, 1.0))

    # Glossy black bulging gecko eyes
    for sx in [-1.0, 1.0]:
        create_uv_sphere(f'Cicak_Eye_{sx}', radius=0.0032, segments=12, ring_count=8,
                         location=t2b(sx * 0.0085, 0.048, 0.0095), mat=mat_eye)

    # 4 Articulated curved gecko legs + fanned adhesive 3-toe gecko pads!
    for idx, (sx, ly, is_front) in enumerate([(-1, 0.020, True), (1, 0.020, True), (-1, -0.018, False), (1, -0.018, False)]):
        knee_x = sx * 0.018
        knee_y = ly + (0.004 if is_front else -0.005)
        foot_x = sx * 0.023
        foot_y = ly + (0.014 if is_front else 0.004)
        leg_pts = [
            t2b(sx * 0.008, ly, 0.004),
            t2b(knee_x, knee_y, 0.0055),
            t2b(foot_x, foot_y, 0.0025),
        ]
        create_curve_tube(f'Cicak_Leg_{idx}', leg_pts, radius=0.0026, radii=[1.05, 0.90, 0.85],
                          resolution_u=10, bevel_res=6, mat=mat_skin)
        # 3 Splayed adhesive toes
        for ti, ta in enumerate([-0.55, 0.0, 0.55]):
            ang = ta + sx * 0.25
            toe_pts = [
                t2b(foot_x, foot_y, 0.0022),
                t2b(foot_x + math.sin(ang) * 0.0065, foot_y + math.cos(ang) * 0.0065, 0.0018),
            ]
            create_curve_tube(f'Cicak_Toe_{idx}_{ti}', toe_pts, radius=0.0011, radii=[0.8, 1.15],
                              resolution_u=6, bevel_res=4, mat=mat_skin)


# =============================================================================
# 7. LAMPU GANTUNG ENAMEL HIJAU KLASIK (OFF AT 02:00 WIB)
#    Origin: (-0.08, 2.54, -0.45) in kitchen3d.html
# =============================================================================

def build_ceiling_lamp():
    clear_scene()

    mat_cord = make_pbr_mat('Lamp_Cord', color=hex_rgba('#1a1d24'), roughness=0.60, metallic=0.25)
    mat_enamel = make_pbr_mat('Lamp_Green_Enamel', color=hex_rgba('#286a54'), roughness=0.24, coat=0.72, double_sided=True)
    mat_white = make_pbr_mat('Lamp_White_Inner', color=hex_rgba('#eef2f6'), roughness=0.28, coat=0.45, double_sided=True)
    mat_brass = make_pbr_mat('Lamp_Brass_Socket', color=hex_rgba('#d8b054'), roughness=0.28, metallic=0.88)
    mat_bulb = make_pbr_mat('Lamp_Glass_Bulb', color=hex_rgba('#eef4fa'), roughness=0.08, transmission=0.72, alpha=0.62, coat=0.90)

    # Ceiling rose canopy + braided cord
    rose_prof = [(0.001, 0.46), (0.055, 0.46), (0.052, 0.44), (0.018, 0.42), (0.009, 0.41)]
    create_lathe('Lamp_CeilingRose', rose_prof, segments=28, mat=mat_cord, subsurf=1)
    create_cylinder('Lamp_Cord', radius1=0.006, radius2=0.006, depth=0.38, vertices=12, location=t2b(0, 0.25, 0), mat=mat_cord)
    create_cylinder('Lamp_Socket', radius1=0.022, radius2=0.018, depth=0.048, vertices=24, location=t2b(0, 0.068, 0), bevel=0.003, mat=mat_brass)

    # Classic Indonesian bell-curved flared enamel shade w/ rolled lip!
    shade_prof = [
        (0.022, 0.068), (0.042, 0.058), (0.110, 0.036), (0.195, 0.002),
        (0.242, -0.028), (0.246, -0.034), (0.238, -0.036), (0.232, -0.028),
    ]
    create_lathe('Lamp_EnamelShade', shade_prof, segments=48, mat=mat_enamel, subsurf=1)
    inner_prof = [(0.022, 0.062), (0.105, 0.032), (0.190, -0.002), (0.234, -0.030)]
    create_lathe('Lamp_WhiteReflector', inner_prof, segments=40, mat=mat_white, subsurf=1)

    # Classic pear-shaped incandescent glass bulb (A60 profile)
    bulb_prof = [
        (0.001, -0.095), (0.022, -0.092), (0.036, -0.075), (0.040, -0.054),
        (0.032, -0.030), (0.018, -0.008), (0.015, 0.014),
    ]
    create_lathe('Lamp_GlassBulb', bulb_prof, segments=28, mat=mat_bulb, subsurf=1)


# =============================================================================
# 8. SAPU IJUK INDONESIA (CLASSIC FAN-SHAPED PALM FIBER BROOM)
#    Origin: kitchen3d.html broomGroup at (1.66, 0, 1.32)
# =============================================================================

def build_broom_sapu():
    clear_scene()

    mat_wood = make_pbr_mat('Broom_Wood_Pole', color=hex_rgba('#b07444'), roughness=0.58)
    mat_red = make_pbr_mat('Broom_Red_Cap', color=hex_rgba('#d83830'), roughness=0.34, coat=0.35)
    mat_ijuk = make_pbr_mat('Broom_Ijuk_Fibers', color=hex_rgba('#1e1a18'), roughness=0.94, bump_strength=0.25, bump_scale=120.0)

    # Smooth tapered wooden handle w/ rounded end grip
    pole_prof = [(0.001, 0.22), (0.013, 0.22), (0.013, 1.18), (0.012, 1.21), (0.006, 1.225), (0.001, 1.228)]
    create_lathe('Broom_Handle', pole_prof, segments=20, mat=mat_wood)

    # Sculpted curved red molded plastic collar cap
    cap = create_box('Broom_RedCap', size=(0.044, 0.20, 0.065), location=t2b(0, 0.215, 0),
                     bevel=0.014, bevel_segments=3, mat=mat_red)

    # Flared fan-shaped woven palm-fiber bristles (swept organic curves!)
    for bi in range(11):
        u = (bi / 10.0) - 0.5  # -0.5 .. +0.5
        z_top = u * 0.17
        z_bot = u * 0.26
        f_pts = [
            t2b(0.0, 0.205, z_top),
            t2b(0.004 * math.sin(bi * 2.1), 0.105, (z_top + z_bot) * 0.5),
            t2b(-0.005 * math.cos(bi * 1.7), 0.004, z_bot),
        ]
        create_curve_tube(f'Ijuk_Tuft_{bi}', f_pts, radius=0.016, radii=[0.95, 1.10, 0.72],
                          resolution_u=8, bevel_res=6, mat=mat_ijuk)
