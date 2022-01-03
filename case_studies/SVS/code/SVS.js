const blockhash = "0x5cb3e33c31019c9e5f77f354f150e4d74eb95a029a69738d45c176bc1447e444"

const fs = require("fs").promises
const seedrandom = require("seedrandom")
const chooser = require("random-seed-weighted-chooser").default
const SparkMD5 = require("spark-md5")

const random = seedrandom(blockhash)

const uniques = [{
    "name": "Ancient Count",
    "amount": 1,
    "fileName": "AncientCount",
    "attributes": [{
        "trait_type": "Unique",
        "value": "Ancient Count"
    }]
}, {
    "name": "Punk Vampire",
    "amount": 1,
    "fileName": "PunkVampire",
    "attributes": [{
        "trait_type": "Unique",
        "value": "Punk Vampire"
    }]
}, {
    "name": "Nosferatu",
    "amount": 1,
    "fileName": "Nosferatu",
    "attributes": [{
        "trait_type": "Unique",
        "value": "Nosferatu"
    }]
}, {
    "name": "The Impaler",
    "amount": 1,
    "fileName": "TheImpaler",
    "attributes": [{
        "trait_type": "Unique",
        "value": "The Impaler"
    }]
}, {
    "name": "Killer Clown",
    "amount": 1,
    "fileName": "KillerClown",
    "attributes": [{
        "trait_type": "Unique",
        "value": "Killer Clown"
    }]
}, {
    "name": "Vampire Lord",
    "amount": 1,
    "fileName": "VampireLord",
    "attributes": [{
        "trait_type": "Unique",
        "value": "Vampire Lord"
    }]
}, {
    "name": "Vampire Nun",
    "amount": 1,
    "fileName": "VampireNun",
    "attributes": [{
        "trait_type": "Unique",
        "value": "Vampire Nun"
    }]
}, {
    "name": "Vampire Slayer",
    "amount": 1,
    "fileName": "VampireSlayer",
    "attributes": [{
        "trait_type": "Unique",
        "value": "Vampire Slayer"
    }]
}, {
    "name": "Bat (1 of 8)",
    "amount": 1,
    "fileName": "Bat1",
    "attributes": [{
        "trait_type": "Unique",
        "value": "Bathead"
    }]
}, {
    "name": "Bat (2 of 8)",
    "amount": 1,
    "fileName": "Bat2",
    "attributes": [{
        "trait_type": "Unique",
        "value": "Bathead"
    }]
}, {
    "name": "Bat (3 of 8)",
    "amount": 1,
    "fileName": "Bat3",
    "attributes": [{
        "trait_type": "Unique",
        "value": "Bathead"
    }]
}, {
    "name": "Bat (4 of 8)",
    "amount": 1,
    "fileName": "Bat4",
    "attributes": [{
        "trait_type": "Unique",
        "value": "Bathead"
    }]
}, {
    "name": "Bat (5 of 8)",
    "amount": 1,
    "fileName": "Bat5",
    "attributes": [{
        "trait_type": "Unique",
        "value": "Bathead"
    }]
}, {
    "name": "Bat (6 of 8)",
    "amount": 1,
    "fileName": "Bat6",
    "attributes": [{
        "trait_type": "Unique",
        "value": "Bathead"
    }]
}, {
    "name": "Bat (7 of 8)",
    "amount": 1,
    "fileName": "Bat7",
    "attributes": [{
        "trait_type": "Unique",
        "value": "Bathead"
    }]
}, {
    "name": "Bat (8 of 8)",
    "amount": 1,
    "fileName": "Bat8",
    "attributes": [{
        "trait_type": "Unique",
        "value": "Bathead"
    }]
}, {
    "name": false,
    "amount": 1,
    "attributes": [{
        "trait_type": "Accessory",
        "value": "None"
    }, {
        "trait_type": "Background",
        "value": "Pastel Green"
    }, {
        "trait_type": "Beard",
        "value": "None"
    }, {
        "trait_type": "Clothes",
        "value": "OnlyFreddy Shirt"
    }, {
        "trait_type": "Eyes",
        "value": "BTC"
    }, {
        "trait_type": "Glasses",
        "value": "VR Headset"
    }, {
        "trait_type": "Hair",
        "value": "Black"
    }, {
        "trait_type": "Hat",
        "value": "None"
    }, {
        "trait_type": "Body",
        "value": "Gold"
    }, {
        "trait_type": "Head",
        "value": "Gold"
    }, {
        "trait_type": "Moon",
        "value": "Sun"
    }, {
        "trait_type": "Mouth",
        "value": "Single Diamond Tooth"
    }]
}, {
    "name": false,
    "amount": 1,
    "attributes": [{
        "trait_type": "Accessory",
        "value": "None"
    }, {
        "trait_type": "Background",
        "value": "Maroon"
    }, {
        "trait_type": "Beard",
        "value": "None"
    }, {
        "trait_type": "Clothes",
        "value": "Cloak"
    }, {
        "trait_type": "Eyes",
        "value": "Red Eyes"
    }, {
        "trait_type": "Glasses",
        "value": "None"
    }, {
        "trait_type": "Hair",
        "value": "Black"
    }, {
        "trait_type": "Hat",
        "value": "None"
    }, {
        "trait_type": "Body",
        "value": "Blue"
    }, {
        "trait_type": "Head",
        "value": "Blue"
    }, {
        "trait_type": "Moon",
        "value": "Sun"
    }, {
        "trait_type": "Mouth",
        "value": "Base"
    }]
}, {
    "name": false,
    "amount": 1,
    "attributes": [{
        "trait_type": "Accessory",
        "value": "Drool"
    }, {
        "trait_type": "Background",
        "value": "Maroon"
    }, {
        "trait_type": "Beard",
        "value": "None"
    }, {
        "trait_type": "Clothes",
        "value": "OnlyFangs Shirt"
    }, {
        "trait_type": "Eyes",
        "value": "Red Eyes"
    }, {
        "trait_type": "Glasses",
        "value": "None"
    }, {
        "trait_type": "Hair",
        "value": "Black"
    }, {
        "trait_type": "Hat",
        "value": "Stake"
    }, {
        "trait_type": "Body",
        "value": "Blue"
    }, {
        "trait_type": "Head",
        "value": "Blue"
    }, {
        "trait_type": "Moon",
        "value": "Moon"
    }, {
        "trait_type": "Mouth",
        "value": "Base"
    }]
}, {
    "name": false,
    "amount": 1,
    "attributes": [{
        "trait_type": "Accessory",
        "value": "Cross"
    }, {
        "trait_type": "Clothes",
        "value": "Gold Tux"
    }, {
        "trait_type": "Eyes",
        "value": "Gold Eyes"
    }, {
        "trait_type": "Hair",
        "value": "Gold"
    }, {
        "trait_type": "Hat",
        "value": "Kings Crown"
    }, {
        "trait_type": "Body",
        "value": "Gold"
    }, {
        "trait_type": "Head",
        "value": "Gold"
    }, {
        "trait_type": "Moon",
        "value": "Moon"
    }, {
        "trait_type": "Mouth",
        "value": "Gold Grills"
    }]
}, {
    "name": false,
    "amount": 1,
    "attributes": [{
        "trait_type": "Accessory",
        "value": "Cross"
    }, {
        "trait_type": "Clothes",
        "value": "Gold Tux"
    }, {
        "trait_type": "Eyes",
        "value": "Gold Eyes"
    }, {
        "trait_type": "Hair",
        "value": "Gold"
    }, {
        "trait_type": "Hat",
        "value": "Mini Crown"
    }, {
        "trait_type": "Body",
        "value": "Gold"
    }, {
        "trait_type": "Head",
        "value": "Gold"
    }, {
        "trait_type": "Moon",
        "value": "Moon"
    }, {
        "trait_type": "Mouth",
        "value": "Gold Grills"
    }]
}, {
    "name": false,
    "amount": 10,
    "attributes": [{
        "trait_type": "Clothes",
        "value": "Slayer"
    }, {
        "trait_type": "Hat",
        "value": "Witch Hunter"
    }]
}, {
    "name": false,
    "amount": 10,
    "attributes": [{
        "trait_type": "Clothes",
        "value": "Sea Captain"
    }, {
        "trait_type": "Glasses",
        "value": "Eye Patch"
    }, {
        "trait_type": "Hat",
        "value": "Sea Captain"
    }]
}, {
    "name": false,
    "amount": 25,
    "attributes": [{
        "trait_type": "Clothes",
        "value": "Detective Trenchcoat"
    }, {
        "trait_type": "Hat",
        "value": "Crooked Fedora"
    }]
}, {
    "name": false,
    "amount": 20,
    "attributes": [{
        "trait_type": "Clothes",
        "value": "Army General"
    }, {
        "trait_type": "Hat",
        "value": "Green Beret"
    }]
}, {
    "name": false,
    "amount": 20,
    "attributes": [{
        "trait_type": "Clothes",
        "value": "Army General"
    }, {
        "trait_type": "Hat",
        "value": "Red Beret"
    }]
}, {
    "name": false,
    "amount": 25,
    "attributes": [{
        "trait_type": "Clothes",
        "value": "Black Hoodie"
    }, {
        "trait_type": "Hat",
        "value": "Black Cap"
    }]
}, {
    "name": false,
    "amount": 25,
    "attributes": [{
        "trait_type": "Clothes",
        "value": "Blue Hoodie"
    }, {
        "trait_type": "Hat",
        "value": "Blue Cap"
    }]
}, {
    "name": false,
    "amount": 25,
    "attributes": [{
        "trait_type": "Clothes",
        "value": "Red Hoodie"
    }, {
        "trait_type": "Hat",
        "value": "Red Cap"
    }]
}, {
    "name": false,
    "amount": 15,
    "attributes": [{
        "trait_type": "Clothes",
        "value": "Old Worn Coat"
    }, {
        "trait_type": "Mouth",
        "value": "Rotten Teeth"
    }]
}, {
    "name": false,
    "amount": 15,
    "attributes": [{
        "trait_type": "Clothes",
        "value": "Navy Admiral"
    }, {
        "trait_type": "Hat",
        "value": "Sea Captain"
    }]
}, {
    "name": false,
    "amount": 10,
    "attributes": [{
        "trait_type": "Eyes",
        "value": "Bloodshot"
    }, {
        "trait_type": "Body",
        "value": "Zombie"
    }, {
        "trait_type": "Head",
        "value": "Zombie"
    }]
}, {
    "name": false,
    "amount": 15,
    "attributes": [{
        "trait_type": "Hair",
        "value": "Green"
    }, {
        "trait_type": "Mouth",
        "value": "Red Lipstick"
    }]
}, {
    "name": false,
    "amount": 10,
    "attributes": [{
        "trait_type": "Beard",
        "value": "Goatee"
    }, {
        "trait_type": "Clothes",
        "value": "The Accountant"
    }, {
        "trait_type": "Glasses",
        "value": "Monocle"
    }, {
        "trait_type": "Hair",
        "value": "Black"
    }, {
        "trait_type": "Body",
        "value": "Purple Count"
    }, {
        "trait_type": "Head",
        "value": "Purple Count"
    }]
}, {
    "name": false,
    "amount": 10,
    "attributes": [{
        "trait_type": "Accessory",
        "value": "Prison Mask"
    }, {
        "trait_type": "Clothes",
        "value": "Prison Uniform"
    }]
}, {
    "name": false,
    "amount": 15,
    "attributes": [{
        "trait_type": "Clothes",
        "value": "Daywalker"
    }, {
        "trait_type": "Glasses",
        "value": "Cool Shades"
    }]
}, {
    "name": false,
    "amount": 15,
    "attributes": [{
        "trait_type": "Clothes",
        "value": "Black Tracksuit"
    }, {
        "trait_type": "Hat",
        "value": "Tennis Headband Blue"
    }]
}, {
    "name": false,
    "amount": 15,
    "attributes": [{
        "trait_type": "Clothes",
        "value": "Red Tracksuit"
    }, {
        "trait_type": "Hat",
        "value": "Tennis Headband Red"
    }]
}, {
    "name": false,
    "amount": 10,
    "attributes": [{
        "trait_type": "Clothes",
        "value": "Space Governor"
    }, {
        "trait_type": "Eyes",
        "value": "Blue"
    }, {
        "trait_type": "Hair",
        "value": "Grey"
    }]
}, {
    "name": false,
    "amount": 10,
    "attributes": [{
        "trait_type": "Clothes",
        "value": "Thriller"
    }, {
        "trait_type": "Eyes",
        "value": "Demonic"
    }, {
        "trait_type": "Glasses",
        "value": "VR Headset"
    }, {
        "trait_type": "Hair",
        "value": "Black"
    }, {
        "trait_type": "Body",
        "value": "Zombie"
    }, {
        "trait_type": "Head",
        "value": "Zombie"
    }]
}, {
    "name": false,
    "amount": 15,
    "attributes": [{
        "trait_type": "Clothes",
        "value": "Flannel"
    }, {
        "trait_type": "Hair",
        "value": "Black"
    }, {
        "trait_type": "Body",
        "value": "Nightcrawler"
    }, {
        "trait_type": "Head",
        "value": "Nightcrawler"
    }, {
        "trait_type": "Mouth",
        "value": "Pierced Tongue"
    }]
}, {
    "name": false,
    "amount": 15,
    "attributes": [{
        "trait_type": "Clothes",
        "value": "Flannel"
    }, {
        "trait_type": "Hair",
        "value": "Black"
    }, {
        "trait_type": "Body",
        "value": "Nightcrawler"
    }, {
        "trait_type": "Head",
        "value": "Nightcrawler"
    }, {
        "trait_type": "Mouth",
        "value": "Tongue"
    }]
}, {
    "name": false,
    "amount": 5,
    "attributes": [{
        "trait_type": "Clothes",
        "value": "Business Suit"
    }, {
        "trait_type": "Hair",
        "value": "None"
    }]
}, {
    "name": false,
    "amount": 10,
    "attributes": [{
        "trait_type": "Clothes",
        "value": "OnlyFangs Shirt"
    }, {
        "trait_type": "Accessory",
        "value": "Drool"
    }]
}, {
    "name": false,
    "amount": 15,
    "attributes": [{
        "trait_type": "Clothes",
        "value": "Reaver Shroud"
    }, {
        "trait_type": "Eyes",
        "value": "No Pupils"
    }, {
        "trait_type": "Hair",
        "value": "Black"
    }]
}, {
    "name": false,
    "amount": 10,
    "attributes": [{
        "trait_type": "Eyes",
        "value": "Black"
    }, {
        "trait_type": "Hat",
        "value": "Devil Horns"
    }, {
        "trait_type": "Body",
        "value": "Shadow"
    }, {
        "trait_type": "Head",
        "value": "Shadow"
    }, {
        "trait_type": "Mouth",
        "value": "Bloody Mouth"
    }]
}, {
    "name": false,
    "amount": 10,
    "attributes": [{
        "trait_type": "Eyes",
        "value": "Demonic"
    }, {
        "trait_type": "Hat",
        "value": "Devil Horns"
    }, {
        "trait_type": "Body",
        "value": "Shadow"
    }, {
        "trait_type": "Head",
        "value": "Shadow"
    }, {
        "trait_type": "Mouth",
        "value": "Bloody Mouth"
    }]
}, {
    "name": false,
    "amount": 5,
    "attributes": [{
        "trait_type": "Accessory",
        "value": "Karate"
    }, {
        "trait_type": "Clothes",
        "value": "Karate Gi"
    }]
}, {
    "name": false,
    "amount": 3,
    "attributes": [{
        "trait_type": "Clothes",
        "value": "Jiangshi Black"
    }, {
        "trait_type": "Hat",
        "value": "Jiangshi Black Talisman"
    }]
}, {
    "name": false,
    "amount": 5,
    "attributes": [{
        "trait_type": "Clothes",
        "value": "Jiangshi"
    }, {
        "trait_type": "Hat",
        "value": "Jiangshi Talisman"
    }]
}, {
    "name": false,
    "amount": 1,
    "attributes": [{
        "trait_type": "Accessory",
        "value": "Cross"
    }, {
        "trait_type": "Background",
        "value": "Maroon"
    }, {
        "trait_type": "Beard",
        "value": "None"
    }, {
        "trait_type": "Clothes",
        "value": "Red Vampire Cloak"
    }, {
        "trait_type": "Eyes",
        "value": "Red Eyes"
    }, {
        "trait_type": "Glasses",
        "value": "Monocle"
    }, {
        "trait_type": "Hair",
        "value": "Black"
    }, {
        "trait_type": "Hat",
        "value": "Kings Crown"
    }, {
        "trait_type": "Body",
        "value": "Gold"
    }, {
        "trait_type": "Head",
        "value": "Gold"
    }, {
        "trait_type": "Moon",
        "value": "Sun"
    }, {
        "trait_type": "Mouth",
        "value": "Gold Grills"
    }]
}]

