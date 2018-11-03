"""

Class CommonFilters implements certain common image
postprocessing filters.

It is not ideal that these filters are all included in a single
monolithic module.  Unfortunately, when you want to apply two filters
at the same time, you have to compose them into a single shader, and
the composition process isn't simply a question of concatenating them:
you have to somehow make them work together.  I suspect that there
exists some fairly simple framework that would make this automatable.
However, until I write some more filters myself, I won't know what
that framework is.  Until then, I'll settle for this
clunky approach.  - Josh

"""

from direct.filter.FilterManager import FilterManager
from panda3d.core import LVecBase4, LPoint2
from panda3d.core import Filename
from panda3d.core import AuxBitplaneAttrib
from panda3d.core import Texture, Shader, ATSNone
import os

CARTOON_BODY="""
float4 cartoondelta = k_cartoonseparation * texpix_txaux.xwyw;
float4 cartoon_c0 = tex2D(k_txaux, %(texcoord)s + cartoondelta.xy);
float4 cartoon_c1 = tex2D(k_txaux, %(texcoord)s - cartoondelta.xy);
float4 cartoon_c2 = tex2D(k_txaux, %(texcoord)s + cartoondelta.wz);
float4 cartoon_c3 = tex2D(k_txaux, %(texcoord)s - cartoondelta.wz);
float4 cartoon_mx = max(cartoon_c0, max(cartoon_c1, max(cartoon_c2, cartoon_c3)));
float4 cartoon_mn = min(cartoon_c0, min(cartoon_c1, min(cartoon_c2, cartoon_c3)));
float cartoon_thresh = saturate(dot(cartoon_mx - cartoon_mn, float4(3,3,0,0)) - 0.5);
result = lerp(result, k_cartooncolor, cartoon_thresh);
"""

