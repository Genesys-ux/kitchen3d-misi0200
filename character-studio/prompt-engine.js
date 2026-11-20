/**
 * Bilingual (Indonesian + English) Prompt-to-Character Engine
 * Mode 1: Instant Smart Semantic Parser (100% offline, zero API key, 25+ archetypes + fine-grained trait & contextual color extraction)
 * Mode 2: Optional Gemini 3.8 Flash Interactions API (BYO API key stored in browser localStorage)
 */
(function (global) {
  'use strict';

  const PROMPT_EXAMPLES = [
    {
      label: '🕵️ Detektif Noir',
      prompt: 'Detektif noir pakai jas hujan gelap, topi fedora miring, kacamata bulat, pegang kaca pembesar, ekspresi curiga'
    },
    {
      label: '👨‍🚀 Astronot Panik',
      prompt: 'Astronot cemas di luar angkasa pakai helm kaca, baju luar angkasa putih, jetpack, pegang pistol laser, ekspresi panik berkeringat'
    },
    {
      label: '👨‍🍳 Koki Pizza',
      prompt: 'Koki pizza Italia ramah berkumis melingkar, topi chef putih, celemek merah, pipi merona, pegang spatula, melambai'
    },
    {
      label: '🏴‍☠️ Bajak Laut',
      prompt: 'Kapten bajak laut garang pakai topi tricorne, penutup mata, janggut lebat, mantel merah emas, pegang pedang'
    },
    {
      label: '🧪 Ilmuwan Gila',
      prompt: 'Ilmuwan gila berambut putih acak, jas lab putih, kacamata bulat, pegang tabung reaksi hijau, senyum licik'
    },
    {
      label: '🧙 Penyihir Ungu',
      prompt: 'Penyihir misterius berjanggut panjang, topi kerucut ungu bintang emas, jubah gelap, pegang tongkat sihir'
    },
    {
      label: '💻 Hacker Neon',
      prompt: 'Hacker cyberpunk pakai hoodie gelap aksen cyan, visor neon futuristik, tas ransel, pegang laptop, ekspresi licik'
    },
    {
      label: '🤠 Koboi Gurun',
      prompt: 'Koboi gurun pakai topi cowboy coklat, rompi kulit, bandana merah, kumis tebal, ekspresi santai'
    },
    {
      label: '⛏️ Penambang Tua',
      prompt: 'Penambang tua pakai helm tambang kuning berlampu, baju flanel kotak-kotak biru, suspender, pegang beliung, ekspresi kaget'
    },
    {
      label: '👑 Raja Emas',
      prompt: 'Raja kerajaan pakai mahkota emas permata merah, jubah raja ungu, seragam jenderal, kumis melingkar, pose heroik'
    },
    {
      label: '⚙️ Steampunk',
      prompt: 'Insinyur steampunk pakai topi tinggi, goggles kuningan, mantel steampunk coklat, tas ransel, pegang kunci inggris, ekspresi fokus'
    },
    {
      label: '🏍️ Biker Keren',
      prompt: 'Rocker biker pakai jaket kulit hitam, kacamata hitam, rambut mohawk merah, sabuk taktis, pose heroik'
    }
  ];

  const COLOR_MAP = [
    { keys: ['merah tua', 'marun', 'maroon', 'crimson', 'burgundy'], hex: '#8F2432', name: 'Merah Tua' },
    { keys: ['merah', 'red', 'scarlet'], hex: '#C9382E', name: 'Merah' },
    { keys: ['biru tua', 'navy', 'dongker', 'midnight'], hex: '#243B6B', name: 'Biru Tua' },
    { keys: ['biru muda', 'sky blue', 'biru langit', 'azure'], hex: '#3898D8', name: 'Biru Muda' },
    { keys: ['biru', 'blue', 'cobalt'], hex: '#2D599E', name: 'Biru' },
    { keys: ['cyan', 'toska', 'tosca', 'teal', 'turqoise', 'turquoise', 'neon'], hex: '#14B8A6', name: 'Cyan' },
    { keys: ['hijau tua', 'emerald', 'army', 'zaitun', 'olive'], hex: '#2F5D46', name: 'Hijau Tua' },
    { keys: ['hijau', 'green', 'lime'], hex: '#2F9B6E', name: 'Hijau' },
    { keys: ['kuning', 'yellow', 'mustard'], hex: '#E5B438', name: 'Kuning' },
    { keys: ['emas', 'gold', 'golden', 'keemasan'], hex: '#E2B44B', name: 'Emas' },
    { keys: ['oranye', 'orange', 'jingga', 'tembaga', 'copper'], hex: '#D96B27', name: 'Oranye' },
    { keys: ['ungu tua', 'indigo', 'violet'], hex: '#4B2D6E', name: 'Ungu Tua' },
    { keys: ['ungu', 'purple', 'lavender'], hex: '#6E3B8E', name: 'Ungu' },
    { keys: ['pink', 'merah muda', 'magenta', 'fuschia', 'rose'], hex: '#C9447A', name: 'Pink' },
    { keys: ['coklat tua', 'dark brown', 'kopi'], hex: '#4E3324', name: 'Coklat Tua' },
    { keys: ['coklat', 'brown', 'kulit', 'leather', 'tan', 'khaki', 'krem tua'], hex: '#8A5A3A', name: 'Coklat' },
    { keys: ['putih', 'white', 'ivory', 'krem', 'cream', 'salju'], hex: '#F3EFE6', name: 'Putih' },
    { keys: ['abu', 'grey', 'gray', 'perak', 'silver', 'metalik', 'besi'], hex: '#5C6472', name: 'Abu-abu' },
    { keys: ['hitam', 'black', 'gelap', 'dark', 'noir', 'bayangan', 'shadow'], hex: '#282530', name: 'Gelap' }
  ];

  const ARCHETYPES = [
    {
      id: 'detective',
      label: 'Detektif Noir',
      keywords: ['detektif', 'detective', 'noir', 'sherlock', 'investigasi', 'mata-mata', 'spy', 'misteri', 'polisi rahasia'],
      cfg: {
        headShape: 'potato', skinColor: '#FCEEE3', blushColor: '#E5BEB2',
        eyes: 'suspicious', eyebrows: 'skeptical', mouth: 'smirk', beard: 'stubble',
        faceAccessory: 'round_glasses', eyeGazeX: 0.45,
        hat: 'fedora', hatPrimary: '#2A2733', hatAccent: '#B58E52', hatTilt: -5,
        backHair: 'side_part', hairColor: '#231D24',
        outfit: 'trench_coat', robeColor: '#3E3947', innerColor: '#EDE4D3', sashColor: '#25212C', trimColor: '#C9A25B',
        beltStyle: 'buckle', cape: 'none', emblem: 'none', pose: 'think', prop: 'magnifying_glass'
      }
    },
    {
      id: 'astronaut',
      label: 'Astronot',
      keywords: ['astronot', 'astronaut', 'antariksa', 'luar angkasa', 'space', 'nasa', 'kosmonot', 'planet', 'roket'],
      cfg: {
        headShape: 'round', skinColor: '#FFF5EC', blushColor: '#F0C7BC',
        eyes: 'shocked', eyebrows: 'raised', mouth: 'small_o', beard: 'none',
        faceAccessory: 'none',
        hat: 'astronaut_helmet', hatPrimary: '#F3F5F8', hatAccent: '#25A8E0', hatTilt: 0,
        backHair: 'short', hairColor: '#3A2820',
        outfit: 'spacesuit', robeColor: '#EAEFF5', innerColor: '#263448', sashColor: '#E04B2D', trimColor: '#38B6FF',
        beltStyle: 'utility_belt', cape: 'jetpack', capeColor: '#48566A', emblem: 'atom', pose: 'ready', prop: 'laser_blaster'
      }
    },
    {
      id: 'chef',
      label: 'Koki / Chef',
      keywords: ['koki', 'chef', 'masak', 'pizza', 'baker', 'roti', 'dapur', 'restoran', 'kuliner', 'kue'],
      cfg: {
        headShape: 'pear', skinColor: '#FFEFE2', blushColor: '#F2B8B0',
        eyes: 'happy', eyebrows: 'happy', mouth: 'happy_open', beard: 'handlebar',
        blush: true, faceAccessory: 'none',
        hat: 'chef_toque', hatPrimary: '#FAF8F3', hatAccent: '#D93829', hatTilt: 4,
        backHair: 'curly', hairColor: '#2E1E18',
        outfit: 'chef_apron', robeColor: '#F9F6EE', innerColor: '#D93829', sashColor: '#2A7B4F', trimColor: '#E8B84B',
        beltStyle: 'knot', cape: 'none', emblem: 'none', pose: 'wave', prop: 'spatula'
      }
    },
    {
      id: 'cyberpunk',
      label: 'Hacker Cyberpunk',
      keywords: ['hacker', 'cyberpunk', 'cyber', 'programmer', 'coder', 'futuristik', 'netrunner', 'tech', 'gamer', 'robot'],
      cfg: {
        headShape: 'tall', skinColor: '#F7E7DC', blushColor: '#DEC0B8',
        eyes: 'smug', eyebrows: 'skeptical', mouth: 'grin_teeth', beard: 'none',
        faceAccessory: 'cyber_visor',
        hat: 'hood', hatPrimary: '#1D2233', hatAccent: '#00F0D8', hatTilt: 0,
        backHair: 'spiky', hairColor: '#1E2A44',
        outfit: 'hoodie', robeColor: '#20263A', innerColor: '#00E5CE', sashColor: '#FF2D87', trimColor: '#00F0D8',
        beltStyle: 'utility_belt', cape: 'backpack', capeColor: '#2B324A', emblem: 'lightning', pose: 'ready', prop: 'laptop'
      }
    },
    {
      id: 'pirate',
      label: 'Kapten Bajak Laut',
      keywords: ['bajak laut', 'pirate', 'perompak', 'kapten laut', 'pelaut', 'kru kapal', 'kapal bajak'],
      cfg: {
        headShape: 'wide', skinColor: '#F0CEB0', blushColor: '#D9A78C',
        eyes: 'smug', eyebrows: 'angry', mouth: 'grin_teeth', beard: 'full_beard',
        faceAccessory: 'eyepatch',
        hat: 'pirate_tricorne', hatPrimary: '#241F29', hatAccent: '#E8B84B', hatTilt: -4,
        backHair: 'long_flow', hairColor: '#231717',
        outfit: 'pirate_coat', robeColor: '#8F2432', innerColor: '#F4ECDC', sashColor: '#D99B2B', trimColor: '#E8B84B',
        beltStyle: 'buckle', cape: 'none', emblem: 'skull', pose: 'heroic', prop: 'sword'
      }
    },
    {
      id: 'wizard',
      label: 'Penyihir',
      keywords: ['penyihir', 'wizard', 'mage', 'sihir', 'magic', 'sorcerer', 'witch', 'dukun', 'merlin', 'gandalf'],
      cfg: {
        headShape: 'tall', skinColor: '#F8ECE4', blushColor: '#DFC4BE',
        eyes: 'focused', eyebrows: 'raised', mouth: 'smirk', beard: 'full_beard',
        faceAccessory: 'none',
        hat: 'wizard_hat', hatPrimary: '#45286B', hatAccent: '#F0C850', hatTilt: -3,
        backHair: 'long_flow', hairColor: '#DDE2EB',
        outfit: 'wizard_robe', robeColor: '#4E2D78', innerColor: '#27173E', sashColor: '#E2B246', trimColor: '#F0C850',
        beltStyle: 'rope_sash', cape: 'short_cape', capeColor: '#361E59', emblem: 'crescent', pose: 'point', prop: 'magic_staff'
      }
    },
    {
      id: 'scientist',
      label: 'Ilmuwan Gila',
      keywords: ['ilmuwan', 'scientist', 'profesor', 'professor', 'kimia', 'lab', 'eksperimen', 'peneliti', 'einstein'],
      cfg: {
        headShape: 'potato', skinColor: '#FFF5EC', blushColor: '#EBC2BA',
        eyes: 'asymmetric', eyebrows: 'raised', mouth: 'grin_teeth', beard: 'mustache',
        faceAccessory: 'round_glasses',
        hat: 'none', hatPrimary: '#35313B', hatAccent: '#3BE87A', hatTilt: 0,
        backHair: 'twin_tufts', hairColor: '#E8ECF2',
        outfit: 'lab_coat', robeColor: '#F5F7FA', innerColor: '#4C9ED9', sashColor: '#D93B3B', trimColor: '#3BE87A',
        beltStyle: 'plain', cape: 'none', emblem: 'atom', pose: 'heroic', prop: 'flask'
      }
    },
    {
      id: 'doctor',
      label: 'Dokter',
      keywords: ['dokter', 'doctor', 'medis', 'perawat', 'klinik', 'rumah sakit', 'tabib'],
      cfg: {
        headShape: 'round', skinColor: '#FCEEE3', blushColor: '#E9C1B8',
        eyes: 'chill', eyebrows: 'happy', mouth: 'smirk', beard: 'none',
        faceAccessory: 'round_glasses',
        hat: 'none', hatPrimary: '#F5F7FA', hatAccent: '#2EB89A', hatTilt: 0,
        backHair: 'side_part', hairColor: '#261D22',
        outfit: 'lab_coat', robeColor: '#F7F9FC', innerColor: '#39A89C', sashColor: '#287D74', trimColor: '#E63946',
        beltStyle: 'plain', cape: 'none', emblem: 'heart', pose: 'ready', prop: 'coffee_mug'
      }
    },
    {
      id: 'cowboy',
      label: 'Koboi Gurun',
      keywords: ['koboi', 'cowboy', 'sheriff', 'western', 'wild west', 'gurun', 'outlaw'],
      cfg: {
        headShape: 'potato', skinColor: '#F2CFAF', blushColor: '#D8A68A',
        eyes: 'chill', eyebrows: 'flat', mouth: 'smirk', beard: 'mustache',
        faceAccessory: 'none',
        hat: 'cowboy', hatPrimary: '#784A2A', hatAccent: '#D9A13B', hatTilt: -4,
        backHair: 'short', hairColor: '#362118',
        outfit: 'vest_western', robeColor: '#6E4226', innerColor: '#F5E7CE', sashColor: '#C9342B', trimColor: '#E5B44A',
        beltStyle: 'buckle', cape: 'none', emblem: 'star', pose: 'akimbo', prop: 'lantern'
      }
    },
    {
      id: 'miner',
      label: 'Penambang / Pekerja',
      keywords: ['penambang', 'miner', 'tambang', 'pekerja', 'tukang', 'buruh', 'proyek', 'konstruksi', 'mandor', 'rel', 'kereta'],
      cfg: {
        headShape: 'wide', skinColor: '#F6DFC9', blushColor: '#DFB6A2',
        eyes: 'shocked', eyebrows: 'worried', mouth: 'teeth_oval', beard: 'stubble',
        faceAccessory: 'none',
        hat: 'miner_helmet', hatPrimary: '#EBB42C', hatAccent: '#FFF4B0', hatTilt: 0,
        backHair: 'short', hairColor: '#2D211C',
        outfit: 'plaid_suspenders', robeColor: '#396294', innerColor: '#5C3A24', sashColor: '#3A281E', trimColor: '#E2B44B',
        beltStyle: 'utility_belt', cape: 'none', emblem: 'none', pose: 'ready', prop: 'pickaxe'
      }
    },
    {
      id: 'mechanic',
      label: 'Mekanik / Steampunk',
      keywords: ['mekanik', 'montir', 'bengkel', 'teknisi', 'engineer', 'insinyur', 'steampunk', 'mesin'],
      cfg: {
        headShape: 'potato', skinColor: '#F4D7BC', blushColor: '#DEB49E',
        eyes: 'focused', eyebrows: 'flat', mouth: 'smirk', beard: 'stubble',
        faceAccessory: 'goggles',
        hat: 'cap', hatPrimary: '#3D4859', hatAccent: '#D97228', hatTilt: 4,
        backHair: 'spiky', hairColor: '#2B201E',
        outfit: 'mechanic_overall', robeColor: '#3B567A', innerColor: '#EFE4D0', sashColor: '#332825', trimColor: '#E2AC44',
        beltStyle: 'utility_belt', cape: 'backpack', capeColor: '#5C4332', emblem: 'gear', pose: 'heroic', prop: 'wrench'
      }
    },
    {
      id: 'millionaire',
      label: 'Jutawan / Gentleman',
      keywords: ['jutawan', 'konglomerat', 'millionaire', 'gentleman', 'sultan', 'bos', 'ceo', 'pengusaha', 'pebisnis', 'victorian', 'pesulap', 'kantoran', 'office'],
      cfg: {
        headShape: 'pear', skinColor: '#FFF3E8', blushColor: '#ECC3B9',
        eyes: 'smug', eyebrows: 'raised', mouth: 'grin_teeth', beard: 'handlebar',
        faceAccessory: 'monocle',
        hat: 'top_hat', hatPrimary: '#24212B', hatAccent: '#D93B34', hatTilt: 3,
        backHair: 'side_part', hairColor: '#38303A',
        outfit: 'suit_tie', robeColor: '#252938', innerColor: '#FAF7F0', sashColor: '#D9382E', trimColor: '#E8BD52',
        beltStyle: 'buckle', cape: 'none', emblem: 'dollar', pose: 'akimbo', prop: 'money_bag'
      }
    },
    {
      id: 'royal',
      label: 'Raja / Bangsawan',
      keywords: ['raja', 'king', 'ratu', 'queen', 'pangeran', 'prince', 'kaisar', 'emperor', 'royal', 'kerajaan', 'mahkota'],
      cfg: {
        headShape: 'wide', skinColor: '#FFF3E8', blushColor: '#EBC2B8',
        eyes: 'smug', eyebrows: 'raised', mouth: 'smirk', beard: 'handlebar',
        faceAccessory: 'none',
        hat: 'crown', hatPrimary: '#F0C042', hatAccent: '#D92E38', hatTilt: 0,
        backHair: 'curly', hairColor: '#3B2822',
        outfit: 'noble_robe', robeColor: '#692975', innerColor: '#FAF3DF', sashColor: '#C92B36', trimColor: '#F0C042',
        beltStyle: 'buckle', cape: 'royal_cape', capeColor: '#A81E32', emblem: 'crown', pose: 'heroic', prop: 'scroll'
      }
    },
    {
      id: 'knight',
      label: 'Ksatria / Pahlawan',
      keywords: ['ksatria', 'knight', 'paladin', 'medieval', 'pahlawan', 'hero', 'superhero', 'pendekar', 'pejuang'],
      cfg: {
        headShape: 'wide', skinColor: '#FCE9D8', blushColor: '#E4B8A8',
        eyes: 'focused', eyebrows: 'angry', mouth: 'grit_teeth', beard: 'none',
        faceAccessory: 'scar',
        hat: 'kabuto', hatPrimary: '#5D6678', hatAccent: '#E8BC4A', hatTilt: 0,
        backHair: 'short', hairColor: '#2A2226',
        outfit: 'medieval_knight', robeColor: '#6D7A8E', innerColor: '#2B3140', sashColor: '#C9322C', trimColor: '#E8BC4A',
        beltStyle: 'buckle', cape: 'short_cape', capeColor: '#B8282E', emblem: 'shield', pose: 'heroic', prop: 'sword'
      }
    },
    {
      id: 'soldier',
      label: 'Agen / Pasukan Taktis',
      keywords: ['tentara', 'soldier', 'militer', 'swat', 'tactical', 'komando', 'agen', 'agent', 'pasukan'],
      cfg: {
        headShape: 'wide', skinColor: '#F2D2B6', blushColor: '#D6AA92',
        eyes: 'focused', eyebrows: 'angry', mouth: 'flat', beard: 'stubble',
        faceAccessory: 'sunglasses',
        hat: 'beret', hatPrimary: '#364A36', hatAccent: '#E5B44C', hatTilt: -4,
        backHair: 'short', hairColor: '#241E22',
        outfit: 'tactical_vest', robeColor: '#3C4D3D', innerColor: '#283329', sashColor: '#252B24', trimColor: '#D4A84E',
        beltStyle: 'utility_belt', cape: 'backpack', capeColor: '#334033', emblem: 'target', pose: 'ready', prop: 'laser_blaster'
      }
    },
    {
      id: 'artist',
      label: 'Seniman / Barista',
      keywords: ['seniman', 'pelukis', 'artist', 'painter', 'perancis', 'french', 'paris', 'barista', 'kafe', 'kopi', 'hipster'],
      cfg: {
        headShape: 'potato', skinColor: '#FFF2E8', blushColor: '#EEBFB8',
        eyes: 'chill', eyebrows: 'skeptical', mouth: 'smirk', beard: 'goatee',
        faceAccessory: 'round_glasses',
        hat: 'beret', hatPrimary: '#9E2A3B', hatAccent: '#231B24', hatTilt: -6,
        backHair: 'curly', hairColor: '#2B1F24',
        outfit: 'haori_stripe', robeColor: '#F4F1EB', innerColor: '#B83244', sashColor: '#252029', trimColor: '#D9A752',
        beltStyle: 'plain', cape: 'scarf', capeColor: '#C93842', emblem: 'none', pose: 'think', prop: 'coffee_mug'
      }
    },
    {
      id: 'host',
      label: 'Host / Podcaster / Penyanyi',
      keywords: ['penyanyi', 'singer', 'host', 'mc', 'podcast', 'presenter', 'reporter', 'wartawan', 'komedian', 'idol', 'youtuber'],
      cfg: {
        headShape: 'round', skinColor: '#FCEADF', blushColor: '#EEB8B2',
        eyes: 'starry', eyebrows: 'happy', mouth: 'happy_open', beard: 'none',
        blush: true, faceAccessory: 'none',
        hat: 'cap', hatPrimary: '#2E5AD9', hatAccent: '#FFB830', hatTilt: 5,
        backHair: 'spiky', hairColor: '#241C28',
        outfit: 'hoodie', robeColor: '#384AE0', innerColor: '#FFB830', sashColor: '#202438', trimColor: '#FFFFFF',
        beltStyle: 'plain', cape: 'none', emblem: 'star', pose: 'wave', prop: 'microphone'
      }
    },
    {
      id: 'skater',
      label: 'Anak Jalanan / Skater',
      keywords: ['skater', 'gaul', 'remaja', 'anak muda', 'street', 'mahasiswa', 'pelajar', 'casual', 'santai', 'punk'],
      cfg: {
        headShape: 'potato', skinColor: '#F8DEC9', blushColor: '#E3B4A4',
        eyes: 'chill', eyebrows: 'flat', mouth: 'smirk', beard: 'none',
        faceAccessory: 'bandage',
        hat: 'beanie', hatPrimary: '#E8A830', hatAccent: '#D93B2B', hatTilt: 4,
        backHair: 'spiky', hairColor: '#221A24',
        outfit: 'street_varsity', robeColor: '#2F8F7B', innerColor: '#F5EFE2', sashColor: '#242029', trimColor: '#F0B840',
        beltStyle: 'plain', cape: 'backpack', capeColor: '#C94432', emblem: 'lightning', pose: 'ready', prop: 'coffee_mug'
      }
    },
    {
      id: 'explorer',
      label: 'Petualang / Penjelajah',
      keywords: ['petualang', 'explorer', 'penjelajah', 'pendaki', 'hiker', 'arkeolog', 'indiana', 'hutan', 'kemah'],
      cfg: {
        headShape: 'potato', skinColor: '#F0CFAF', blushColor: '#D6A890',
        eyes: 'focused', eyebrows: 'raised', mouth: 'smirk', beard: 'stubble',
        faceAccessory: 'none',
        hat: 'fedora', hatPrimary: '#6E4A2E', hatAccent: '#3B2518', hatTilt: -4,
        backHair: 'short', hairColor: '#32221B',
        outfit: 'safari_explorer', robeColor: '#9E7E54', innerColor: '#EFE4CC', sashColor: '#A8322C', trimColor: '#D4A64A',
        beltStyle: 'utility_belt', cape: 'backpack', capeColor: '#5B422E', emblem: 'none', pose: 'point', prop: 'lantern'
      }
    },
    {
      id: 'ninja',
      label: 'Ninja / Pencuri Bayangan',
      keywords: ['ninja', 'shinobi', 'assassin', 'pencuri', 'thief', 'maling', 'perampok', 'robber', 'bayangan'],
      cfg: {
        headShape: 'tall', skinColor: '#FCEEE3', blushColor: '#E2BEB4',
        eyes: 'focused', eyebrows: 'angry', mouth: 'flat', beard: 'none',
        faceAccessory: 'none',
        hat: 'hood', hatPrimary: '#1E1D28', hatAccent: '#D93232', hatTilt: 0,
        backHair: 'spiky', hairColor: '#1B1620',
        outfit: 'tactical_vest', robeColor: '#232230', innerColor: '#363448', sashColor: '#C92B2B', trimColor: '#D93232',
        beltStyle: 'knot', cape: 'scarf', capeColor: '#C92B2B', emblem: 'none', pose: 'ready', prop: 'sword'
      }
    },
    {
      id: 'qing',
      label: 'Pejabat Qing',
      keywords: ['qing', 'pejabat', 'guanmao', 'mandarin', 'dinasti', 'tiongkok'],
      cfg: {
        headShape: 'potato', skinColor: '#FFFDFB', blushColor: '#EDD0CA',
        eyes: 'shocked', eyebrows: 'worried', mouth: 'teeth_oval', beard: 'goatee',
        faceAccessory: 'none',
        hat: 'guanmao', hatPrimary: '#35313B', hatAccent: '#EE372B', hatTilt: 0,
        backHair: 'qing_braid', hairColor: '#211821',
        outfit: 'magua', robeColor: '#9C3666', innerColor: '#F8D896', sashColor: '#EE372B', trimColor: '#C9AB6B',
        beltStyle: 'bow', cape: 'none', emblem: 'none', pose: 'akimbo', prop: 'none'
      }
    },
    {
      id: 'samurai',
      label: 'Samurai',
      keywords: ['samurai', 'ronin', 'shogun', 'bushido', 'jepang', 'jingasa', 'katana'],
      cfg: {
        headShape: 'potato', skinColor: '#FFFDFB', blushColor: '#EDD0CA',
        eyes: 'chill', eyebrows: 'flat', mouth: 'smirk', beard: 'none',
        faceAccessory: 'none',
        hat: 'jingasa', hatPrimary: '#2B2830', hatAccent: '#E8B84B', hatTilt: 0,
        backHair: 'chonmage', hairColor: '#211821',
        outfit: 'haori_stripe', robeColor: '#2F9B82', innerColor: '#FAF4E4', sashColor: '#2B242E', trimColor: '#E8B84B',
        beltStyle: 'knot', cape: 'none', emblem: 'none', pose: 'point', prop: 'sword'
      }
    },
    {
      id: 'guard',
      label: 'Prajurit Istana',
      keywords: ['prajurit', 'penjaga', 'guard', 'pengawal', 'tombak'],
      cfg: {
        headShape: 'wide', skinColor: '#FFFDFB', blushColor: '#EDD0CA',
        eyes: 'panic', eyebrows: 'worried', mouth: 'open_yell', beard: 'none',
        sweatDrop: true, faceAccessory: 'none',
        hat: 'hachimaki', hatPrimary: '#F7F3EC', hatAccent: '#D92E26', hatTilt: 0,
        backHair: 'chonmage', hairColor: '#211821',
        outfit: 'armor', robeColor: '#C94228', innerColor: '#302A33', sashColor: '#D69F3E', trimColor: '#F0C869',
        beltStyle: 'buckle', cape: 'none', emblem: 'none', pose: 'ready', prop: 'spear'
      }
    },
    {
      id: 'scholar',
      label: 'Penasihat / Cendekia',
      keywords: ['penasihat', 'cendekia', 'scholar', 'filsuf', 'ming', 'bijak', 'guru'],
      cfg: {
        headShape: 'tall', skinColor: '#FFFDFB', blushColor: '#EDD0CA',
        eyes: 'smug', eyebrows: 'raised', mouth: 'smirk', beard: 'mandarin',
        faceAccessory: 'none',
        hat: 'futou', hatPrimary: '#24222D', hatAccent: '#E5B44C', hatTilt: 0,
        backHair: 'short', hairColor: '#211821',
        outfit: 'noble_robe', robeColor: '#2D4F85', innerColor: '#F5E3B8', sashColor: '#C92B2B', trimColor: '#E8BE5E',
        beltStyle: 'buckle', cape: 'none', emblem: 'none', pose: 'crossed', prop: 'scroll'
      }
    }
  ];

  function hashString(str) {
    let h = 2166136261;
    for (let i = 0; i < str.length; i++) {
      h ^= str.charCodeAt(i);
      h = Math.imul(h, 16777619);
    }
    return h >>> 0;
  }

  function hasAny(text, list) {
    for (let i = 0; i < list.length; i++) {
      const kw = list[i];
      if (kw.length <= 4 && !kw.includes(' ')) {
        const re = new RegExp(`(^|[^a-z0-9])${kw.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}([^a-z0-9]|$)`, 'i');
        if (re.test(text)) return kw;
      } else if (text.includes(kw)) {
        return kw;
      }
    }
    return null;
  }

  function findColorNear(text, anchorKeywords) {
    const clauses = text.split(/[,.;]+|\b(?:dan|dengan|pakai|memakai|pegang|memegang|ekspresi|wearing|with|holding)\b/i);
    for (const clause of clauses) {
      let bestAnchorPos = -1;
      for (const anchor of anchorKeywords) {
        const pos = clause.indexOf(anchor);
        if (pos !== -1 && (bestAnchorPos === -1 || pos < bestAnchorPos)) {
          bestAnchorPos = pos;
        }
      }
      if (bestAnchorPos === -1) continue;
      let bestColor = null;
      let bestDist = Infinity;
      for (const c of COLOR_MAP) {
        for (const ck of c.keys) {
          const cPos = clause.indexOf(ck);
          if (cPos === -1) continue;
          if (ck.length <= 4 && !hasAny(clause, [ck])) continue;
          const dist = Math.abs(cPos - bestAnchorPos);
          if (dist < bestDist) {
            bestDist = dist;
            bestColor = c;
          }
        }
      }
      if (bestColor) return bestColor;
    }
    return null;
  }

  function findAnyColor(text) {
    for (const c of COLOR_MAP) {
      if (hasAny(text, c.keys)) return c;
    }
    return null;
  }

  function toDisplayName(prompt, fallbackLabel) {
    const clean = (prompt || '').trim();
    if (!clean) return fallbackLabel || 'Karakter Prompt';
    const head = clean.split(/\b(?:pakai|memakai|berpakaian|dengan|yang|pegang|memegang|ekspresi|berkumis|berjanggut|berambut|di|dari|dalam|untuk|wearing|with|holding|looking|in|on|at|of|for)\b/i)[0].trim();
    const candidate = (head.length >= 3 && head.length <= 44) ? head : (fallbackLabel || clean.slice(0, 30));
    return candidate
      .replace(/[^a-zA-Z0-9\s\-']/g, ' ')
      .replace(/\s+/g, ' ')
      .trim()
      .split(' ')
      .slice(0, 3)
      .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
      .join(' ') || (fallbackLabel || 'Karakter Kustom');
  }

  function toComponentName(displayName) {
    const words = (displayName || 'CustomCharacter')
      .replace(/[^a-zA-Z0-9\s]/g, ' ')
      .trim()
      .split(/\s+/)
      .filter(Boolean)
      .map((w) => w.charAt(0).toUpperCase() + w.slice(1).toLowerCase());
    let base = words.join('') || 'Custom';
    if (/^[0-9]/.test(base)) base = 'Char' + base;
    if (!base.endsWith('Character') && !base.endsWith('Rig')) base += 'Character';
    return base;
  }

  /**
   * Local Instant Semantic Prompt Engine (Zero API Key Required)
   */
  function generateFromPromptLocal(promptText, variantIndex) {
    const DEFAULT_CONFIG = global.CharacterEngine ? global.CharacterEngine.DEFAULT_CONFIG : {};
    const raw = (promptText || '').trim();
    const text = raw.toLowerCase();
    const seed = hashString(text + '#' + (variantIndex || 0));
    const seededPick = (arr, salt) => arr[(seed + (salt || 0)) % arr.length];

    const matchedTags = [];

    // 1. Score archetypes
    let bestArch = null;
    let bestScore = 0;
    for (const arch of ARCHETYPES) {
      let score = 0;
      for (const kw of arch.keywords) {
        if (text.includes(kw)) score += kw.includes(' ') ? 3 : 2;
      }
      if (score > bestScore) {
        bestScore = score;
        bestArch = arch;
      }
    }

    const cfg = {
      ...DEFAULT_CONFIG,
      prompt: raw,
      sweatDrop: false,
      blush: false,
      angerVein: false,
      eyeGazeX: 0,
      eyeGazeY: 0,
      hatTilt: 0,
      hatLiftY: 0,
      customLayers: []
    };

    if (bestArch) {
      Object.assign(cfg, bestArch.cfg);
      matchedTags.push(`Tema: ${bestArch.label}`);
    } else {
      // Creative fallback: cohesive multi-genre palette & fresh non-historical silhouette!
      const fallbackOutfits = ['trench_coat', 'suit_tie', 'hoodie', 'plaid_suspenders', 'vest_western', 'lab_coat', 'wizard_robe', 'tactical_vest'];
      const fallbackHats = ['fedora', 'beanie', 'cap', 'beret', 'bowler', 'cowboy', 'hood', 'none'];
      const fallbackPalettes = [
        { robe: '#2D599E', inner: '#F4ECDC', sash: '#D94B38', trim: '#E8B84B', hat: '#262B38' },
        { robe: '#2F8A72', inner: '#FAF4E4', sash: '#2A232E', trim: '#E5B84B', hat: '#253835' },
        { robe: '#6E3B8E', inner: '#EFE4F8', sash: '#E5A838', trim: '#F2CA52', hat: '#36214A' },
        { robe: '#B84434', inner: '#FAF0DC', sash: '#29222C', trim: '#E8BE5E', hat: '#3B2828' },
        { robe: '#3B4659', inner: '#E2E8F0', sash: '#22B8CF', trim: '#38D9A9', hat: '#232A38' }
      ];
      const pal = seededPick(fallbackPalettes, 3);
      cfg.outfit = seededPick(fallbackOutfits, 5);
      cfg.hat = seededPick(fallbackHats, 7);
      cfg.backHair = seededPick(['short', 'spiky', 'curly', 'side_part'], 11);
      cfg.robeColor = pal.robe;
      cfg.innerColor = pal.inner;
      cfg.sashColor = pal.sash;
      cfg.trimColor = pal.trim;
      cfg.hatPrimary = pal.hat;
      cfg.hatAccent = pal.sash;
      cfg.skinColor = '#FCEEE3';
      cfg.blushColor = '#E6BEB2';
      cfg.eyes = 'chill';
      cfg.eyebrows = 'flat';
      cfg.mouth = 'smirk';
      cfg.beard = 'none';
      cfg.beltStyle = 'buckle';
      cfg.pose = 'ready';
      cfg.prop = 'none';
      matchedTags.push('Tema: Karakter Orisinal');
    }

    // Apply subtle variation when user clicks "Variasi Prompt"
    if (variantIndex && variantIndex > 0) {
      cfg.hatTilt = seededPick([-7, -4, 0, 4, 7], 19);
      cfg.headShape = seededPick(['potato', 'round', 'tall', 'wide', 'pear'], 23);
      cfg.pose = seededPick(['akimbo', 'ready', 'point', 'crossed', 'wave', 'heroic', 'think'], 29);
    }

    // 2. Explicit Headwear Overrides
    const hatRules = [
      { val: 'none', tag: 'Tanpa Topi', keys: ['tanpa topi', 'no hat', 'gak pakai topi', 'tidak pakai topi'] },
      { val: 'fedora', tag: 'Topi Fedora', keys: ['fedora', 'topi detektif'] },
      { val: 'chef_toque', tag: 'Topi Chef', keys: ['topi chef', 'topi koki', 'toque'] },
      { val: 'astronaut_helmet', tag: 'Helm Astronot', keys: ['helm astronot', 'helm kaca', 'space helmet', 'helm luar angkasa'] },
      { val: 'cowboy', tag: 'Topi Koboi', keys: ['topi koboi', 'cowboy hat', 'topi cowboy'] },
      { val: 'pirate_tricorne', tag: 'Topi Tricorne', keys: ['tricorne', 'topi bajak laut', 'pirate hat'] },
      { val: 'wizard_hat', tag: 'Topi Penyihir', keys: ['topi penyihir', 'topi kerucut', 'wizard hat', 'witch hat'] },
      { val: 'top_hat', tag: 'Top Hat', keys: ['top hat', 'topi tinggi', 'topi pesulap', 'topi sulap'] },
      { val: 'bowler', tag: 'Topi Bowler', keys: ['bowler', 'derby hat'] },
      { val: 'beanie', tag: 'Kupluk Beanie', keys: ['beanie', 'kupluk', 'topi rajut'] },
      { val: 'cap', tag: 'Topi Cap', keys: ['topi baseball', 'baseball cap', 'topi cap', 'topi pet', 'topi truk'] },
      { val: 'crown', tag: 'Mahkota', keys: ['mahkota', 'crown'] },
      { val: 'miner_helmet', tag: 'Helm Tambang', keys: ['helm tambang', 'helm proyek', 'hard hat', 'helm lampu', 'miner helmet'] },
      { val: 'hood', tag: 'Tudung Hood', keys: ['tudung', 'hoodie tutup', 'berkerudung', 'assassin hood', 'hood'] },
      { val: 'beret', tag: 'Topi Baret', keys: ['baret', 'beret'] },
      { val: 'guanmao', tag: 'Topi Guanmao', keys: ['guanmao', 'topi qing'] },
      { val: 'jingasa', tag: 'Topi Jingasa', keys: ['jingasa', 'caping samurai'] },
      { val: 'hachimaki', tag: 'Ikat Kepala', keys: ['hachimaki', 'ikat kepala', 'headband'] },
      { val: 'futou', tag: 'Topi Futou', keys: ['futou'] },
      { val: 'kabuto', tag: 'Helm Kabuto', keys: ['kabuto', 'helm samurai', 'helm perang'] }
    ];
    for (const r of hatRules) {
      if (hasAny(text, r.keys)) {
        cfg.hat = r.val;
        matchedTags.push(r.tag);
        break;
      }
    }
    if (hasAny(text, ['topi miring', 'miring', 'askew', 'tilted'])) {
      cfg.hatTilt = -12;
      matchedTags.push('Topi Miring');
    }

    // 3. Explicit Outfit Overrides (24 Realistic 3D Layered Outfits!)
    const outfitRules = [
      { val: 'cyber_jacket', tag: 'Jaket Cyber Tech', keys: ['jaket cyber', 'cyber jacket', 'techwear', 'jaket futuristik', 'jaket neon'] },
      { val: 'steampunk_coat', tag: 'Mantel Steampunk', keys: ['steampunk', 'mantel steampunk', 'rompi jam saku', 'mantel victorian'] },
      { val: 'royal_uniform', tag: 'Seragam Jenderal', keys: ['seragam jenderal', 'seragam kerajaan', 'seragam militer', 'jenderal', 'laksamana', 'epaulet'] },
      { val: 'leather_biker', tag: 'Jaket Kulit Biker', keys: ['jaket kulit', 'biker', 'leather jacket', 'jaket motor', 'rocker'] },
      { val: 'medieval_knight', tag: 'Zirah Plate Ksatria', keys: ['zirah plate', 'plate armor', 'baju zirah besi', 'baju ksatria', 'zirah baja'] },
      { val: 'hanbok_kimono', tag: 'Kimono / Yukata', keys: ['yukata', 'hanbok', 'kimono sutra', 'kimono berlapis'] },
      { val: 'mechanic_overall', tag: 'Wearpack / Overall', keys: ['wearpack', 'overall', 'baju mekanik', 'baju montir', 'baju bengkel'] },
      { val: 'street_varsity', tag: 'Jaket Varsity', keys: ['varsity', 'bomber', 'jaket kampus', 'jaket baseball'] },
      { val: 'safari_explorer', tag: 'Jaket Safari', keys: ['safari', 'jaket petualang', 'jaket lapangan', 'baju ekspedisi'] },
      { val: 'trench_coat', tag: 'Jas Hujan / Trench', keys: ['jas hujan', 'trench coat', 'trench', 'mantel detektif'] },
      { val: 'suit_tie', tag: 'Jas & Dasi', keys: ['jas dan dasi', 'setelan jas', 'suit', 'blazer', 'tuksedo', 'tuxedo', 'dasi'] },
      { val: 'spacesuit', tag: 'Baju Astronot', keys: ['baju astronot', 'baju luar angkasa', 'spacesuit', 'baju antariksa'] },
      { val: 'chef_apron', tag: 'Celemek Chef', keys: ['celemek', 'apron', 'baju koki', 'baju chef'] },
      { val: 'lab_coat', tag: 'Jas Lab', keys: ['jas lab', 'jas dokter', 'lab coat'] },
      { val: 'plaid_suspenders', tag: 'Flanel + Suspender', keys: ['flanel', 'kotak-kotak', 'plaid', 'suspender', 'bretel'] },
      { val: 'hoodie', tag: 'Hoodie', keys: ['hoodie', 'jaket hoodie', 'sweater'] },
      { val: 'pirate_coat', tag: 'Mantel Kapten', keys: ['mantel kapten', 'baju bajak laut', 'pirate coat'] },
      { val: 'wizard_robe', tag: 'Jubah Sihir', keys: ['jubah sihir', 'jubah penyihir', 'wizard robe', 'jubah bintang'] },
      { val: 'vest_western', tag: 'Rompi Kulit', keys: ['rompi kulit', 'rompi koboi', 'bandana', 'western vest'] },
      { val: 'tactical_vest', tag: 'Rompi Taktis', keys: ['rompi taktis', 'tactical', 'rompi anti peluru', 'baju tentara'] },
      { val: 'armor', tag: 'Zirah Lamellar', keys: ['zirah', 'armor', 'baju besi', 'baju perang'] },
      { val: 'haori_stripe', tag: 'Haori Garis', keys: ['haori', 'kimono', 'baju garis'] },
      { val: 'magua', tag: 'Jubah Magua', keys: ['magua', 'baju qing'] },
      { val: 'noble_robe', tag: 'Jubah Bangsawan', keys: ['jubah bangsawan', 'jubah kerajaan', 'jubah raja'] }
    ];
    for (const r of outfitRules) {
      if (hasAny(text, r.keys)) {
        cfg.outfit = r.val;
        matchedTags.push(r.tag);
        break;
      }
    }

    // 4. Cape / Back Gear Overrides
    const capeRules = [
      { val: 'jetpack', tag: 'Jetpack', keys: ['jetpack', 'roket punggung', 'pendorong'] },
      { val: 'royal_cape', tag: 'Jubah Raja', keys: ['jubah raja', 'royal cape', 'jubah panjang'] },
      { val: 'short_cape', tag: 'Jubah Cape', keys: ['cape', 'jubah terbang', 'sayap jubah', 'berjubah'] },
      { val: 'scarf', tag: 'Syal', keys: ['syal', 'scarf', 'selendang'] },
      { val: 'backpack', tag: 'Tas Ransel', keys: ['ransel', 'backpack', 'tas punggung', 'tas'] }
    ];
    for (const r of capeRules) {
      if (hasAny(text, r.keys)) {
        cfg.cape = r.val;
        matchedTags.push(r.tag);
        break;
      }
    }

    // 5. Face Accessory Overrides
    const accRules = [
      { val: 'cyber_visor', tag: 'Visor Cyber', keys: ['visor', 'kacamata futuristik', 'kacamata neon', 'cyber visor'] },
      { val: 'sunglasses', tag: 'Kacamata Hitam', keys: ['kacamata hitam', 'sunglasses', 'shades'] },
      { val: 'goggles', tag: 'Goggles', keys: ['goggles', 'kacamata las', 'kacamata steampunk'] },
      { val: 'monocle', tag: 'Monokel', keys: ['monokel', 'monocle'] },
      { val: 'round_glasses', tag: 'Kacamata Bulat', keys: ['kacamata', 'glasses', 'berkacamata'] },
      { val: 'eyepatch', tag: 'Penutup Mata', keys: ['penutup mata', 'eyepatch', 'mata satu'] },
      { val: 'scar', tag: 'Luka Wajah', keys: ['bekas luka', 'luka pipi', 'scar'] },
      { val: 'bandage', tag: 'Plester Pipi', keys: ['plester', 'bandage', 'perban'] }
    ];
    for (const r of accRules) {
      if (hasAny(text, r.keys)) {
        cfg.faceAccessory = r.val;
        matchedTags.push(r.tag);
        break;
      }
    }

    // 6. Hair & Beard Overrides
    const hairRules = [
      { val: 'bald', tag: 'Botak', keys: ['botak', 'bald', 'plontos'] },
      { val: 'twin_tufts', tag: 'Rambut Acak Ilmuwan', keys: ['rambut acak', 'rambut gila', 'rambut eistein', 'rambut mekar'] },
      { val: 'spiky', tag: 'Rambut Runcing', keys: ['rambut runcing', 'spiky', 'rambut jabrik', 'anime hair'] },
      { val: 'curly', tag: 'Rambut Keriting', keys: ['keriting', 'curly', 'kribo', 'ikal'] },
      { val: 'long_flow', tag: 'Rambut Panjang', keys: ['rambut panjang', 'long hair', 'gondrong'] },
      { val: 'mohawk', tag: 'Mohawk', keys: ['mohawk', 'punk'] },
      { val: 'side_part', tag: 'Belah Samping', keys: ['belah samping', 'rambut rapi'] },
      { val: 'qing_braid', tag: 'Kepang', keys: ['kepang', 'braid'] },
      { val: 'chonmage', tag: 'Sanggul', keys: ['sanggul', 'chonmage', 'topknot'] }
    ];
    for (const r of hairRules) {
      if (hasAny(text, r.keys)) { cfg.backHair = r.val; matchedTags.push(r.tag); break; }
    }

    const beardRules = [
      { val: 'none', tag: 'Tanpa Janggut', keys: ['tanpa kumis', 'tanpa janggut', 'wajah polos', 'clean shaven'] },
      { val: 'handlebar', tag: 'Kumis Melingkar', keys: ['kumis melingkar', 'kumis tebal', 'handlebar', 'kumis koki'] },
      { val: 'full_beard', tag: 'Janggut Lebat', keys: ['janggut lebat', 'janggut panjang', 'jenggot lebat', 'jenggot panjang', 'full beard', 'berjenggot lebat'] },
      { val: 'mandarin', tag: 'Kumis + Goatee', keys: ['kumis mandarin', 'kumis panjang'] },
      { val: 'goatee', tag: 'Goatee', keys: ['goatee', 'janggut runcing', 'jenggot'] },
      { val: 'mustache', tag: 'Berkumis', keys: ['kumis', 'mustache', 'berkumis'] },
      { val: 'stubble', tag: 'Brewok Tipis', keys: ['brewok', 'stubble'] }
    ];
    for (const r of beardRules) {
      if (hasAny(text, r.keys)) { cfg.beard = r.val; matchedTags.push(r.tag); break; }
    }

    // 7. Expression & Emotion Overrides
    if (hasAny(text, ['panik', 'panic', 'ketakutan', 'cemas', 'takut', 'gugup', 'nervous'])) {
      cfg.eyes = 'panic'; cfg.eyebrows = 'worried'; cfg.mouth = 'open_yell'; cfg.sweatDrop = true;
      matchedTags.push('Ekspresi: Panik');
    } else if (hasAny(text, ['kaget', 'terkejut', 'shocked', 'syok', 'melotot'])) {
      cfg.eyes = 'shocked'; cfg.eyebrows = 'raised'; cfg.mouth = 'small_o'; cfg.sweatDrop = true;
      matchedTags.push('Ekspresi: Kaget');
    } else if (hasAny(text, ['marah', 'geram', 'garang', 'kesal', 'angry', 'galak', 'emosi'])) {
      cfg.eyes = 'angry'; cfg.eyebrows = 'angry'; cfg.mouth = 'grit_teeth'; cfg.angerVein = true;
      matchedTags.push('Ekspresi: Marah');
    } else if (hasAny(text, ['curiga', 'suspicious', 'menyelidik', 'skeptis', 'introgasi'])) {
      cfg.eyes = 'suspicious'; cfg.eyebrows = 'skeptical'; cfg.mouth = 'flat'; cfg.eyeGazeX = 0.55;
      matchedTags.push('Ekspresi: Curiga');
    } else if (hasAny(text, ['licik', 'smug', 'jahat', 'nakal', 'scheming', 'sombong'])) {
      cfg.eyes = 'smug'; cfg.eyebrows = 'skeptical'; cfg.mouth = 'grin_teeth';
      matchedTags.push('Ekspresi: Licik');
    } else if (hasAny(text, ['senang', 'bahagia', 'ceria', 'ramah', 'happy', 'ketawa', 'tertawa', 'gembira'])) {
      cfg.eyes = 'happy'; cfg.eyebrows = 'happy'; cfg.mouth = 'happy_open'; cfg.blush = true;
      matchedTags.push('Ekspresi: Ceria');
    } else if (hasAny(text, ['kagum', 'berbinar', 'starry', 'antusias', 'excited'])) {
      cfg.eyes = 'starry'; cfg.eyebrows = 'raised'; cfg.mouth = 'happy_open'; cfg.blush = true;
      matchedTags.push('Ekspresi: Berbinar');
    } else if (hasAny(text, ['datar', 'deadpan', 'bosan', 'malas', 'lelah', 'capek', 'ngantuk'])) {
      cfg.eyes = 'deadpan'; cfg.eyebrows = 'flat'; cfg.mouth = 'flat';
      matchedTags.push('Ekspresi: Deadpan');
    } else if (hasAny(text, ['bingung', 'kocak', 'lucu', 'aneh', 'konyol', 'goofy', 'o_o', 'bonk'])) {
      cfg.eyes = 'asymmetric'; cfg.eyebrows = 'skeptical'; cfg.mouth = 'small_o';
      matchedTags.push('Ekspresi: Kocak O_o');
    } else if (hasAny(text, ['fokus', 'serius', 'tegas', 'determined', 'focused'])) {
      cfg.eyes = 'focused'; cfg.eyebrows = 'angry'; cfg.mouth = 'flat';
      matchedTags.push('Ekspresi: Fokus');
    } else if (hasAny(text, ['santai', 'tenang', 'cool', 'chill', 'keren'])) {
      cfg.eyes = 'chill'; cfg.eyebrows = 'flat'; cfg.mouth = 'smirk';
      matchedTags.push('Ekspresi: Santai');
    }

    if (hasAny(text, ['keringat', 'berkeringat', 'sweat'])) cfg.sweatDrop = true;
    if (hasAny(text, ['merona', 'pipi merah', 'blush', 'malu'])) cfg.blush = true;
    if (hasAny(text, ['urat marah', 'kesal banget'])) cfg.angerVein = true;
    if (hasAny(text, ['senyum', 'smirk', 'smile'])) cfg.mouth = 'smirk';
    if (hasAny(text, ['teriak', 'yell', 'berteriak'])) cfg.mouth = 'open_yell';
    if (hasAny(text, ['cemberut', 'sedih', 'frown'])) cfg.mouth = 'frown';

    // 8. Prop Overrides
    const propRules = [
      { val: 'none', tag: 'Tanpa Properti', keys: ['tanpa properti', 'tangan kosong', 'no prop'] },
      { val: 'magnifying_glass', tag: 'Kaca Pembesar', keys: ['kaca pembesar', 'lup', 'magnifying'] },
      { val: 'spatula', tag: 'Spatula', keys: ['spatula', 'sodet', 'penggorengan', 'wajan'] },
      { val: 'laser_blaster', tag: 'Pistol Laser', keys: ['laser', 'blaster', 'pistol', 'senjata api'] },
      { val: 'flask', tag: 'Tabung Reaksi', keys: ['tabung reaksi', 'ramuan', 'potion', 'flask', 'kimia', 'botol ramuan'] },
      { val: 'magic_staff', tag: 'Tongkat Sihir', keys: ['tongkat sihir', 'tongkat', 'staff', 'wand'] },
      { val: 'sword', tag: 'Pedang', keys: ['pedang', 'sword', 'katana', 'golok', 'cutlass'] },
      { val: 'pickaxe', tag: 'Beliung', keys: ['beliung', 'pickaxe', 'kapak', 'cangkul'] },
      { val: 'coffee_mug', tag: 'Cangkir Kopi', keys: ['kopi', 'coffee', 'mug', 'cangkir', 'teh'] },
      { val: 'laptop', tag: 'Laptop', keys: ['laptop', 'komputer', 'notebook'] },
      { val: 'lantern', tag: 'Lentera', keys: ['lentera', 'lantern', 'obor', 'lampu gantung'] },
      { val: 'microphone', tag: 'Mikrofon', keys: ['mikrofon', 'microphone', 'mic'] },
      { val: 'money_bag', tag: 'Karung Uang', keys: ['karung uang', 'kantong uang', 'kantong emas', 'uang', 'duit', 'money bag', 'cash'] },
      { val: 'wrench', tag: 'Kunci Inggris', keys: ['kunci inggris', 'wrench', 'obeng', 'perkakas'] },
      { val: 'bomb', tag: 'Bom', keys: ['bom', 'bomb', 'granat', 'dinamit'] },
      { val: 'spear', tag: 'Tombak', keys: ['tombak', 'spear', 'yari'] },
      { val: 'fan', tag: 'Kipas', keys: ['kipas', 'fan'] },
      { val: 'scroll', tag: 'Gulungan Surat', keys: ['gulungan', 'scroll', 'surat', 'peta'] }
    ];
    for (const r of propRules) {
      if (hasAny(text, r.keys)) { cfg.prop = r.val; matchedTags.push(`Properti: ${r.tag}`); break; }
    }

    // 9. Pose & Head Shape Overrides
    const poseRules = [
      { val: 'wave', keys: ['melambai', 'sapa', 'menyapa', 'wave', 'dadah'] },
      { val: 'point', keys: ['menunjuk', 'point', 'tunjuk'] },
      { val: 'crossed', keys: ['bersedekap', 'lipat tangan', 'crossed'] },
      { val: 'panic', keys: ['angkat tangan', 'panik'] },
      { val: 'heroic', keys: ['heroik', 'gagah', 'heroic', 'pahlawan'] },
      { val: 'think', keys: ['berpikir', 'mikir', 'thinking', 'dagu'] },
      { val: 'akimbo', keys: ['bertolak pinggang', 'pinggang', 'akimbo'] }
    ];
    for (const r of poseRules) {
      if (hasAny(text, r.keys)) { cfg.pose = r.val; break; }
    }

    if (hasAny(text, ['gemuk', 'lebar', 'chubby', 'kekar', 'besar', 'wide'])) cfg.headShape = 'wide';
    else if (hasAny(text, ['kurus', 'tinggi', 'lonjong', 'tall', 'slim'])) cfg.headShape = 'tall';
    else if (hasAny(text, ['bulat', 'imut', 'round', 'cute'])) cfg.headShape = 'round';
    else if (hasAny(text, ['tembem', 'pear'])) cfg.headShape = 'pear';

    // 10. Emblem Overrides
    const embRules = [
      { val: 'star', keys: ['bintang', 'star'] },
      { val: 'skull', keys: ['tengkorak', 'skull'] },
      { val: 'lightning', keys: ['petir', 'kilat', 'lightning'] },
      { val: 'shield', keys: ['perisai', 'tameng', 'shield'] },
      { val: 'heart', keys: ['hati', 'cinta', 'heart'] },
      { val: 'dollar', keys: ['dolar', 'dollar'] },
      { val: 'atom', keys: ['atom', 'nuklir'] },
      { val: 'crescent', keys: ['bulan sabit', 'crescent'] },
      { val: 'gear', keys: ['gir', 'gear', 'roda gigi'] }
    ];
    for (const r of embRules) {
      if (hasAny(text, r.keys)) { cfg.emblem = r.val; break; }
    }

    // 11. Skin Tone Overrides
    if (hasAny(text, ['hijau alien', 'alien', 'goblin', 'orc'])) { cfg.skinColor = '#9ED88C'; cfg.blushColor = '#74B468'; matchedTags.push('Kulit: Alien'); }
    else if (hasAny(text, ['kulit biru', 'smurf', 'manusia es', 'frost'])) { cfg.skinColor = '#9ECDF2'; cfg.blushColor = '#7AA8D4'; }
    else if (hasAny(text, ['robot', 'cyborg', 'kulit metalik'])) { cfg.skinColor = '#DCE3EC'; cfg.blushColor = '#B0BCCB'; }
    else if (hasAny(text, ['sawo matang', 'tan skin'])) { cfg.skinColor = '#D9A679'; cfg.blushColor = '#BF8462'; }
    else if (hasAny(text, ['kulit gelap', 'dark skin', 'kulit coklat'])) { cfg.skinColor = '#A86E4B'; cfg.blushColor = '#8A5236'; }
    else if (hasAny(text, ['pucat', 'vampir', 'hantu', 'pale'])) { cfg.skinColor = '#F3F4F8'; cfg.blushColor = '#D2D4E2'; }

    // 12. Contextual Color Extraction!
    const hatCol = findColorNear(text, ['topi', 'helm', 'mahkota', 'kupluk', 'baret', 'fedora', 'hat', 'helmet', 'cap', 'hood']);
    const robeCol = findColorNear(text, ['baju', 'jas', 'jubah', 'mantel', 'hoodie', 'jaket', 'rompi', 'zirah', 'pakaian', 'outfit', 'coat', 'suit', 'robe', 'shirt']);
    const innerCol = findColorNear(text, ['celemek', 'apron', 'kerah', 'kemeja', 'kaos', 'dalam', 'aksen', 'accent']);
    const sashCol = findColorNear(text, ['sabuk', 'pita', 'dasi', 'bandana', 'belt', 'sash', 'tie']);
    const hairCol = findColorNear(text, ['rambut', 'hair', 'kumis', 'janggut', 'jenggot']);

    if (robeCol) { cfg.robeColor = robeCol.hex; matchedTags.push(`Outfit: ${robeCol.name}`); }
    if (hatCol) { cfg.hatPrimary = hatCol.hex; matchedTags.push(`Topi: ${hatCol.name}`); }
    if (innerCol) { cfg.innerColor = innerCol.hex; }
    if (sashCol) { cfg.sashColor = sashCol.hex; }
    if (hairCol) { cfg.hairColor = hairCol.hex; matchedTags.push(`Rambut: ${hairCol.name}`); }

    // If user mentioned a general color without specifying clothing/hat, apply harmoniously!
    if (!robeCol && !hatCol) {
      const anyCol = findAnyColor(text);
      if (anyCol && !text.includes('kacamata hitam') && !text.includes('tabung reaksi hijau')) {
        cfg.robeColor = anyCol.hex;
        matchedTags.push(`Warna: ${anyCol.name}`);
      }
    }

    // Special hair color shortcuts
    if (hasAny(text, ['pirang', 'blonde', 'rambut kuning'])) cfg.hairColor = '#E0B44A';
    else if (hasAny(text, ['rambut putih', 'uban', 'beruban', 'white hair'])) cfg.hairColor = '#E6EAF0';
    else if (hasAny(text, ['rambut merah', 'red hair', 'ginger'])) cfg.hairColor = '#B83D28';

    cfg.name = toDisplayName(raw, bestArch ? bestArch.label : 'Karakter Kustom');

    // Suggest an initial animation mode if the prompt describes an action!
    let recommendedAnim = null;
    if (hasAny(text, ['melambai', 'sapa', 'menyapa', 'wave'])) recommendedAnim = 'wave';
    else if (hasAny(text, ['berlari', 'lari', 'sprint', 'running'])) recommendedAnim = 'run';
    else if (hasAny(text, ['berjalan', 'jalan', 'walking'])) recommendedAnim = 'walk';
    else if (hasAny(text, ['melompat', 'lompat', 'jump'])) recommendedAnim = 'jump';
    else if (hasAny(text, ['tertawa', 'ketawa', 'tawa', 'laugh'])) recommendedAnim = 'laugh';
    else if (hasAny(text, ['bicara', 'pidato', 'berbicara', 'talking'])) recommendedAnim = 'talk';
    else if (hasAny(text, ['bonk', 'kepentok', 'pusing'])) recommendedAnim = 'bonk';

    return {
      config: cfg,
      meta: {
        engine: 'local',
        detectedArchetype: bestArch ? bestArch.label : 'Karakter Orisinal',
        matchedTags: matchedTags.slice(0, 7),
        componentName: toComponentName(cfg.name),
        recommendedAnim
      }
    };
  }

  /**
   * Optional Gemini 3.8 Flash Interactions API Mode (BYO API Key)
   * Uses https://generativelanguage.googleapis.com/v1beta/interactions with structured JSON output.
   */
  async function generateFromPromptWithGemini(promptText, apiKey) {
    const DEFAULT_CONFIG = global.CharacterEngine ? global.CharacterEngine.DEFAULT_CONFIG : {};
    const validEnums = {
      headShape: ['potato', 'round', 'tall', 'wide', 'pear'],
      eyes: ['shocked', 'chill', 'angry', 'smug', 'panic', 'happy', 'suspicious', 'asymmetric', 'focused', 'deadpan', 'starry'],
      eyebrows: ['worried', 'flat', 'angry', 'raised', 'skeptical', 'happy'],
      mouth: ['teeth_oval', 'smirk', 'open_yell', 'frown', 'flat', 'grin_teeth', 'grit_teeth', 'small_o', 'happy_open'],
      beard: ['none', 'goatee', 'mandarin', 'mustache', 'handlebar', 'full_beard', 'stubble'],
      faceAccessory: ['none', 'round_glasses', 'sunglasses', 'cyber_visor', 'monocle', 'eyepatch', 'goggles', 'scar', 'bandage'],
      hat: ['guanmao', 'jingasa', 'hachimaki', 'futou', 'kabuto', 'fedora', 'chef_toque', 'astronaut_helmet', 'cowboy', 'pirate_tricorne', 'wizard_hat', 'top_hat', 'bowler', 'beanie', 'cap', 'crown', 'miner_helmet', 'hood', 'beret', 'none'],
      backHair: ['qing_braid', 'chonmage', 'short', 'bald', 'spiky', 'curly', 'long_flow', 'side_part', 'twin_tufts', 'mohawk'],
      outfit: ['magua', 'armor', 'haori_stripe', 'noble_robe', 'trench_coat', 'suit_tie', 'spacesuit', 'chef_apron', 'lab_coat', 'plaid_suspenders', 'hoodie', 'pirate_coat', 'wizard_robe', 'vest_western', 'tactical_vest', 'cyber_jacket', 'steampunk_coat', 'royal_uniform', 'leather_biker', 'medieval_knight', 'hanbok_kimono', 'mechanic_overall', 'street_varsity', 'safari_explorer'],
      beltStyle: ['bow', 'buckle', 'knot', 'plain', 'utility_belt', 'rope_sash'],
      cape: ['none', 'short_cape', 'royal_cape', 'scarf', 'jetpack', 'backpack'],
      emblem: ['none', 'star', 'skull', 'lightning', 'shield', 'heart', 'crown', 'dollar', 'atom', 'crescent', 'target', 'gear'],
      pose: ['akimbo', 'ready', 'panic', 'point', 'crossed', 'wave', 'heroic', 'think'],
      prop: ['none', 'bomb', 'spear', 'fan', 'scroll', 'magnifying_glass', 'spatula', 'laser_blaster', 'flask', 'magic_staff', 'sword', 'pickaxe', 'coffee_mug', 'laptop', 'lantern', 'microphone', 'money_bag', 'wrench']
    };

    const schema = {
      type: 'object',
      properties: {
        name: { type: 'string' },
        headShape: { type: 'string', enum: validEnums.headShape },
        skinColor: { type: 'string' },
        blushColor: { type: 'string' },
        eyes: { type: 'string', enum: validEnums.eyes },
        eyebrows: { type: 'string', enum: validEnums.eyebrows },
        mouth: { type: 'string', enum: validEnums.mouth },
        beard: { type: 'string', enum: validEnums.beard },
        faceAccessory: { type: 'string', enum: validEnums.faceAccessory },
        sweatDrop: { type: 'boolean' },
        blush: { type: 'boolean' },
        angerVein: { type: 'boolean' },
        eyeGazeX: { type: 'number' },
        eyeGazeY: { type: 'number' },
        hat: { type: 'string', enum: validEnums.hat },
        hatPrimary: { type: 'string' },
        hatAccent: { type: 'string' },
        hatTilt: { type: 'number' },
        backHair: { type: 'string', enum: validEnums.backHair },
        hairColor: { type: 'string' },
        outfit: { type: 'string', enum: validEnums.outfit },
        robeColor: { type: 'string' },
        innerColor: { type: 'string' },
        sashColor: { type: 'string' },
        trimColor: { type: 'string' },
        beltStyle: { type: 'string', enum: validEnums.beltStyle },
        cape: { type: 'string', enum: validEnums.cape },
        capeColor: { type: 'string' },
        emblem: { type: 'string', enum: validEnums.emblem },
        pose: { type: 'string', enum: validEnums.pose },
        prop: { type: 'string', enum: validEnums.prop },
        tags: { type: 'array', items: { type: 'string' } }
      },
      required: ['name', 'headShape', 'eyes', 'eyebrows', 'mouth', 'hat', 'outfit', 'robeColor', 'pose', 'prop']
    };

    const instruction = [
      'You are an expert 2.5D stylized cartoon character designer.',
      'Design a cohesive, expressive, story-authentic character matching the user prompt.',
      'Use harmonious hex colors (#RRGGBB). Match skin tone, headwear, hair under hat, outfit, face accessory, expression, and handheld prop closely to the prompt.',
      'Return ONLY valid JSON matching the schema. Keep `name` short (2-4 words) in the same language as the prompt.',
      'User prompt: ' + promptText
    ].join('\n');

    const res = await fetch('https://generativelanguage.googleapis.com/v1beta/interactions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-goog-api-key': apiKey.trim()
      },
      body: JSON.stringify({
        model: 'gemini-3.8-flash',
        input: instruction,
        response_format: {
          type: 'text',
          mime_type: 'application/json',
          schema
        }
      })
    });

    if (!res.ok) {
      const errText = await res.text().catch(() => '');
      throw new Error(`Gemini API HTTP ${res.status}: ${errText.slice(0, 160)}`);
    }

    const data = await res.json();
    let jsonText = data.output_text || '';
    if (!jsonText && Array.isArray(data.outputs)) {
      for (let i = data.outputs.length - 1; i >= 0; i--) {
        if (data.outputs[i] && typeof data.outputs[i].text === 'string') {
          jsonText = data.outputs[i].text;
          break;
        }
      }
    }
    const parsed = JSON.parse(jsonText);

    const isHex = (v) => typeof v === 'string' && /^#[0-9A-Fa-f]{6}$/.test(v);
    const clampNum = (v, min, max, def) => (typeof v === 'number' && !Number.isNaN(v) ? Math.max(min, Math.min(max, v)) : def);

    const cfg = { ...DEFAULT_CONFIG, prompt: promptText, customLayers: [] };
    if (typeof parsed.name === 'string' && parsed.name.trim()) cfg.name = parsed.name.trim().slice(0, 42);
    for (const [k, allowed] of Object.entries(validEnums)) {
      if (allowed.includes(parsed[k])) cfg[k] = parsed[k];
    }
    for (const ck of ['skinColor', 'blushColor', 'hatPrimary', 'hatAccent', 'hairColor', 'robeColor', 'innerColor', 'sashColor', 'trimColor', 'capeColor']) {
      if (isHex(parsed[ck])) cfg[ck] = parsed[ck];
    }
    cfg.sweatDrop = !!parsed.sweatDrop;
    cfg.blush = !!parsed.blush;
    cfg.angerVein = !!parsed.angerVein;
    cfg.eyeGazeX = clampNum(parsed.eyeGazeX, -1, 1, 0);
    cfg.eyeGazeY = clampNum(parsed.eyeGazeY, -1, 1, 0);
    cfg.hatTilt = clampNum(parsed.hatTilt, -25, 25, 0);

    const tags = Array.isArray(parsed.tags) && parsed.tags.length > 0
      ? parsed.tags.slice(0, 6)
      : [`Topi: ${cfg.hat}`, `Outfit: ${cfg.outfit}`, `Properti: ${cfg.prop}`];

    return {
      config: cfg,
      meta: {
        engine: 'gemini',
        detectedArchetype: 'Gemini 3.8 Flash AI',
        matchedTags: tags,
        componentName: toComponentName(cfg.name)
      }
    };
  }

  global.PromptEngine = {
    PROMPT_EXAMPLES,
    generateFromPromptLocal,
    generateFromPromptWithGemini,
    toComponentName
  };
})(typeof window !== 'undefined' ? window : globalThis);