const weights = {
    "Accessory": [
        { "name": "Cigar", "weight": 10 },
        { "name": "Ciggy", "weight": 5 },
        { "name": "Cross", "weight": 7 },
        { "name": "Diamond Stud", "weight": 3 },
        { "name": "Drool", "weight": 5 },
        { "name": "Gold Hoop", "weight": 4 },
        { "name": "Gold Stud", "weight": 4 },
        { "name": "Joint", "weight": 5 },
        { "name": "Long Ciggy", "weight": 8 },
        { "name": "Pipe", "weight": 10 },
        { "name": "Prison Mask", "weight": 4 },
        { "name": "Silver Hoop", "weight": 5 },
        { "name": "Silver Stud", "weight": 5 },
        { "name": "Flu Mask", "weight": 5 },
        { "name": "Flu Mask Bloody", "weight": 5 },
        { "name": "Paperclip Earring", "weight": 3 },
        { "name": "None", "weight": 25 }
    ],
    "Background": [
        { "name": "Blue", "weight": 13 },
        { "name": "Pastel Green", "weight": 13 },
        { "name": "Cool Brown", "weight": 13 },
        { "name": "Light Red", "weight": 13 },
        { "name": "Magenta", "weight": 13 },
        { "name": "Orange", "weight": 13 },
        { "name": "Pea Green", "weight": 13 },
        { "name": "Pink", "weight": 13 },
        { "name": "Dark Teal", "weight": 13 },
        { "name": "Forest Green", "weight": 13 },
        { "name": "Green", "weight": 13 },
        { "name": "Maroon", "weight": 13 },
        { "name": "Red", "weight": 12 },
        { "name": "Rust Brown", "weight": 12 },
        { "name": "Teal", "weight": 12 },
        { "name": "Twilight Purple", "weight": 12 }
    ],
    "Beard": [
        { "name": "Big Beard", "weight": 10 },
        { "name": "Goatee", "weight": 10 },
        { "name": "Moustache", "weight": 5 },
        { "name": "Stubble", "weight": 15 },
        { "name": "None", "weight": 60 }
    ],
    "Clothes": [
        { "name": "Army General", "weight": 75 },
        { "name": "Black Fur Coat", "weight": 300 },
        { "name": "Black Hoodie", "weight": 250 },
        { "name": "Black Tracksuit", "weight": 200 },
        { "name": "Black Turtleneck", "weight": 100 },
        { "name": "Black Tux", "weight": 50 },
        { "name": "Bloody Singlet", "weight": 100 },
        { "name": "Blue Hoodie", "weight": 300 },
        { "name": "Blue Tux", "weight": 40 },
        { "name": "Brown Fur Coat", "weight": 300 },
        { "name": "Bulls Jersey", "weight": 250 },
        { "name": "Business Suit", "weight": 100 },
        { "name": "Celtics Jersey", "weight": 250 },
        { "name": "Cloak", "weight": 100 },
        { "name": "Daywalker", "weight": 60 },
        { "name": "Detective Trenchcoat", "weight": 200 },
        { "name": "Flannel", "weight": 100 },
        { "name": "Gold Tux", "weight": 20 },
        { "name": "Impaler Armor", "weight": 40 },
        { "name": "Lakers Jersey", "weight": 250 },
        { "name": "Leather Jacket", "weight": 200 },
        { "name": "Navy Admiral", "weight": 75 },
        { "name": "Old Worn Coat", "weight": 250 },
        { "name": "OnlyFangs Shirt", "weight": 160 },
        { "name": "Pajamas", "weight": 40 },
        { "name": "Prison Uniform", "weight": 40 },
        { "name": "Reaver Shroud", "weight": 40 },
        { "name": "Red Hoodie", "weight": 300 },
        { "name": "Red Tracksuit", "weight": 200 },
        { "name": "Red Tux", "weight": 30 },
        { "name": "Red Vampire Cloak", "weight": 50 },
        { "name": "Sea Captain", "weight": 200 },
        { "name": "Slayer", "weight": 200 },
        { "name": "Space Governor", "weight": 150 },
        { "name": "The Accountant", "weight": 40 },
        { "name": "Thriller", "weight": 40 },
        { "name": "Turtleneck", "weight": 150 },
        { "name": "Vampire Lord", "weight": 20 },
        { "name": "Vampire Nobility", "weight": 100 },
        { "name": "White Tux", "weight": 80 },
        { "name": "Jiangshi", "weight": 20 },
        { "name": "Jiangshi Black", "weight": 20 },
        { "name": "Karate Gi", "weight": 20 },
        { "name": "Roadwarrior", "weight": 50 },
        { "name": "OnlyFreddy Shirt", "weight": 0 },
        { "name": "Ruffian", "weight": 40 },
        { "name": "Striped Suit", "weight": 100 },
        { "name": "None", "weight": 200 }
    ],
    "Eyes": [
        { "name": "Red Eyes", "weight": 220 },
        { "name": "Black", "weight": 120 },
        { "name": "Bloodshot", "weight": 80 },
        { "name": "Blue Laser", "weight": 35 },
        { "name": "Blue", "weight": 220 },
        { "name": "BTC", "weight": 1 },
        { "name": "Dark", "weight": 120 },
        { "name": "Demonic", "weight": 100 },
        { "name": "Single Gold Eye", "weight": 60 },
        { "name": "Gold Eyes", "weight": 30 },
        { "name": "Hypno", "weight": 30 },
        { "name": "No Pupils", "weight": 50 },
        { "name": "Red Laser", "weight": 15 }
    ],
    "Glasses": [
        { "name": "3D Glasses", "weight": 3 },
        { "name": "Anime Hero Sunglasses", "weight": 7 },
        { "name": "Blindfold", "weight": 7 },
        { "name": "Cool Shades", "weight": 6 },
        { "name": "Eye Patch", "weight": 15 },
        { "name": "Glasses", "weight": 13 },
        { "name": "Holo Shades", "weight": 8 },
        { "name": "Monocle", "weight": 5 },
        { "name": "Old Fashioned Glasses", "weight": 10 },
        { "name": "Pit Viper Cool", "weight": 4 },
        { "name": "Pit Viper Hot", "weight": 4 },
        { "name": "The Hitman", "weight": 5 },
        { "name": "VR Headset", "weight": 2 },
        { "name": "None", "weight": 16 }
    ],
    "Hair": [
        { "name": "Base", "weight": 20 },
        { "name": "Black", "weight": 12 },
        { "name": "Blond", "weight": 12 },
        { "name": "Blue", "weight": 10 },
        { "name": "Brown", "weight": 10 },
        { "name": "Gold", "weight": 3 },
        { "name": "Green", "weight": 7 },
        { "name": "Grey", "weight": 11 },
        { "name": "Platinum", "weight": 2 },
        { "name": "Purple", "weight": 8 },
        { "name": "Red", "weight": 5 },
        { "name": "None", "weight": 1 }
    ],
    "Hat": [
        { "name": "Black Cap", "weight": 40 },
        { "name": "Blue Cap", "weight": 40 },
        { "name": "Cat Ears Black", "weight": 30 },
        { "name": "Cat Ears White", "weight": 30 },
        { "name": "Crooked Fedora", "weight": 30 },
        { "name": "Crossbow Bolt", "weight": 20 },
        { "name": "Flat Cap", "weight": 50 },
        { "name": "Giant Moth", "weight": 20 },
        { "name": "Green Beret", "weight": 50 },
        { "name": "Halo", "weight": 20 },
        { "name": "Headphones", "weight": 30 },
        { "name": "Kings Crown", "weight": 30 },
        { "name": "Laser Moth", "weight": 10 },
        { "name": "Mini Crown", "weight": 30 },
        { "name": "Red Beret", "weight": 50 },
        { "name": "Red Cap", "weight": 50 },
        { "name": "Sea Captain", "weight": 30 },
        { "name": "Spinner Cap", "weight": 30 },
        { "name": "Stake", "weight": 20 },
        { "name": "SVS Cap", "weight": 20 },
        { "name": "Tennis Headband Blue", "weight": 50 },
        { "name": "Tennis Headband Red", "weight": 50 },
        { "name": "Third Eye", "weight": 20 },
        { "name": "Witch Hunter", "weight": 50 },
        { "name": "Devil Horns", "weight": 2 },
        { "name": "Jiangshi Black Talisman", "weight": 0 },
        { "name": "Jiangshi Talisman", "weight": 0 },
        { "name": "Jiangshi Black", "weight": 4 },
        { "name": "Jiangshi", "weight": 4 },
        { "name": "Karate", "weight": 5 },
        { "name": "Small Bowler Hat", "weight": 10 },
        { "name": "None", "weight": 200 }
    ],
    "Body": [
        { "name": "Blue", "weight": 32 },
        { "name": "Burning", "weight": 10 },
        { "name": "Cyborg", "weight": 12 },
        { "name": "Gold", "weight": 1 },
        { "name": "Nightcrawler", "weight": 10 },
        { "name": "Purple Count", "weight": 15 },
        { "name": "Shadow", "weight": 8 },
        { "name": "Zombie", "weight": 5 },
        { "name": "Sparkle", "weight": 3 }
    ],
    "Head": [
        { "name": "Blue", "weight": 32 },
        { "name": "Burning", "weight": 10 },
        { "name": "Cyborg", "weight": 12 },
        { "name": "Gold", "weight": 1 },
        { "name": "Nightcrawler", "weight": 10 },
        { "name": "Purple Count", "weight": 15 },
        { "name": "Shadow", "weight": 8 },
        { "name": "Sparkle", "weight": 3 },
        { "name": "Zombie", "weight": 5 }
    ],
    "Moon": [
        { "name": "Blood Moon", "weight": 10 },
        { "name": "Moon", "weight": 70 },
        { "name": "Sun", "weight": 20 }
    ],
    "Mouth": [
        { "name": "Base", "weight": 26 },
        { "name": "Black Lipstick", "weight": 6 },
        { "name": "Bloody Mouth", "weight": 8 },
        { "name": "Diamond Fangs", "weight": 3 },
        { "name": "Diamond Grills", "weight": 3 },
        { "name": "Disgust", "weight": 5 },
        { "name": "Gold Fangs", "weight": 4 },
        { "name": "Gold Grills", "weight": 4 },
        { "name": "Pierced Tongue", "weight": 5 },
        { "name": "Rainbow Grills", "weight": 2 },
        { "name": "Red Lipstick", "weight": 10 },
        { "name": "Rotten Teeth", "weight": 6 },
        { "name": "Single Bloody Tooth", "weight": 6 },
        { "name": "Single Diamond Tooth", "weight": 2 },
        { "name": "Tongue", "weight": 13 }
    ]
}

