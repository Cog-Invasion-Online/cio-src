# Filename: DisneyCharGlobals.py
# Created by:  blach (21Jun16)

from panda3d.core import Point3

from lib.coginvasion.globals import CIGlobals

MICKEY = 0
MINNIE = 1
PLUTO = 2
SLEEP_DONALD = 3
SAILOR_DONALD = 4
DAISY = 5
GOOFY = 6

PLUTO_STANDUP_TIME = 0.916666666667
SLEEP_DONALD_N2W_TIME = 1.5

MAX_RANGE = 20.0
CHAT_THRESHOLD = 10

CHECK_FOR_PEEPS_RANGE = (5.0, 10.0)
TALK_AGAIN_RANGE = (10.0, 15.0)
LONELY_TIME_RANGE = (10.0, 20.0)
TIMES_LONELY_RANGE = (1, 2)

SHARED_COMMENT_CHANCE = range(1, 70 + 1)
UNIQUE_COMMENT_CHANCE = range(71, 100 + 1)

def getBam(num, mdl):
    return "phase_{0}/models/char/{1}.bam".format(num, mdl)

def getDial(num, name):
    if game.process == 'client':
        return base.loadSfx('phase_{0}/audio/dial/{1}.ogg'.format(num, name))

HOOD2CHAR = {
    CIGlobals.ToontownCentral:    MICKEY,
    CIGlobals.DaisyGardens:       DAISY,
    CIGlobals.DonaldsDreamland:   SLEEP_DONALD,
    CIGlobals.TheBrrrgh:          PLUTO,
    CIGlobals.MinniesMelodyland:  MINNIE,
    CIGlobals.DonaldsDock:        SAILOR_DONALD
}

CHAR_DATA = {

    MICKEY:        (getBam(3, 'mickey-1200'),
                    {'walk':     getBam(3, 'mickey-walk'),
                     'neutral':  getBam(3, 'mickey-wait'),
                     'run':      getBam(3, 'mickey-run')},
                    3.0,
                    'Mickey',
                    True,
                    getDial(3, 'mickey')),

    MINNIE:        (getBam(3, 'minnie-1200'),
                    {'walk':     getBam(3, 'minnie-walk'),
                     'neutral':  getBam(3, 'minnie-wait'),
                     'run':      getBam(3, 'minnie-run')},
                    3.0,
                    'Minnie',
                    True,
                    getDial(3, 'minnie')),

    PLUTO:         (getBam(6, 'pluto-1000'),
                    {'walk':     getBam(6, 'pluto-walk'),
                     'neutral':  getBam(6, 'pluto-neutral'),
                     'sit':      getBam(6, 'pluto-sit'),
                     'stand':    getBam(6, 'pluto-stand')},
                    3.0,
                    'Pluto',
                    False),

    DAISY:         (getBam(4, 'daisyduck_1600'),
                    {'walk':     getBam(4, 'daisyduck_walk'),
                     'neutral':  getBam(4, 'daisyduck_idle')},
                    4.5,
                    'Daisy',
                    True,
                    getDial(4, 'daisy')),


    GOOFY:         (getBam(6, 'TT_G-1500'),
                    {'walk':     getBam(6, 'TT_GWalk'),
                     'neutral':  getBam(6, 'TT_GWait'),
                     'run':      getBam(6, 'TT_GRun')},
                    4.8,
                    'Goofy',
                    False),

    SLEEP_DONALD:  (getBam(6, 'DL_donald-1000'),
                    {'walk':         getBam(6, 'DL_donald-walk'),
                     'neutral':      getBam(6, 'DL_donald-neutral'),
                     'walk2neutral': getBam(6, 'DL_donald-transition'),
                     'neutral2walk': getBam(6, 'DL_donald-transBack')},
                    4.5,
                    'Donald',
                    True,
                    None),

    SAILOR_DONALD: (getBam(6, 'donald-wheel-1000'),
                    {'wheel':    getBam(6, 'donald-wheel-wheel')},
                    4.5,
                    'Donald',
                    False)

}

SHARED_GREETINGS = 0
SHARED_COMMENTS = 1
SHARED_GOODBYES = 2

CHAR_GREETINGS = 3
CHAR_COMMENTS = 4
CHAR_GOODBYES = 5

