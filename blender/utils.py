"""
Blender 3.6 / 4.x shared procedural geometry, material, texture & glTF export utilities
for the Indonesian Kitchen 3D Studio (Misi 02:00 WIB) prop pipeline.

Run via:
    blender --background --factory-startup --python blender/build_all.py
"""

import math
import os
import random
import bpy
import bmesh
from mathutils import Vector, Euler, Matrix


# =============================================================================
# 1. SCENE & VERSION COMPATIBILITY HELPERS
# =============================================================================

def clear_scene():
    """Reset the active Blender scene to an empty state."""
    bpy.ops.wm.read_factory_settings(use_empty=True)


def set_smooth(obj, angle_deg=38.0):
    """Apply smooth shading safely on both Blender 3.6 and Blender 4.1+."""
    if obj.type != 'MESH' or not obj.data:
        return
    mesh = obj.data
    n_polys = len(mesh.polygons)
    if n_polys > 0:
        mesh.polygons.foreach_set('use_smooth', [True] * n_polys)
    # Blender 3.x had mesh.use_auto_smooth; Blender 4.1+ removed it in favor of Smooth by Angle / sharp edges.
    if hasattr(mesh, 'use_auto_smooth'):
        mesh.use_auto_smooth = True
        mesh.auto_smooth_angle = math.radians(angle_deg)
    mesh.update()


def set_flat(obj):
    if obj.type != 'MESH' or not obj.data:
        return
    mesh = obj.data
    n_polys = len(mesh.polygons)
    if n_polys > 0:
        mesh.polygons.foreach_set('use_smooth', [False] * n_polys)
    mesh.update()


def add_subsurf(obj, levels=2, render_levels=2, simple=False):
    mod = obj.modifiers.new(name='Subsurf', type='SUBSURF')
    mod.levels = levels
    mod.render_levels = render_levels
    if simple:
        mod.subdivision_type = 'SIMPLE'
    return mod


def add_bevel(obj, width=0.004, segments=3, limit_angle_deg=30.0):
    mod = obj.modifiers.new(name='Bevel', type='BEVEL')
    mod.width = width
    mod.segments = segments
    mod.limit_method = 'ANGLE'
    mod.angle_limit = math.radians(limit_angle_deg)
    mod.harden_normals = False
    return mod


def add_solidify(obj, thickness=0.004, offset=0.0):
    mod = obj.modifiers.new(name='Solidify', type='SOLIDIFY')
    mod.thickness = thickness
    mod.offset = offset
    return mod


def boolean_diff(target_obj, cutter_obj, solver='EXACT'):
    """Apply a Boolean difference modifier cleanly and delete the cutter."""
    bpy.context.view_layer.update()
    mod = target_obj.modifiers.new(name='BoolDiff', type='BOOLEAN')
    mod.operation = 'DIFFERENCE'
    mod.object = cutter_obj
    if hasattr(mod, 'solver'):
        try:
            mod.solver = solver
        except Exception:
            pass
    bpy.context.view_layer.objects.active = target_obj
    bpy.ops.object.select_all(action='DESELECT')
    target_obj.select_set(True)
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(cutter_obj, do_unlink=True)


def apply_all_modifiers(obj):
    if obj.type != 'MESH' or not obj.modifiers:
        return
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    for mod in list(obj.modifiers):
        try:
            bpy.ops.object.modifier_apply(modifier=mod.name)
        except Exception:
            pass


def link_obj(obj, parent=None):
    if obj.name not in bpy.context.scene.collection.objects:
        bpy.context.scene.collection.objects.link(obj)
    if parent is not None:
        obj.parent = parent
    return obj


def make_empty(name, location=(0.0, 0.0, 0.0), parent=None):
    empty = bpy.data.objects.new(name, None)
    empty.location = Vector(location)
    return link_obj(empty, parent)


# =============================================================================
# 2. PBR PRINCIPLED BSDF MATERIAL BUILDER (BLENDER 3.6 + 4.x SAFE)
# =============================================================================

def _set_bsdf_input(bsdf, names, value):
    for n in names:
        if n in bsdf.inputs:
            bsdf.inputs[n].default_value = value
            return True
    return False


