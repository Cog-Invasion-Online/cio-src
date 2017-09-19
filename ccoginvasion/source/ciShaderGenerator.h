/**
 * COG INVASION ONLINE
 * Copyright (c) CIO Team. All rights reserved.
 *
 * @file ciShaderGenerator.h
 * @author Brian Lach
 * @date September 17, 2017
 */

#ifndef CI_SHADER_GENERATOR_H
#define CI_SHADER_GENERATOR_H

#include <shaderGenerator.h>

/**
 * This is our extension of Panda's shader generator to implement
 * PSSM shadows using DirectionalLights. We can also do other things
 * we may desire.
 */
class EXPORT_CLASS CIShaderGenerator : public ShaderGenerator {
PUBLISHED:
  CIShaderGenerator(GraphicsStateGuardianBase *gsg, GraphicsOutputBase *host);
  virtual ~CIShaderGenerator();

  virtual CPT(ShaderAttrib) synthesize_shader(const RenderState *rs,
                                              const GeomVertexAnimationSpec &anim);

  const char *alloc_texunit();

  void reset_register_allocator();

  CPT(RenderAttrib) create_shader_attrib(const string &shader_pgm);

  void set_pssm_depthmaps(PT(Texture) zero, PT(Texture) one,
                          PT(Texture) two);

  void set_pssm_lights(const NodePath &zero, const NodePath &one,
                       const NodePath &two);

  void set_pssm_depth(PN_stdfloat zero, PN_stdfloat one,
                      PN_stdfloat two);

private:
  int _texunits_used;

  PT(Texture) _depthmap0;
  PT(Texture) _depthmap1;
  PT(Texture) _depthmap2;

  NodePath _light0;
  NodePath _light1;
  NodePath _light2;

  PN_stdfloat _depth0;
  PN_stdfloat _depth1;
  PN_stdfloat _depth2;

  CPT(RenderAttrib) _final;

public:
  static TypeHandle get_class_type() {
    return _type_handle;
  }
  static void init_type() {
    ShaderGenerator::init_type();
    register_type(_type_handle, "CIShaderGenerator",
                  ShaderGenerator::get_class_type());
  }
  virtual TypeHandle get_type() const {
    return get_class_type();
  }
  virtual TypeHandle force_init_type() {
    init_type(); return get_class_type();
  }

private:
  static TypeHandle _type_handle;
};

#endif // CI_SHADER_GENERATOR_H