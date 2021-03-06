import json

shop = {
    "SHOP": [{
        "name": "Pendentif de sagesse de Leonard de Vinci :medal:",
        "description":
        "Avec ce pendentif, vous serez un peu moins bête (c'est déjà un bon début).",
        "price": 3000,
        "item_number": 1,
    }, {
        "name": "Baton de Merlin :magic_wand:",
        "description": "Par la barbe de l'enchanteur, le voilà retrouvé !",
        "price": 10000,
        "item_number": 2,
    }, {
        "name": "Bottes de sept lieues :boot:",
        "description": "Vous ne serez plus jamais en retard !",
        "price": 2000,
        "item_number": 3,
    }, {
        "name": "Couronne de la reine d'Angleterre :crown:",
        "description": "Gardée jalousement dans son château, la voilà !",
        "price": 3000,
        "item_number": 4,
    }, {
        "name": "Excalibur :dagger:",
        "description":
        "Enfin retirée du rocher, elle permet d'outrepasser les lourdaux qui se protègent avec un bouclier ! Vous pourrez rester virtuose une semaine après utilisation !",
        "price": 4000,
        "item_number": 5,
    }, {
        "name": "Arc de Robin des Bois :bow_and_arrow:",
        "description": "Ne rate jamais sa cible !",
        "price": 8000,
        "item_number": 6
    }, {
        "name": "Eclair de Zeus :zap:",
        "description": "Foudroyez vos ennemis !",
        "price": 10000,
        "item_number": 7,
    }, {
        "name": "Exploitation pétrolière :construction_site:",
        "description":
        "Investissez dans le pétrole et gagnez automatiquement de l'argent !",
        "price": 5000,
        "item_number": 8,
    }, {
        "name": "Sablier temporel :hourglass:",
        "description": "Réinitialisez vos temps d'attente !!!",
        "price": 3000,
        "item_number": 9,
    }, {
        "name": "Bouclier Divin :shield:",
        "description":
        "Empêchez les gens de vous voler pendant une semaine (sauf si ils possèdent excalibur) !!!",
        "price": 2000,
        "item_number": 10,
    }, {
        "name": "Crotte :poop:",
        "description": "Offrez la à vos amis !",
        "price": 10,
        "item_number": 11,
    }, {
        "name": "Justice corrompue :scales:",
        "description":
        "Faite la preuve de votre richesse est corrompez le monde entier !",
        "price": 1000000000,
        "item_number": 12,
    }, {
        "name": "Richesse exquise :reminder_ribbon:",
        "description": "Montrez une preuve de votre raffinement extrême !",
        "price": 1000000000000,
        "item_number": 13,
    }, {
        "name": "Richesse suprême :rosette: ",
        "description":
        "L'objet qui ferait mourir de jalousie un milliardaire !",
        "price": 99000000000000000,
        "item_number": 14
    }, {
        "name": "Part d'action :part_alternation_mark:",
        "description":
        "Achetez et revendez des parts d'entreprises et entrez en bourse ! (Attention, risque de perte de votre argent et de dépression !)",
        "price": 98765432101239810,
        "item_number": 15
    }],

    "PREFIXES": {
        "daily": "←+→",
        "hebdo": "-@_@-",
        "gold": "°-°",
        "beg": "-_-",
        "report": "+_+",
        "steal": "X_X",
        "items": "¤_¤",
        "bannis": "*_*",
        "shield": "→0←",
        "xp": "↔xp↔",
        "level": "↔lvl↔",
        "auto_gold_won": "_*-*_",
        "sablier": "♀_♀",
        "inactivity": "O_O",
        "excalibur": "T_T",

        "user_action_possessions": "U_U|user_actions|",

        "Red_actions": "U_U|base_action|Red",
        "Green_actions": "U_U|base_action|Green",
        "Blue_actions": "U_U|base_action|Blue",

        "Red_historic": "U_U|base_action|Red|history",
        "Green_historic": "U_U|base_action|Green|history",
        "Blue_historic": "U_U|base_action|Blue|history",
    }
}

json_string = json.dumps(shop, ensure_ascii=False, indent=4)
print(json_string)

# Transférer en json
with open('language/fr.json', 'w') as outfile:
    outfile.write(json_string)