function generateAttributes(predefined) {
    const chooseSpecific = (trait, rules, include) => {
        if (include) rules.push("None")
        return chooser.chooseWeightedObject(weights[trait].filter(t => include == rules.includes(t.name)), "weight", 1, random()).name
    }

    const attributes = {}
    Object.keys(weights)
        .forEach(trait_type => attributes[trait_type] = predefined.find(attr => attr.trait_type == trait_type)?.value || chooser.chooseWeightedObject(weights[trait_type], "weight", 1, random()).name)

    let lastAttributes
    while (JSON.stringify(lastAttributes) !== JSON.stringify(attributes)) {
        lastAttributes = JSON.parse(JSON.stringify(attributes))

        // These are all clashes
        attributes.Body = attributes.Head
        if (attributes.Hat == "Headphones") attributes.Accessory = chooseSpecific("Accessory", ["Cross"], false)
        if (attributes.Accessory == "Drool") attributes.Mouth = "Base"
        if (attributes.Body == "Shadow") attributes.Mouth = chooseSpecific("Mouth", ["Black Lipstick", "Red Lipstick"], false)

        if (["Blue Laser", "Red Laser", "BTC"].includes(attributes.Eyes)) {
            if (attributes.Accessory == "Prison Mask") attributes.Accessory = chooseSpecific("Accessory", ["Prison Mask"], false)
            attributes.Glasses = "None"
        }

        if (attributes.Accessory == "Prison Mask") {
            attributes.Hat = chooseSpecific("Hat", ["Crossbow Bolt", "Giant Moth", "Halo", "Laser Moth", "Stake", "Third Eye"], true)
            attributes.Beard = "None"
            attributes.Glasses = "None"
            attributes.Mouth = chooseSpecific("Mouth", ["Tongue"], false)
        }

        if (["Tongue", "Pierced Tongue"].includes(attributes.Mouth)) attributes.Accessory = chooseSpecific("Accessory", [ attributes.Hat == "Headphones" ? false : "Cross", "Diamond Stud", "Gold Hoop", "Gold Stud", "Silver Hoop", "Silver Stud"].filter(Boolean), true)

        if (["Disgust", "Rotten Teeth", "Tongue", "Pierced Tongue"].includes(attributes.Mouth)) attributes.Accessory = chooseSpecific("Accessory", ["Diamond Stud", attributes.Hat == "Headphones" ? false : "Cross", "Gold Hoop", "Gold Stud", "Silver Hoop", "Silver Stud"], true)
        if (attributes.Hair == "None") attributes.Hat = "None"

        if (attributes.Hat.includes("Jiangshi")) attributes.Glasses = "None"
        if (attributes.Hat == "Third Eye") attributes.Glasses = chooseSpecific("Glasses", ["Monocle", "Eye Patch"], true)

        if (attributes.Body == "Burning") attributes.Moon = "Sun"
        if (attributes.Accessory.includes("Flu Mask")) {
            attributes.Glasses = chooseSpecific("Glasses", ["Holo Shades", "Monocle", "Eye Patch", "Anime Hero Sunglasses"], true)
            attributes.Beard = "None"
        }

        if (["Anime Hero Sunglasses", "VR Headset", "Blindfold"].includes(attributes.Glasses)) attributes.Hat = "None"
        if (attributes.Glasses == "Blindfold") {
            if (attributes.Hair == "None") attributes.Hair = chooseSpecific("Hair", [], false)
        }
    }

    if (attributes.Hair == "None" && attributes.Glasses == "Eye Patch") attributes.Glasses = "None"
    if (attributes.Glasses == "Eye Patch" && ["Blue Laser", "Red Laser"].includes(attributes.Eyes)) {
        attributes.Eyes = `Single ${attributes.Eyes.replace(" Laser", "")} Laser Eye`
    }

    if (attributes.Hat.includes("Talisman")) attributes.Accessory = "None"

    return Object.keys(attributes).map(trait_type => ({
        trait_type,
        value: attributes[trait_type]
    }))
}

