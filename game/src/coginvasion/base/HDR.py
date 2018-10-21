"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file HDR.py
@author Brian Lach
@date October 21, 2018

"""

from panda3d.core import Shader, ComputeNode, Vec2, Vec4, PTALVecBase2f, Texture, SamplerState

from direct.gui.DirectGui import OnscreenImage

import math

class HDR:

    NumBuckets = 16
    Size = 128
    
    def __init__(self):
        self.ptaBucketRange = None
        self.sceneBuf = None
        self.sceneTex = None
        self.histogramCompute = None
        self.histogramTex = None
        self.exposureCompute = None
        self.exposureTex = None
        self.debugTex = None
        self.debugCompute = None
        self.debugImg = None

    def isSupported(self):
        return base.win.getGsg().getSupportsComputeShaders()

    def disable(self):
        base.filters.delExposure()

        taskMgr.remove("hdrUpdate")

        if self.debugCompute:
            self.debugCompute.removeNode()
        self.debugCompute = None
        if self.debugImg:
            self.debugImg.destroy()
        self.debugImg = None
        self.debugTex = None

        if self.exposureCompute:
            self.exposureCompute.removeNode()
        self.exposureCompute = None
        self.exposureTex = None

        if self.histogramCompute:
            self.histogramCompute.removeNode()
        self.histogramCompute = None
        self.histogramTex = None

        if self.sceneBuf:
            self.sceneBuf.clearRenderTextures()
            base.win.removeOutput(self.sceneBuf)
        self.sceneBuf = None
        self.sceneTex = None

        self.ptaBucketRange = None

    def enable(self):
        if not self.isSupported():
            # HDR/auto exposure is implemented using compute
            # shaders, which are only supported by more modern
            # graphics cards and requires at least OpenGL 4.3.
            return

        self.sceneBuf = base.win.makeTextureBuffer('hdrSceneBuf', self.Size, self.Size)
        self.sceneTex = self.sceneBuf.getTexture()
        base.makeCamera(self.sceneBuf, useCamera = base.cam)

        # Build luminance histogram bucket ranges.
        self.ptaBucketRange = PTALVecBase2f.emptyArray(self.NumBuckets)
        for i in xrange(self.NumBuckets):
            # Use even distribution
            bmin = float(i) / float(self.NumBuckets)
            bmax = float(i + 1) / float(self.NumBuckets)

            # Use a distribution with slightly more bins in the low range.
            if bmin > 0.0:
                bmin = math.pow(bmin, 1.5)
            if bmax > 0.0:
                bmax = math.pow(bmax, 1.5)

        self.histogramTex = Texture('histogram')
        self.histogramTex.setup1dTexture(self.NumBuckets, Texture.TInt, Texture.FR32i)
        self.histogramTex.setClearColor(Vec4(0.0))
        self.histogramTex.clearImage()
        self.histogramCompute = render.attachNewNode(ComputeNode('histogramCompute'))
        self.histogramCompute.node().addDispatch(self.Size / 16, self.Size / 16, 1)
        self.histogramCompute.setShader(Shader.loadCompute(Shader.SLGLSL, "phase_14/models/shaders/build_histogram.compute.glsl"))
        self.histogramCompute.setShaderInput("scene_texture", self.sceneTex)
        self.histogramCompute.setShaderInput("histogram_texture", self.histogramTex)
        self.histogramCompute.setShaderInput("bucketrange", self.ptaBucketRange)

        self.exposureTex = Texture('exposure')
        self.exposureTex.setup1dTexture(1, Texture.TFloat, Texture.FR16)
        self.exposureTex.setClearColor(Vec4(0.0))
        self.exposureTex.clearImage()
        self.exposureCompute = render.attachNewNode(ComputeNode('exposureCompute'))
        self.exposureCompute.node().addDispatch(1, 1, 1)
        self.exposureCompute.setShader(Shader.loadCompute(Shader.SLGLSL, "phase_14/models/shaders/calc_luminance.compute.glsl"))
        self.exposureCompute.setShaderInput("histogram_texture", self.histogramTex)
        self.exposureCompute.setShaderInput("avg_lum_texture", self.exposureTex)
        self.exposureCompute.setShaderInput("bucketrange", self.ptaBucketRange)
        self.exposureCompute.setShaderInput("exposure_minmax", Vec2(0.5, 2.0))
        self.exposureCompute.setShaderInput("adaption_rate_brightdark", Vec2(0.6, 0.6))
        self.exposureCompute.setShaderInput("exposure_scale", 2.0)
        self.exposureCompute.setShaderInput("config_minAvgLum", base.config.GetFloat("hdr-min-avglum", 3.0))
        self.exposureCompute.setShaderInput("config_perctBrightPixels", base.config.GetFloat("hdr-percent-bright-pixels", 5.0))
        self.exposureCompute.setShaderInput("config_perctTarget", base.config.GetFloat("hdr-percent-target", 60.0))
        
        base.filters.setExposure(self.exposureTex)

        taskMgr.add(self.__update, "hdrUpdate")

        if base.config.GetBool("hdr-debug-histogram", False):
            self.debugTex = Texture('histogramDebugTex')
            self.debugTex.setup2dTexture(self.NumBuckets, 1, Texture.TFloat, Texture.FR32)
            self.debugTex.setMagfilter(SamplerState.FTNearest)
            self.debugTex.setClearColor(Vec4(0.3, 0.3, 0.5, 1.0))
            self.debugTex.clearImage()
            self.debugCompute = render.attachNewNode(ComputeNode('debugHistogramCompute'))
            self.debugCompute.node().addDispatch(1, 1, 1)
            self.debugCompute.setShader(Shader.loadCompute(Shader.SLGLSL, "phase_14/models/shaders/debug_histogram.compute.glsl"))
            self.debugCompute.setShaderInput("histogram_texture", self.histogramTex)
            self.debugCompute.setShaderInput("debug_texture", self.debugTex)
            self.debugImg = OnscreenImage(image = self.debugTex, scale = 0.3, pos = (-0.6, -0.7, -0.7))

    def __update(self, task):
        # We need to calculate a brand new histogram each frame,
        # so let's clear the one from last frame.
        self.histogramTex.clearImage()

        return task.cont