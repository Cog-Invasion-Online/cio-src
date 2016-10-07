"""
  
  Filename: ChatBalloon.py
  Created by: blach (09July14)
  
"""

from pandac.PandaModules import NodePath, TextNode, DepthWriteAttrib

class ChatBalloon:
    TEXT_SHIFT = (0.225, -0.05, 1.25)
    TEXT_SHIFT_PROP = 0.08
    NATIVE_WIDTH = 9.8
    MIN_WIDTH = 2.5
    MIN_HEIGHT = 1.0
    BUBBLE_PADDING = 0.4
    BUBBLE_PADDING_PROP = 0.05
    BUTTON_SCALE = 10
    BUTTON_SHIFT = (-0.2, 0, 0.6)

    def __init__(self, model):
        self.model = model

    def generate(self, text, font, textColor=(0,0,0,1), balloonColor=(1,1,1,1),
                 wordWrap = 10.0, button=None):
        root = NodePath('balloon')

        balloon = self.model.copyTo(root)
        top = balloon.find('**/top')
        middle = balloon.find('**/middle')
        bottom = balloon.find('**/bottom')
        
        if top.isEmpty() or middle.isEmpty() or bottom.isEmpty():
            raise StandardError("invalid chat balloon model")

        balloon.setColor(balloonColor)
        if balloonColor[3] < 1.0:
            balloon.setTransparency(1)
       
        t = root.attachNewNode(TextNode('text'))
        t.node().setFont(font)
        t.node().setWordwrap(wordWrap)
        t.node().setText(text)
        t.node().setTextColor(textColor)

        width, height = t.node().getWidth(), t.node().getHeight()
        if height < self.MIN_HEIGHT:
            height = self.MIN_HEIGHT
        bubblePadding = self.BUBBLE_PADDING
        if width == self.MIN_WIDTH:
            bubblePadding /= 2
        else:
            bubblePadding *= 0.75

        t.setAttrib(DepthWriteAttrib.make(0))
        t.setPos(self.TEXT_SHIFT)
        t.setX(t, self.TEXT_SHIFT_PROP*width)
        t.setZ(t, height)

        if button:
            np = button.copyTo(root)
            np.setPos(t, width - bubblePadding, 0, -height + bubblePadding)
            np.setPos(np, self.BUTTON_SHIFT)
            np.setScale(self.BUTTON_SCALE)
            t.setZ(t, bubblePadding * 2)

        if width < self.MIN_WIDTH:
            width = self.MIN_WIDTH
            t.setX(t, width/2)
            t.node().setAlign(TextNode.ACenter)

        width *= 1 + self.BUBBLE_PADDING_PROP
        width += bubblePadding
        balloon.setSx(width/self.NATIVE_WIDTH)
        if button:
            height += bubblePadding * 2
        middle.setSz(height)
        top.setZ(top, height-1)

        return root