const generateMetadata = (attributes, tokenId) => ({
    name: uniqueNames[tokenId - 1] || `Sneaky Vampire #${tokenId}`,
    description: `[Image without background](https://ipfs.io/ipfs/bafybeibltrk5hoi5p3swpiw5wnthqxh7z5xvker6xlqjqjfvqdpgbb4asi/${tokenId}_no_bg.png)`,
    attributes,
    image: `ipfs://bafybeibltrk5hoi5p3swpiw5wnthqxh7z5xvker6xlqjqjfvqdpgbb4asi/${tokenId}.png`
})

function run() {
    const vampires = [],
          vampireHashes = []
    
    for (let i = 8888; i--;) {
        const attributes = generateAttributes([])
        const hash = SparkMD5.hash(JSON.stringify(attributes))
        if (vampireHashes.includes(hash)) { i++; continue }
        vampireHashes.push(hash)
        vampires.push(attributes)
    }

    global.uniqueNames = {}
    uniques.forEach(unique => {
        for (let i = unique.amount; i--;) {
            let index
            while (index == null || uniqueNames[index]) {
                index = Math.floor(random() * 8888) + 1
            }

            uniqueNames[index] = unique.name
            vampires[index] = unique.fileName
                ? unique.attributes // For pregenerated uniques
                : generateAttributes(unique.attributes, random) // For forced sets
        }
    })

    const totalHash = SparkMD5.hash(JSON.stringify(vampires))
    console.log("Combined hash of all vampires:", totalHash)

    // i + 1: tokens start at 1, not 0
    const fullMetadata = vampires.map((attributes, i) => generateMetadata(attributes, i + 1))
    fs.writeFile("./all_alt.json", JSON.stringify(fullMetadata))
}

run()