def make_pbr_mat(
    name,
    color=(0.8, 0.8, 0.8, 1.0),
    roughness=0.45,
    metallic=0.0,
    coat=0.0,
    coat_roughness=0.15,
    transmission=0.0,
    ior=1.45,
    alpha=1.0,
    emission=None,
    emission_strength=0.0,
    double_sided=False,
    image=None,
    bump_strength=0.0,
    bump_scale=18.0,
):
    """Create a glTF-compatible Principled BSDF material."""
    if len(color) == 3:
        color = (color[0], color[1], color[2], 1.0)

    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    mat.use_backface_culling = not double_sided

    nt = mat.node_tree
    nt.nodes.clear()

    out = nt.nodes.new('ShaderNodeOutputMaterial')
    out.location = (420, 0)

    bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (80, 0)
    nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])

    _set_bsdf_input(bsdf, ['Base Color'], color)
    _set_bsdf_input(bsdf, ['Metallic'], metallic)
    _set_bsdf_input(bsdf, ['Roughness'], roughness)
    _set_bsdf_input(bsdf, ['IOR'], ior)
    _set_bsdf_input(bsdf, ['Alpha'], alpha)

    if coat > 0.0:
        _set_bsdf_input(bsdf, ['Coat Weight', 'Clearcoat'], coat)
        _set_bsdf_input(bsdf, ['Coat Roughness', 'Clearcoat Roughness'], coat_roughness)

    if transmission > 0.0:
        _set_bsdf_input(bsdf, ['Transmission Weight', 'Transmission'], transmission)

    if emission is not None and emission_strength > 0.0:
        em = emission if len(emission) == 4 else (emission[0], emission[1], emission[2], 1.0)
        _set_bsdf_input(bsdf, ['Emission Color', 'Emission'], em)
        _set_bsdf_input(bsdf, ['Emission Strength'], emission_strength)

    if alpha < 0.999 or transmission > 0.05:
        if hasattr(mat, 'blend_method'):
            mat.blend_method = 'BLEND'

    if image is not None:
        tex_node = nt.nodes.new('ShaderNodeTexImage')
        tex_node.location = (-260, 120)
        tex_node.image = image
        nt.links.new(tex_node.outputs['Color'], bsdf.inputs['Base Color'])

    if bump_strength > 0.0:
        noise = nt.nodes.new('ShaderNodeTexNoise')
        noise.location = (-460, -180)
        noise.inputs['Scale'].default_value = bump_scale
        noise.inputs['Detail'].default_value = 6.0
        bump = nt.nodes.new('ShaderNodeBump')
        bump.location = (-180, -180)
        bump.inputs['Strength'].default_value = bump_strength
        bump.inputs['Distance'].default_value = 0.004
        nt.links.new(noise.outputs['Fac'], bump.inputs['Height'])
        nt.links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

    return mat


def hex_rgba(hex_str, alpha=1.0):
    """Convert '#rrggbb' to linear RGB tuple for Blender Principled BSDF."""
    s = hex_str.lstrip('#')
    r = int(s[0:2], 16) / 255.0
    g = int(s[2:4], 16) / 255.0
    b = int(s[4:6], 16) / 255.0

    def srgb_to_lin(c):
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    return (srgb_to_lin(r), srgb_to_lin(g), srgb_to_lin(b), alpha)


def assign_mat(obj, mat):
    if obj.type != 'MESH' or not obj.data:
        return
    if len(obj.data.materials) == 0:
        obj.data.materials.append(mat)
    else:
        obj.data.materials[0] = mat


# =============================================================================
# 3. COORDINATE MAPPING (THREE.JS Y-UP <-> BLENDER Z-UP)
# =============================================================================
# Important: Blender's glTF exporter with export_yup=True maps:
#   Blender (X, Y, Z)  --->  glTF / Three.js (X, Z, -Y)
# Therefore, to place something at Three.js local coordinates (tx, ty, tz),
# we place it in Blender at:
#   Blender (tx, -tz, ty)
# Notice that +Z in Blender is UP (which becomes +Y UP in Three.js!).
# And -Y in Blender becomes +Z (front) in Three.js!

