"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file ZoneUtil.py
@author Brian Lach
@date ???

"""

from src.coginvasion.npc.NPCGlobals import lToonHQ
from src.coginvasion.base.Lighting import OutdoorLightingConfig

Playground = "Playground"
OToontown = "OToontown"
CogTropolis = "CogTropolis"
Estate = "The Estate"
ToontownCentral = "Toontown Central"
BattleTTC = "CogTropolis Central"
DonaldsDock = "Donald's Dock"
MinniesMelodyland = "Minnie's Melodyland"
TheBrrrgh = "The Brrrgh"
DonaldsDreamland = "Donald's Dreamland"
GoofySpeedway = "Goofy Speedway"
CashbotHQ = "Cashbot HQ"
SellbotHQ = "Sellbot HQ"
LawbotHQ = "Lawbot HQ"
BossbotHQ = "Bossbot HQ"
MinigameArea = "Minigame Grounds"
OutdoorZone = "Outdoor Area"
GolfZone = "Minigolf Area"
DaisyGardens = "Daisy Gardens"
Minigame = "Minigame"
RecoverArea = "Recover Area"

Hood2ZoneId = {ToontownCentral: 2000, DonaldsDock: 1000, TheBrrrgh: 3000,
               MinniesMelodyland: 4000, DaisyGardens: 5000, DonaldsDreamland: 9000,
               MinigameArea: 10000, CogTropolis: 12000}
ZoneId2Hood = {2000: ToontownCentral, 1000: DonaldsDock, 3000: TheBrrrgh,
               4000: MinniesMelodyland, 5000: DaisyGardens, 9000: DonaldsDreamland,
               10000: MinigameArea, 12000: CogTropolis}
HoodAbbr2Hood = {"TT" : ToontownCentral, "DD" : DonaldsDock, "BR" : TheBrrrgh, "MM" : MinniesMelodyland,
                 "DG" : DaisyGardens, "DL" : DonaldsDreamland, "MG" : MinigameArea}
ZoneId2HoodAbbr = {2000: "TT", 1000: "DD", 3000: "BR", 4000: "MM", 5000: "DG", 9000: "DL", 10000: "MG", 12000: "CT"}

ZoneId2DNAFilePrefix = {
    # The TTC DNA prefix points to where the branch zone files are only. Safezone DNA is in phase_4 for TTC.
    2000 : "phase_5/dna/toontown_central_",
    3000 : "phase_6/dna/donalds_dock_",
    4000 : "phase_6/dna/minnies_melody_land_",
    5000 : "phase_8/dna/daisys_garden_",
    9000 : "phase_8/dna/donalds_dreamland_"
}

SellbotFactory = "Sellbot Factory"
ToonBattleOriginalLevel = "Original Level"
ToontownCentralId = 2000
MinigameAreaId = 10000
RecoverAreaId = 11000
CogTropolisId = 12000
TheBrrrghId = 3000
DonaldsDockId = 1000
MinniesMelodylandId = 4000
DonaldsDreamlandId = 9000
DaisyGardensId = 5000
GoofySpeedwayId = 8000
QuietZone = 1
UberZone = 2
DistrictZone = 3
DynamicZonesBegin = 61000
DynamicZonesEnd = 1 << 20
safeZoneLSRanges = {ToontownCentral: 6,
    MinigameArea: 6,
    RecoverArea: 8}

zone2TitleDict = {2513: ('Toon Hall', ''),
 2514: ('Toontown Bank', ''),
 2516: ('Toontown School House', ''),
 2518: ('Toontown Library', ''),
 2519: ('Gag Shop', ''),
 2520: (lToonHQ, ''),
 2521: ('Clothing Shop', ''),
 2522: ('Pet Shop', ''),
 2601: ('All Smiles Tooth Repair', ''),
 2602: ('', ''),
 2603: ("It's Time To Read", ''),
 2604: ('Hogwash & Dry', ''),
 2605: ('Toontown Sign Factory', ''),
 2606: ('', ''),
 2607: ('Jumping Beans', ''),
 2610: ('Dr. Tom Foolery', ''),
 2611: ('', ''),
 2616: ("Weird Beard's Disguise Shop", ''),
 2617: ('Silly Stunts', ''),
 2618: ('All That Razz', ''),
 2621: ('Paper Airplanes', ''),
 2624: ('Happy Hooligans', ''),
 2625: ('House of Bad Pies', ''),
 2626: ("Jesse's Joke Repair", ''),
 2629: ("The Laughin' Place", ''),
 2632: ('Clown Class', ''),
 2633: ('Tee-Hee Tea Shop', ''),
 2638: ('Toontown Playhouse', ''),
 2639: ('Monkey Tricks', ''),
 2643: ('Canned Bottles', ''),
 2644: ('Impractical Jokes', ''),
 2649: ('All Fun and Games Shop', ''),
 2652: ('', ''),
 2653: ("JJ's Diner", ''),
 2654: ('Laughing Lessons', ''),
 2655: ('Funny Money Savings & Loan', ''),
 2656: ('Used Clown Cars', ''),
 2657: ("Frank's Pranks", ''),
 2659: ('Joy Buzzers to the World', ''),
 2660: ('Tickle Machines', ''),
 2661: ('Daffy Taffy', ''),
 2662: ('Dr. I.M. Euphoric', ''),
 2663: ('Toontown Cinerama', ''),
 2664: ('The Merry Mimes', ''),
 2665: ("Mary's Go Around Travel Company", ''),
 2666: ('Laughing Gas Station', ''),
 2667: ('Happy Times', ''),
 2669: ("Muldoon's Maroon Balloons", ''),
 2670: ('Soup Forks', ''),
 2671: ('', ''),
 2701: ('', ''),
 2704: ('Movie Multiplex', ''),
 2705: ("Wiseacre's Noisemakers", ''),
 2708: ('Blue Glue', ''),
 2711: ('Toontown Post Office', ''),
 2712: ('Chortle Cafe', ''),
 2713: ('Laughter Hours Cafe', ''),
 2714: ('Kooky CinePlex', ''),
 2716: ('Soup and Crack Ups', ''),
 2717: ('Bottled Cans', ''),
 2720: ('Crack Up Auto Repair', ''),
 2725: ('', ''),
 2727: ('Seltzer Bottles and Cans', ''),
 2728: ('Vanishing Cream', ''),
 2729: ('14 Karat Goldfish', ''),
 2730: ('News for the Amused', ''),
 2731: ('', ''),
 2732: ('Spaghetti and Goofballs', ''),
 2733: ('Cast Iron Kites', ''),
 2734: ('Suction Cups and Saucers', ''),
 2735: ('The Kaboomery', ''),
 2739: ("Sidesplitter's Mending", ''),
 2740: ('Used Firecrackers', ''),
 2741: ('', ''),
 2742: ('', ''),
 2743: ('Ragtime Dry Cleaners', ''),
 2744: ('', ''),
 2747: ('Visible Ink', ''),
 2748: ('Jest for Laughs', ''),
 2801: ('Sofa Whoopee Cushions', ''),
 2802: ('Inflatable Wrecking Balls', ''),
 2803: ('The Karnival Kid', ''),
 2804: ('Dr. Pulyurleg, Chiropractor', ''),
 2805: ('', ''),
 2809: ('The Punch Line Gym', ''),
 2814: ('Toontown Theatre', ''),
 2818: ('The Flying Pie', ''),
 2821: ('', ''),
 2822: ('Rubber Chicken Sandwiches', ''),
 2823: ('Sundae Funnies Ice Cream', ''),
 2824: ('Punchline Movie Palace', ''),
 2829: ('Phony Baloney', ''),
 2830: ("Zippy's Zingers", ''),
 2831: ("Professor Wiggle's House of Giggles", ''),
 2832: ('', ''),
 2833: ('', ''),
 2834: ('Funny Bone Emergency Room', ''),
 2836: ('', ''),
 2837: ('Hardy Harr Seminars', ''),
 2839: ('Barely Palatable Pasta', ''),
 2841: ('', ''),
 1506: ('Gag Shop', ''),
 1507: ('Toon Headquarters', ''),
 1508: ('Clothing Shop', ''),
 1510: ('', ''),
 1602: ('Used Life Preservers', ''),
 1604: ('Wet Suit Dry Cleaners', ''),
 1606: ("Hook's Clock Repair", ''),
 1608: ("Luff 'N Stuff", ''),
 1609: ('Every Little Bait', ''),
 1612: ('Dime & Quarterdeck Bank', ''),
 1613: ('Squid Pro Quo, Attorneys at Law', ''),
 1614: ('Trim the Nail Boutique', ''),
 1615: ("Yacht's All, Folks!", ''),
 1616: ("Blackbeard's Beauty Parlor", ''),
 1617: ('Out to See Optics', ''),
 1619: ('Disembark! Tree Surgeons', ''),
 1620: ('From Fore to Aft', ''),
 1621: ('Poop Deck Gym', ''),
 1622: ('Bait and Switches Electrical Shop', ''),
 1624: ('Soles Repaired While U Wait', ''),
 1626: ('Salmon Chanted Evening Formal Wear', ''),
 1627: ("Billy Budd's Big Bargain Binnacle Barn", ''),
 1628: ('Piano Tuna', ''),
 1629: ('', ''),
 1701: ('Buoys and Gulls Nursery School', ''),
 1703: ('Wok the Plank Chinese Food', ''),
 1705: ('Sails for Sale', ''),
 1706: ('Peanut Butter and Jellyfish', ''),
 1707: ('Gifts With a Porpoise', ''),
 1709: ('Windjammers and Jellies', ''),
 1710: ('Barnacle Bargains', ''),
 1711: ('Deep Sea Diner', ''),
 1712: ('Able-Bodied Gym', ''),
 1713: ("Art's Smart Chart Mart", ''),
 1714: ("Reel 'Em Inn", ''),
 1716: ('Mermaid Swimwear', ''),
 1717: ('Be More Pacific Ocean Notions', ''),
 1718: ('Run Aground Taxi Service', ''),
 1719: ("Duck's Back Water Company", ''),
 1720: ('The Reel Deal', ''),
 1721: ('All For Nautical', ''),
 1723: ("Squid's Seaweed", ''),
 1724: ("That's  a Moray!", ''),
 1725: ("Ahab's Prefab Sea Crab Center", ''),
 1726: ('Root Beer Afloats', ''),
 1727: ('This Oar That', ''),
 1728: ('Good Luck Horseshoe Crabs', ''),
 1729: ('', ''),
 1802: ('Nautical But Nice', ''),
 1804: ('Mussel Beach Gymnasium', ''),
 1805: ('Tackle Box Lunches', ''),
 1806: ('Cap Size Hat Store', ''),
 1807: ('Keel Deals', ''),
 1808: ('Knots So Fast', ''),
 1809: ('Rusty Buckets', ''),
 1810: ('Anchor Management', ''),
 1811: ("What's Canoe With You?", ''),
 1813: ('Pier Pressure Plumbing', ''),
 1814: ('The Yo Ho Stop and Go', ''),
 1815: ("What's Up, Dock?", ''),
 1818: ('Seven Seas Cafe', ''),
 1819: ("Docker's Diner", ''),
 1820: ('Hook, Line, and Sinker Prank Shop', ''),
 1821: ("King Neptoon's Cannery", ''),
 1823: ('The Clam Bake Diner', ''),
 1824: ('Dog Paddles', ''),
 1825: ('Wholly Mackerel! Fish Market', ''),
 1826: ("Claggart's Clever Clovis Closet", ''),
 1828: ("Alice's Ballast Palace", ''),
 1829: ('Seagull Statue Store', ''),
 1830: ('Lost and Flounder', ''),
 1831: ('Kelp Around the House', ''),
 1832: ("Melville's Massive Mizzenmast Mart", ''),
 1833: ('This Transom Man Custom Tailored Suits', ''),
 1834: ('Rudderly Ridiculous!', ''),
 1835: ('', ''),
 4503: ('Gag Shop', ''),
 4504: ('Toon Headquarters', ''),
 4506: ('Clothing Shop', ''),
 4508: ('', ''),
 4603: ("Tom-Tom's Drums", ''),
 4604: ('In Four-Four Time', ''),
 4605: ("Fifi's Fiddles", ''),
 4606: ('Casa De Castanets', ''),
 4607: ('Catchy Toon Apparel', ''),
 4609: ('Do, Rae, Me Piano Keys', ''),
 4610: ('Please Refrain', ''),
 4611: ('Tuning Forks and Spoons', ''),
 4612: ("Dr. Fret's Dentistry", ''),
 4614: ('Shave and a Haircut for a Song', ''),
 4615: ("Piccolo's Pizza", ''),
 4617: ('Happy Mandolins', ''),
 4618: ('Rests Rooms', ''),
 4619: ('More Scores', ''),
 4622: ('Chin Rest Pillows', ''),
 4623: ('Flats Sharpened', ''),
 4625: ('Tuba Toothpaste', ''),
 4626: ('Notations', ''),
 4628: ('Accidental Insurance', ''),
 4629: ("Riff's Paper Plates", ''),
 4630: ('Music Is Our Forte', ''),
 4631: ('Canto Help You', ''),
 4632: ('Dance Around the Clock Shop', ''),
 4635: ('Tenor Times', ''),
 4637: ('For Good Measure', ''),
 4638: ('Hard Rock Shop', ''),
 4639: ('Four Score Antiques', ''),
 4641: ('Blues News', ''),
 4642: ('Ragtime Dry Cleaners', ''),
 4645: ('Club 88', ''),
 4646: ('', ''),
 4648: ('Carry a Toon Movers', ''),
 4649: ('', ''),
 4652: ('Full Stop Shop', ''),
 4653: ('', ''),
 4654: ('Pitch Perfect Roofing', ''),
 4655: ("The Treble Chef's Cooking School", ''),
 4656: ('', ''),
 4657: ('Barbershop Quartet', ''),
 4658: ('Plummeting Pianos', ''),
 4659: ('', ''),
 4701: ('The Schmaltzy Waltz School of Dance', ''),
 4702: ('Timbre! Equipment for the Singing Lumberjack', ''),
 4703: ('I Can Handel It!', ''),
 4704: ("Tina's Concertina Concerts", ''),
 4705: ('Zither Here Nor There', ''),
 4707: ("Doppler's Sound Effects Studio", ''),
 4709: ('On Ballet! Climbing Supplies', ''),
 4710: ('Hurry Up, Slow Polka! School of Driving', ''),
 4712: ('C-Flat Tire Repair', ''),
 4713: ('B-Sharp Fine Menswear', ''),
 4716: ('Four-Part Harmonicas', ''),
 4717: ('Sonata Your Fault! Discount Auto Insurance', ''),
 4718: ('Chopin Blocks and Other Kitchen Supplies', ''),
 4719: ('Madrigal Motor Homes', ''),
 4720: ('Name That Toon', ''),
 4722: ('Overture Understudies', ''),
 4723: ('Haydn Go Seek Playground Supplies', ''),
 4724: ('White Noise for Girls and Boys', ''),
 4725: ('The Baritone Barber', ''),
 4727: ('Vocal Chords Braided', ''),
 4728: ("Sing Solo We Can't Hear You", ''),
 4729: ('Double Reed Bookstore', ''),
 4730: ('Lousy Lyrics', ''),
 4731: ('Toon Tunes', ''),
 4732: ('Etude Brute? Theatre Company', ''),
 4733: ('', ''),
 4734: ('', ''),
 4735: ('Accordions, If You Want In, Just Bellow!', ''),
 4736: ('Her and Hymn Wedding Planners', ''),
 4737: ('Harp Tarps', ''),
 4738: ('Canticle Your Fancy Gift Shop', ''),
 4739: ('', ''),
 4801: ("Marshall's Stacks", ''),
 4803: ('What a Mezzo! Maid Service', ''),
 4804: ('Mixolydian Scales', ''),
 4807: ('Relax the Bach', ''),
 4809: ("I Can't Understanza!", ''),
 4812: ('', ''),
 4817: ('The Ternary Pet Shop', ''),
 4819: ("Yuki's Ukeleles", ''),
 4820: ('', ''),
 4821: ("Anna's Cruises", ''),
 4827: ('Common Time Watches', ''),
 4828: ("Schumann's Shoes for Men", ''),
 4829: ("Pachelbel's Canonballs", ''),
 4835: ('Ursatz for Kool Katz', ''),
 4836: ('Reggae Regalia', ''),
 4838: ('Kazoology School of Music', ''),
 4840: ('Coda Pop Musical Beverages', ''),
 4841: ('Lyre, Lyre, Pants on Fire!', ''),
 4842: ('The Syncopation Corporation', ''),
 4843: ('', ''),
 4844: ('Con Moto Cycles', ''),
 4845: ("Ellie's Elegant Elegies", ''),
 4848: ('Lotsa Lute Savings & Loan', ''),
 4849: ('', ''),
 4850: ('The Borrowed Chord Pawn Shop', ''),
 4852: ('Flowery Flute Fleeces', ''),
 4853: ("Leo's Fenders", ''),
 4854: ("Wagner's Vocational Violin Videos", ''),
 4855: ('The Teli-Caster Network', ''),
 4856: ('', ''),
 4862: ("Quentin's Quintessen\x03tial Quadrilles", ''),
 4867: ("Mr. Costello's Yellow Cellos", ''),
 4868: ('', ''),
 4870: ("Ziggy's Zoo of Zigeuner\x03musik", ''),
 4871: ("Harry's House of Harmonious Humbuckers", ''),
 4872: ("Fast Freddie's Fretless Fingerboards", ''),
 4873: ('', ''),
 5501: ('Gag Shop', ''),
 5502: (lToonHQ, ''),
 5503: ('Clothing Shop', ''),
 5505: ('', ''),
 5601: ('Eye of the Potato Optometry', ''),
 5602: ("Artie Choke's Neckties", ''),
 5603: ('Lettuce Alone', ''),
 5604: ('Cantaloupe Bridal Shop', ''),
 5605: ('Vege-tables and Chairs', ''),
 5606: ('Petals', ''),
 5607: ('Compost Office', ''),
 5608: ('Mom and Pop Corn', ''),
 5609: ('Berried Treasure', ''),
 5610: ("Black-eyed Susan's Boxing Lessons", ''),
 5611: ("Gopher's Gags", ''),
 5613: ('Crop Top Barbers', ''),
 5615: ("Bud's Bird Seed", ''),
 5616: ('Dew Drop Inn', ''),
 5617: ("Flutterby's Butterflies", ''),
 5618: ("Peas and Q's", ''),
 5619: ("Jack's Beanstalks", ''),
 5620: ('Rake It Inn', ''),
 5621: ('Grape Expectations', ''),
 5622: ('Petal Pusher Bicycles', ''),
 5623: ('Bubble Bird Baths', ''),
 5624: ("Mum's the Word", ''),
 5625: ('Leaf It Bees', ''),
 5626: ('Pine Needle Crafts', ''),
 5627: ('', ''),
 5701: ('From Start to Spinach', ''),
 5702: ("Jake's Rakes", ''),
 5703: ("Photo Cynthia's Camera Shop", ''),
 5704: ('Lisa Lemon Used Cars', ''),
 5705: ('Poison Oak Furniture', ''),
 5706: ('14 Carrot Jewelers', ''),
 5707: ('Musical Fruit', ''),
 5708: ("We'd Be Gone Travel Agency", ''),
 5709: ('Astroturf Mowers', ''),
 5710: ('Tuft Guy Gym', ''),
 5711: ('Garden Hosiery', ''),
 5712: ('Silly Statues', ''),
 5713: ('Trowels and Tribulations', ''),
 5714: ('Spring Rain Seltzer Bottles', ''),
 5715: ('Hayseed News', ''),
 5716: ('Take It or Leaf It Pawn Shop', ''),
 5717: ('The Squirting Flower', ''),
 5718: ('The Dandy Lion Exotic Pets', ''),
 5719: ('Trellis the Truth! Private Investi\x03gators', ''),
 5720: ('Vine and Dandy Menswear', ''),
 5721: ('Root 66 Diner', ''),
 5725: ('Barley, Hops, and Malt Shop', ''),
 5726: ("Bert's Dirt", ''),
 5727: ('Gopher Broke Savings & Loan', ''),
 5728: ('', ''),
 5802: (lToonHQ, ''),
 5804: ('Just Vase It', ''),
 5805: ('Snail Mail', ''),
 5809: ('Fungi Clown School', ''),
 5810: ('Honeydew This', ''),
 5811: ('Lettuce Inn', ''),
 5815: ('Grass Roots', ''),
 5817: ('Apples and Oranges', ''),
 5819: ('Green Bean Jeans', ''),
 5821: ('Squash and Stretch Gym', ''),
 5826: ('Ant Farming Supplies', ''),
 5827: ('Dirt. Cheap.', ''),
 5828: ('Couch Potato Furniture', ''),
 5830: ('Spill the Beans', ''),
 5833: ('The Salad Bar', ''),
 5835: ('Flower Bed and Breakfast', ''),
 5836: ("April's Showers and Tubs", ''),
 5837: ('School of Vine Arts', ''),
 9501: ('Lullaby Library', ''),
 9503: ('The Snooze Bar', ''),
 9504: ('Gag Shop', ''),
 9505: (lToonHQ, ''),
 9506: ('Clothing Shop', ''),
 9508: ('', ''),
 9601: ('Snuggle Inn', ''),
 9602: ('Forty Winks for the Price of Twenty', ''),
 9604: ("Ed's Red Bed Spreads", ''),
 9605: ('Cloud Nine Design', ''),
 9607: ("Big Mama's Bahama Pajamas", ''),
 9608: ('Cat Nip for Cat Naps', ''),
 9609: ('Deep Sleep for Cheap', ''),
 9613: ('Clock Cleaners', ''),
 9616: ('Lights Out Electric Co.', ''),
 9617: ('Crib Notes - Music to Sleep By', ''),
 9619: ('Relax to the Max', ''),
 9620: ("PJ's Taxi Service", ''),
 9622: ('Sleepy Time Pieces', ''),
 9625: ('Curl Up Beauty Parlor', ''),
 9626: ('Bed Time Stories', ''),
 9627: ('The Sleepy Teepee', ''),
 9628: ('Call It a Day Calendars', ''),
 9629: ('Silver Lining Jewelers', ''),
 9630: ('Rock to Sleep Quarry', ''),
 9631: ('Down Time Watch Repair', ''),
 9633: ('The Dreamland Screening Room', ''),
 9634: ('Mind Over Mattress', ''),
 9636: ('Insomniac Insurance', ''),
 9639: ('House of Hibernation', ''),
 9640: ('Nightstand Furniture Company', ''),
 9642: ('Sawing Wood Slumber Lumber', ''),
 9643: ('Shut-Eye Optometry', ''),
 9644: ('Pillow Fights Nightly', ''),
 9645: ('The All Tucked Inn', ''),
 9647: ('Make Your Bed! Hardware Store', ''),
 9649: ('Snore or Less', ''),
 9650: ('Crack of Dawn Repairs', ''),
 9651: ('For Richer or Snorer', ''),
 9652: ('', ''),
 9703: ('Fly By Night Travel Agency', ''),
 9704: ('Night Owl Pet Shop', ''),
 9705: ('Asleep At The Wheel Car Repair', ''),
 9706: ('Tooth Fairy Dentistry', ''),
 9707: ("Dawn's Yawn & Garden Center", ''),
 9708: ('Bed Of Roses Florist', ''),
 9709: ('Pipe Dream Plumbers', ''),
 9710: ('REM Optometry', ''),
 9711: ('Wake-Up Call Phone Company', ''),
 9712: ("Counting Sheep - So You Don't Have To!", ''),
 9713: ('Wynken, Blynken & Nod, Attorneys at Law', ''),
 9714: ('Dreamboat Marine Supply', ''),
 9715: ('First Security Blanket Bank', ''),
 9716: ('Wet Blanket Party Planners', ''),
 9717: ("Baker's Dozin' Doughnuts", ''),
 9718: ("Sandman's Sandwiches", ''),
 9719: ('Armadillo Pillow Company', ''),
 9720: ('Talking In Your Sleep Voice Training', ''),
 9721: ('Snug As A Bug Rug Dealer', ''),
 9722: ('Dream On Talent Agency', ''),
 9725: ("Cat's Pajamas", ''),
 9727: ('You Snooze, You Lose', ''),
 9736: ('Dream Jobs Employment Agency', ''),
 9737: ("Waltzing Matilda's Dance School", ''),
 9738: ('House of Zzzzzs', ''),
 9740: ('Hit The Sack Fencing School', ''),
 9741: ("Don't Let The Bed Bugs Bite Exterminators", ''),
 9744: ("Rip Van Winkle's Wrinkle Cream", ''),
 9752: ('Midnight Oil & Gas Company', ''),
 9753: ("Moonbeam's Ice Creams", ''),
 9754: ('Sleepless in the Saddle All Night Pony Rides', ''),
 9755: ('Bedknobs & Broomsticks Movie House', ''),
 9756: ('', ''),
 9759: ('Sleeping Beauty Parlor', ''),
 3507: ('Gag Shop', ''),
 3508: (lToonHQ, ''),
 3509: ('Clothing Shop', ''),
 3511: ('', ''),
 3601: ('Northern Lights Electric Company', ''),
 3602: ("Nor'easter Bonnets", ''),
 3605: ('', ''),
 3607: ('The Blizzard Wizard', ''),
 3608: ('Nothing to Luge', ''),
 3610: ("Mike's Massive Mukluk Mart", ''),
 3611: ("Mr. Cow's Snow Plows", ''),
 3612: ('Igloo Design', ''),
 3613: ('Ice Cycle Bikes', ''),
 3614: ('Snowflakes Cereal Company', ''),
 3615: ('Fried Baked Alaskas', ''),
 3617: ('Cold Air Balloon Rides', ''),
 3618: ('Snow Big Deal! Crisis Management', ''),
 3620: ('Skiing Clinic', ''),
 3621: ('The Melting Ice Cream Bar', ''),
 3622: ('', ''),
 3623: ('The Mostly Toasty Bread Company', ''),
 3624: ('Subzero Sandwich Shop', ''),
 3625: ("Auntie Freeze's Radiator Supply", ''),
 3627: ('St. Bernard Kennel Club', ''),
 3629: ('Pea Soup Cafe', ''),
 3630: ('Icy London, Icy France Travel Agency', ''),
 3634: ('Easy Chair Lifts', ''),
 3635: ('Used Firewood', ''),
 3636: ('Affordable Goosebumps', ''),
 3637: ("Kate's Skates", ''),
 3638: ('Toboggan or Not Toboggan', ''),
 3641: ("Fred's Red Sled Beds", ''),
 3642: ('Eye of the Storm Optics', ''),
 3643: ('Snowball Hall', ''),
 3644: ('Melted Ice Cubes', ''),
 3647: ('The Sanguine Penguin Tuxedo Shop', ''),
 3648: ('Instant Ice', ''),
 3649: ('Hambrrrgers', ''),
 3650: ('Antarctic Antiques', ''),
 3651: ("Frosty Freddy's Frozen Frankfurters", ''),
 3653: ('Ice House Jewelry', ''),
 3654: ('', ''),
 3702: ('Winter Storage', ''),
 3703: ('', ''),
 3705: ('Icicles Built for Two', ''),
 3706: ("Shiverin' Shakes Malt Shop", ''),
 3707: ('Snowplace Like Home', ''),
 3708: ("Pluto's Place", ''),
 3710: ('Dropping Degrees Diner', ''),
 3711: ('', ''),
 3712: ('Go With the Floe', ''),
 3713: ('Chattering Teeth, Subzero Dentist', ''),
 3715: ("Aunt Arctic's Soup Shop", ''),
 3716: ('Road Salt and Pepper', ''),
 3717: ('Juneau What I Mean?', ''),
 3718: ('Designer Inner Tubes', ''),
 3719: ('Ice Cube on a Stick', ''),
 3721: ("Noggin's Toboggan Bargains", ''),
 3722: ('Snow Bunny Ski Shop', ''),
 3723: ("Shakey's Snow Globes", ''),
 3724: ('The Chattering Chronicle', ''),
 3725: ('You Sleigh Me', ''),
 3726: ('Solar Powered Blankets', ''),
 3728: ('Lowbrow Snowplows', ''),
 3729: ('', ''),
 3730: ('Snowmen Bought & Sold', ''),
 3731: ('Portable Fireplaces', ''),
 3732: ('The Frozen Nose', ''),
 3734: ('Icy Fine, Do You? Optometry', ''),
 3735: ('Polar Ice Caps', ''),
 3736: ('Diced Ice at a Nice Price', ''),
 3737: ('Downhill Diner', ''),
 3738: ("Heat-Get It While It's Hot", ''),
 3739: ('', ''),
 3801: ('Toon HQ', ''),
 3806: ('Alpine Chow Line', ''),
 3807: ('Used Groundhog Shadows', ''),
 3808: ('The Sweater Lodge', ''),
 3809: ('Ice Saw It Too', ''),
 3810: ('A Better Built Quilt', ''),
 3811: ('Your Snow Angel', ''),
 3812: ('Mittens for Kittens', ''),
 3813: ("Snowshoes You Can't Refuse", ''),
 3814: ('Malt in Your Mouth Soda Fountain', ''),
 3815: ('The Toupee Chalet', ''),
 3816: ('Just So Mistletoe', ''),
 3817: ('Winter Wonderland Walking Club', ''),
 3818: ('The Shovel Hovel', ''),
 3819: ('Clean Sweep Chimney Service', ''),
 3820: ('Snow Whitening', ''),
 3821: ('Hibernation Vacations', ''),
 3823: ('Precipitation Foundation', ''),
 3824: ('Open Fire Chestnut Roasting', ''),
 3825: ('Cool Cat Hats', ''),
 3826: ('Oh My Galoshes!', ''),
 3827: ('Choral Wreaths', ''),
 3828: ("Snowman's Land", ''),
 3829: ('Pinecone Zone', ''),
 3830: ('Wait and See Goggle Defogging', '')
}

PunchlinePlace = "Punchline Place"
SillyStreet = "Silly Street"
LoopyLane = "Loopy Lane"
BarnacleBoulevard = "Barnacle Boulevard"
SeaweedStreet = "Seaweed Street"
LighthouseLane = "Lighthouse Lane"
AltoAvenue = "Alto Avenue"
BaritoneBoulevard = "Baritone Boulevard"
TenorTerrace = "Tenor Terrace"
ElmStreet = "Elm Street"
MapleStreet = "Maple Street"
OakStreet = "Oak Street"
SleetStreet = "Sleet Street"
WalrusWay = "Walrus Way"
PolarPlace = "Polar Place"
LullabyLane = "Lullaby Lane"
PajamaPlace = "Pajama Place"
WallStreet = "Wall Street"
ProprietaryPlace = "Proprietary Place"
LimitedLiabilityLane = "Limited Liability Lane"
BranchZone2StreetName = {
    2100: SillyStreet,
    2300: PunchlinePlace,
    2200: LoopyLane,
    1300: LighthouseLane,
    1200: SeaweedStreet,
    1100: BarnacleBoulevard,
    4100: AltoAvenue,
    4200: BaritoneBoulevard,
    4300: TenorTerrace,
    3100: WalrusWay,
    3200: SleetStreet,
    3300: PolarPlace,
    9100: LullabyLane,
    9200: PajamaPlace,
    5100: ElmStreet,
    5200: MapleStreet,
    5300: OakStreet,

    22100: WallStreet,
    22300: ProprietaryPlace,
    22200: LimitedLiabilityLane,
    21300: LighthouseLane,
    21200: SeaweedStreet,
    21100: BarnacleBoulevard,
    24100: AltoAvenue,
    24200: BaritoneBoulevard,
    24300: TenorTerrace,
    23100: WalrusWay,
    23200: SleetStreet,
    23300: PolarPlace,
    29100: LullabyLane,
    29200: PajamaPlace,
    25100: ElmStreet,
    25200: MapleStreet,
    25300: OakStreet
}

def isInInterior(zoneId):
    return int(str(zoneId)[1:]) >= 500 and int(str(zoneId)[1:]) <= 999

def getWhereName(zoneId):
    if str(zoneId)[-3:] == '000':
        return 'playground'
    elif int(str(zoneId)[-3:]) < 400:
        return 'street'
    elif isInInterior(zoneId):
        return 'toonInterior'
    else:
        return 'street'

def getBranchZone(zoneId):
    branchZone = zoneId - zoneId % 100
    if zoneId % 1000 >= 500:
        branchZone -= 500
    return branchZone
    
def getStreetName(zoneId):
    return BranchZone2StreetName[getBranchZone(zoneId)]

def getLoaderName(zoneId):
    if str(getBranchZone(zoneId))[-3:] == '000':
        return 'safeZoneLoader'
    elif int(str(getBranchZone(zoneId))[-3:]) >= 100 and int(str(getBranchZone(zoneId))[-3:]) <= 999:
        return 'townLoader'
    else:
        return None

def isStreetInSameHood(zoneId):
    return str(zoneId)[0] == str(base.localAvatar.zoneId)[0]

def isStreet(zoneId):
    return getWhereName(zoneId) == 'street'

def getCanonicalBranchZone(zoneId):
    return getBranchZone(getCanonicalZoneId(zoneId))

def getCanonicalZoneId(zoneId):
    zoneId = zoneId % 2000
    if zoneId < 1000:
        zoneId = zoneId + ToontownCentralId
    else:
        zoneId = zoneId - 1000 + GoofySpeedwayId
    return zoneId

def getTrueZoneId(zoneId, currentZoneId):
    hoodId = getHoodId(zoneId, street = 1)
    offset = currentZoneId - currentZoneId % 2000
    
    isClient = (metadata.PROCESS == 'client')
    if hoodId == ToontownCentral and not isClient or isClient and hoodId == ToontownCentral:
        return zoneId - ToontownCentralId + offset
    elif hoodId == GoofySpeedway:
        return zoneId - GoofySpeedwayId + offset + 1000
    return zoneId

def getHoodId(zoneId, street = 0):
    if street:
        if str(zoneId)[0] == '1' and len(str(zoneId)) == 4:
            return DonaldsDock
        elif str(zoneId)[:2] == '10' and len(str(zoneId)) == 5:
            return MinigameArea
        elif str(zoneId)[:2] == '12' and len(str(zoneId)) == 5:
            return CogTropolis
        elif str(zoneId)[0] == '2':
            return ToontownCentral
        elif str(zoneId)[0] == '3':
            return TheBrrrgh
        elif str(zoneId)[0] == '4':
            return MinniesMelodyland
        elif str(zoneId)[0] == '5':
            return DaisyGardens
        elif str(zoneId)[0] == '9':
            return DonaldsDreamland
    else:
        if zoneId < DynamicZonesBegin:
            return ZoneId2Hood.get(zoneId, None)

def getDNAFilePrefixFromZoneId(zoneId):
    if not zoneId in ZoneId2DNAFilePrefix.values():
        zoneId = getCanonicalBranchZone(zoneId)
    return ZoneId2DNAFilePrefix.get(zoneId, "")

def getZoneId(hoodId):
    if hoodId == BattleTTC:
        hoodId = ToontownCentral
    return Hood2ZoneId[hoodId]
    
def isOnSameStreet(zoneId):
    return getBranchZone(zoneId) == getBranchZone(base.localAvatar.zoneId)
    
def isOnCurrentPlayground(zoneId):
    return getHoodId(getBranchZone(zoneId)) == getHoodId(base.localAvatar.zoneId, 1)
    
def isLocatedInCurrentPlayground(zoneId):
    return getHoodId(zoneId, 1) == getHoodId(base.localAvatar.zoneId, 1)
    
def isAtSamePlaygroundButDifferentBranch(zoneId):
    return isLocatedInCurrentPlayground(zoneId) and not isOnSameStreet(zoneId)

def getOutdoorLightingConfig(hoodId):
    olc = OutdoorLightingConfig.makeDefault()

    if hoodId == TheBrrrgh:
        olc.snow = True
        
    data = base.loader.envConfig.getHoodSection(hoodId)
    if not data:
        # No lighting config exists for this hood, just give the default.
        return olc
        
    olc.setSkyType(data.skyType)
    olc.ambient = data.outdoorAmbientColor
    olc.sun = data.sunColor
    olc.sunAngle = data.sunAngle
    olc.fog = data.fogColor
    olc.fogDensity = data.fogDensity

    return olc
