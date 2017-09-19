/**
 * COG INVASION ONLINE
 * Copyright (c) CIO Team. All rights reserved.
 *
 * @file ciShaderGenerator.cxx
 * @author Brian Lach
 * @date September 17, 2017
 */

#include "ciShaderGenerator.h"

// Panda includes:
#include <material.h>
#include <pointLight.h>
#include <directionalLight.h>
#include <spotLight.h>
#include <texGenAttrib.h>
#include <textureAttrib.h>
#include <lightRampAttrib.h>
#include <alphaTestAttrib.h>
#include <fogAttrib.h>
#include <fog.h>
#include <config_pgraphnodes.h>

ConfigVariableInt parallax_mapping_samples
("parallax-mapping-samples", 3,
 PRC_DESC("Sets the amount of samples to use in the parallax mapping "
 "implementation. A value of 0 means to disable it entirely."));

ConfigVariableDouble parallax_mapping_scale
("parallax-mapping-scale", 0.1,
 PRC_DESC("Sets the strength of the effect of parallax mapping, that is, "
 "how much influence the height values have on the texture "
 "coordinates."));

TypeHandle CIShaderGenerator::_type_handle;

const int max_splits = 3;

CIShaderGenerator::
CIShaderGenerator(GraphicsStateGuardianBase *gsg, GraphicsOutputBase *host) :
  ShaderGenerator(gsg, host),
  _texunits_used(0),
  _depthmap0(NULL),
  _depthmap1(NULL),
  _depthmap2(NULL),
  _depth0(0.0),
  _depth1(0.0),
  _depth2(0.0) {
}

CIShaderGenerator::
~CIShaderGenerator() {
}

void CIShaderGenerator::
reset_register_allocator() {
  ShaderGenerator::reset_register_allocator();
  _texunits_used = 0;
}

void CIShaderGenerator::
set_pssm_depthmaps(PT(Texture) zero, PT(Texture) one, PT(Texture) two) {
  _depthmap0 = zero;
  _depthmap1 = one;
  _depthmap2 = two;
}

void CIShaderGenerator::
set_pssm_depth(PN_stdfloat z, PN_stdfloat o, PN_stdfloat tw) {
  _depth0 = z;
  _depth1 = o;
  _depth2 = tw;
}

void CIShaderGenerator::
set_pssm_lights(const NodePath &z, const NodePath &o, const NodePath &tw) {
  _light0 = z;
  _light1 = o;
  _light2 = tw;
}

CPT(RenderAttrib) CIShaderGenerator::
create_shader_attrib(const string &shader_pgm) {
  CPT(RenderAttrib) attr = ShaderGenerator::create_shader_attrib(shader_pgm);

  // Apply pssm inputs.
  // The data is supplied to this class from src.coginvasion.base.SunLight
  attr = DCAST(ShaderAttrib, attr)->set_shader_input("depth", _depth0, _depth1, _depth2);
  attr = DCAST(ShaderAttrib, attr)->set_shader_input("depthmap0", _depthmap0);
  attr = DCAST(ShaderAttrib, attr)->set_shader_input("depthmap1", _depthmap1);
  attr = DCAST(ShaderAttrib, attr)->set_shader_input("depthmap2", _depthmap2);
  attr = DCAST(ShaderAttrib, attr)->set_shader_input("pssm_light0", _light0);
  attr = DCAST(ShaderAttrib, attr)->set_shader_input("pssm_light1", _light1);
  attr = DCAST(ShaderAttrib, attr)->set_shader_input("pssm_light2", _light2);

  return attr;
}

const char *CIShaderGenerator::
alloc_texunit() {
  // There can be up to 16 TEXUNITs, but we aren't going to need any more than 6.
  switch (_texunits_used) {
  case 0:
    _texunits_used++;
    return "TEXUNIT0";
  case 1:
    _texunits_used++;
    return "TEXUNIT1";
  case 2:
    _texunits_used++;
    return "TEXUNIT2";
  case 3:
    _texunits_used++;
    return "TEXUNIT3";
  case 4:
    _texunits_used++;
    return "TEXUNIT4";
  case 5:
    _texunits_used++;
    return "TEXUNIT5";
  }

  return "UNKNOWN";
}

/**
 * This may be the longest function ever written.
 * It creates a CG shader based on the current render state.
 * Most of this code is just taken directly from ShaderGenerator
 * but modified a bit to implement PSSM shadows on DirectionalLights.
 * There's no way to just have this function change a few things.
 * You have to completely override it.
 */