def t2b(tx, ty, tz):
    """Convert Three.js local (X, Y_up, Z_front) to Blender (X, Y_back, Z_up)."""
    return Vector((tx, -tz, ty))


# =============================================================================
# 4. PROCEDURAL CURVED MESH PRIMITIVES (LATHE, BEZIER TUBE, BOX, CYLINDER)
# =============================================================================

def create_lathe(
    name,
    profile_rz,
    segments=48,
    mat=None,
    location=(0.0, 0.0, 0.0),
    parent=None,
    cap_bottom=False,
    cap_top=False,
    smooth_angle=42.0,
    subsurf=0,
):
    """
    Revolve a list of (radius, z_height) pairs around Blender's +Z axis (Three.js +Y up).
    Automatically creates cylindrical UVs so textures wrap cleanly without pinching!
    """
    bm = bmesh.new()
    rings = []
    min_z = min(z for _, z in profile_rz)
    max_z = max(z for _, z in profile_rz)
    z_span = max(1e-6, max_z - min_z)

    for r, z in profile_rz:
        ring = []
        r_safe = max(0.0002, r)
        for s in range(segments):
            ang = (s / segments) * math.tau
            v = bm.verts.new((math.cos(ang) * r_safe, math.sin(ang) * r_safe, z))
            ring.append(v)
        rings.append((ring, (z - min_z) / z_span))

    uv_layer = bm.loops.layers.uv.new('UVMap')

    for ri in range(len(rings) - 1):
        r0, v0 = rings[ri]
        r1, v1 = rings[ri + 1]
        for s in range(segments):
            sn = (s + 1) % segments
            u0 = s / segments
            u1 = (s + 1) / segments
            try:
                f = bm.faces.new((r0[s], r0[sn], r1[sn], r1[s]))
                uvs = [(u0, v0), (u1, v0), (u1, v1), (u0, v1)]
                for loop, uv in zip(f.loops, uvs):
                    loop[uv_layer].uv = uv
            except ValueError:
                pass

    if cap_bottom and len(rings) > 0:
        try:
            bm.faces.new(list(reversed(rings[0][0])))
        except ValueError:
            pass
    if cap_top and len(rings) > 0:
        try:
            bm.faces.new(list(rings[-1][0]))
        except ValueError:
            pass

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(name, mesh)
    obj.location = Vector(location)
    link_obj(obj, parent)
    if mat:
        assign_mat(obj, mat)
    if subsurf > 0:
        add_subsurf(obj, levels=subsurf, render_levels=subsurf)
    set_smooth(obj, smooth_angle)
    return obj


def create_curve_tube(
    name,
    points_blender,
    radius=0.008,
    radii=None,
    resolution_u=16,
    bevel_res=8,
    cyclic=False,
    fill_caps=True,
    mat=None,
    parent=None,
    location=(0.0, 0.0, 0.0),
):
    """Create a smooth NURBS/Catmull curve mesh tube with optional per-point radius taper."""
    curve_data = bpy.data.curves.new(name=f'{name}_Curve', type='CURVE')
    curve_data.dimensions = '3D'
    curve_data.resolution_u = resolution_u
    curve_data.bevel_depth = radius
    curve_data.bevel_resolution = bevel_res
    curve_data.use_fill_caps = fill_caps

    spline = curve_data.splines.new('NURBS')
    spline.points.add(len(points_blender) - 1)
    for idx, pt in enumerate(points_blender):
        spline.points[idx].co = (pt[0], pt[1], pt[2], 1.0)
        if radii is not None and idx < len(radii):
            spline.points[idx].radius = radii[idx]
    spline.use_cyclic_u = cyclic
    spline.use_endpoint_u = not cyclic
    spline.order_u = min(4, len(points_blender))

    curve_obj = bpy.data.objects.new(name, curve_data)
    curve_obj.location = Vector(location)
    link_obj(curve_obj, parent)

    bpy.context.view_layer.update()
    bpy.context.view_layer.objects.active = curve_obj
    bpy.ops.object.select_all(action='DESELECT')
    curve_obj.select_set(True)
    bpy.ops.object.convert(target='MESH')
    mesh_obj = bpy.context.active_object
    mesh_obj.name = name

    if mat:
        assign_mat(mesh_obj, mat)
    set_smooth(mesh_obj, 50.0)
    return mesh_obj