CHATTER = {
    # Shared stuff
    SHARED_GREETINGS: ['Hi, %s!',
        'Yoo-hoo %s, nice to see you.',
        "I'm glad you're here today!",
        'Well, hello there, %s.'],
    SHARED_COMMENTS: ["That's a great name, %s.",
        'I like your name.',
        'Watch out for the Cogs.',
        'Looks like the trolley is coming!',
        "I need to go to see Goofy to get some pies!",
        'Whew, I just stopped a bunch of Cogs. I need a rest!',
        'Yikes, some of those Cogs are big guys!',
        "You look like you're having fun.",
        "Oh boy, I'm having a good day.",
        "I like what you're wearing.",
        "I think I'll go fishing this afternoon.",
        'Have fun in my neighborhood.',
        'I hope you are enjoying your stay in Toontown!',
        "I heard it's snowing at the Brrrgh.",
        'Have you ridden the trolley today?',
        'I like to meet new people.',
        'Wow, there are lots of Cogs in the Brrrgh.',
        'I love to play tag. Do you?',
        'Trolley games are fun to play.',
        'I like to make people laugh.',
        "It's fun helping my friends.",
        "A-hem, are you lost?  Don't forget your map is in your Shticker Book.",
        'I hear Daisy has planted some new flowers in her garden.',
        'If you press the Ctrl key, you can jump!'],
    SHARED_GOODBYES: ['I have to go now, bye!',
        "I think I'll go play a trolley game.",
        "Well, so long. I'll be seeing you, %s!",
        "I'd better hurry and get to work stopping those Cogs.",
        "It's time for me to get going.",
        'Sorry, but I have to go.',
        'Good-bye.',
        'See you later, %s!',
        "I think I'm going to go practice tossing cupcakes.",
        "I'm going to join a group and stop some Cogs.",
        'It was nice to see you today, %s.',
        "I have a lot to do today. I'd better get busy."],

    # Individual phrases
    CHAR_GREETINGS: {
        MICKEY: ['Welcome to Toontown Central.', "Hi, my name is Mickey. What's yours?"],
        MINNIE: ['Welcome to Melodyland.', "Hi, my name is Minnie. What's yours?"],
        DAISY: ['Welcome to my garden!', "Hello, I'm Daisy. What's your name?", "It's so nice to see you %s!"],
        SLEEP_DONALD: ['Welcome to Dreamland.', "Hi, my name is Donald. What's yours?"]
    },
    CHAR_COMMENTS: {
        MICKEY: ['Hey, have you seen Donald?',
                "I'm going to go watch the fog roll in at Donald's Dock.",
                'If you see my pal Goofy, say hi to him for me.',
                'I hear Daisy has planted some new flowers in her garden.'],
        MINNIE: ['The hills are alive with the sound of music!',
              'You have a cool outfit, %s.',
              'Hey, have you seen Mickey?',
              'If you see my friend Goofy, say hi to him for me.',
              "Wow, there are lots of Cogs near Donald's Dreamland.",
              "I heard it's foggy at the Donald's Dock.",
              "Be sure and try the maze in Daisy Gardens.",
              "I think I'll go catch some tunes.",
              'Hey %s, look at that over there.',
              'I love the sound of music.',
              "I bet you didn't know Melodyland is also called TuneTown!  Hee Hee!",
              'I love to play the Matching Game. Do you?',
              'I like to make people giggle.',
              'Boy, trotting around in heels all day is hard on your feet!',
              'Nice shirt, %s.',
              'Is that a Jellybean on the ground?'],
        DAISY: ['My prize winning flower is at the center of the garden maze.',
              'I just love strolling through the maze.',
              "I haven't seen Goofy all day.",
              'I wonder where Goofy is.',
              "Have you seen Donald? I can't find him anywhere.",
              'If you see my friend Minnie, please say "Hello" to her for me.',
              'The better gardening tools you have the better plants you can grow.',
              "There are far too many Cogs near Donald's Dock.",
              'Watering your garden every day keeps your plants happy.',
              'To grow a Pink Daisy plant a yellow and red Jellybean together.',
              'Yellow daisies are easy to grow, just plant a yellow Jellybean.',
              'If you see sand under a plant it needs water or it will wilt!'],
        SLEEP_DONALD: ['Sometimes this place gives me the creeps.',
              'Be sure and try the maze in Daisy Gardens.',
              "Oh boy, I'm having a good day.",
              'Hey, have you seen Mickey?',
              'If you see my buddy Goofy, say hi to him for me.',
              "I think I'll go fishing this afternoon.",
              "Wow, there are lots of Cogs at Donald's Dock.",
              "Hey, didn't I take you on a boat ride at Donald's Dock?",
              "I haven't seen Daisy all day.",
              'I hear Daisy has planted some new flowers in her garden.',
              'Quack.']
    },
    CHAR_GOODBYES: {
        MICKEY: ["I'm going to MelodyLand to see Minnie!",
                "Gosh, I'm late for my date with Minnie!",
                "Looks like it's time for Pluto's dinner!",
                "I think I'll go swimming at Donald's Dock.",
                "It's time for a nap. I'm going to Dreamland."],
        MINNIE: ["Gosh, I'm late for my date with Mickey!",
                "Looks like it's time for Pluto's dinner.",
                "It's time for a nap. I'm going to Dreamland."],
        DAISY: ["I'm going to Melody Land to see Minnie!",
                "I'm late for my picnic with Donald!",
                "I think I'll go swimming at Donald's Dock.",
                "Oh, I'm a little sleepy. I think I'll go to Dreamland."],
        SLEEP_DONALD: ["I'm going to Melody Land to see Minnie!",
              "Gosh, I'm late for my date with Daisy!",
              "I think I'll go swimming at my dock.",
              "I think I'll take my boat for a spin at my dock."]
    }
}