# Some GPUs do not support variable-length loops.
#
# We fill in the actual value of numsamples in the loop limit
# when the shader is configured.
#
SSAO_BODY="""//Cg

#define SAMPLES             8
#define RADIUS              4
#define BIAS                0.005
#define BIAS_OFFSET         0.0001
#define ILLUM_INFLUENCE     0.05
#define ZFAR                3.0
#define ZNEAR               1.0
#define CONTRAST            1.0

#define PI                  3.14159265

void vshader(float4 vtx_position : POSITION,
             out float4 l_position : POSITION,
             out float2 l_texcoordD : TEXCOORD0,
             uniform float4 texpad_depth,
             uniform float4x4 mat_modelproj)
{
  l_position = mul(mat_modelproj, vtx_position);
  l_texcoordD = (vtx_position.xz * texpad_depth.xy) + texpad_depth.xy;
}

float2 rand(float2 coord, float2 size)
{
    float noiseX = frac(sin(dot(coord, float2(12.9898,78.233))) * 43758.5453) * 2.0f-1.0f;
	float noiseY = frac(sin(dot(coord, float2(12.9898,78.233)*2.0)) * 43758.5453) * 2.0f-1.0f;

	return float2(noiseX,noiseY)*0.001;
}

float readDepth(in float2 coord, sampler2D tex)
{
	return tex2Dlod(tex, float4(coord, 0, 0)).a * (ZNEAR / ZFAR);
}

float compareDepths(in float depth1, in float depth2, inout int far)
{
	float garea = 1.0; //gauss bell width    
	float diff = (depth1 - depth2)*100.0; //depth difference (0-100)

	//reduce left bell width to avoid self-shadowing
	if ( diff < BIAS + BIAS_OFFSET )
	{
		garea = BIAS;
	}
	else
	{
		far = 1;
	}
	
	float gauss = pow(2.7182,-2.0*(diff-BIAS)*(diff-BIAS)/(garea*garea));
	return gauss;
}

float calcAO(float2 uv, float depth, float dw, float dh, sampler tex)
{
	float dd = (1.0-depth)*RADIUS;

	float temp = 0.0;
	float temp2 = 0.0;
	float coordw = uv.x + dw*dd;
	float coordh = uv.y + dh*dd;
	float coordw2 = uv.x - dw*dd;
	float coordh2 = uv.y - dh*dd;
	
	float2 coord = float2(coordw , coordh);
	float2 coord2 = float2(coordw2, coordh2);
	
	int far = 0;
	temp = compareDepths(depth, readDepth(coord,tex),far);
	//DEPTH EXTRAPOLATION:
	if (far > 0)
	{
		temp2 = compareDepths(readDepth(coord2,tex),depth,far);
		temp += (1.0-temp)*temp2;
	}
	
	return temp;
}

float DoSSAO( in float2 uv, in float2 texelSize, in sampler color_depth )
{
    float ao_out = 0.0;
    
	float2 size = 1.0f / texelSize;
	float2 noise = rand(uv,size);
	float depth = readDepth(uv, color_depth);
	
	float w = texelSize.x/clamp(depth, 0.25f, 1.0)+(noise.x*(1.0f-noise.x));
	float h = texelSize.y/clamp(depth, 0.25f, 1.0)+(noise.y*(1.0f-noise.y));
	
	float pw;
	float ph;
	
	float ao = 0;

	float dl = PI*(3.0-sqrt(5.0));
	float dz = 1.0/float( SAMPLES );
	float z = 1.0 - dz/1.0;
	float l = 0.0;
	
	for (int i = 1; i <= SAMPLES; i++)
	{
		float r = sqrt(1.0-z);

		pw = cos(l)*r;
		ph = sin(l)*r;
		ao += calcAO( uv, depth, pw*w, ph*h, color_depth );     
		z = z - dz;
		l = l + dl;
	}
	ao /= float( SAMPLES );
	ao = 1.0-ao;

	float3 color = tex2D(color_depth,uv).rgb;
	
	float3 lumcoeff = float3( 0.2126f, 0.7152f, 0.0722f );
	float lum = dot( color.rgb, lumcoeff );

	ao_out = lerp( ao, 1.0f, lum*ILLUM_INFLUENCE );
	ao_out = ((ao_out - 0.5f) * max(CONTRAST, 0.0)) + 0.5f;
    return ao_out;
}

void fshader(out float4 o_color : COLOR,
             uniform float4 texpix_depth,
             in float2 l_texcoordD : TEXCOORD0,
             uniform sampler2D k_depth : TEXUNIT0)
{
    float ssao_out = DoSSAO(l_texcoordD, texpix_depth.xy, k_depth);
    
    float3 out_col = ssao_out;
    out_col *= 2.0;
    
    o_color = float4(out_col, 1.0);
}
"""

TONEMAP = """

float3 uncharted2Tonemap(float3 x)
{
    float A = 0.15;
    float B = 0.50;
    float C = 0.10;
    float D = 0.20;
    float E = 0.02;
    float F = 0.30;
    float W = 11.2;
    
    float3 val = ((x*(A*x+C*B)+D*E)/(x*(A*x+B)+D*F))-E/F;
    return val;
}

"""


class FilterConfig:
    pass