def create_box(
    name,
    size=(0.1, 0.1, 0.1),
    location=(0.0, 0.0, 0.0),
    rotation=(0.0, 0.0, 0.0),
    bevel=0.0,
    bevel_segments=3,
    mat=None,
    parent=None,
):
    """Create a box of exact (sx, sy, sz) dimensions in Blender space with optional bevel."""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= size[0]
        v.co.y *= size[1]
        v.co.z *= size[2]

    # Box-projected UVs
    uv_layer = bm.loops.layers.uv.new('UVMap')
    for f in bm.faces:
        n = f.normal
        for loop in f.loops:
            co = loop.vert.co
            if abs(n.x) >= abs(n.y) and abs(n.x) >= abs(n.z):
                u = (co.y / max(1e-5, size[1])) + 0.5
                v = (co.z / max(1e-5, size[2])) + 0.5
            elif abs(n.y) >= abs(n.x) and abs(n.y) >= abs(n.z):
                u = (co.x / max(1e-5, size[0])) + 0.5
                v = (co.z / max(1e-5, size[2])) + 0.5
            else:
                u = (co.x / max(1e-5, size[0])) + 0.5
                v = (co.y / max(1e-5, size[1])) + 0.5
            loop[uv_layer].uv = (u, v)

    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(name, mesh)
    obj.location = Vector(location)
    obj.rotation_euler = Euler(rotation, 'XYZ')
    link_obj(obj, parent)
    if mat:
        assign_mat(obj, mat)
    if bevel > 0.0:
        add_bevel(obj, width=bevel, segments=bevel_segments)
        set_smooth(obj, 35.0)
    else:
        set_flat(obj)
    return obj


def create_cylinder(
    name,
    radius1=0.05,
    radius2=None,
    depth=0.1,
    vertices=32,
    location=(0.0, 0.0, 0.0),
    rotation=(0.0, 0.0, 0.0),
    bevel=0.0,
    cap_ends=True,
    mat=None,
    parent=None,
):
    if radius2 is None:
        radius2 = radius1
    bm = bmesh.new()
    bmesh.ops.create_cone(
        bm,
        cap_ends=cap_ends,
        cap_tris=False,
        segments=vertices,
        radius1=radius1,
        radius2=radius2,
        depth=depth,
    )
    uv_layer = bm.loops.layers.uv.new('UVMap')
    for f in bm.faces:
        for loop in f.loops:
            co = loop.vert.co
            u = (math.atan2(co.y, co.x) / math.tau) + 0.5
            v = (co.z / max(1e-5, depth)) + 0.5
            loop[uv_layer].uv = (u, v)

    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(name, mesh)
    obj.location = Vector(location)
    obj.rotation_euler = Euler(rotation, 'XYZ')
    link_obj(obj, parent)
    if mat:
        assign_mat(obj, mat)
    if bevel > 0.0:
        add_bevel(obj, width=bevel, segments=2)
    set_smooth(obj, 38.0)
    return obj


def create_torus(
    name,
    major_radius=0.1,
    minor_radius=0.01,
    major_seg=48,
    minor_seg=16,
    location=(0.0, 0.0, 0.0),
    rotation=(0.0, 0.0, 0.0),
    mat=None,
    parent=None,
):
    bm = bmesh.new()
    rings = []
    for i in range(major_seg):
        theta = (i / major_seg) * math.tau
        ct, st = math.cos(theta), math.sin(theta)
        ring = []
        for j in range(minor_seg):
            phi = (j / minor_seg) * math.tau
            cp, sp = math.cos(phi), math.sin(phi)
            r = major_radius + minor_radius * cp
            ring.append(bm.verts.new((r * ct, r * st, minor_radius * sp)))
        rings.append(ring)

    for i in range(major_seg):
        inext = (i + 1) % major_seg
        for j in range(minor_seg):
            jnext = (j + 1) % minor_seg
            bm.faces.new((rings[i][j], rings[inext][j], rings[inext][jnext], rings[i][jnext]))

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(name, mesh)
    obj.location = Vector(location)
    obj.rotation_euler = Euler(rotation, 'XYZ')
    link_obj(obj, parent)
    if mat:
        assign_mat(obj, mat)
    set_smooth(obj, 60.0)
    return obj