CPT(ShaderAttrib) CIShaderGenerator::
synthesize_shader(const RenderState *rs, const GeomVertexAnimationSpec &anim) {
  cout << "Synthesizing shader..." << endl;

  analyze_renderstate(rs);
  reset_register_allocator();

  if (pgraphnodes_cat.is_debug()) {
    pgraphnodes_cat.debug()
      << "Generating shader for render state " << rs << ":\n";
    rs->write(pgraphnodes_cat.debug(false), 2);
  }

  // These variables will hold the results of register allocation.

  const char *tangent_freg = 0;
  const char *binormal_freg = 0;
  string tangent_input;
  string binormal_input;
  pmap<const InternalName *, const char *> texcoord_fregs;
  pvector<const char *> lightcoord_fregs;

  /////////////////////////////////////////////////
  // For directional light pssm:
  pmap<int, pvector<const char *>> shadowcoord_fregs;
  //////////////////////////////////////////////////

  const char *world_position_freg = 0;
  const char *world_normal_freg = 0;
  const char *eye_position_freg = 0;
  const char *eye_normal_freg = 0;
  const char *hpos_freg = 0;

  const char *position_vreg;
  const char *transform_weight_vreg = 0;
  const char *normal_vreg;
  const char *color_vreg = 0;
  const char *transform_index_vreg = 0;

  if (_use_generic_attr) {
    position_vreg = "ATTR0";
    transform_weight_vreg = "ATTR1";
    normal_vreg = "ATTR2";
    transform_index_vreg = "ATTR7";
  } else {
    position_vreg = "POSITION";
    normal_vreg = "NORMAL";
  }

  if (_vertex_colors) {
    // Reserve COLOR0
    color_vreg = _use_generic_attr ? "ATTR3" : "COLOR0";
    _vcregs_used = 1;
    _fcregs_used = 1;
  }

  // Generate the shader's text.

  ostringstream text;

  text << "//Cg\n";

  text << "/* Generated shader for render state:\n";
  rs->write(text, 2);
  text << "*/\n";

  text << "void vshader(\n";
  const TextureAttrib *texture = DCAST(TextureAttrib, rs->get_attrib_def(TextureAttrib::get_class_slot()));
  const TexGenAttrib *tex_gen = DCAST(TexGenAttrib, rs->get_attrib_def(TexGenAttrib::get_class_slot()));
  for (int i = 0; i < _num_textures; ++i) {
    TextureStage *stage = texture->get_on_stage(i);
    if (!tex_gen->has_stage(stage)) {
      const InternalName *texcoord_name = stage->get_texcoord_name();

      if (texcoord_fregs.count(texcoord_name) == 0) {
        const char *freg = alloc_freg();
        string tcname = texcoord_name->join("_");
        texcoord_fregs[texcoord_name] = freg;

        text << "\t in float4 vtx_" << tcname << " : " << alloc_vreg() << ",\n";
        text << "\t out float4 l_" << tcname << " : " << freg << ",\n";
      }
    }

    if ((_map_index_normal == i && (_lighting || _out_aux_normal) && _auto_normal_on) || _map_index_height == i) {
      const InternalName *texcoord_name = stage->get_texcoord_name();
      PT(InternalName) tangent_name = InternalName::get_tangent();
      PT(InternalName) binormal_name = InternalName::get_binormal();

      if (texcoord_name != InternalName::get_texcoord()) {
        tangent_name = tangent_name->append(texcoord_name->get_basename());
        binormal_name = binormal_name->append(texcoord_name->get_basename());
      }
      tangent_input = tangent_name->join("_");
      binormal_input = binormal_name->join("_");

      text << "\t in float4 vtx_" << tangent_input << " : " << alloc_vreg() << ",\n";
      text << "\t in float4 vtx_" << binormal_input << " : " << alloc_vreg() << ",\n";

      if (_map_index_normal == i && (_lighting || _out_aux_normal) && _auto_normal_on) {
        tangent_freg = alloc_freg();
        binormal_freg = alloc_freg();
        text << "\t out float4 l_tangent : " << tangent_freg << ",\n";
        text << "\t out float4 l_binormal : " << binormal_freg << ",\n";
      }
    }
  }
  if (_vertex_colors) {
    text << "\t in float4 vtx_color : " << color_vreg << ",\n";
    text << "\t out float4 l_color : COLOR0,\n";
  }
  if (_need_world_position || _need_world_normal) {
    text << "\t uniform float4x4 trans_model_to_world,\n";
  }
  if (_need_world_position) {
    world_position_freg = alloc_freg();
    text << "\t out float4 l_world_position : " << world_position_freg << ",\n";
  }
  if (_need_world_normal) {
    world_normal_freg = alloc_freg();
    text << "\t out float4 l_world_normal : " << world_normal_freg << ",\n";
  }
  if (_need_eye_position) {
    text << "\t uniform float4x4 trans_model_to_view,\n";
    eye_position_freg = alloc_freg();
    text << "\t out float4 l_eye_position : " << eye_position_freg << ",\n";
  } else if ((_lighting || _out_aux_normal) && (_map_index_normal >= 0 && _auto_normal_on)) {
    text << "\t uniform float4x4 trans_model_to_view,\n";
  }
  if (_need_eye_normal) {
    eye_normal_freg = alloc_freg();
    text << "\t uniform float4x4 tpose_view_to_model,\n";
    text << "\t out float4 l_eye_normal : " << eye_normal_freg << ",\n";
  }
  if (_map_index_height >= 0 || _need_world_normal || _need_eye_normal) {
    text << "\t in float3 vtx_normal : " << normal_vreg << ",\n";
  }
  if (_map_index_height >= 0) {
    text << "\t uniform float4 mspos_view,\n";
    text << "\t out float3 l_eyevec,\n";
  }
  if (_lighting && _shadows && _auto_shadow_on) {
    for (size_t i = 0; i < _lights.size(); ++i) {
      if (_lights[i]->is_shadow_caster()) {
        lightcoord_fregs.push_back(alloc_freg());
        if (_lights[i]->is_of_type(PointLight::get_class_type())) {
          text << "\t uniform float4x4 trans_model_to_light" << i << ",\n";
        } else {
          text << "\t uniform float4x4 trans_model_to_clip_of_light" << i << ",\n";
        }
        text << "\t out float4 l_lightcoord" << i << " : " << lightcoord_fregs[i] << ",\n";

        if (_lights[i]->is_of_type(DirectionalLight::get_class_type())) {
          // There should only be one DirectionalLight in any scene in CIO, don't try to add a second one lol.
          for (int j = 0; j < max_splits; j++) {
            const char *shfreg = alloc_freg();
            shadowcoord_fregs[i].push_back(shfreg);
            text << "\t out float4 l_shadowcoord" << j << " : " << shfreg << ",\n";
            text << "\t uniform mspos_light" << j << ",\n";
          }
        }

      } else {
        lightcoord_fregs.push_back(NULL);
      }
    }
  }
  if (_fog) {
    hpos_freg = alloc_freg();
    text << "\t out float4 l_hpos : " << hpos_freg << ",\n";
  }
  if (anim.get_animation_type() == GeomEnums::AT_hardware &&
      anim.get_num_transforms() > 0) {
    int num_transforms;
    if (anim.get_indexed_transforms()) {
      num_transforms = 120;
    } else {
      num_transforms = anim.get_num_transforms();
    }
    if (transform_weight_vreg == NULL) {
      transform_weight_vreg = alloc_vreg();
    }
    if (transform_index_vreg == NULL) {
      transform_index_vreg = alloc_vreg();
    }
    text << "\t uniform float4x4 tbl_transforms[" << num_transforms << "],\n";
    text << "\t in float4 vtx_transform_weight : " << transform_weight_vreg << ",\n";
    if (anim.get_indexed_transforms()) {
      text << "\t in uint4 vtx_transform_index : " << transform_index_vreg << ",\n";
    }
  }
  text << "\t in float4 vtx_position : " << position_vreg << ",\n";
  text << "\t out float4 l_position : POSITION,\n";
  text << "\t uniform float4x4 mat_modelproj\n";
  text << ") {\n";

  if (anim.get_animation_type() == GeomEnums::AT_hardware &&
      anim.get_num_transforms() > 0) {

    if (!anim.get_indexed_transforms()) {
      text << "\t const uint4 vtx_transform_index = uint4(0, 1, 2, 3);\n";
    }

    text << "\t float4x4 matrix = tbl_transforms[vtx_transform_index.x] * vtx_transform_weight.x";
    if (anim.get_num_transforms() > 1) {
      text << "\n\t                 + tbl_transforms[vtx_transform_index.y] * vtx_transform_weight.y";
    }
    if (anim.get_num_transforms() > 2) {
      text << "\n\t                 + tbl_transforms[vtx_transform_index.z] * vtx_transform_weight.z";
    }
    if (anim.get_num_transforms() > 3) {
      text << "\n\t                 + tbl_transforms[vtx_transform_index.w] * vtx_transform_weight.w";
    }
    text << ";\n";

    text << "\t vtx_position = mul(matrix, vtx_position);\n";
    if (_need_world_normal || _need_eye_normal) {
      text << "\t vtx_normal = mul((float3x3)matrix, vtx_normal);\n";
    }
  }

  text << "\t l_position = mul(mat_modelproj, vtx_position);\n";
  if (_fog) {
    text << "\t l_hpos = l_position;\n";
  }
  if (_need_world_position) {
    text << "\t l_world_position = mul(trans_model_to_world, vtx_position);\n";
  }
  if (_need_world_normal) {
    text << "\t l_world_normal = mul(trans_model_to_world, float4(vtx_normal, 0));\n";
  }
  if (_need_eye_position) {
    text << "\t l_eye_position = mul(trans_model_to_view, vtx_position);\n";
  }
  if (_need_eye_normal) {
    if (_normalize_normals) {
      text << "\t l_eye_normal.xyz = normalize(mul((float3x3)tpose_view_to_model, vtx_normal));\n";
    } else {
      text << "\t l_eye_normal.xyz = mul((float3x3)tpose_view_to_model, vtx_normal);\n";
    }
    text << "\t l_eye_normal.w = 0;\n";
  }
  pmap<const InternalName *, const char *>::const_iterator it;
  for (it = texcoord_fregs.begin(); it != texcoord_fregs.end(); ++it) {
    // Pass through all texcoord inputs as-is.
    string tcname = it->first->join("_");
    text << "\t l_" << tcname << " = vtx_" << tcname << ";\n";
  }
  if (_vertex_colors) {
    text << "\t l_color = vtx_color;\n";
  }
  if ((_lighting || _out_aux_normal) && (_map_index_normal >= 0 && _auto_normal_on)) {
    text << "\t l_tangent.xyz = normalize(mul((float3x3)trans_model_to_view, vtx_" << tangent_input << ".xyz));\n";
    text << "\t l_tangent.w = 0;\n";
    text << "\t l_binormal.xyz = normalize(mul((float3x3)trans_model_to_view, -vtx_" << binormal_input << ".xyz));\n";
    text << "\t l_binormal.w = 0;\n";
  }
  if (_shadows && _auto_shadow_on) {
    text << "\t float4x4 biasmat = {0.5f, 0.0f, 0.0f, 0.5f, 0.0f, 0.5f, 0.0f, 0.5f, 0.0f, 0.0f, 0.5f, 0.5f, 0.0f, 0.0f, 0.0f, 1.0f};\n";
    for (size_t i = 0; i < _lights.size(); ++i) {
      if (_lights[i]->is_shadow_caster()) {
        if (_lights[i]->is_of_type(PointLight::get_class_type())) {
          text << "\t l_lightcoord" << i << " = mul(trans_model_to_light" << i << ", vtx_position);\n";
        } else {
          text << "\t l_lightcoord" << i << " = mul(biasmat, mul(trans_model_to_clip_of_light" << i << ", vtx_position));\n";
        }

        if (_lights[i]->is_of_type(DirectionalLight::get_class_type())) {
          // There should only be one DirectionalLight in a scene in Cog Invasion so we're just going to do this.
          for (int j = 0; j < max_splits; j++) {
            text << "\t l_shadowcoord" << j << " = l_lightcoord" << i << " * float4(0.5, 0.5, 0.5, 1.0) + l_lightcoord" << i << ".w * float4(0.5, 0.5, 0.5, 0.0);\n";
          }
        }
      }
    }
  }
  if (_map_index_height >= 0) {
    text << "\t float3 eyedir = mspos_view.xyz - vtx_position.xyz;\n";
    text << "\t l_eyevec.x = dot(vtx_" << tangent_input << ".xyz, eyedir);\n";
    text << "\t l_eyevec.y = dot(vtx_" << binormal_input << ".xyz, eyedir);\n";
    text << "\t l_eyevec.z = dot(vtx_normal, eyedir);\n";
    text << "\t l_eyevec = normalize(l_eyevec);\n";
  }
  text << "}\n\n";

  // Fragment shader

  text << "void fshader(\n";
  if (_fog) {
    text << "\t in float4 l_hpos : " << hpos_freg << ",\n";
    text << "\t in uniform float4 attr_fog,\n";
    text << "\t in uniform float4 attr_fogcolor,\n";
  }
  if (_need_world_position) {
    text << "\t in float4 l_world_position : " << world_position_freg << ",\n";
  }
  if (_need_world_normal) {
    text << "\t in float4 l_world_normal : " << world_normal_freg << ",\n";
  }
  if (_need_eye_position) {
    text << "\t in float4 l_eye_position : " << eye_position_freg << ",\n";
  }
  if (_need_eye_normal) {
    text << "\t in float4 l_eye_normal : " << eye_normal_freg << ",\n";
  }
  for (it = texcoord_fregs.begin(); it != texcoord_fregs.end(); ++it) {
    text << "\t in float4 l_" << it->first->join("_") << " : " << it->second << ",\n";
  }
  const TexMatrixAttrib *tex_matrix = DCAST(TexMatrixAttrib, rs->get_attrib_def(TexMatrixAttrib::get_class_slot()));
  for (int i = 0; i<_num_textures; i++) {
    TextureStage *stage = texture->get_on_stage(i);
    Texture *tex = texture->get_on_texture(stage);
    nassertr(tex != NULL, NULL);
    text << "\t uniform sampler" << texture_type_as_string(tex->get_texture_type()) << " tex_" << i << ",\n";
    if (tex_matrix->has_stage(stage)) {
      text << "\t uniform float4x4 texmat_" << i << ",\n";
    }
  }
  if ((_lighting || _out_aux_normal) && (_map_index_normal >= 0 && _auto_normal_on)) {
    text << "\t in float3 l_tangent : " << tangent_freg << ",\n";
    text << "\t in float3 l_binormal : " << binormal_freg << ",\n";
  }
  if (_lighting) {
    for (size_t i = 0; i < _lights.size(); ++i) {
      if (_lights[i]->is_of_type(DirectionalLight::get_class_type())) {
        // Once again: there should only be one DirectionalLight!!!
        text << "\t uniform float4x4 dlight_light" << i << "_rel_view,\n";

      } else if (_lights[i]->is_of_type(PointLight::get_class_type())) {
        text << "\t uniform float4x4 plight_light" << i << "_rel_view,\n";

      } else if (_lights[i]->is_of_type(Spotlight::get_class_type())) {
        text << "\t uniform float4x4 slight_light" << i << "_rel_view,\n";
        text << "\t uniform float4   satten_light" << i << ",\n";
      }

      if (_shadows && _lights[i]->is_shadow_caster() && _auto_shadow_on) {
        if (_lights[i]->is_of_type(PointLight::get_class_type())) {
          text << "\t uniform samplerCUBE shadow_light" << i << ",\n";
        } else if (_use_shadow_filter) {
          text << "\t uniform sampler2DShadow shadow_light" << i << ",\n";
        } else {
          text << "\t uniform sampler2D shadow_light" << i << ",\n";
        }
        text << "\t in float4 l_lightcoord" << i << " : " << lightcoord_fregs[i] << ",\n";

        if (_lights[i]->is_of_type(DirectionalLight::get_class_type())) {
          text << "\t in float4 l_fragCoord : WPOS,\n";
          text << "\t uniform float4 k_depth,\n";
          for (int j = 0; j < max_splits; j++) {
            const char *tu = alloc_texunit();
            text << "\t uniform sampler2D k_depthmap" << j << " : " << tu << ",\n";
            const char *tc = shadowcoord_fregs[i][j];
            text << "\t in float4 l_shadowcoord" << j << " : " << tc << ",\n";
          }
        }
        
      }
    }
    if (_need_material_props) {
      text << "\t uniform float4x4 attr_material,\n";
    }
    if (_have_specular) {
      if (_material->get_local()) {
        text << "\t uniform float4 mspos_view,\n";
      } else {
        text << "\t uniform float4 row1_view_to_model,\n";
      }
    }
  }
  if (_map_index_height >= 0) {
    text << "\t float3 l_eyevec,\n";
  }
  if (_out_aux_any) {
    text << "\t out float4 o_aux : COLOR1,\n";
  }
  text << "\t out float4 o_color : COLOR0,\n";
  if (_vertex_colors) {
    text << "\t in float4 l_color : COLOR0,\n";
  } else {
    text << "\t uniform float4 attr_color,\n";
  }
  for (int i = 0; i<_num_clip_planes; ++i) {
    text << "\t uniform float4 clipplane_" << i << ",\n";
  }
  text << "\t uniform float4 attr_ambient,\n";
  text << "\t uniform float4 attr_colorscale\n";
  text << ") {\n";
  // Clipping first!
  for (int i = 0; i<_num_clip_planes; ++i) {
    text << "\t if (l_world_position.x * clipplane_" << i << ".x + l_world_position.y ";
    text << "* clipplane_" << i << ".y + l_world_position.z * clipplane_" << i << ".z + clipplane_" << i << ".w <= 0) {\n";
    text << "\t discard;\n";
    text << "\t }\n";
  }
  text << "\t float4 result;\n";
  if (_out_aux_any) {
    text << "\t o_aux = float4(0, 0, 0, 0);\n";
  }
  // Now generate any texture coordinates according to TexGenAttrib.  If it
  // has a TexMatrixAttrib, also transform them.
  for (int i = 0; i<_num_textures; i++) {
    TextureStage *stage = texture->get_on_stage(i);
    if (tex_gen != NULL && tex_gen->has_stage(stage)) {
      switch (tex_gen->get_mode(stage)) {
      case TexGenAttrib::M_world_position:
        text << "\t float4 texcoord" << i << " = l_world_position;\n";
        break;
      case TexGenAttrib::M_world_normal:
        text << "\t float4 texcoord" << i << " = l_world_normal;\n";
        break;
      case TexGenAttrib::M_eye_position:
        text << "\t float4 texcoord" << i << " = l_eye_position;\n";
        break;
      case TexGenAttrib::M_eye_normal:
        text << "\t float4 texcoord" << i << " = l_eye_normal;\n";
        text << "\t texcoord" << i << ".w = 1.0f;\n";
        break;
      default:
        pgraphnodes_cat.error() << "Unsupported TexGenAttrib mode\n";
        text << "\t float4 texcoord" << i << " = float4(0, 0, 0, 0);\n";
      }
    } else {
      // Cg seems to be able to optimize this temporary away when appropriate.
      const InternalName *texcoord_name = stage->get_texcoord_name();
      text << "\t float4 texcoord" << i << " = l_" << texcoord_name->join("_") << ";\n";
    }
    if (tex_matrix != NULL && tex_matrix->has_stage(stage)) {
      text << "\t texcoord" << i << " = mul(texmat_" << i << ", texcoord" << i << ");\n";
      text << "\t texcoord" << i << ".xyz /= texcoord" << i << ".w;\n";
    }
  }
  text << "\t // Fetch all textures.\n";
  if (_map_index_height >= 0 && parallax_mapping_samples > 0) {
    Texture *tex = texture->get_on_texture(texture->get_on_stage(_map_index_height));
    nassertr(tex != NULL, NULL);
    text << "\t float4 tex" << _map_index_height << " = tex" << texture_type_as_string(tex->get_texture_type());
    text << "(tex_" << _map_index_height << ", texcoord" << _map_index_height << ".";
    switch (tex->get_texture_type()) {
    case Texture::TT_cube_map:
    case Texture::TT_3d_texture:
    case Texture::TT_2d_texture_array:
      text << "xyz";
      break;
    case Texture::TT_2d_texture:
      text << "xy";
      break;
    case Texture::TT_1d_texture:
      text << "x";
      break;
    default:
      break;
    }
    text << ");\n\t float3 parallax_offset = l_eyevec.xyz * (tex" << _map_index_height;
    if (_map_height_in_alpha) {
      text << ".aaa";
    } else {
      text << ".rgb";
    }
    text << " * 2.0 - 1.0) * " << parallax_mapping_scale << ";\n";
    // Additional samples
    for (int i = 0; i<parallax_mapping_samples - 1; i++) {
      text << "\t parallax_offset = l_eyevec.xyz * (parallax_offset + (tex" << _map_index_height;
      if (_map_height_in_alpha) {
        text << ".aaa";
      } else {
        text << ".rgb";
      }
      text << " * 2.0 - 1.0)) * " << 0.5 * parallax_mapping_scale << ";\n";
    }
  }
  for (int i = 0; i<_num_textures; i++) {
    if (i != _map_index_height) {
      Texture *tex = texture->get_on_texture(texture->get_on_stage(i));
      nassertr(tex != NULL, NULL);
      // Parallax mapping pushes the texture coordinates of the other textures
      // away from the camera.
      if (_map_index_height >= 0 && parallax_mapping_samples > 0) {
        text << "\t texcoord" << i << ".xyz -= parallax_offset;\n";
      }
      text << "\t float4 tex" << i << " = tex" << texture_type_as_string(tex->get_texture_type());
      text << "(tex_" << i << ", texcoord" << i << ".";
      switch (tex->get_texture_type()) {
      case Texture::TT_cube_map:
      case Texture::TT_3d_texture:
      case Texture::TT_2d_texture_array:
        text << "xyz";
        break;
      case Texture::TT_2d_texture:
        text << "xy";
        break;
      case Texture::TT_1d_texture:
        text << "x";
        break;
      default:
        break;
      }
      text << ");\n";
    }
  }
  if (_lighting || _out_aux_normal) {
    if (_map_index_normal >= 0 && _auto_normal_on) {
      text << "\t // Translate tangent-space normal in map to view-space.\n";
      text << "\t float3 tsnormal = ((float3)tex" << _map_index_normal << " * 2) - 1;\n";
      text << "\t l_eye_normal.xyz *= tsnormal.z;\n";
      text << "\t l_eye_normal.xyz += l_tangent * tsnormal.x;\n";
      text << "\t l_eye_normal.xyz += l_binormal * tsnormal.y;\n";
    }
  }
  if (_need_eye_normal) {
    text << "\t // Correct the surface normal for interpolation effects\n";
    text << "\t l_eye_normal.xyz = normalize(l_eye_normal.xyz);\n";
  }
  if (_out_aux_normal) {
    text << "\t // Output the camera-space surface normal\n";
    text << "\t o_aux.rgb = (l_eye_normal.xyz*0.5) + float3(0.5,0.5,0.5);\n";
  }
  if (_lighting) {
    text << "\t // Begin view-space light calculations\n";
    text << "\t float ldist,lattenv,langle;\n";
    text << "\t float4 lcolor,lspec,lpoint,latten,ldir,leye;\n";
    text << "\t float3 lvec,lhalf;\n";
    if (_shadows && _auto_shadow_on) {
      text << "\t float lshad;\n";
    }
    if (_separate_ambient_diffuse) {
      if (_have_ambient) {
        text << "\t float4 tot_ambient = float4(0,0,0,0);\n";
      }
      if (_have_diffuse) {
        text << "\t float4 tot_diffuse = float4(0,0,0,0);\n";
      }
    } else {
      if (_have_ambient || _have_diffuse) {
        text << "\t float4 tot_diffuse = float4(0,0,0,0);\n";
      }
    }
    if (_have_specular) {
      text << "\t float4 tot_specular = float4(0,0,0,0);\n";
      if (_material->has_specular()) {
        text << "\t float shininess = attr_material[3].w;\n";
      } else {
        text << "\t float shininess = 50; // no shininess specified, using default\n";
      }
    }
    if (_separate_ambient_diffuse && _have_ambient) {
      text << "\t tot_ambient += attr_ambient;\n";
    } else if (_have_diffuse) {
      text << "\t tot_diffuse += attr_ambient;\n";
    }
  }
  for (size_t i = 0; i < _lights.size(); ++i) {
    if (_lights[i]->is_of_type(DirectionalLight::get_class_type())) {
      text << "\t // Directional Light " << i << "\n";
      text << "\t lcolor = dlight_light" << i << "_rel_view[0];\n";
      text << "\t lspec  = dlight_light" << i << "_rel_view[1];\n";
      text << "\t lvec   = dlight_light" << i << "_rel_view[2].xyz;\n";
      text << "\t lcolor *= saturate(dot(l_eye_normal.xyz, lvec.xyz));\n";
      if (_shadows && _lights[i]->is_shadow_caster() && _auto_shadow_on) {
        text << "\t float depth = l_fragCoord.z / l_fragCoord.w;\n";
        text << "\t if (depth < k_depth.x) {\n";
        text << "\t\t lshad = tex2Dproj(k_depthmap0, l_shadowcoord0);\n";
        text << "\t }\n";
        text << "\t else if (depth < k_depth.y) {\n";
        text << "\t\t lshad = tex2Dproj(k_depthmap1, l_shadowcoord1);\n";
        text << "\t }\n";
        text << "\t else if (depth < k_depth.z) {\n";
        text << "\t\t lshad = tex2Dproj(k_depthmap2, l_shadowcoord2);\n";
        text << "\t }\n";
        //if (_use_shadow_filter) {
        //  text << "\t lshad = shadow2DProj(shadow_light" << i << ", l_lightcoord" << i << ").r;\n";
        //} else {
        //  text << "\t lshad = tex2Dproj(shadow_light" << i << ", l_lightcoord" << i << ").r > l_lightcoord" << i << ".z / l_lightcoord" << i << ".w;\n";
        //}
        text << "\t lcolor *= lshad;\n";
        text << "\t lspec *= lshad;\n";
      }
      if (_have_diffuse) {
        text << "\t tot_diffuse += lcolor;\n";
      }
      if (_have_specular) {
        if (_material->get_local()) {
          text << "\t lhalf = normalize(lvec - normalize(l_eye_position.xyz));\n";
        } else {
          text << "\t lhalf = dlight_light" << i << "_rel_view[3].xyz;\n";
        }
        text << "\t lspec *= pow(saturate(dot(l_eye_normal.xyz, lhalf)), shininess);\n";
        text << "\t tot_specular += lspec;\n";
      }
    } else if (_lights[i]->is_of_type(PointLight::get_class_type())) {
      text << "\t // Point Light " << i << "\n";
      text << "\t lcolor = plight_light" << i << "_rel_view[0];\n";
      text << "\t lspec  = plight_light" << i << "_rel_view[1];\n";
      text << "\t lpoint = plight_light" << i << "_rel_view[2];\n";
      text << "\t latten = plight_light" << i << "_rel_view[3];\n";
      text << "\t lvec   = lpoint.xyz - l_eye_position.xyz;\n";
      text << "\t ldist = length(lvec);\n";
      text << "\t lvec /= ldist;\n";
      text << "\t lattenv = 1/(latten.x + latten.y*ldist + latten.z*ldist*ldist);\n";
      text << "\t lcolor *= lattenv * saturate(dot(l_eye_normal.xyz, lvec));\n";
      if (_shadows && _lights[i]->is_shadow_caster() && _auto_shadow_on) {
        text << "\t ldist = max(abs(l_lightcoord" << i << ".x), max(abs(l_lightcoord" << i << ".y), abs(l_lightcoord" << i << ".z)));\n";
        text << "\t ldist = ((latten.w+lpoint.w)/(latten.w-lpoint.w))+((-2*latten.w*lpoint.w)/(ldist * (latten.w-lpoint.w)));\n";
        text << "\t lshad = texCUBE(shadow_light" << i << ", l_lightcoord" << i << ".xyz).r >= ldist * 0.5 + 0.5;\n";
        text << "\t lcolor *= lshad;\n";
        text << "\t lspec *= lshad;\n";
      }
      if (_have_diffuse) {
        text << "\t tot_diffuse += lcolor;\n";
      }
      if (_have_specular) {
        if (_material->get_local()) {
          text << "\t lhalf = normalize(lvec - normalize(l_eye_position.xyz));\n";
        } else {
          text << "\t lhalf = normalize(lvec - float3(0, 1, 0));\n";
        }
        text << "\t lspec *= lattenv;\n";
        text << "\t lspec *= pow(saturate(dot(l_eye_normal.xyz, lhalf)), shininess);\n";
        text << "\t tot_specular += lspec;\n";
      }
    } else if (_lights[i]->is_of_type(Spotlight::get_class_type())) {
      text << "\t // Spot Light " << i << "\n";
      text << "\t lcolor = slight_light" << i << "_rel_view[0];\n";
      text << "\t lspec  = slight_light" << i << "_rel_view[1];\n";
      text << "\t lpoint = slight_light" << i << "_rel_view[2];\n";
      text << "\t ldir   = slight_light" << i << "_rel_view[3];\n";
      text << "\t latten = satten_light" << i << ";\n";
      text << "\t lvec   = lpoint.xyz - l_eye_position.xyz;\n";
      text << "\t ldist  = length(lvec);\n";
      text << "\t lvec /= ldist;\n";
      text << "\t langle = saturate(dot(ldir.xyz, lvec));\n";
      text << "\t lattenv = 1/(latten.x + latten.y*ldist + latten.z*ldist*ldist);\n";
      text << "\t lattenv *= pow(langle, latten.w);\n";
      text << "\t if (langle < ldir.w) lattenv = 0;\n";
      text << "\t lcolor *= lattenv * saturate(dot(l_eye_normal.xyz, lvec));\n";
      if (_shadows && _lights[i]->is_shadow_caster() && _auto_shadow_on) {
        if (_use_shadow_filter) {
          text << "\t lshad = shadow2DProj(shadow_light" << i << ", l_lightcoord" << i << ").r;\n";
        } else {
          text << "\t lshad = tex2Dproj(shadow_light" << i << ", l_lightcoord" << i << ").r > l_lightcoord" << i << ".z / l_lightcoord" << i << ".w;\n";
        }
        text << "\t lcolor *= lshad;\n";
        text << "\t lspec *= lshad;\n";
      }

      if (_have_diffuse) {
        text << "\t tot_diffuse += lcolor;\n";
      }
      if (_have_specular) {
        if (_material->get_local()) {
          text << "\t lhalf = normalize(lvec - normalize(l_eye_position.xyz));\n";
        } else {
          text << "\t lhalf = normalize(lvec - float3(0,1,0));\n";
        }
        text << "\t lspec *= lattenv;\n";
        text << "\t lspec *= pow(saturate(dot(l_eye_normal.xyz, lhalf)), shininess);\n";
        text << "\t tot_specular += lspec;\n";
      }
    }
  }
  if (_lighting) {
    const LightRampAttrib *light_ramp = DCAST(LightRampAttrib, rs->get_attrib_def(LightRampAttrib::get_class_slot()));
    if (_auto_ramp_on && _have_diffuse) {
      switch (light_ramp->get_mode()) {
      case LightRampAttrib::LRT_single_threshold:
      {
        PN_stdfloat t = light_ramp->get_threshold(0);
        PN_stdfloat l0 = light_ramp->get_level(0);
        text << "\t // Single-threshold light ramp\n";
        text << "\t float lr_in = dot(tot_diffuse.rgb, float3(0.33,0.34,0.33));\n";
        text << "\t float lr_scale = (lr_in < " << t << ") ? 0.0 : (" << l0 << "/lr_in);\n";
        text << "\t tot_diffuse = tot_diffuse * lr_scale;\n";
        break;
      }
      case LightRampAttrib::LRT_double_threshold:
      {
        PN_stdfloat t0 = light_ramp->get_threshold(0);
        PN_stdfloat t1 = light_ramp->get_threshold(1);
        PN_stdfloat l0 = light_ramp->get_level(0);
        PN_stdfloat l1 = light_ramp->get_level(1);
        text << "\t // Double-threshold light ramp\n";
        text << "\t float lr_in = dot(tot_diffuse.rgb, float3(0.33,0.34,0.33));\n";
        text << "\t float lr_out = 0.0;\n";
        text << "\t if (lr_in > " << t0 << ") lr_out=" << l0 << ";\n";
        text << "\t if (lr_in > " << t1 << ") lr_out=" << l1 << ";\n";
        text << "\t tot_diffuse = tot_diffuse * (lr_out / lr_in);\n";
        break;
      }
      default:
        break;
      }
    }
    text << "\t // Begin view-space light summation\n";
    if (_have_emission) {
      if (_map_index_glow >= 0 && _auto_glow_on) {
        text << "\t result = attr_material[2] * saturate(2 * (tex" << _map_index_glow << ".a - 0.5));\n";
      } else {
        text << "\t result = attr_material[2];\n";
      }
    } else {
      if (_map_index_glow >= 0 && _auto_glow_on) {
        text << "\t result = saturate(2 * (tex" << _map_index_glow << ".a - 0.5));\n";
      } else {
        text << "\t result = float4(0,0,0,0);\n";
      }
    }
    if ((_have_ambient) && (_separate_ambient_diffuse)) {
      if (_material->has_ambient()) {
        text << "\t result += tot_ambient * attr_material[0];\n";
      } else if (_vertex_colors) {
        text << "\t result += tot_ambient * l_color;\n";
      } else if (_flat_colors) {
        text << "\t result += tot_ambient * attr_color;\n";
      } else {
        text << "\t result += tot_ambient;\n";
      }
    }
    if (_have_diffuse) {
      if (_material->has_diffuse()) {
        text << "\t result += tot_diffuse * attr_material[1];\n";
      } else if (_vertex_colors) {
        text << "\t result += tot_diffuse * l_color;\n";
      } else if (_flat_colors) {
        text << "\t result += tot_diffuse * attr_color;\n";
      } else {
        text << "\t result += tot_diffuse;\n";
      }
    }
    if (light_ramp->get_mode() == LightRampAttrib::LRT_default) {
      text << "\t result = saturate(result);\n";
    }
    text << "\t // End view-space light calculations\n";

    // Combine in alpha, which bypasses lighting calculations.  Use of lerp
    // here is a workaround for a radeon driver bug.
    if (_calc_primary_alpha) {
      if (_vertex_colors) {
        text << "\t result.a = l_color.a;\n";
      } else if (_flat_colors) {
        text << "\t result.a = attr_color.a;\n";
      } else {
        text << "\t result.a = 1;\n";
      }
    }
  } else {
    if (_vertex_colors) {
      text << "\t result = l_color;\n";
    } else if (_flat_colors) {
      text << "\t result = attr_color;\n";
    } else {
      text << "\t result = float4(1, 1, 1, 1);\n";
    }
  }

  // Loop first to see if something is using primary_color or
  // last_saved_result.
  bool have_saved_result = false;
  bool have_primary_color = false;
  for (int i = 0; i<_num_textures; i++) {
    TextureStage *stage = texture->get_on_stage(i);
    if (stage->get_mode() != TextureStage::M_combine) continue;
    if (stage->uses_primary_color() && !have_primary_color) {
      text << "\t float4 primary_color = result;\n";
      have_primary_color = true;
    }
    if (stage->uses_last_saved_result() && !have_saved_result) {
      text << "\t float4 last_saved_result = result;\n";
      have_saved_result = true;
    }
  }

  // Now loop through the textures to compose our magic blending formulas.
  for (int i = 0; i<_num_textures; i++) {
    TextureStage *stage = texture->get_on_stage(i);
    switch (stage->get_mode()) {
    case TextureStage::M_modulate:
    {
      int num_components = texture->get_on_texture(texture->get_on_stage(i))->get_num_components();

      if (num_components == 1) {
        text << "\t result.a *= tex" << i << ".a;\n";
      } else if (num_components == 3) {
        text << "\t result.rgb *= tex" << i << ".rgb;\n";
      } else {
        text << "\t result.rgba *= tex" << i << ".rgba;\n";
      }

      break;
    }
    case TextureStage::M_modulate_glow:
    case TextureStage::M_modulate_gloss:
      // in the case of glow or spec we currently see the specularity evenly
      // across the surface even if transparency or masking is present not
      // sure if this is desired behavior or not.  *MOST* would construct a
      // spec map based off of what isisn't seen based on the masktransparency
      // this may have to be left alone for now agartner
      text << "\t result.rgb *= tex" << i << ";\n";
      break;
    case TextureStage::M_decal:
      text << "\t result.rgb = lerp(result, tex" << i << ", tex" << i << ".a).rgb;\n";
      break;
    case TextureStage::M_blend:
    {
      LVecBase4 c = stage->get_color();
      text << "\t result.rgb = lerp(result, tex" << i << " * float4("
        << c[0] << ", " << c[1] << ", " << c[2] << ", " << c[3] << "), tex" << i << ".r).rgb;\n";
      break;
    }
    case TextureStage::M_replace:
      text << "\t result = tex" << i << ";\n";
      break;
    case TextureStage::M_add:
      text << "\t result.rgb += tex" << i << ".rgb;\n";
      if (_calc_primary_alpha) {
        text << "\t result.a   *= tex" << i << ".a;\n";
      }
      break;
    case TextureStage::M_combine:
      text << "\t result.rgb = ";
      if (stage->get_combine_rgb_mode() != TextureStage::CM_undefined) {
        text << combine_mode_as_string(stage, stage->get_combine_rgb_mode(), false, i);
      } else {
        text << "tex" << i << ".rgb";
      }
      if (stage->get_rgb_scale() != 1) {
        text << " * " << stage->get_rgb_scale();
      }
      text << ";\n\t result.a = ";
      if (stage->get_combine_alpha_mode() != TextureStage::CM_undefined) {
        text << combine_mode_as_string(stage, stage->get_combine_alpha_mode(), true, i);
      } else {
        text << "tex" << i << ".a";
      }
      if (stage->get_alpha_scale() != 1) {
        text << " * " << stage->get_alpha_scale();
      }
      text << ";\n";
      break;
    case TextureStage::M_blend_color_scale:
      text << "\t result.rgb = lerp(result, tex" << i << " * attr_colorscale, tex" << i << ".r).rgb;\n";
      break;
    default:
      break;
    }
    if (stage->get_saved_result() && have_saved_result) {
      text << "\t last_saved_result = result;\n";
    }
  }
  // Apply the color scale.
  text << "\t result *= attr_colorscale;\n";

  if (_subsume_alpha_test) {
    const AlphaTestAttrib *alpha_test = DCAST(AlphaTestAttrib, rs->get_attrib_def(AlphaTestAttrib::get_class_slot()));
    text << "\t // Shader includes alpha test:\n";
    double ref = alpha_test->get_reference_alpha();
    switch (alpha_test->get_mode()) {
    case RenderAttrib::M_never:
      text << "\t discard;\n";
      break;
    case RenderAttrib::M_less:
      text << "\t if (result.a >= " << ref << ") discard;\n";
      break;
    case RenderAttrib::M_equal:
      text << "\t if (result.a != " << ref << ") discard;\n";
      break;
    case RenderAttrib::M_less_equal:
      text << "\t if (result.a > " << ref << ") discard;\n";
      break;
    case RenderAttrib::M_greater:
      text << "\t if (result.a <= " << ref << ") discard;\n";
      break;
    case RenderAttrib::M_not_equal:
      text << "\t if (result.a == " << ref << ") discard;\n";
      break;
    case RenderAttrib::M_greater_equal:
      text << "\t if (result.a < " << ref << ") discard;\n";
      break;
    case RenderAttrib::M_none:
    case RenderAttrib::M_always:
    default:
      break;
    }
  }

  if (_out_primary_glow) {
    if (_map_index_glow >= 0 && _auto_glow_on) {
      text << "\t result.a = tex" << _map_index_glow << ".a;\n";
    } else {
      text << "\t result.a = 0.5;\n";
    }
  }
  if (_out_aux_glow) {
    if (_map_index_glow >= 0 && _auto_glow_on) {
      text << "\t o_aux.a = tex" << _map_index_glow << ".a;\n";
    } else {
      text << "\t o_aux.a = 0.5;\n";
    }
  }

  if (_lighting) {
    if (_have_specular) {
      if (_material->has_specular()) {
        text << "\t tot_specular *= attr_material[3];\n";
      }
      if (_map_index_gloss >= 0 && _auto_gloss_on) {
        text << "\t tot_specular *= tex" << _map_index_gloss << ".a;\n";
      }
      text << "\t result.rgb = result.rgb + tot_specular.rgb;\n";
    }
  }
  if (_auto_ramp_on) {
    const LightRampAttrib *light_ramp = DCAST(LightRampAttrib, rs->get_attrib_def(LightRampAttrib::get_class_slot()));
    switch (light_ramp->get_mode()) {
    case LightRampAttrib::LRT_hdr0:
      text << "\t result.rgb = (result*result*result + result*result + result) / (result*result*result + result*result + result + 1);\n";
      break;
    case LightRampAttrib::LRT_hdr1:
      text << "\t result.rgb = (result*result + result) / (result*result + result + 1);\n";
      break;
    case LightRampAttrib::LRT_hdr2:
      text << "\t result.rgb = result / (result + 1);\n";
      break;
    default: break;
    }
  }

  // Apply fog.
  if (_fog) {
    const FogAttrib *fog_attr = DCAST(FogAttrib, rs->get_attrib_def(FogAttrib::get_class_slot()));
    Fog *fog = fog_attr->get_fog();

    switch (fog->get_mode()) {
    case Fog::M_linear:
      text << "\t result.rgb = lerp(attr_fogcolor.rgb, result.rgb, saturate((attr_fog.z - l_hpos.z) * attr_fog.w));\n";
      break;
    case Fog::M_exponential: // 1.442695f = 1 / log(2)
      text << "\t result.rgb = lerp(attr_fogcolor.rgb, result.rgb, saturate(exp2(attr_fog.x * l_hpos.z * -1.442695f)));\n";
      break;
    case Fog::M_exponential_squared:
      text << "\t result.rgb = lerp(attr_fogcolor.rgb, result.rgb, saturate(exp2(attr_fog.x * attr_fog.x * l_hpos.z * l_hpos.z * -1.442695f)));\n";
      break;
    }
  }

  // The multiply is a workaround for a radeon driver bug.  It's annoying as
  // heck, since it produces an extra instruction.
  text << "\t o_color = result * 1.000001;\n";
  if (_subsume_alpha_test) {
    text << "\t // Shader subsumes normal alpha test.\n";
  }
  if (_disable_alpha_write) {
    text << "\t // Shader disables alpha write.\n";
  }
  text << "}\n";

  cout << "Writing output to shader-generator-output.txt" << endl;
  ofstream ofile;
  ofile.open("shader-generator-output.txt");
  ofile << text.str();
  ofile.flush();
  ofile.close();

  // Insert the shader into the shader attrib.
  CPT(RenderAttrib) shattr = create_shader_attrib(text.str());
  if (_subsume_alpha_test) {
    shattr = DCAST(ShaderAttrib, shattr)->set_flag(ShaderAttrib::F_subsume_alpha_test, true);
  }
  if (_disable_alpha_write) {
    shattr = DCAST(ShaderAttrib, shattr)->set_flag(ShaderAttrib::F_disable_alpha_write, true);
  }
  clear_analysis();
  reset_register_allocator();
  return DCAST(ShaderAttrib, shattr);
}