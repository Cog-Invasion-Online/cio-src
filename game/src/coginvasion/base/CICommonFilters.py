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

from CIFilterManager import FilterManager
from panda3d.core import LVecBase4, LPoint2
from panda3d.core import Filename, NodePath
from panda3d.core import AuxBitplaneAttrib
from panda3d.core import Texture, Shader, ATSNone
from panda3d.bsp import AUXBITS_NORMAL, AUXBITS_ARME
import os

SSAO_VERT = """#version 330

uniform mat4 p3d_ModelViewProjectionMatrix;
in vec4 p3d_Vertex;
in vec4 texcoord;

out vec2 l_texcoord;

void main()
{
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
    l_texcoord = texcoord.xy;
}

"""
SSAO_PIXEL="""#version 330

#define SAMPLES             8
#define RADIUS              4
#define BIAS                0.005
#define BIAS_OFFSET         0.0001
#define ILLUM_INFLUENCE     0.05
#define ZFAR                3.0
#define ZNEAR               1.0
#define CONTRAST            1.0

#define PI                  3.14159265

vec2 rand(vec2 coord, vec2 size)
{
    float noiseX = fract(sin(dot(coord, vec2(12.9898,78.233))) * 43758.5453) * 2.0f-1.0f;
	float noiseY = fract(sin(dot(coord, vec2(12.9898,78.233)*2.0)) * 43758.5453) * 2.0f-1.0f;

	return vec2(noiseX,noiseY)*0.001;
}

float readDepth(in vec2 coord, sampler2D tex)
{
	return textureLod(tex, vec4(coord, 0, 0)).a * (ZNEAR / ZFAR);
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

float calcAO(vec2 uv, float depth, float dw, float dh, sampler2D tex)
{
	float dd = (1.0-depth)*RADIUS;

	float temp = 0.0;
	float temp2 = 0.0;
	float coordw = uv.x + dw*dd;
	float coordh = uv.y + dh*dd;
	float coordw2 = uv.x - dw*dd;
	float coordh2 = uv.y - dh*dd;
	
	vec2 coord = vec2(coordw , coordh);
	vec2 coord2 = vec2(coordw2, coordh2);
	
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

float DoSSAO( in vec2 uv, in vec2 texelSize, in sampler2D color_depth )
{
    float ao_out = 0.0;
    
	vec2 size = 1.0f / texelSize;
	vec2 noise = rand(uv,size);
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

	vec3 color = tex2D(color_depth,uv).rgb;
	
	vec3 lumcoeff = vec3( 0.2126f, 0.7152f, 0.0722f );
	float lum = dot( color.rgb, lumcoeff );

	ao_out = mix( ao, 1.0f, lum*ILLUM_INFLUENCE );
	ao_out = ((ao_out - 0.5f) * max(CONTRAST, 0.0)) + 0.5f;
    return ao_out;
}

in vec2 l_texcoord;
uniform sampler2D depthSampler;
out vec4 o_color;

void main()
{
    float ssao_out = DoSSAO(l_texcoord, vec2(textureSize(depthSampler, 0)), depthSampler);
    
    vec3 out_col = vec3(ssao_out);
    out_col *= 2.0;
    
    o_color = vec4(out_col, 1.0);
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
        self.ssr = []
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
        
        for ssr in self.ssr:
            ssr.removeNode()
        self.ssr = []
        
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
        return self.textures[tex]

    def reconfigure(self, fullrebuild, changed):
        """ Reconfigure is called whenever any configuration change is made. """

        configuration = self.configuration

        if (fullrebuild):

            self.cleanup()

            if not self.manager.win.gsg.getSupportsBasicShaders():
                return False

            auxbits = 0
			# Color texture is already created at init,
			# we don't need to make it.
            needtex = set()
            needtexcoord = set(["color"])
                
            if ("SSR" in configuration):
                needtex.add("depth")
                needtex.add("aux0")
                needtex.add("aux1")
                needtex.add("ssrreflection")
                auxbits |= (AUXBITS_NORMAL | AUXBITS_ARME) # aux glow for ARME

            if ("AmbientOcclusion" in configuration):
                needtex.add("depth")
                needtex.add("ssao0")
                needtex.add("ssao1")
                needtex.add("ssao2")

            if ("DOF" in configuration):
                needtex.add("blur0")
                needtex.add("blur1")

            if ("DOF" in configuration):
                needtex.add("depth")

            if ("FXAA" in configuration):
                needtex.add("fxaa")

            if ("Bloom" in configuration):
                needtex.add("bloom0")
                needtex.add("bloom1")
                needtex.add("bloom2")
                needtex.add("bloom3")

            for tex in needtex:
                self.makeTexture(tex)

            self.finalQuad = self.manager.renderSceneInto(textures = self.textures, auxbits=auxbits)
            if (self.finalQuad == None):
                self.cleanup()
                return False
                
            if ("SSR" in configuration):
                self.ssr.append(self.manager.renderQuadInto("ssr-reflection", colortex = self.textures["ssrreflection"]))
                
                self.ssr[0].setShader(Shader.load(Shader.SL_GLSL, "resources/phase_14/models/shaders/ssr.vert.glsl",
                                                                  "resources/phase_14/models/shaders/ssr_reflection.frag.glsl"))
                self.ssr[0].setShaderInput("colorSampler", self.textures["color"])
                self.ssr[0].setShaderInput("depthSampler", self.textures["depth"])
                self.ssr[0].setShaderInput("normalSampler", self.textures["aux0"])
                self.ssr[0].setShaderInput("armeSampler", self.textures["aux1"])

            if ("FXAA" in configuration):
                fxaa=self.textures["fxaa"]
                self.fxaa = self.manager.renderQuadInto(colortex=fxaa)
                self.fxaa.setShader(Shader.load(Shader.SL_GLSL, "phase_14/models/shaders/fxaa.vert.glsl", "phase_14/models/shaders/fxaa.frag.glsl"))
                self.fxaa.setShaderInput("sceneTexture", self.textures["color"])

            if ("AmbientOcclusion" in configuration):
                ssao0=self.textures["ssao0"]
                ssao1=self.textures["ssao1"]
                ssao2=self.textures["ssao2"]
                self.ssao.append(self.manager.renderQuadInto(colortex=ssao0))
                self.ssao.append(self.manager.renderQuadInto(colortex=ssao1,div=2))
                self.ssao.append(self.manager.renderQuadInto(colortex=ssao2))
                self.ssao[0].setShaderInput("depthSampler", self.textures["depth"])
                self.ssao[0].setShader(Shader.make(Shader.SL_GLSL, SSAO_VERT, SSAO_PIXEL))
                self.ssao[1].setShaderInput("src", ssao0)
                self.ssao[1].setShader(self.loadShader("phase_3/models/shaders/filter-blurx.sha"))
                self.ssao[2].setShaderInput("src", ssao1)
                self.ssao[2].setShader(self.loadShader("phase_3/models/shaders/filter-blury.sha"))
                
            if ("DOF" in configuration):
                blur0=self.textures["blur0"]
                blur1=self.textures["blur1"]
                self.blur.append(self.manager.renderQuadInto(colortex=blur0,div=2))
                self.blur.append(self.manager.renderQuadInto(colortex=blur1))
                self.blur[0].setShaderInput("src", self.textures["color"])
                self.blur[0].setShader(self.loadShader("phase_3/models/shaders/filter-blurx.sha"))
                self.blur[1].setShaderInput("src", blur0)
                self.blur[1].setShader(self.loadShader("phase_3/models/shaders/filter-blury.sha"))

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
                    downsampler="phase_3/models/shaders/filter-copy.sha"
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

            vtext = "#version 330\n"
            vtext += "uniform mat4 p3d_ModelViewProjectionMatrix;\n"
            vtext += "in vec4 p3d_Vertex;\n"
            vtext += "in vec4 texcoord;\n"
            vtext += "out vec2 l_texcoord;\n"
            vtext += "void main()\n"
            vtext += "{\n"
            vtext += "  gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;\n"
            vtext += "  l_texcoord = texcoord.xy;\n"
            vtext += "}\n"

            ptext = "#version 330\n"
            ptext += "out vec4 outputColor;\n"
            ptext += "in vec2 l_texcoord;\n"

            for key in self.textures:
                ptext += "uniform sampler2D tx_" + key + ";\n"

            if ("DOF" in configuration):
                ptext += "uniform vec4 dofParams;\n"

            ptext += "void main()\n"
            ptext += "{\n"
            if ("FXAA" in configuration):
                ptext += "  vec4 result = texture(tx_fxaa, l_texcoord);\n"
            else:
                ptext += "  vec4 result = texture(tx_color, l_texcoord);\n"
            if ("AmbientOcclusion" in configuration):
                ptext += "  result *= texture(tx_ssao2, l_texcoord).r;\n"
            if ("SSR" in configuration):
                ptext += "  result.rgb += texture(tx_ssrreflection, l_texcoord).rgb;\n"
            if ("DOF" in configuration):
                ptext += "  float blurFactor;\n"
                ptext += "  float distance = dofParams.x;\n"
                ptext += "  float range = dofParams.y;\n"
                ptext += "  float near = dofParams.z;\n"
                ptext += "  float far = dofParams.w;\n"
                ptext += "  float depth = texture(tx_depth, l_texcoord).r;\n"
                ptext += "  float sceneZ = (-near * far) / (depth - far);\n"
                ptext += "  blurFactor = 1 - clamp(abs(sceneZ - distance) / range, 0, 1);\n"
                ptext += "  result = mix(texture(tx_blur1, l_texcoord), result, blurFactor);\n"
            if ("Bloom" in configuration):
                ptext += "  vec3 bloom = texture(tx_bloom3, l_texcoord).rgb;\n"
                ptext += "  result.rgb += bloom.rgb;\n"
                
            ptext += "  outputColor = result;\n"
            ptext += "}\n"

            shader = Shader.make(Shader.SL_GLSL, vtext, ptext)
            if not shader:
                return False
            self.finalQuad.setShader(shader)
            for tex in self.textures:
                self.finalQuad.setShaderInput("tx_"+tex, self.textures[tex])

            self.task = taskMgr.add(self.update, "common-filters-update")
			
            messenger.send("CICommonFilters_reconfigure")
            
        if (changed == "SSR") or fullrebuild:
            if ("SSR" in configuration):
                ssrconf = configuration["SSR"]
                self.ssr[0].setShaderInput("camera", self.manager.camera)
                self.ssr[0].setShaderInput("params", ssrconf.reflParams)

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

        if (changed == "AmbientOcclusion") or fullrebuild:
            if ("AmbientOcclusion" in configuration):
                config = configuration["AmbientOcclusion"]
                self.ssao[0].setShaderInput("totalStrength", config.totalStrength)
                self.ssao[0].setShaderInput("base", config.base)
                self.ssao[0].setShaderInput("area", config.area)
                self.ssao[0].setShaderInput("falloff", config.falloff)
                self.ssao[0].setShaderInput("numSamples", config.numsamples)
                self.ssao[0].setShaderInput("radius", config.radius)

        self.update()
        return True

    def update(self, task = None):
        """Updates the shader inputs that need to be updated every frame.
        Normally, you shouldn't call this, it's being called in a task."""

        if task != None:
            return task.cont

    def enablePostProcess(self):
        self.reconfigure(True, None)

    def disablePostProcess(self):
        self.cleanup()

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
        
    def setSSR(self, raytraceMaxLength = 256.0, raytraceMaxThickness = 0.2,
               reflectionEnhancer = 1.0, blurOffset = (1, 1), blurNum = 3,
               accumBlendRatio = 0.1):
        fullrebuild = (("SSR" in self.configuration) == False)
        newconfig = FilterConfig()
        newconfig.reflParams = (raytraceMaxLength, raytraceMaxThickness, reflectionEnhancer)
        newconfig.blurParams = (blurOffset[0], blurOffset[1], blurNum)
        newconfig.accumBlendRatio = accumBlendRatio
        self.configuration["SSR"] = newconfig
        return self.reconfigure(fullrebuild, "SSR")
        
    def delSSR(self):
        if ("SSR" in self.configuration):
            del self.configuration["SSR"]
            return self.reconfigure(True, "SSR")
        return True

    #snake_case alias:
    set_bloom = setBloom
    set_ambient_occlusion = setAmbientOcclusion
    del_bloom = delBloom
    del_ambient_occlusion = delAmbientOcclusion
    load_shader = loadShader