def create_uv_sphere(
    name,
    radius=0.05,
    segments=24,
    ring_count=16,
    scale=(1.0, 1.0, 1.0),
    location=(0.0, 0.0, 0.0),
    rotation=(0.0, 0.0, 0.0),
    mat=None,
    parent=None,
):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=segments, v_segments=ring_count, radius=radius)
    for v in bm.verts:
        v.co.x *= scale[0]
        v.co.y *= scale[1]
        v.co.z *= scale[2]
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(name, mesh)
    obj.location = Vector(location)
    obj.rotation_euler = Euler(rotation, 'XYZ')
    link_obj(obj, parent)
    if mat:
        assign_mat(obj, mat)
    set_smooth(obj, 60.0)
    return obj


# =============================================================================
# 5. PURE-PYTHON PROCEDURAL TEXTURE GENERATORS (NO PIL REQUIRED)
# =============================================================================

def make_plaid_image(name, base_hex, stripe1_hex, stripe2_hex, size=256):
    """Generate a crisp Indonesian bolster gingham/plaid cloth texture packed into Blender."""
    img = bpy.data.images.new(name, width=size, height=size, alpha=False)

    def parse(h):
        h = h.lstrip('#')
        return (int(h[0:2], 16) / 255.0, int(h[2:4], 16) / 255.0, int(h[4:6], 16) / 255.0)

    c_base = parse(base_hex)
    c1 = parse(stripe1_hex)
    c2 = parse(stripe2_hex)
    rng = random.Random(hash(name) & 0xFFFFFFFF)

    pixels = [0.0] * (size * size * 4)
    cell = size // 8
    idx = 0
    for y in range(size):
        cy = y % cell
        wy = (y % 4 == 0)
        for x in range(size):
            cx = x % cell
            wx = (x % 4 == 0)
            r, g, b = c_base
            # Primary plaid bands
            if cx < cell * 0.28:
                r = r * 0.35 + c1[0] * 0.65
                g = g * 0.35 + c1[1] * 0.65
                b = b * 0.35 + c1[2] * 0.65
            if cy < cell * 0.28:
                r = r * 0.45 + c1[0] * 0.55
                g = g * 0.45 + c1[1] * 0.55
                b = b * 0.45 + c1[2] * 0.55
            # Secondary accent pinstripe
            if abs(cx - cell * 0.62) < 2.2 or abs(cy - cell * 0.62) < 2.2:
                r = r * 0.25 + c2[0] * 0.75
                g = g * 0.25 + c2[1] * 0.75
                b = b * 0.25 + c2[2] * 0.75
            # Fine woven cotton thread grain
            weave = 0.96 if (wx ^ wy) else 1.03
            grain = (rng.random() - 0.5) * 0.03
            pixels[idx] = max(0.0, min(1.0, r * weave + grain))
            pixels[idx + 1] = max(0.0, min(1.0, g * weave + grain))
            pixels[idx + 2] = max(0.0, min(1.0, b * weave + grain))
            pixels[idx + 3] = 1.0
            idx += 4

    img.pixels.foreach_set(pixels)
    img.pack()
    return img


