"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file GagGlobals.py
@author Maverick Liberty
@date July 07, 2015

"""

from panda3d.core import VBase4, Point4, Point3
from src.coginvasion.gags.GagType import GagType
from src.coginvasion.npc.DisneyCharGlobals import Mickey, Goofy, Pluto, Donald
from src.coginvasion.globals.CIGlobals import calcAttackDamage

from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.PyDatagramIterator import PyDatagramIterator

from collections import OrderedDict
import types
import math

WholeCreamPie = "Whole Cream Pie"
WholeFruitPie = "Whole Fruit Pie"
CreamPieSlice = "Cream Pie Slice"
FruitPieSlice = "Fruit Pie Slice"
BirthdayCake = "Birthday Cake"
WeddingCake = "Wedding Cake"
TNT = "TNT"
SeltzerBottle = "Seltzer Bottle"
GrandPiano = "Grand Piano"
Safe = "Safe"
BambooCane = "Bamboo Cane"
JugglingBalls = "Juggling Balls"
Megaphone = "Megaphone"
Cupcake = "Cupcake"
TrapDoor = "Trap Door"
Quicksand = "Quicksand"
BananaPeel = "Banana Peel"
Lipstick = "Lipstick"
Foghorn = "Foghorn"
Aoogah = "Aoogah"
ElephantHorn = "Elephant Horn"
Opera = "Opera Singer"
BikeHorn = "Bike Horn"
Whistle = "Whistle"
Bugle = "Bugle"
PixieDust = "Pixie Dust"
FlowerPot = "Flower Pot"
Sandbag = "Sandbag"
Anvil = "Anvil"
Geyser = "Geyser"
BigWeight = "Big Weight"
StormCloud = "Storm Cloud"
WaterGlass = "Glass of Water"
FireHose = "Fire Hose"
SquirtFlower = "Squirting Flower"
WaterGun = "Squirt Gun"
HL2Shotgun = "HL2 Shotgun" # easter egg!
HL2Pistol = "HL2 Pistol"

MajorDrops = [GrandPiano, Safe, BigWeight]
Stunnables = MajorDrops + [TNT]

ToonHealJokes = [['What goes TICK-TICK-TICK-WOOF?', 'A watchdog! '],
 ['Why do male deer need braces?', "Because they have 'buck teeth'!"],
 ['Why is it hard for a ghost to tell a lie?', 'Because you can see right through him.'],
 ['What did the ballerina do when she hurt her foot?', 'She called the toe truck!'],
 ['What has one horn and gives milk?', 'A milk truck!'],
 ["Why don't witches ride their brooms when they're angry?", "They don't want to fly off the handle!"],
 ['Why did the dolphin cross the ocean?', 'To get to the other tide.'],
 ['What kind of mistakes do spooks make?', 'Boo boos.'],
 ['Why did the chicken cross the playground?', 'To get to the other slide!'],
 ['Where does a peacock go when he loses his tail?', 'A retail store.'],
 ["Why didn't the skeleton cross the road?", "He didn't have the guts."],
 ["Why wouldn't they let the butterfly into the dance?", 'Because it was a moth ball.'],
 ["What's gray and squirts jam at you?", 'A mouse eating a doughnut.'],
 ['What happened when 500 hares got loose on the main street?', 'The police had to comb the area.'],
 ["What's the difference between a fish and a piano?", "You can tune a piano, but you can't tuna fish!"],
 ['What do people do in clock factories?', 'They make faces all day.'],
 ['What do you call a blind dinosaur?', "An I-don't-think-he-saurus."],
 ['If you drop a white hat into the Red Sea, what does it become?', 'Wet.'],
 ['Why was Cinderella thrown off the basketball team?', 'She ran away from the ball.'],
 ['Why was Cinderella such a bad player?', 'She had a pumpkin for a coach.'],
 ["What two things can't you have for breakfast?", 'Lunch and dinner.'],
 ['What do you give an elephant with big feet?', 'Big shoes.'],
 ['Where do baby ghosts go during the day?', 'Day-scare centers.'],
 ['What did Snow White say to the photographer?', 'Some day my prints will come.'],
 ["What's Tarzan's favorite song?", 'Jungle bells.'],
 ["What's green and loud?", 'A froghorn.'],
 ["What's worse than raining cats and dogs?", 'Hailing taxis.'],
 ['When is the vet busiest?', "When it's raining cats and dogs."],
 ['What do you call a gorilla wearing ear-muffs?', "Anything you want, he can't hear you."],
 ['Where would you weigh a whale?', 'At a whale-weigh station.'],
 ['What travels around the world but stays in the corner?', 'A stamp.'],
 ['What do you give a pig with a sore throat?', 'Oinkment.'],
 ['What did the hat say to the scarf?', 'You hang around while I go on a head.'],
 ["What's the best parting gift?", 'A comb.'],
 ['What kind of cats like to go bowling?', 'Alley cats.'],
 ["What's wrong if you keep seeing talking animals?", "You're having Disney spells."],
 ['What did one eye say to the other?', 'Between you and me, something smells.'],
 ["What's round, white and giggles?", 'A tickled onion.'],
 ['What do you get when you cross Bambi with a ghost?', 'Bamboo.'],
 ['Why do golfers take an extra pair of socks?', 'In case they get a hole in one.'],
 ['What do you call a fly with no wings?', 'A walk.'],
 ['Who did Frankenstein take to the prom?', 'His ghoul friend.'],
 ['What lies on its back, one hundred feet in the air?', 'A sleeping centipede.'],
 ['How do you keep a bull from charging?', 'Take away his credit card.'],
 ['What do you call a chicken at the North Pole?', 'Lost.'],
 ['What do you get if you cross a cat with a dog?', 'An animal that chases itself.'],
 ['What did the digital watch say to the grandfather clock?', 'Look dad, no hands.'],
 ['Where does Ariel the mermaid go to see movies?', 'The dive-in.'],
 ['What do you call a mosquito with a tin suit?', 'A bite in shining armor.'],
 ['What do giraffes have that no other animal has?', 'Baby giraffes.'],
 ['Why did the man hit the clock?', 'Because the clock struck first.'],
 ['Why did the apple go out with a fig?', "Because it couldn't find a date."],
 ['What do you get when you cross a parrot with a monster?', 'A creature that gets a cracker whenever it asks for one.'],
 ["Why didn't the monster make the football team?", 'Because he threw like a ghoul!'],
 ['What do you get if you cross a Cocker Spaniel with a Poodle and a rooster?', 'A cockapoodledoo!'],
 ['What goes dot-dot-dash-dash-squeak?', 'Mouse code.'],
 ["Why aren't elephants allowed on beaches?", "They can't keep their trunks up."],
 ['What is at the end of everything?', 'The letter G.'],
 ['How do trains hear?', 'Through the engineers.'],
 ['What does the winner of a marathon lose?', 'His breath.'],
 ['Why did the pelican refuse to pay for his meal?', 'His bill was too big.'],
 ['What has six eyes but cannot see?', 'Three blind mice.'],
 ["What works only when it's fired?", 'A rocket.'],
 ["Why wasn't there any food left after the monster party?", 'Because everyone was a goblin!'],
 ['What bird can be heard at mealtimes?', 'A swallow.'],
 ['What goes Oh, Oh, Oh?', 'Santa walking backwards.'],
 ['What has green hair and runs through the forest?', 'Moldy locks.'],
 ['Where do ghosts pick up their mail?', 'At the ghost office.'],
 ['Why do dinosaurs have long necks?', 'Because their feet smell.'],
 ['What do mermaids have on toast?', 'Mermarlade.'],
 ['Why do elephants never forget?', 'Because nobody ever tells them anything.'],
 ["What's in the middle of a jellyfish?", 'A jellybutton.'],
 ['What do you call a very popular perfume?', 'A best-smeller.'],
 ["Why can't you play jokes on snakes?", 'Because you can never pull their legs.'],
 ['Why did the baker stop making donuts?', 'He got sick of the hole business.'],
 ['Why do mummies make excellent spies?', "They're good at keeping things under wraps."],
 ['How do you stop an elephant from going through the eye of a needle?', 'Tie a knot in its tail.'],
 ["What goes 'Ha Ha Ha Thud'?", 'Someone laughing his head off.'],
 ["My friend thinks he's a rubber band.", 'I told him to snap out of it.'],
 ["My sister thinks she's a pair of curtains.", 'I told her to pull herself together!'],
 ['Did you hear about the dentist that married the manicurist?', 'Within a month they were fighting tooth and nail.'],
 ['Why do hummingbirds hum?', "Because they don't know the words."],
 ['Why did the baby turkey bolt down his food?', 'Because he was a little gobbler.'],
 ['Where did the whale go when it was bankrupt?', 'To the loan shark.'],
 ['How does a sick sheep feel?', 'Baah-aahd.'],
 ["What's gray, weighs 10 pounds and squeaks?", 'A mouse that needs to go on a diet.'],
 ['Why did the dog chase his tail?', 'To make ends meet.'],
 ['Why do elephants wear running shoes?', 'For jogging of course.'],
 ['Why are elephants big and gray?', "Because if they were small and yellow they'd be canaries."],
 ['If athletes get tennis elbow what do astronauts get?', 'Missile toe.'],
 ['Did you hear about the man who hated Santa?', 'He suffered from Claustrophobia.'],
 ['Why did ' + Donald + ' sprinkle sugar on his pillow?', 'Because he wanted to have sweet dreams.'],
 ['Why did ' + Goofy + ' take his comb to the dentist?', 'Because it had lost all its teeth.'],
 ['Why did ' + Goofy + ' wear his shirt in the bath?', 'Because the label said wash and wear.'],
 ['Why did the dirty chicken cross the road?', 'For some fowl purpose.'],
 ["Why didn't the skeleton go to the party?", 'He had no body to go with.'],
 ['Why did the burglar take a shower?', 'To make a clean getaway.'],
 ['Why does a sheep have a woolly coat?', "Because he'd look silly in a plastic one."],
 ['Why do potatoes argue all the time?', "They can't see eye to eye."],
 ['Why did ' + Pluto + ' sleep with a banana peel?', 'So he could slip out of bed in the morning.'],
 ['Why did the mouse wear brown sneakers?', 'His white ones were in the wash.'],
 ['Why are false teeth like stars?', 'They come out at night.'],
 ['Why are Saturday and Sunday so strong?', 'Because the others are weekdays.'],
 ['Why did the archaeologist go bankrupt?', 'Because his career was in ruins.'],
 ['What do you get if you cross the Atlantic on the Titanic?', 'Very wet.'],
 ['What do you get if you cross a chicken with cement?', 'A brick-layer.'],
 ['What do you get if you cross a dog with a phone?', 'A golden receiver.'],
 ['What do you get if you cross an elephant with a shark?', 'Swimming trunks with sharp teeth.'],
 ['What did the tablecloth say to the table?', "Don't move, I've got you covered."],
 ['Did you hear about the time ' + Goofy + ' ate a candle?', 'He wanted a light snack.'],
 ['What did the balloon say to the pin?', 'Hi Buster.'],
 ['What did the big chimney say to the little chimney?', "You're too young to smoke."],
 ['What did the carpet say to the floor?', 'I got you covered.'],
 ['What did the necklace say to the hat?', "You go ahead, I'll hang around."],
 ['What goes zzub-zzub?', 'A bee flying backwards.'],
 ['How do you communicate with a fish?', 'Drop him a line.'],
 ["What do you call a dinosaur that's never late?", 'A prontosaurus.'],
 ['What do you get if you cross a bear and a skunk?', 'Winnie-the-phew.'],
 ['How do you clean a tuba?', 'With a tuba toothpaste.'],
 ['What do frogs like to sit on?', 'Toadstools.'],
 ['Why was the math book unhappy?', 'It had too many problems.'],
 ['Why was the school clock punished?', 'It tocked too much.'],
 ["What's a polygon?", 'A dead parrot.'],
 ['What needs a bath and keeps crossing the street?', 'A dirty double crosser.'],
 ['What do you get if you cross a camera with a crocodile?', 'A snap shot.'],
 ['What do you get if you cross an elephant with a canary?', 'A very messy cage.'],
 ['What do you get if you cross a jeweler with a plumber?', 'A ring around the bathtub.'],
 ['What do you get if you cross an elephant with a crow?', 'Lots of broken telephone poles.'],
 ['What do you get if you cross a plum with a tiger?', 'A purple people eater.'],
 ["What's the best way to save water?", 'Dilute it.'],
 ["What's a lazy shoe called?", 'A loafer.'],
 ["What's green, noisy and dangerous?", 'A thundering herd of cucumbers.'],
 ['What color is a shout?', 'Yellow!'],
 ['What do you call a sick duck?', 'A mallardy.'],
 ["What's worse then a giraffe with a sore throat?", "A centipede with athlete's foot."],
 ['What goes ABC...slurp...DEF...slurp?', 'Someone eating alphabet soup.'],
 ["What's green and jumps up and down?", 'Lettuce at a dance.'],
 ["What's a cow after she gives birth?", 'De-calf-inated.'],
 ['What do you get if you cross a cow and a camel?', 'Lumpy milk shakes.'],
 ["What's white with black and red spots?", 'A Dalmatian with measles.'],
 ["What's brown has four legs and a trunk?", 'A mouse coming back from vacation.'],
 ["What does a skunk do when it's angry?", 'It raises a stink.'],
 ["What's gray, weighs 200 pounds and says, Here Kitty, kitty?", 'A 200 pound mouse.'],
 ["What's the best way to catch a squirrel?", 'Climb a tree and act like a nut.'],
 ["What's the best way to catch a rabbit?", 'Hide in a bush and make a noise like lettuce.'],
 ['What do you call a spider that just got married?', 'A newly web.'],
 ['What do you call a duck that robs banks?', 'A safe quacker.'],
 ["What's furry, meows and chases mice underwater?", 'A catfish.'],
 ["What's a funny egg called?", 'A practical yolker.'],
 ["What's green on the outside and yellow inside?", 'A banana disguised as a cucumber.'],
 ['What did the elephant say to the lemon?', "Let's play squash."],
 ['What weighs 4 tons, has a trunk and is bright red?', 'An embarrassed elephant.'],
 ["What's gray, weighs 4 tons, and wears glass slippers?", 'Cinderelephant.'],
 ["What's an elephant in a fridge called?", 'A very tight squeeze.'],
 ['What did the elephant say to her naughty child?', 'Tusk!  Tusk!'],
 ['What did the peanut say to the elephant?', "Nothing -- Peanuts can't talk."],
 ['What do elephants say when they bump into each other?', "Small world, isn't it?"],
 ['What did the cashier say to the register?', "I'm counting on you."],
 ['What did the flea say to the other flea?', 'Shall we walk or take the cat?'],
 ['What did the big hand say to the little hand?', 'Got a minute.'],
 ['What does the sea say to the sand?', 'Not much.  It usually waves.'],
 ['What did the stocking say to the shoe?', 'See you later, I gotta run.'],
 ['What did one tonsil say to the other tonsil?', 'It must be spring, here comes a swallow.'],
 ['What did the soil say to the rain?', 'Stop, or my name is mud.'],
 ['What did the puddle say to the rain?', 'Drop in sometime.'],
 ['What did the bee say to the rose?', 'Hi, bud.'],
 ['What did the appendix say to the kidney?', "The doctor's taking me out tonight."],
 ['What did the window say to the venetian blinds?', "If it wasn't for you it'd be curtains for me."],
 ['What did the doctor say to the sick orange?', 'Are you peeling well?'],
 ['What do you get if you cross a chicken with a banjo?', 'A self-plucking chicken.'],
 ['What do you get if you cross a hyena with a bouillon cube?', 'An animal that makes a laughing stock of itself.'],
 ['What do you get if you cross a rabbit with a spider?', 'A hare net.'],
 ['What do you get if you cross a germ with a comedian?', 'Sick jokes.'],
 ['What do you get if you cross a hyena with a mynah bird?', 'An animal that laughs at its own jokes.'],
 ['What do you get if you cross a railway engine with a stick of gum?', 'A chew-chew train.'],
 ['What would you get if you crossed an elephant with a computer?', 'A big know-it-all.'],
 ['What would you get if you crossed an elephant with a skunk?', 'A big stinker.'],
 ['Why did ' + Mickey + ' take a trip to outer space?', 'He wanted to find ' + Pluto + '.']]

Throw = "Throw"
Squirt = "Squirt"
Drop = "Drop"
Sound = "Sound"
Lure = "Lure"
ToonUp = "Toon-Up"
Trap = "Trap"

# Data that should be able to be quickly picked up by the client and server.
# Values: [default current supply, default max supply, default damage (or health), and, if necessary, toon-up amount.
gagData = {
    HL2Shotgun : {'minDamage': 40,
                  'maxDamage': 60,
                  'minMaxSupply': 24,
                  'maxSupply': 32,
                  'supply': 32,
                  'track': Trap},
    HL2Pistol : {'minDamage': 5,
                 'maxDamage': 8,
                 'minMaxSupply': 100,
                 'maxSupply': 150,
                 'supply': 150,
                 'track': Trap},
    BirthdayCake : {'health': 10,
        'minDamage' : 48, 
        'maxDamage': 100,
        'minMaxSupply' : 3,
        'maxSupply': 3, 
        'supply': 3, 
    'track' : Throw},
    TNT : {'minDamage' : 90, 
        'maxDamage': 180, 
        'maxSupply': 10, 
        'supply': 10, 
    'track' : Trap},
    FireHose : {'health': 6,
        'minDamage' : 3,
        'maxDamage' : 5,
        'minMaxSupply' : 50,
        'maxSupply' : 100,
        'supply' : 100,
    'track' : Squirt},
    Geyser : {'damage': 105, 
        'maxSupply': 1, 
        'supply': 1, 
    'track' : Squirt},
    BananaPeel : {'minDamage': 10,
        'maxDamage' : 12,
        'minMaxSupply' : 5, 
        'maxSupply': 20, 
        'supply': 5, 
    'track' : Trap},
    Lipstick : {'healRange': (25, 30),
        'minMaxSupply' : 5, 
        'maxSupply': 20, 
        'supply': 5, 
    'track' : ToonUp},
    Anvil : {'damage': 30,
        'minMaxSupply' : 5,
        'maxSupply': 20, 
        'supply': 5, 
    'track' : Drop},
    WaterGun : {'health': 2,
        'minDamage' : 3,
        'maxDamage': 4, 
        'minMaxSupply': 50,
        'maxSupply' : 100, 
        'supply': 100, 
    'track' : Squirt},
    JugglingBalls : {'healRange': (90, 120),
        'maxSupply': 3, 
        'supply': 3, 
    'track' : ToonUp},
    Safe : {'damage': 60,
        'minMaxSupply' : 3,
        'maxSupply': 7, 
        'supply': 3, 
    'track' : Drop},
    WholeCreamPie : {'health': 5, 
        'minDamage': 36,
        'maxDamage' : 40, 
        'minMaxSupply': 50,
        'maxSupply' : 50, 
        'supply': 3, 
    'track' : Throw},
    WholeFruitPie : {'health': 3,
        'minDamage' : 24,
        'damage': 27, 
        'minMaxSupply' : 5,
        'maxSupply': 15, 
        'supply': 5,
    'track' : Throw},
    SquirtFlower : {'minDamage': 3, 
        'maxDamage' : 4,
        'minMaxSupply' : 10,
        'maxSupply' : 30,
        'supply': 10, 
    'track' : Squirt},
    BikeHorn : {'minDamage': 3,
        'maxDamage' : 4,
        'minMaxSupply' : 10, 
        'maxSupply': 30, 
        'supply': 10, 
    'track' : Sound},
    TrapDoor : {'minDamage' : 60,
        'maxDamage': 70, 
        'minMaxSupply' : 3,
        'maxSupply': 5, 
        'supply': 3, 
    'track' : Trap},
    FlowerPot : {'damage' : 10,
        'minMaxSupply' : 10,
        'maxSupply': 30, 
        'supply': 10, 
    'track' : Drop},
    Aoogah : {'minDamage': 14,
        'maxDamage' : 16,
        'minMaxSupply' : 5, 
        'maxSupply': 15, 
        'supply': 5, 
    'track' : Sound},
    Megaphone : {'healRange': (10, 20),
        'minMaxSupply' : 5,
        'maxSupply': 25, 
        'supply': 5, 
    'track' : ToonUp},
    Opera : {'damage': 90, 
        'maxSupply': 1, 
        'supply': 1, 
    'track' : Sound},
    BambooCane : {'healRange': (40, 45),
        'minMaxSupply' : 5,
        'maxSupply' : 15,
        'supply': 5, 
    'track' : ToonUp},
    Cupcake : {'health': 1, 
        'minDamage' : 4, 
        'maxDamage': 6,
        'minMaxSupply' : 10,
        'maxSupply': 30, 
        'supply': 10, 
    'track' : Throw},
    Bugle : {'minDamage': 9,
        'maxDamage' : 11,
        'minMaxSupply' : 5, 
        'maxSupply': 20,
        'supply': 5, 
    'track' : Sound},
    Sandbag : {'damage': 18,
        'minMaxSupply' : 5, 
        'maxSupply': 25, 
        'supply': 5, 
    'track' : Drop},
    WaterGlass : {'health': 2, 
        'minDamage': 6, 
        'maxDamage' : 8,
        'minMaxSupply': 5, 
        'maxSupply': 25, 
        'supply' : 5,
    'track' : Squirt},
    SeltzerBottle : {'health': 5,
        'minDamage' : 18,
        'maxDamage' : 21,
        'minMaxSupply' : 5,
        'maxSupply' : 15,
        'supply' : 10, 
    'track' : Squirt},
    PixieDust : {'healRange': (50, 70),
        'minMaxSupply' : 3,
        'maxSupply': 7, 
        'supply': 3, 
    'track' : ToonUp},
    Foghorn : {'minDamage': 25,
        'maxDamage' : 50, 
        'maxSupply': 3, 
        'supply': 3, 
    'track' : Sound},
    GrandPiano : {'minDamage': 85,
        'maxDamage' : 170,
        'maxSupply' : 3,
        'supply' : 3, 
    'track' : Drop},
    StormCloud : {'minDamage': 36,
        'maxDamage' : 80, 
        'maxSupply': 3, 
        'supply': 3,
    'track' : Squirt},
    WeddingCake : {'health': 25, 
        'damage': 120, 
        'maxSupply': 3, 
        'supply': 3, 
    'track' : Throw},
    ElephantHorn : {'minDamage': 19,
        'maxDamage' : 21, 
        'minMaxSupply': 3,
        'maxSupply' : 7, 
        'supply': 3, 
    'track' : Sound},
    Whistle : {'minDamage': 5,
        'maxDamage' : 7,
        'minMaxSupply' : 5,
        'maxSupply' : 25, 
        'supply': 5, 
    'track' : Sound},
    FruitPieSlice : {'health': 1, 
        'minDamage' : 8, 
        'maxDamage': 10,
        'minMaxSupply' : 5, 
        'maxSupply': 25, 
        'supply': 5, 
    'track' : Throw},
    Quicksand : {'minDamage': 45, 
        'maxDamage' : 50,
        'minMaxSupply': 3, 
        'maxSupply': 10, 
        'supply' : 3,
    'track' : Trap},
    CreamPieSlice : {'health': 2,
        'minDamage' : 14,
        'maxDamage': 17,
        'minMaxSupply' : 5, 
        'maxSupply': 20, 
        'supply': 5, 
    'track' : Throw},
    BigWeight : {'damage': 45,
        'minMaxSupply' : 5,
        'maxSupply' : 15, 
        'supply': 5, 
    'track' : Drop},
}

InventoryIconByName = {WholeCreamPie : '**/inventory_creampie',
 BirthdayCake : '**/inventory_cake',
 CreamPieSlice : '**/inventory_cream_pie_slice',
 TNT : '**/inventory_tnt',
 SeltzerBottle : '**/inventory_seltzer_bottle',
 WholeFruitPie : '**/inventory_fruitpie',
 WeddingCake : '**/inventory_wedding',
 FruitPieSlice : '**/inventory_fruit_pie_slice',
 GrandPiano : '**/inventory_piano',
 BambooCane : '**/inventory_bamboo_cane',
 JugglingBalls : '**/inventory_juggling_cubes',
 Safe : '**/inventory_safe_box',
 Megaphone : '**/inventory_megaphone',
 Cupcake : '**/inventory_tart',
 TrapDoor : '**/inventory_trapdoor',
 Quicksand : '**/inventory_quicksand_icon',
 Lipstick : '**/inventory_lipstick',
 Foghorn : '**/inventory_fog_horn',
 Aoogah : '**/inventory_aoogah',
 ElephantHorn : '**/inventory_elephant',
 Opera : '**/inventory_opera_singer',
 BikeHorn : '**/inventory_bikehorn',
 Whistle : '**/inventory_whistle',
 Bugle : '**/inventory_bugle',
 PixieDust : '**/inventory_pixiedust',
 Anvil : '**/inventory_anvil',
 FlowerPot : '**/inventory_flower_pot',
 Sandbag : '**/inventory_sandbag',
 Geyser : '**/inventory_geyser',
 BigWeight : '**/inventory_weight',
 StormCloud : '**/inventory_storm_cloud',
 BananaPeel : '**/inventory_bannana_peel',
 WaterGlass : '**/inventory_glass_of_water',
 WaterGun : '**/inventory_water_gun',
 FireHose : '**/inventory_firehose',
 SquirtFlower : '**/inventory_squirt_flower',
 HL2Shotgun : '**/inventory_water_gun',
 HL2Pistol : '**/inventory_water_gun'}

TrackIdByName = {Throw : GagType.THROW,
                 Squirt : GagType.SQUIRT,
                 Drop : GagType.DROP,
                 Sound : GagType.SOUND,
                 Lure : GagType.LURE,
                 ToonUp : GagType.TOON_UP,
                 Trap : GagType.TRAP}
TrackColorByName = {ToonUp : (211 / 255.0, 148 / 255.0, 255 / 255.0),
 Trap : (249 / 255.0, 255 / 255.0, 93 / 255.0),
 Lure : (79 / 255.0, 190 / 255.0, 76 / 255.0),
 Sound : (93 / 255.0, 108 / 255.0, 239 / 255.0),
 Throw : (255 / 255.0, 145 / 255.0, 66 / 255.0),
 Squirt : (255 / 255.0, 65 / 255.0, 199 / 255.0),
 Drop : (67 / 255.0, 243 / 255.0, 255 / 255.0)}
Type2TrackName = {GagType.TOON_UP : 0, GagType.TRAP : 1, GagType.LURE : 2, GagType.SOUND : 3, GagType.THROW : 4, GagType.SQUIRT : 5, GagType.DROP : 6}
TrackNameById = OrderedDict({GagType.TOON_UP : ToonUp, GagType.TRAP : Trap, GagType.LURE : Lure,
                             GagType.SOUND : Sound, GagType.THROW : Throw, GagType.SQUIRT : Squirt, GagType.DROP : Drop})
#TrackGagNamesByTrackName = {Throw : [Cupcake,
#  FruitPieSlice,
#  CreamPieSlice,
#  WholeFruitPie,
#  WholeCreamPie,
#  BirthdayCake,
#  WeddingCake],
# ToonUp : [Megaphone,
#  Lipstick,
#  BambooCane,
#  PixieDust,
#  JugglingBalls],
# Sound : [BikeHorn,
#  Whistle,
#  Bugle,
#  Aoogah,
#  ElephantHorn,
#  Foghorn,
#  Opera],
# Drop : [FlowerPot,
#  Sandbag,
#  Anvil,
#  BigWeight,
#  Safe,
#  GrandPiano],
# Squirt : [SquirtFlower,
#  WaterGlass,
#  WaterGun,
#  SeltzerBottle,
#  FireHose,
#  StormCloud,
#  Geyser],
# Trap : [BananaPeel,
#  Quicksand,
#  TrapDoor,
#  TNT,
#  HL2Shotgun],
# Lure : []}

TrackGagNamesByTrackName = {Throw: [WholeCreamPie], ToonUp: [], Lure: [], Sound: [], Drop: [], Squirt: [], Trap: [HL2Shotgun, HL2Pistol, TNT]}

TrackExperienceAmounts = {
    Throw : [10, 50, 400, 2000, 6000, 10000],
    ToonUp: [20, 200, 800, 2000, 6000], # 10000
    Sound : [40, 200, 1000, 2500, 7500, 10000],
    Drop: [20, 100, 500, 2000, 6000, 10000],
    Trap: [20, 800, 2000, 6000, 10000],#100, 800, 2000, 6000, 10000],
    Squirt: [10, 50, 400, 2000, 6000, 10000],
    Lure: [20, 100, 800, 2000, 6000, 10000]
}

def getTrackHighestExperience(track):
    exps = TrackExperienceAmounts[track]
    return exps[len(exps) - 1]

def calculateMaxSupply(avatar, name, data):
    """ This calculates the max supply an avatar can hold with their experience """
    maxSupply = data.get('maxSupply')
    minMaxSupply = maxSupply
    
    if 'minMaxSupply' in data.keys():
        minMaxSupply = data.get('minMaxSupply')
    
    if not avatar is None and minMaxSupply != maxSupply:
        track = data.get('track')
        trackExp = avatar.trackExperience.get(track)
        
        if trackExp == 0:
            return int(minMaxSupply)
        elif trackExp >= MaxedTrackExperiences[track]:
            return int(maxSupply)
        
        trackExperiences = TrackExperienceAmounts.get(track)
        gagIndex = TrackGagNamesByTrackName.get(track).index(name)
        unlockAtExp = float(trackExperiences[gagIndex])
        
        increaseEvery = float(unlockAtExp / maxSupply)
        increaseAmt = (float(trackExp - unlockAtExp) / increaseEvery)
        
        if (minMaxSupply + increaseAmt) > maxSupply:
            return int(maxSupply)
        else:
            return int(minMaxSupply + increaseAmt)
    elif minMaxSupply == maxSupply:
        return int(maxSupply)
    else:
        return int(minMaxSupply)

def calcBaseDamage(avatar, name, data):
    track = data.get('track')
    trackExp = avatar.trackExperience.get(track)
        
    minDamage = float(data.get('minDamage'))
    maxDamage = float(data.get('maxDamage'))
    gagIndex = TrackGagNamesByTrackName.get(track).index(name)
    unlockAtExp = float(TrackExperienceAmounts.get(track)[gagIndex])
    nextGagUnlockExp = unlockAtExp
        
    if (gagIndex + 1) < len(TrackExperienceAmounts.get(track)):
        nextGagUnlockExp = float(TrackExperienceAmounts.get(track)[gagIndex + 1])
        
    scaleDmgEvery = float((nextGagUnlockExp - unlockAtExp) / (maxDamage - minDamage))
    earnedExpSinceUnlock = float(trackExp - unlockAtExp)
        
    if scaleDmgEvery == 0:
        baseDmg = maxDamage
    else:
        dmgAdditions = math.ceil(earnedExpSinceUnlock / scaleDmgEvery)
            
        if (minDamage + dmgAdditions) > maxDamage:
            baseDmg = maxDamage
        else:
            baseDmg = float(minDamage + dmgAdditions)

    return baseDmg

def calculateDamage(avId, name, data):
    """ This calculates the damage a gag will do on a Cog (This is an AI-side method) """
    if type(avId) is int:
        avatar = base.air.doId2do.get(avId, None)
    else:
        avatar = avId

    baseDmg = 0
    
    if 'damage' in data.keys():
        baseDmg = float(data.get('damage'))
    elif 'minDamage' in data.keys():
        baseDmg = calcBaseDamage(avatar, name, data)

    dist = data.get('distance', 10)
    ramp = calcAttackDamage(dist, baseDmg)

    return ramp

# These are the splat scales
splatSizes = {
    WholeCreamPie: 0.5, WholeFruitPie: 0.45,
    CreamPieSlice: 0.35, BirthdayCake: 0.6,
    WeddingCake: 0.7, FruitPieSlice: 0.35,
    SeltzerBottle: 0.6, Cupcake: 0.25,
    WaterGlass: 0.35, WaterGun : 0.35,
    FireHose: 0.6, SquirtFlower: 0.2
}

# Let's define some gag sounds.
WHOLE_PIE_SPLAT_SFX = "phase_4/audio/sfx/AA_wholepie_only.ogg"
SLICE_SPLAT_SFX = "phase_5/audio/sfx/AA_slice_only.ogg"
TART_SPLAT_SFX = "phase_3.5/audio/sfx/AA_tart_only.ogg"
PIE_WOOSH_SFX = "phase_3.5/audio/sfx/AA_pie_throw_only.ogg"
WEDDING_SPLAT_SFX = "phase_5/audio/sfx/AA_throw_wedding_cake_cog.ogg"
SELTZER_SPRAY_SFX = "phase_5/audio/sfx/AA_squirt_seltzer.ogg"
SELTZER_HIT_SFX = "phase_4/audio/sfx/Seltzer_squirt_2dgame_hit.ogg"
SELTZER_MISS_SFX = "phase_4/audio/sfx/AA_squirt_seltzer_miss.ogg"
PIANO_DROP_SFX = "phase_5/audio/sfx/AA_drop_piano.ogg"
PIANO_MISS_SFX = "phase_5/audio/sfx/AA_drop_piano_miss.ogg"
SAFE_DROP_SFX = "phase_5/audio/sfx/AA_drop_safe.ogg"
SAFE_MISS_SFX = "phase_5/audio/sfx/AA_drop_safe_miss.ogg"
WEIGHT_DROP_SFX = "phase_5/audio/sfx/AA_drop_bigweight.ogg"
WEIGHT_MISS_SFX = "phase_5/audio/sfx/AA_drop_bigweight_miss.ogg"
ANVIL_DROP_SFX = "phase_5/audio/sfx/AA_drop_anvil.ogg"
ANVIL_MISS_SFX = "phase_4/audio/sfx/AA_drop_anvil_miss.ogg"
BAG_DROP_SFX = "phase_5/audio/sfx/AA_drop_sandbag.ogg"
BAG_MISS_SFX = "phase_5/audio/sfx/AA_drop_sandbag_miss.ogg"
POT_DROP_SFX = "phase_5/audio/sfx/AA_drop_flowerpot.ogg"
POT_MISS_SFX = "phase_5/audio/sfx/AA_drop_flowerpot_miss.ogg"
BAMBOO_CANE_SFX = "phase_5/audio/sfx/AA_heal_happydance.ogg"
JUGGLE_SFX = "phase_5/audio/sfx/AA_heal_juggle.ogg"
SMOOCH_SFX = "phase_5/audio/sfx/AA_heal_smooch.ogg"
TELLJOKE_SFX = "phase_5/audio/sfx/AA_heal_telljoke.ogg"
TRAP_DOOR_SFX = "phase_5/audio/sfx/TL_trap_door.ogg"
QUICKSAND_SFX = "phase_5/audio/sfx/TL_quicksand.ogg"
BANANA_SFX = "phase_5/audio/sfx/TL_banana.ogg"
FALL_SFX = "phase_5/audio/sfx/Toon_bodyfall_synergy.ogg"
FOG_APPEAR_SFX = "phase_5/audio/sfx/mailbox_full_wobble.ogg"
FOG_SFX = "phase_5/audio/sfx/SZ_DD_foghorn.ogg"
ELEPHANT_APPEAR_SFX = "phase_5/audio/sfx/toonbldg_grow.ogg"
ELEPHANT_SFX = "phase_5/audio/sfx/AA_sound_elephant.ogg"
AOOGAH_APPEAR_SFX = "phase_5/audio/sfx/TL_step_on_rake.ogg"
AOOGAH_SFX = "phase_5/audio/sfx/AA_sound_aoogah.ogg"
OPERA_SFX = "phase_5/audio/sfx/AA_sound_Opera_Singer.ogg"
OPERA_HIT_SFX = "phase_5/audio/sfx/AA_sound_Opera_Singer_Cog_Glass.ogg"
BIKE_HORN_APPEAR_SFX = "phase_5/audio/sfx/MG_tag_1.ogg"
BIKE_HORN_SFX = "phase_5/audio/sfx/AA_sound_bikehorn.ogg"
WHISTLE_APPEAR_SFX = "phase_5/audio/sfx/LB_receive_evidence.ogg"
WHISTLE_SFX = "phase_4/audio/sfx/AA_sound_whistle.ogg"
BUGLE_APPEAR_SFX = "phase_4/audio/sfx/m_match_trumpet.ogg"
BUGLE_SFX = "phase_5/audio/sfx/AA_sound_bugle.ogg"
PIXIE_DUST_SFX = "phase_5/audio/sfx/AA_heal_pixiedust.ogg"
GEYSER_HIT_SFX = "phase_5/audio/sfx/AA_squirt_Geyser.ogg"
CLOUD_HIT_SFX = "phase_5/audio/sfx/AA_throw_stormcloud.ogg"
CLOUD_MISS_SFX = "phase_5/audio/sfx/AA_throw_stormcloud_miss.ogg"
SPIT_SFX = "phase_5/audio/sfx/AA_squirt_glasswater.ogg"
WATERGUN_SFX = "phase_5/audio/sfx/AA_squirt_neonwatergun.ogg"
FIREHOSE_SFX = "phase_5/audio/sfx/firehose_spray.ogg"
FLOWER_HIT_SFX = "phase_3.5/audio/sfx/AA_squirt_flowersquirt.ogg"
FLOWER_MISS_SFX = "phase_5/audio/sfx/AA_squirt_flowersquirt_miss.ogg"
NULL_SFX = "phase_3/audio/sfx/null.ogg"
DEFAULT_DRAW_SFX = "phase_5/audio/sfx/General_device_appear.ogg"

# These are globals for splats.
SPLAT_MDL = "phase_3.5/models/props/splat-mod.bam"
SPLAT_CHAN = "phase_3.5/models/props/splat-chan.bam"
SPRAY_MDL = "phase_3.5/models/props/spray.bam"
SPRAY_LEN = 1.5

# These are all the different colors for splats.
TART_SPLAT_COLOR = VBase4(55.0 / 255.0, 40.0 / 255.0, 148.0 / 255.0, 1.0)
CREAM_SPLAT_COLOR = VBase4(250.0 / 255.0, 241.0 / 255.0, 24.0 / 255.0, 1.0)
CAKE_SPLAT_COLOR = VBase4(253.0 / 255.0, 119.0 / 255.0, 220.0 / 255.0, 1.0)
WATER_SPRAY_COLOR = Point4(0.75, 0.75, 1.0, 0.8)

PNT3NEAR0 = Point3(0.01, 0.01, 0.01)
PNT3NORMAL = Point3(1, 1, 1)

# The range these gags extend.
TNT_RANGE = 15
SELTZER_RANGE = 25

# How much gags heal.
WEDDING_HEAL = 25
BDCAKE_HEAL = 10
CREAM_PIE_HEAL = 5
FRUIT_PIE_HEAL = 3
CREAM_PIE_SLICE_HEAL = 2
FRUIT_PIE_SLICE_HEAL = 1
CUPCAKE_HEAL = 1
SELTZER_HEAL = 5
WATERGLASS_HEAL = 2
WATERGUN_HEAL = 4
FIREHOSE_HEAL = 6

# Scales of gags.
CUPCAKE_SCALE = 0.5

def loadProp(phase, name):
    return loader.loadModel('phase_%s/models/props/%s.bam' % (str(phase), name))

def getProp(phase, name):
    return 'phase_%s/models/props/%s.bam' % (str(phase), name)

def getGagByID(gId):
    return base.attackMgr.getAttackName(gId)

def getIDByName(name):
    for aID, cls in base.attackMgr.AttackClasses.items():
        if cls.Name == name:
            return aID

def getGagData(gagId):
    return gagData.get(getGagByID(gagId))

# Expecting a dictionary like so:
# TRACK_NAME : EXP
# Returns a blob of the track data.
def trackExperienceToNetString(tracks):
    dg = PyDatagram()
    
    for track, exp in tracks.iteritems():
        dg.addUint8(TrackNameById.values().index(track))
        dg.addInt16(exp)
    dgi = PyDatagramIterator(dg)
    return dgi.getRemainingBytes()

# Expects a TRACK_NAME : EXP dictionary and the backpack that should get updates.
def processTrackData(trackData, backpack):
    addedGag = False

    for track, exp in trackData.iteritems():
        expAmounts = TrackExperienceAmounts.get(track)
        gags = TrackGagNamesByTrackName.get(track)
        
        for i in xrange(len(expAmounts)):
            maxEXP = expAmounts[i]
            if exp >= maxEXP and len(gags) > i:
                gagAtLevel = gags[i]
                gagId = getIDByName(gagAtLevel)
                
                if not backpack.hasGag(gagAtLevel):
                    addedGag = True
                    backpack.addGag(gagId, 1, None)
                
    for gagId in backpack.avatar.attacks.keys():
        gagName = getGagByID(gagId)
        maxSupply = calculateMaxSupply(backpack.avatar, gagName, gagData.get(gagName))
        backpack.setMaxSupply(gagId, maxSupply)

    return addedGag

def getTrackExperienceFromNetString(netString):
    dg = PyDatagram(netString)
    dgi = PyDatagramIterator(dg)
    
    tracks = {}
    
    for track in TrackNameById.values():
        tracks[track] = 0
    
    while dgi.getRemainingSize() > 0:
        trackId = dgi.getUint8()
        exp = dgi.getInt16()
        
        tracks[TrackNameById.get(trackId)] = exp
    return tracks

def getMaxExperienceValue(exp, track):
    levels = TrackExperienceAmounts[track]
    
    if exp > -1:
        for i in range(len(levels)):
            if exp < levels[i] or (i == (len(levels) - 1) and exp >= levels[i]):
                return levels[i]
    return -1
    
def getTrackName(tId):
    return TrackNameById.get(tId, "not found")
    
def getTrackOfGag(arg, getId = False):
    if type(arg) == types.IntType:

        # This is a gag id.
        for trackName, gagList in TrackGagNamesByTrackName.items():

            if getGagByID(arg) in gagList:

                if not getId:
                    # Return the name of the track as a string
                    return trackName
                else:
                    # Return the int ID of the track
                    return TrackIdByName[trackName]

    elif type(arg) == types.StringType:

        # This is a gag name.
        for trackName, gagList in TrackGagNamesByTrackName.items():

            if arg in gagList:

                if not getId:
                    # Return the name of the track as a string
                    return trackName
                else:
                    # Return the int ID of the track
                    return TrackIdByName[trackName]

# The idea here is that tracks with a default exp of -1 aren't unlocked yet.
# Throw and squirt fetch the first max exp amount defined in the TrackExperienceAmounts dict.
DefaultTrackExperiences = {
    ToonUp : -1,
    Trap : -1,
    Lure : -1,
    Sound : -1,
    Throw : 0,
    Squirt : 0,
    Drop : -1
}

MaxedTrackExperiences = {
    ToonUp : getTrackHighestExperience(ToonUp),
    Trap   : getTrackHighestExperience(Trap),
    Lure   : -1,
    Sound  : getTrackHighestExperience(Sound),
    Throw  : getTrackHighestExperience(Throw),
    Squirt : getTrackHighestExperience(Squirt),
    Drop   : getTrackHighestExperience(Drop)
}

# Cupcake, squirt flower
InitLoadout = [13, 35]

def getDefaultBackpack(isAI = False):
    defaultBackpack = None
    if not isAI:
        from src.coginvasion.gags.backpack.Backpack import Backpack
        defaultBackpack = Backpack(None)
    else:
        from src.coginvasion.gags.backpack.BackpackAI import BackpackAI
        defaultBackpack = BackpackAI(None)
    cupcake = getGagData(13)
    flower = getGagData(35)
    defaultBackpack.addGag(13, cupcake.get('supply'), cupcake.get('maxSupply'))
    defaultBackpack.addGag(35, flower.get('supply'), flower.get('maxSupply'))
    return defaultBackpack

# Specifies which gags are allowed to be used. This should only be temporary until all the gags are implemented correctly.
#tempAllowedGags = #[Cupcake, FruitPieSlice, CreamPieSlice, WholeFruitPie, WholeCreamPie, BirthdayCake,
                  # WaterGun, FireHose,
                  # FlowerPot, Sandbag, Anvil, BigWeight, Safe, GrandPiano,
                  # TNT, HL2Shotgun,
                  # Megaphone, Lipstick, JugglingBalls, BambooCane, PixieDust,
                  # BikeHorn, Whistle, Bugle, Aoogah, ElephantHorn, Foghorn, Opera]
tempAllowedGags = [WholeCreamPie, HL2Shotgun, HL2Pistol, TNT]
