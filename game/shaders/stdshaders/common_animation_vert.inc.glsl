#pragma once

#define HAS_HARDWARE_SKINNING defined(HARDWARE_SKINNING) && NUM_TRANSFORMS > 0

#if HAS_HARDWARE_SKINNING
    uniform mat4 p3d_TransformTable[NUM_TRANSFORMS];
    in vec4 transform_weight;
    #ifdef INDEXED_TRANSFORMS
        in uvec4 transform_index;
    #endif
#endif

void DoHardwareAnimation(inout vec4 finalVertex, inout vec3 finalNormal, vec4 vertexPos, vec3 normal)
{
    #if HAS_HARDWARE_SKINNING

        #ifndef INDEXED_TRANSFORMS
            const uvec4 transform_index = uvec4(0, 1, 2, 3);
        #endif

        mat4 matrix = p3d_TransformTable[transform_index.x] * transform_weight.x
        #if NUM_TRANSFORMS > 1
            + p3d_TransformTable[transform_index.y] * transform_weight.y
        #endif
        #if NUM_TRANSFORMS > 2
            + p3d_TransformTable[transform_index.z] * transform_weight.z
        #endif
        #if NUM_TRANSFORMS > 3
            + p3d_TransformTable[transform_index.w] * transform_weight.w
        #endif
        ;

        finalVertex = matrix * vertexPos;
        #if defined(NEED_WORLD_NORMAL) || defined(NEED_EYE_NORMAL)
            finalNormal = mat3(matrix) * normal;
        #endif

    #endif
}