def make_lpg_stencil_image(name='LPG3kg_Tex', w=512, h=256):
    """Generate authentic Pertamina LPG 3kg Melon powder-coated green texture w/ red shoulder band & dark stencil stripe."""
    img = bpy.data.images.new(name, width=w, height=h, alpha=False)
    rng = random.Random(1452)
    pixels = [0.0] * (w * h * 4)
    idx = 0
    for y in range(h):
        v = y / float(h - 1)  # 0 = foot, 1 = neck
        for x in range(w):
            u = x / float(w - 1)
            # Authentic Pertamina Melon Green (#6ca947)
            r, g, b = 0.42, 0.66, 0.27
            # Slight darker underside grime near foot ring
            if v < 0.14:
                d = 0.62 + (v / 0.14) * 0.38
                r *= d; g *= d; b *= d
            # Iconic Red safety warning ring on upper shoulder (v ≈ 0.80..0.85)
            if 0.79 <= v <= 0.84:
                r, g, b = 0.76, 0.13, 0.10
            # Dark horizontal stencil band around mid belly (v ≈ 0.44..0.58) on kitchen-facing side
            if 0.46 <= v <= 0.56 and 0.28 <= u <= 0.72:
                # Subtle simulated lettering bars
                if (0.525 <= v <= 0.552 and int(u * 90) % 3 != 0) or (0.470 <= v <= 0.495 and int(u * 130) % 2 == 0):
                    r, g, b = 0.10, 0.13, 0.08
            # Subtle brushed powder-coat micro-speckle
            n = (rng.random() - 0.5) * 0.025
            pixels[idx] = max(0.0, min(1.0, r + n))
            pixels[idx + 1] = max(0.0, min(1.0, g + n))
            pixels[idx + 2] = max(0.0, min(1.0, b + n))
            pixels[idx + 3] = 1.0
            idx += 4

    img.pixels.foreach_set(pixels)
    img.pack()
    return img


def make_bottle_label_image(name, bg_hex, stripe_hex, w=256, h=128):
    """Generate colorful Indonesian kitchen condiment bottle label texture."""
    img = bpy.data.images.new(name, width=w, height=h, alpha=False)

    def parse(hx):
        hx = hx.lstrip('#')
        return (int(hx[0:2], 16) / 255.0, int(hx[2:4], 16) / 255.0, int(hx[4:6], 16) / 255.0)

    c_bg = parse(bg_hex)
    c_st = parse(stripe_hex)
    pixels = [0.0] * (w * h * 4)
    idx = 0
    for y in range(h):
        v = y / float(h - 1)
        for x in range(w):
            u = x / float(w - 1)
            r, g, b = c_bg
            if v < 0.14 or v > 0.86:
                r, g, b = c_st
            elif 0.30 <= v <= 0.70 and 0.22 <= u <= 0.78:
                # Emblem oval / cream label medallion
                dx = (u - 0.50) / 0.26
                dy = (v - 0.50) / 0.19
                if dx * dx + dy * dy <= 1.0:
                    r, g, b = 0.96, 0.92, 0.80
                    if 0.44 <= v <= 0.56 and abs(u - 0.50) < 0.18 and int(u * 80) % 2 == 0:
                        r, g, b = c_bg
            pixels[idx] = r
            pixels[idx + 1] = g
            pixels[idx + 2] = b
            pixels[idx + 3] = 1.0
            idx += 4

    img.pixels.foreach_set(pixels)
    img.pack()
    return img


# =============================================================================
# 6. GLB EXPORT PIPELINE
# =============================================================================

def finalize_and_export_glb(out_path):
    """Apply modifiers on all mesh objects, compute clean stats, and export glTF 2.0 .glb."""
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)

    total_verts = 0
    total_tris = 0
    for obj in list(bpy.context.scene.objects):
        if obj.type == 'MESH':
            apply_all_modifiers(obj)
            mesh = obj.data
            mesh.calc_loop_triangles()
            total_verts += len(mesh.vertices)
            total_tris += len(mesh.loop_triangles)

    bpy.ops.object.select_all(action='SELECT')

    export_kwargs = dict(
        filepath=out_path,
        export_format='GLB',
        export_yup=True,
        export_apply=True,
        export_texcoords=True,
        export_normals=True,
        export_materials='EXPORT',
        use_selection=False,
    )
    # Optional Draco/image args differ slightly across Blender versions; keep portable core kwargs!
    try:
        bpy.ops.export_scene.gltf(**export_kwargs)
    except TypeError:
        export_kwargs.pop('use_selection', None)
        bpy.ops.export_scene.gltf(**export_kwargs)

    size_bytes = os.path.getsize(out_path) if os.path.exists(out_path) else 0
    return {
        'file': os.path.basename(out_path),
        'vertices': total_verts,
        'triangles': total_tris,
        'bytes': size_bytes,
    }