class CommonFilters:

    """ Class CommonFilters implements certain common image postprocessing
    filters.  The constructor requires a filter builder as a parameter. """

    def __init__(self, win, cam):
        self.manager = FilterManager(win, cam)
        self.configuration = {}
        self.task = None
        self.finalQuad = None
        self.bloom = []
        self.blur = []
        self.ssao = []
        self.fxaa = None
        self.textures = {}
        # always have a color texture available
        self.makeTexture("color")
        self.cleanup()

    def loadShader(self, name):
        return Shader.load(name)
		
	def fullCleanup(self):
		self.cleanup()
		self.textures = {}

    def cleanup(self):
        self.manager.cleanup()
		
        for tex in self.textures.keys():
            # Preserve color texture
            if tex != "color":
                del self.textures[tex]
        
        if self.finalQuad:
            self.finalQuad.removeNode()
        self.finalQuad = None

        if self.fxaa:
            self.fxaa.removeNode()
        self.fxaa = None
        
        for bloom in self.bloom:
            bloom.removeNode()
        self.bloom = []
        
        for blur in self.blur:
            blur.removeNode()
        self.blur = []
        
        for ssao in self.ssao:
            ssao.removeNode()
        self.ssao = []
        
        if self.task != None:
          taskMgr.remove(self.task)
          self.task = None
		  
    def makeTexture(self, tex):
        self.textures[tex] = Texture("scene-" + tex)
        self.textures[tex].setWrapU(Texture.WMClamp)
        self.textures[tex].setWrapV(Texture.WMClamp)

    def reconfigure(self, fullrebuild, changed):
        """ Reconfigure is called whenever any configuration change is made. """

        configuration = self.configuration

        if (fullrebuild):

            self.cleanup()

            if (len(configuration) == 0):
                return

            if not self.manager.win.gsg.getSupportsBasicShaders():
                return False

            auxbits = 0
			# Color texture is already created at init,
			# we don't need to make it.
            needtex = set()
            needtexcoord = set(["color"])

            if ("CartoonInk" in configuration):
                needtex.add("aux")
                auxbits |= AuxBitplaneAttrib.ABOAuxNormal
                needtexcoord.add("aux")

            if ("AmbientOcclusion" in configuration):
                needtex.add("depth")
                needtex.add("ssao0")
                needtex.add("ssao1")
                needtex.add("ssao2")
                needtex.add("aux")
                auxbits |= AuxBitplaneAttrib.ABOAuxNormal
                needtexcoord.add("ssao2")

            if ("BlurSharpen" in configuration or "DOF" in configuration):
                needtex.add("blur0")
                needtex.add("blur1")
                needtexcoord.add("blur1")

            if ("DOF" in configuration):
                needtex.add("depth")

            if ("FXAA" in configuration):
                needtex.add("fxaa")

            if ("Bloom" in configuration):
                needtex.add("bloom0")
                needtex.add("bloom1")
                needtex.add("bloom2")
                needtex.add("bloom3")
                auxbits |= AuxBitplaneAttrib.ABOGlow
                needtexcoord.add("bloom3")

            if ("ViewGlow" in configuration):
                auxbits |= AuxBitplaneAttrib.ABOGlow

            if ("VolumetricLighting" in configuration):
                needtex.add(configuration["VolumetricLighting"].source)

            for tex in needtex:
                self.makeTexture(tex)

            self.finalQuad = self.manager.renderSceneInto(textures = self.textures, auxbits=auxbits)
            if (self.finalQuad == None):
                self.cleanup()
                return False

            if ("FXAA" in configuration):
                fxaa=self.textures["fxaa"]
                self.fxaa = self.manager.renderQuadInto(colortex=fxaa)
                self.fxaa.setShader(Shader.load(Shader.SL_GLSL, "phase_14/models/shaders/fxaa.vert.glsl", "phase_14/models/shaders/fxaa.frag.glsl"))
                self.fxaa.setShaderInput("sceneTexture", self.textures["color"])

            if ("BlurSharpen" in configuration or "DOF" in configuration):
                blur0=self.textures["blur0"]
                blur1=self.textures["blur1"]
                self.blur.append(self.manager.renderQuadInto(colortex=blur0,div=2))
                self.blur.append(self.manager.renderQuadInto(colortex=blur1))
                self.blur[0].setShaderInput("src", self.textures["color"])
                self.blur[0].setShader(self.loadShader("phase_3/models/shaders/filter-blurx.sha"))
                self.blur[1].setShaderInput("src", blur0)
                self.blur[1].setShader(self.loadShader("phase_3/models/shaders/filter-blury.sha"))

            if ("AmbientOcclusion" in configuration):
                ssao0=self.textures["ssao0"]
                ssao1=self.textures["ssao1"]
                ssao2=self.textures["ssao2"]
                self.ssao.append(self.manager.renderQuadInto(colortex=ssao0))
                self.ssao.append(self.manager.renderQuadInto(colortex=ssao1,div=2))
                self.ssao.append(self.manager.renderQuadInto(colortex=ssao2))
                self.ssao[0].setShaderInput("depth", self.textures["depth"])
                self.ssao[0].setShaderInput("normal", self.textures["aux"])
                self.ssao[0].setShaderInput("random", loader.loadTexture("maps/random.rgb"))
                self.ssao[0].setShader(Shader.make(SSAO_BODY, Shader.SL_Cg))
                self.ssao[1].setShaderInput("src", ssao0)
                self.ssao[1].setShader(self.loadShader("phase_3/models/shaders/filter-blurx.sha"))
                self.ssao[2].setShaderInput("src", ssao1)
                self.ssao[2].setShader(self.loadShader("phase_3/models/shaders/filter-blury.sha"))

            if ("Bloom" in configuration):
                bloomconf = configuration["Bloom"]
                bloom0=self.textures["bloom0"]
                bloom1=self.textures["bloom1"]
                bloom2=self.textures["bloom2"]
                bloom3=self.textures["bloom3"]
                if (bloomconf.size == "large"):
                    scale=8
                    downsampler="phase_3/models/shaders/filter-down4.sha"
                elif (bloomconf.size == "medium"):
                    scale=4
                    downsampler="phase_3/models/shaders/filter-copy.sha"
                else:
                    scale=2
                    downsampler="phase_3/models/shaders/ilter-copy.sha"
                self.bloom.append(self.manager.renderQuadInto(colortex=bloom0, div=2,     align=scale))
                self.bloom.append(self.manager.renderQuadInto(colortex=bloom1, div=scale, align=scale))
                self.bloom.append(self.manager.renderQuadInto(colortex=bloom2, div=scale, align=scale))
                self.bloom.append(self.manager.renderQuadInto(colortex=bloom3, div=scale, align=scale))
                self.bloom[0].setShaderInput("src", self.textures["color"])
                self.bloom[0].setShader(self.loadShader("phase_3/models/shaders/filter-bloomi.sha"))
                self.bloom[1].setShaderInput("src", bloom0)
                self.bloom[1].setShader(self.loadShader(downsampler))
                self.bloom[2].setShaderInput("src", bloom1)
                self.bloom[2].setShader(self.loadShader("phase_3/models/shaders/filter-bloomx.sha"))
                self.bloom[3].setShaderInput("src", bloom2)
                self.bloom[3].setShader(self.loadShader("phase_3/models/shaders/filter-bloomy.sha"))

            texcoords = {}
            texcoordPadding = {}

            for tex in needtexcoord:
                if self.textures[tex].getAutoTextureScale() != ATSNone or \
                                           "HalfPixelShift" in configuration:
                    texcoords[tex] = "l_texcoord_" + tex
                    texcoordPadding["l_texcoord_" + tex] = tex
                else:
                    # Share unpadded texture coordinates.
                    texcoords[tex] = "l_texcoord"
                    texcoordPadding["l_texcoord"] = None

            texcoordSets = list(enumerate(texcoordPadding.keys()))

            text = "//Cg\n"
            text += "void vshader(float4 vtx_position : POSITION,\n"
            text += "  out float4 l_position : POSITION,\n"

            for texcoord, padTex in texcoordPadding.items():
                if padTex is not None:
                    text += "  uniform float4 texpad_tx%s,\n" % (padTex)
                    if ("HalfPixelShift" in configuration):
                        text += "  uniform float4 texpix_tx%s,\n" % (padTex)

            for i, name in texcoordSets:
                text += "  out float2 %s : TEXCOORD%d,\n" % (name, i)

            text += "  uniform float4x4 mat_modelproj)\n"
            text += "{\n"
            text += "  l_position = mul(mat_modelproj, vtx_position);\n"

            for texcoord, padTex in texcoordPadding.items():
                if padTex is None:
                    text += "  %s = vtx_position.xz * float2(0.5, 0.5) + float2(0.5, 0.5);\n" % (texcoord)
                else:
                    text += "  %s = (vtx_position.xz * texpad_tx%s.xy) + texpad_tx%s.xy;\n" % (texcoord, padTex, padTex)

                    if ("HalfPixelShift" in configuration):
                        text += "  %s += texpix_tx%s.xy * 0.5;\n" % (texcoord, padTex)

            text += "}\n"
            
            if ("Exposure" in configuration):
                text += TONEMAP

            text += "void fshader(\n"

            for i, name in texcoordSets:
                text += "  float2 %s : TEXCOORD%d,\n" % (name, i)

            for key in self.textures:
                text += "  uniform sampler2D k_tx" + key + ",\n"

            if ("CartoonInk" in configuration):
                text += "  uniform float4 k_cartoonseparation,\n"
                text += "  uniform float4 k_cartooncolor,\n"
                text += "  uniform float4 texpix_txaux,\n"

            if ("BlurSharpen" in configuration):
                text += "  uniform float4 k_blurval,\n"

            if ("DOF" in configuration):
                text += "  uniform float4 k_dofParams,\n"

            if ("VolumetricLighting" in configuration):
                text += "  uniform float4 k_casterpos,\n"
                text += "  uniform float4 k_vlparams,\n"
                
            if ("Exposure" in configuration):
                text += "  uniform sampler1D k_exposuretex,\n"
                
            text += "  out float4 o_color : COLOR)\n"
            text += "{\n"
            if ("FXAA" in configuration):
                text += "  float4 result = tex2D(k_txfxaa, %s);\n" % (texcoords["color"])
            else:
                text += "  float4 result = tex2D(k_txcolor, %s);\n" % (texcoords["color"])
            if ("Exposure" in configuration):
                #text += "  result = saturate(result);\n"
                text += "  float exposure = tex1D(k_exposuretex, 0).r;result.rgb *= exposure;\n"
            if ("CartoonInk" in configuration):
                text += CARTOON_BODY % {"texcoord" : texcoords["aux"]}
            if ("AmbientOcclusion" in configuration):
                text += "  result *= tex2D(k_txssao2, %s).r;\n" % (texcoords["ssao2"])
            if ("BlurSharpen" in configuration or "DOF" in configuration):
                text += "  float blurFactor;\n"
                if ("DOF" in configuration):
                    text += "  float distance = k_dofParams.x;\n"
                    text += "  float range = k_dofParams.y;\n"
                    text += "  float near = k_dofParams.z;\n"
                    text += "  float far = k_dofParams.w;\n"
                    text += "  float depth = tex2D(k_txdepth, l_texcoord).r;\n"
                    text += "  float sceneZ = (-near * far) / (depth - far);\n"
                    text += "  blurFactor = 1 - saturate(abs(sceneZ - distance) / range);\n"
                    if ("BlurSharpen" in configuration):
                            text += "  blurFactor *= k_blurval.x;\n"
                elif ("BlurSharpen" in configuration):
                    text += "  blurFactor = k_blurval.x;\n"
                text += "  result = lerp(tex2D(k_txblur1, %s), result, blurFactor);\n" % (texcoords["blur1"])
            if ("Bloom" in configuration):
                #text += "  result = saturate(result);\n";
                text += "  float4 bloom = 0.5 * tex2D(k_txbloom3, %s);\n" % (texcoords["bloom3"])
                #if ("Exposure" in configuration):
                #    text += "  bloom *= float4(exposure);\n"
                text += "  result = 1-((1-bloom)*(1-result));\n"
            if ("ViewGlow" in configuration):
                text += "  result.r = result.a;\n"
            if ("VolumetricLighting" in configuration):
                text += "  float decay = 1.0f;\n"
                text += "  float2 curcoord = %s;\n" % (texcoords["color"])
                text += "  float2 lightdir = curcoord - k_casterpos.xy;\n"
                text += "  lightdir *= k_vlparams.x;\n"
                text += "  half4 sample = tex2D(k_txcolor, curcoord);\n"
                text += "  float3 vlcolor = sample.rgb * sample.a;\n"
                text += "  for (int i = 0; i < %s; i++) {\n" % (int(configuration["VolumetricLighting"].numsamples))
                text += "    curcoord -= lightdir;\n"
                text += "    sample = tex2D(k_tx%s, curcoord);\n" % (configuration["VolumetricLighting"].source)
                text += "    sample *= sample.a * decay;//*weight\n"
                text += "    vlcolor += sample.rgb;\n"
                text += "    decay *= k_vlparams.y;\n"
                text += "  }\n"
                text += "  result += float4(vlcolor * k_vlparams.z, 1);\n"
                
            #if ("Exposure" in configuration):
            #    text += "  result.rgb = (result*result*result + result*result + result) / (result*result*result + result*result + result + 1);\n"

            if ("GammaAdjust" in configuration):
                gamma = configuration["GammaAdjust"]
                if gamma == 0.5:
                    text += "  result.rgb = sqrt(result.rgb);\n"
                elif gamma == 2.0:
                    text += "  result.rgb *= result.rgb;\n"
                elif gamma != 1.0:
                    text += "  result.rgb = pow(result.rgb, %ff);\n" % (gamma)

            if ("Inverted" in configuration):
                text += "  result = float4(1, 1, 1, 1) - result;\n"
                
            text += "  o_color = saturate(result);\n"
            text += "}\n"

            shader = Shader.make(text, Shader.SL_Cg)
            if not shader:
                return False
            self.finalQuad.setShader(shader)
            for tex in self.textures:
                self.finalQuad.setShaderInput("tx"+tex, self.textures[tex])

            self.task = taskMgr.add(self.update, "common-filters-update")
			
            messenger.send("CICommonFilters_reconfigure")

        if (changed == "CartoonInk") or fullrebuild:
            if ("CartoonInk" in configuration):
                c = configuration["CartoonInk"]
                self.finalQuad.setShaderInput("cartoonseparation", LVecBase4(c.separation, 0, c.separation, 0))
                self.finalQuad.setShaderInput("cartooncolor", c.color)

        if (changed == "BlurSharpen") or fullrebuild:
            if ("BlurSharpen" in configuration):
                blurval = configuration["BlurSharpen"]
                self.finalQuad.setShaderInput("blurval", LVecBase4(blurval, blurval, blurval, blurval))

        if (changed == "DOF") or fullrebuild:
            if ("DOF" in configuration):
                conf = configuration["DOF"]
                self.finalQuad.setShaderInput("dofParams", LVecBase4(conf.distance, conf.range, conf.near, conf.far))

        if (changed == "Bloom") or fullrebuild:
            if ("Bloom" in configuration):
                bloomconf = configuration["Bloom"]
                intensity = bloomconf.intensity * 3.0
                self.bloom[0].setShaderInput("blend", bloomconf.blendx, bloomconf.blendy, bloomconf.blendz, bloomconf.blendw * 2.0)
                self.bloom[0].setShaderInput("trigger", bloomconf.mintrigger, 1.0/(bloomconf.maxtrigger-bloomconf.mintrigger), 0.0, 0.0)
                self.bloom[0].setShaderInput("desat", bloomconf.desat)
                self.bloom[3].setShaderInput("intensity", intensity, intensity, intensity, intensity)

        if (changed == "VolumetricLighting") or fullrebuild:
            if ("VolumetricLighting" in configuration):
                config = configuration["VolumetricLighting"]
                tcparam = config.density / float(config.numsamples)
                self.finalQuad.setShaderInput("vlparams", tcparam, config.decay, config.exposure, 0.0)

        if (changed == "AmbientOcclusion") or fullrebuild:
            if ("AmbientOcclusion" in configuration):
                config = configuration["AmbientOcclusion"]
                self.ssao[0].setShaderInput("totalStrength", config.totalStrength)
                self.ssao[0].setShaderInput("base", config.base)
                self.ssao[0].setShaderInput("area", config.area)
                self.ssao[0].setShaderInput("falloff", config.falloff)
                self.ssao[0].setShaderInput("numSamples", config.numsamples)
                self.ssao[0].setShaderInput("radius", config.radius)
         
        if (changed == "Exposure") or fullrebuild:
            if ("Exposure" in configuration):
                self.finalQuad.setShaderInput("exposuretex", configuration["Exposure"].exposureTex)

        self.update()
        return True

    def update(self, task = None):
        """Updates the shader inputs that need to be updated every frame.
        Normally, you shouldn't call this, it's being called in a task."""

        if "VolumetricLighting" in self.configuration:
            caster = self.configuration["VolumetricLighting"].caster
            casterpos = LPoint2()
            self.manager.camera.node().getLens().project(caster.getPos(self.manager.camera), casterpos)
            self.finalQuad.setShaderInput("casterpos", LVecBase4(casterpos.getX() * 0.5 + 0.5, (casterpos.getY() * 0.5 + 0.5), 0, 0))
        if task != None:
            return task.cont

    def setFXAA(self):
        fullrebuild = (("FXAA" in self.configuration) == False)
        newconfig = FilterConfig()
        self.configuration["FXAA"] = newconfig
        return self.reconfigure(fullrebuild, "FXAA")

    def delFXAA(self):
        if ("FXAA" in self.configuration):
            del self.configuration["FXAA"]
            return self.reconfigure(True, "FXAA")
        return True
            
    def setExposure(self, exposureTex):
        fullrebuild = (("Exposure" in self.configuration) == False)
        newconfig = FilterConfig()
        newconfig.exposureTex = exposureTex
        self.configuration["Exposure"] = newconfig
        return self.reconfigure(fullrebuild, "Exposure")
        
    def delExposure(self):
        if ("Exposure" in self.configuration):
            del self.configuration["Exposure"]
            return self.reconfigure(True, "Exposure")
        return True

    def setCartoonInk(self, separation=1, color=(0, 0, 0, 1)):
        fullrebuild = (("CartoonInk" in self.configuration) == False)
        newconfig = FilterConfig()
        newconfig.separation = separation
        newconfig.color = color
        self.configuration["CartoonInk"] = newconfig
        return self.reconfigure(fullrebuild, "CartoonInk")

    def delCartoonInk(self):
        if ("CartoonInk" in self.configuration):
            del self.configuration["CartoonInk"]
            return self.reconfigure(True, "CartoonInk")
        return True

    def setBloom(self, blend=(0.3,0.4,0.3,0.0), mintrigger=0.6, maxtrigger=1.0, desat=0.6, intensity=1.0, size="medium"):
        if   (size==0): size="off"
        elif (size==1): size="small"
        elif (size==2): size="medium"
        elif (size==3): size="large"
        if (size=="off"):
            self.delBloom()
            return
        if (maxtrigger==None): maxtrigger=mintrigger+0.8
        oldconfig = self.configuration.get("Bloom", None)
        fullrebuild = True
        if (oldconfig) and (oldconfig.size == size):
            fullrebuild = False
        newconfig = FilterConfig()
        (newconfig.blendx, newconfig.blendy, newconfig.blendz, newconfig.blendw) = blend
        newconfig.maxtrigger = maxtrigger
        newconfig.mintrigger = mintrigger
        newconfig.desat = desat
        newconfig.intensity = intensity
        newconfig.size = size
        self.configuration["Bloom"] = newconfig
        return self.reconfigure(fullrebuild, "Bloom")

    def delBloom(self):
        if ("Bloom" in self.configuration):
            del self.configuration["Bloom"]
            return self.reconfigure(True, "Bloom")
        return True

    def setHalfPixelShift(self):
        fullrebuild = (("HalfPixelShift" in self.configuration) == False)
        self.configuration["HalfPixelShift"] = 1
        return self.reconfigure(fullrebuild, "HalfPixelShift")

    def delHalfPixelShift(self):
        if ("HalfPixelShift" in self.configuration):
            del self.configuration["HalfPixelShift"]
            return self.reconfigure(True, "HalfPixelShift")
        return True

    def setViewGlow(self):
        fullrebuild = (("ViewGlow" in self.configuration) == False)
        self.configuration["ViewGlow"] = 1
        return self.reconfigure(fullrebuild, "ViewGlow")

    def delViewGlow(self):
        if ("ViewGlow" in self.configuration):
            del self.configuration["ViewGlow"]
            return self.reconfigure(True, "ViewGlow")
        return True

    def setInverted(self):
        fullrebuild = (("Inverted" in self.configuration) == False)
        self.configuration["Inverted"] = 1
        return self.reconfigure(fullrebuild, "Inverted")

    def delInverted(self):
        if ("Inverted" in self.configuration):
            del self.configuration["Inverted"]
            return self.reconfigure(True, "Inverted")
        return True

    def setVolumetricLighting(self, caster, numsamples = 32, density = 5.0, decay = 0.1, exposure = 0.1, source = "color"):
        oldconfig = self.configuration.get("VolumetricLighting", None)
        fullrebuild = True
        if (oldconfig) and (oldconfig.source == source) and (oldconfig.numsamples == int(numsamples)):
            fullrebuild = False
        newconfig = FilterConfig()
        newconfig.caster = caster
        newconfig.numsamples = int(numsamples)
        newconfig.density = density
        newconfig.decay = decay
        newconfig.exposure = exposure
        newconfig.source = source
        self.configuration["VolumetricLighting"] = newconfig
        return self.reconfigure(fullrebuild, "VolumetricLighting")

    def delVolumetricLighting(self):
        if ("VolumetricLighting" in self.configuration):
            del self.configuration["VolumetricLighting"]
            return self.reconfigure(True, "VolumetricLighting")
        return True

    def setDepthOfField(self, distance = 20.0, range = 40.0, near = 1.0, far = 1000.0):
        fullrebuild = (("DOF" in self.configuration) == False)
        conf = FilterConfig()
        conf.distance = distance
        conf.range = range
        conf.near = near
        conf.far = far
        self.configuration["DOF"] = conf
        return self.reconfigure(fullrebuild, "DOF")

    def delDepthOfField(self):
        if ("DOF" in self.configuration):
            del self.configuration["DOF"]
            return self.reconfigure(True, "DOF")
        return True

    def setBlurSharpen(self, amount=0.0):
        """Enables the blur/sharpen filter. If the 'amount' parameter is 1.0, it will not have effect.
        A value of 0.0 means fully blurred, and a value higher than 1.0 sharpens the image."""
        fullrebuild = (("BlurSharpen" in self.configuration) == False)
        self.configuration["BlurSharpen"] = amount
        return self.reconfigure(fullrebuild, "BlurSharpen")

    def delBlurSharpen(self):
        if ("BlurSharpen" in self.configuration):
            del self.configuration["BlurSharpen"]
            return self.reconfigure(True, "BlurSharpen")
        return True

    def setAmbientOcclusion(self, numsamples = 16, area = 0.075, base = 0.2, totalStrength = 1.0, radius = 0.0002, falloff = 0.000001):
        fullrebuild = (("AmbientOcclusion" in self.configuration) == False)

        if (not fullrebuild):
            fullrebuild = (numsamples != self.configuration["AmbientOcclusion"].numsamples)

        newconfig = FilterConfig()
        newconfig.numsamples = numsamples
        newconfig.radius = radius
        newconfig.area = area
        newconfig.totalStrength = totalStrength
        newconfig.falloff = falloff
        newconfig.base = base
        self.configuration["AmbientOcclusion"] = newconfig
        return self.reconfigure(fullrebuild, "AmbientOcclusion")

    def delAmbientOcclusion(self):
        if ("AmbientOcclusion" in self.configuration):
            del self.configuration["AmbientOcclusion"]
            return self.reconfigure(True, "AmbientOcclusion")
        return True

    def setGammaAdjust(self, gamma):
        """ Applies additional gamma correction to the image.  1.0 = no correction. """
        old_gamma = self.configuration.get("GammaAdjust", 1.0)
        if old_gamma != gamma:
            self.configuration["GammaAdjust"] = gamma
            return self.reconfigure(True, "GammaAdjust")
        return True

    def delGammaAdjust(self):
        if ("GammaAdjust" in self.configuration):
            old_gamma = self.configuration["GammaAdjust"]
            del self.configuration["GammaAdjust"]
            return self.reconfigure((old_gamma != 1.0), "GammaAdjust")
        return True

    #snake_case alias:
    del_cartoon_ink = delCartoonInk
    set_half_pixel_shift = setHalfPixelShift
    del_half_pixel_shift = delHalfPixelShift
    set_inverted = setInverted
    del_inverted = delInverted
    del_view_glow = delViewGlow
    set_volumetric_lighting = setVolumetricLighting
    del_gamma_adjust = delGammaAdjust
    set_bloom = setBloom
    set_view_glow = setViewGlow
    set_ambient_occlusion = setAmbientOcclusion
    set_cartoon_ink = setCartoonInk
    del_bloom = delBloom
    del_ambient_occlusion = delAmbientOcclusion
    load_shader = loadShader
    set_blur_sharpen = setBlurSharpen
    del_blur_sharpen = delBlurSharpen
    del_volumetric_lighting = delVolumetricLighting
    set_gamma_adjust = setGammaAdjust
