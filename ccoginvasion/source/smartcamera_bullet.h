#ifndef SMARTCAMERA_BULLET_H
#define SMARTCAMERA_BULLET_H

#include "config_ccoginvasion.h"

#include <nodePath.h>

class EXPCL_CCOGINVASION SmartCamera
{
PUBLISHED:
        //SmartCamera();

private:
        NodePath _camera;
        NodePath _avatar;
};

#endif // SMARTCAMERA_BULLET_H