WALK_POINTS = {

    MICKEY: {'a': (Point3(60.0747, 52.659, 7.41771), ('g', 'h')),
             'b': (Point3(-5.95494, -21.4209, 0), ('m', 'c', 'd', 'e', 'o')),
             'c': (Point3(-5.4999, -40.0779, 0), ('b', 'd', 'e', 'm', 'o')),
             'd': (Point3(9.65957, -20.8311, 0), ('b', 'c', 'e', 'm')),
             'e': (Point3(22.7863, -0.0606082, 0), ('d', 'c', 'l')),
             'f': (Point3(63.1616, -52.7423, 7.439), ('g', 'o')),
             'g': (Point3(81.3877, 9.65348, 7.48232), ('a', 'f', 'n')),
             'h': (Point3(8.7541, 80.5623, 7.42876), ('a', 'k', 'l', 'm')),
             'i': (Point3(-74.6984, 31.4853, 7.42593), ('j')),
             'j': (Point3(-81.5135, -2.68973, 7.43156), ('i', 'm', 'p')),
             'k': (Point3(4.27018, 47.9447, 0), ('h', 'n', 'l', 'm')),
             'l': (Point3(-10.9282, 22.9522, 0), ('k', 'h', 'm', 'n', 'g', 'e')),
             'm': (Point3(-39.1202, 0.618695, 0), ('l', 'k', 'h', 'b', 'd', 'c')),
             'n': (Point3(47.9755, 17.2803, -0.248394), ('g', 'k')),
             'o': (Point3(5.88337, -82.0521, 7.43866), ('b', 'c', 'f', 'p')),
             'p': (Point3(-53.2309, -69.5668, 7.99316), ('j', 'o'))},

    MINNIE: {'a': (Point3(53.334, 71.057, 6.525), ('b', 'r')),
             'b': (Point3(127.756, 58.665, -11.75), ('a', 's', 'c')),
             'c': (Point3(130.325, 15.174, -2.003), ('b', 'd')),
             'd': (Point3(126.173, 7.057, 0.522), ('c', 'e')),
             'e': (Point3(133.843, -6.618, 4.71), ('d',
                    'f',
                    'g',
                    'h')),
             'f': (Point3(116.876, 1.119, 3.304), 'e'),
             'g': (Point3(116.271, -41.568, 3.304), ('e', 'h')),
             'h': (Point3(128.983, -49.656, -0.231), ('e',
                    'g',
                    'i',
                    'j')),
             'i': (Point3(106.024, -75.249, -4.498), 'h'),
             'j': (Point3(135.016, -93.072, -13.376), ('h', 'k', 'z')),
             'k': (Point3(123.966, -100.242, -10.879), ('j', 'l')),
             'l': (Point3(52.859, -109.081, 6.525), ('k', 'm')),
             'm': (Point3(-32.071, -107.049, 6.525), ('l', 'n')),
             'n': (Point3(-40.519, -99.685, 6.525), ('m', 'o')),
             'o': (Point3(-40.245, -88.634, 6.525), ('n', 'p')),
             'p': (Point3(-66.3, -62.192, 6.525), ('o', 'q')),
             'q': (Point3(-66.212, 23.069, 6.525), ('p', 'r')),
             'r': (Point3(-18.344, 69.532, 6.525), ('q', 'a')),
             's': (Point3(91.357, 44.546, -13.475), ('b', 't')),
             't': (Point3(90.355, 6.279, -13.475), ('s', 'u')),
             'u': (Point3(-13.765, 42.362, -14.553), ('t', 'v')),
             'v': (Point3(-52.627, 7.428, -14.553), ('u', 'w')),
             'w': (Point3(-50.654, -54.879, -14.553), ('v', 'x')),
             'x': (Point3(-3.711, -81.819, -14.553), ('w', 'y')),
             'y': (Point3(90.777, -49.714, -13.475), ('z', 'x')),
             'z': (Point3(90.059, -79.426, -13.475), ('j', 'y'))},

    DAISY: {'a': (Point3(64.995, 169.665, 10.027), ('b', 'q')),
             'b': (Point3(48.893, 208.912, 10.027), ('a', 'c')),
             'c': (Point3(5.482, 210.479, 10.03), ('b', 'd')),
             'd': (Point3(-34.153, 203.284, 10.029), ('c', 'e')),
             'e': (Point3(-66.656, 174.334, 10.026), ('d', 'f')),
             'f': (Point3(-55.994, 162.33, 10.026), ('e', 'g')),
             'g': (Point3(-84.554, 142.099, 0.027), ('f', 'h')),
             'h': (Point3(-92.215, 96.446, 0.027), ('g', 'i')),
             'i': (Point3(-63.168, 60.055, 0.027), ('h', 'j')),
             'j': (Point3(-37.637, 69.974, 0.027), ('i', 'k')),
             'k': (Point3(-3.018, 26.157, 0.027), ('j', 'l', 'm')),
             'l': (Point3(-0.711, 46.843, 0.027), 'k'),
             'm': (Point3(26.071, 46.401, 0.027), ('k', 'n')),
             'n': (Point3(30.87, 67.432, 0.027), ('m', 'o')),
             'o': (Point3(93.903, 90.685, 0.027), ('n', 'p')),
             'p': (Point3(88.129, 140.575, 0.027), ('o', 'q')),
             'q': (Point3(53.988, 158.232, 10.027), ('p', 'a'))},

    SLEEP_DONALD: {'a': (Point3(-94.883, -94.024, 0.025), 'b'),
                 'b': (Point3(-13.962, -92.233, 0.025), ('a', 'h')),
                 'c': (Point3(68.417, -91.929, 0.025), ('m', 'g')),
                 'd': (Point3(68.745, 91.227, 0.025), ('k', 'i')),
                 'e': (Point3(4.047, 94.26, 0.025), ('i', 'j')),
                 'f': (Point3(-91.271, 90.987, 0.025), 'j'),
                 'g': (Point3(43.824, -94.129, 0.025), ('c', 'h')),
                 'h': (Point3(13.905, -91.334, 0.025), ('b', 'g')),
                 'i': (Point3(43.062, 88.152, 0.025), ('d', 'e')),
                 'j': (Point3(-48.96, 88.565, 0.025), ('e', 'f')),
                 'k': (Point3(75.118, 52.84, -16.62), ('d', 'l')),
                 'l': (Point3(44.677, 27.091, -15.385), ('k', 'm')),
                 'm': (Point3(77.009, -16.022, -14.975), ('l', 'c'))},

    PLUTO: {'a': (Point3(-110.0, -37.8, 8.6), ('b', 'c')),
             'b': (Point3(-11.9, -128.2, 6.2), ('a', 'c')),
             'c': (Point3(48.9, -14.4, 6.2), ('b', 'a', 'd')),
             'd': (Point3(0.25, 80.5, 6.2), ('c', 'e')),
             'e': (Point3(-83.3, 36.1, 6.2), ('d', 'a'))}
}
