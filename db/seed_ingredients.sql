-- Ingredient catalog. Nutrition per 100 g, rounded from USDA FoodData Central.
-- Columns: name, category, kcal, protein, carbs, fat, fiber, iron,
--          is_vegetable, is_healthy_fat, is_common, always_on_hand

INSERT INTO ingredients
    (name, category, kcal, protein_g, carbs_g, fat_g, fiber_g, iron_mg,
     is_vegetable, is_healthy_fat, is_common, always_on_hand)
VALUES
-- Protein
('chicken breast',        'protein', 120, 22.5,  0.0,  2.6,  0.0, 0.40, false, false, true,  false),
('chicken thigh',         'protein', 121, 19.7,  0.0,  4.1,  0.0, 0.80, false, false, false, false),
('ground turkey',         'protein', 150, 18.7,  0.0,  8.3,  0.0, 1.00, false, false, false, false),
('ground beef',           'protein', 176, 20.0,  0.0, 10.0,  0.0, 2.30, false, false, true,  false),
('sirloin steak',         'protein', 160, 21.0,  0.0,  8.0,  0.0, 1.70, false, false, false, false),
('salmon',                'protein', 208, 20.0,  0.0, 13.0,  0.0, 0.30, false, true,  false, false),
('canned tuna',           'protein', 116, 25.5,  0.0,  0.8,  0.0, 1.30, false, false, true,  false),
('canned sardines',       'protein', 208, 24.6,  0.0, 11.5,  0.0, 2.90, false, true,  false, false),
('shrimp',                'protein',  85, 20.0,  0.0,  0.5,  0.0, 0.50, false, false, false, false),
('cod',                   'protein',  82, 18.0,  0.0,  0.7,  0.0, 0.40, false, false, false, false),
('eggs',                  'protein', 143, 12.6,  0.7,  9.5,  0.0, 1.80, false, false, true,  false),
('firm tofu',             'protein', 144, 17.3,  2.8,  8.7,  2.3, 2.70, false, false, true,  false),
('tempeh',                'protein', 192, 20.3,  7.6, 10.8,  0.0, 2.70, false, false, false, false),
-- Legumes
('red lentils',           'legume',  358, 23.9, 63.0,  2.2, 10.8, 7.40, false, false, true,  false),
('cooked lentils',        'legume',  116,  9.0, 20.0,  0.4,  7.9, 3.30, false, false, false, false),
('chickpeas',             'legume',  164,  8.9, 27.4,  2.6,  7.6, 2.90, false, false, true,  false),
('black beans',           'legume',  132,  8.9, 23.7,  0.5,  8.7, 2.10, false, false, true,  false),
('kidney beans',          'legume',  127,  8.7, 22.8,  0.5,  6.4, 2.90, false, false, false, false),
('edamame',               'legume',  121, 11.9,  8.9,  5.2,  5.2, 2.30, false, false, false, false),
('hummus',                'legume',  166,  7.9, 14.3,  9.6,  6.0, 2.40, false, true,  false, false),
-- Dairy
('milk',                  'dairy',    50,  3.3,  4.8,  2.0,  0.0, 0.00, false, false, true,  false),
('greek yogurt',          'dairy',    59, 10.2,  3.6,  0.4,  0.0, 0.10, false, false, true,  false),
('cottage cheese',        'dairy',    84, 11.0,  4.3,  2.3,  0.0, 0.20, false, false, false, false),
('feta',                  'dairy',   264, 14.2,  4.1, 21.3,  0.0, 0.70, false, false, false, false),
('cheddar',               'dairy',   403, 24.9,  1.3, 33.0,  0.0, 0.70, false, false, true,  false),
('mozzarella',            'dairy',   254, 24.3,  2.8, 15.9,  0.0, 0.20, false, false, false, false),
('parmesan',              'dairy',   392, 35.8,  3.2, 25.8,  0.0, 0.80, false, false, false, false),
('butter',                'dairy',   717,  0.9,  0.1, 81.0,  0.0, 0.00, false, false, true,  false),
-- Vegetables
('spinach',               'vegetable', 23, 2.9,  3.6,  0.4,  2.2, 2.70, true,  false, true,  false),
('kale',                  'vegetable', 35, 2.9,  4.4,  1.5,  4.1, 1.60, true,  false, false, false),
('broccoli',              'vegetable', 34, 2.8,  6.6,  0.4,  2.6, 0.70, true,  false, true,  false),
('cauliflower',           'vegetable', 25, 1.9,  5.0,  0.3,  2.0, 0.40, true,  false, false, false),
('bell pepper',           'vegetable', 31, 1.0,  6.0,  0.3,  2.1, 0.40, true,  false, true,  false),
('tomato',                'vegetable', 18, 0.9,  3.9,  0.2,  1.2, 0.30, true,  false, true,  false),
('canned tomatoes',       'vegetable', 24, 1.1,  4.4,  0.3,  1.9, 1.10, true,  false, true,  false),
('onion',                 'vegetable', 40, 1.1,  9.3,  0.1,  1.7, 0.20, true,  false, true,  false),
('carrot',                'vegetable', 41, 0.9,  9.6,  0.2,  2.8, 0.30, true,  false, true,  false),
('zucchini',              'vegetable', 17, 1.2,  3.1,  0.3,  1.0, 0.40, true,  false, false, false),
('mushrooms',             'vegetable', 22, 3.1,  3.3,  0.3,  1.0, 0.50, true,  false, false, false),
('cucumber',              'vegetable', 15, 0.7,  3.6,  0.1,  0.5, 0.30, true,  false, true,  false),
('romaine lettuce',       'vegetable', 17, 1.2,  3.3,  0.3,  2.1, 1.00, true,  false, false, false),
('arugula',               'vegetable', 25, 2.6,  3.7,  0.7,  1.6, 1.50, true,  false, false, false),
('sweet potato',          'vegetable', 86, 1.6, 20.1,  0.1,  3.0, 0.60, true,  false, false, false),
('frozen peas',           'vegetable', 81, 5.4, 14.5,  0.4,  5.1, 1.50, true,  false, true,  false),
('green beans',           'vegetable', 31, 1.8,  7.0,  0.2,  2.7, 1.00, true,  false, false, false),
('asparagus',             'vegetable', 20, 2.2,  3.9,  0.1,  2.1, 2.10, true,  false, false, false),
('brussels sprouts',      'vegetable', 43, 3.4,  9.0,  0.3,  3.8, 1.40, true,  false, false, false),
('cabbage',               'vegetable', 25, 1.3,  5.8,  0.1,  2.5, 0.50, true,  false, false, false),
('corn',                  'vegetable', 86, 3.3, 19.0,  1.4,  2.7, 0.50, true,  false, false, false),
('celery',                'vegetable', 14, 0.7,  3.0,  0.2,  1.6, 0.20, true,  false, false, false),
('eggplant',              'vegetable', 25, 1.0,  5.9,  0.2,  3.0, 0.20, true,  false, false, false),
('bok choy',              'vegetable', 13, 1.5,  2.2,  0.2,  1.0, 0.80, true,  false, false, false),
('beets',                 'vegetable', 43, 1.6,  9.6,  0.2,  2.8, 0.80, true,  false, false, false),
('butternut squash',      'vegetable', 45, 1.0, 11.7,  0.1,  2.0, 0.70, true,  false, false, false),
('scallions',             'vegetable', 32, 1.8,  7.3,  0.2,  2.6, 1.50, true,  false, false, false),
('potato',                'starch',    77, 2.0, 17.5,  0.1,  2.2, 0.80, false, false, true,  false),
-- Aromatics and herbs
('garlic',                'aromatic', 149, 6.4, 33.0,  0.5,  2.1, 1.70, false, false, true,  false),
('ginger',                'aromatic',  80, 1.8, 17.8,  0.8,  2.0, 0.60, false, false, false, false),
('jalapeno',              'aromatic',  29, 0.9,  6.5,  0.4,  2.8, 0.30, false, false, false, false),
('cilantro',              'herb',      23, 2.1,  3.7,  0.5,  2.8, 1.80, false, false, false, false),
('basil',                 'herb',      23, 3.2,  2.7,  0.6,  1.6, 3.20, false, false, false, false),
('parsley',               'herb',      36, 3.0,  6.3,  0.8,  3.3, 6.20, false, false, false, false),
('lemon',                 'fruit',     29, 1.1,  9.3,  0.3,  2.8, 0.60, false, false, true,  false),
('lime',                  'fruit',     30, 0.7, 10.5,  0.2,  2.8, 0.60, false, false, false, false),
-- Fruit
('avocado',               'fruit',    160, 2.0,  8.5, 14.7,  6.7, 0.60, false, true,  true,  false),
('banana',                'fruit',     89, 1.1, 22.8,  0.3,  2.6, 0.30, false, false, true,  false),
('apple',                 'fruit',     52, 0.3, 13.8,  0.2,  2.4, 0.10, false, false, true,  false),
('blueberries',           'fruit',     57, 0.7, 14.5,  0.3,  2.4, 0.30, false, false, false, false),
('strawberries',          'fruit',     32, 0.7,  7.7,  0.3,  2.0, 0.40, false, false, false, false),
('mango',                 'fruit',     60, 0.8, 15.0,  0.4,  1.6, 0.20, false, false, false, false),
('orange',                'fruit',     47, 0.9, 11.8,  0.1,  2.4, 0.10, false, false, false, false),
-- Grains
('rolled oats',           'grain',    379, 13.2, 67.7, 6.5, 10.1, 4.30, false, false, true,  false),
('brown rice',            'grain',    370,  7.9, 77.0, 2.9,  3.5, 1.50, false, false, true,  false),
('white rice',            'grain',    365,  7.1, 80.0, 0.7,  1.3, 0.80, false, false, true,  false),
('quinoa',                'grain',    368, 14.1, 64.2, 6.1,  7.0, 4.60, false, false, false, false),
('pasta',                 'grain',    371, 13.0, 74.7, 1.5,  3.2, 3.30, false, false, true,  false),
('whole wheat pasta',     'grain',    352, 14.0, 71.0, 2.5,  9.0, 3.60, false, false, false, false),
('whole wheat bread',     'grain',    252, 12.4, 43.0, 3.5,  6.0, 2.50, false, false, true,  false),
('whole wheat tortillas', 'grain',    300,  8.6, 49.0, 7.5,  6.2, 2.60, false, false, false, false),
('corn tortillas',        'grain',    218,  5.7, 44.6, 2.9,  6.3, 1.20, false, false, false, false),
('couscous',              'grain',    376, 12.8, 77.4, 0.6,  5.0, 1.10, false, false, false, false),
('rice noodles',          'grain',    364,  6.0, 80.0, 0.6,  1.6, 0.70, false, false, false, false),
-- Nuts, seeds and oils
('olive oil',             'fat',      884,  0.0,  0.0, 100.0, 0.0, 0.60, false, true,  true,  false),
('sesame oil',            'fat',      884,  0.0,  0.0, 100.0, 0.0, 0.00, false, true,  false, false),
('almonds',               'nut',      579, 21.2, 21.6, 49.9, 12.5, 3.70, false, true, false, false),
('walnuts',               'nut',      654, 15.2, 13.7, 65.2,  6.7, 2.90, false, true, false, false),
('cashews',               'nut',      553, 18.2, 30.2, 43.9,  3.3, 6.70, false, true, false, false),
('peanut butter',         'nut',      588, 25.0, 20.0, 50.0,  6.0, 1.90, false, true, true,  false),
('chia seeds',            'seed',     486, 16.5, 42.1, 30.7, 34.4, 7.70, false, true, false, false),
('ground flaxseed',       'seed',     534, 18.3, 28.9, 42.2, 27.3, 5.70, false, true, false, false),
('pumpkin seeds',         'seed',     559, 30.2, 10.7, 49.0,  6.0, 8.80, false, true, false, false),
('tahini',                'seed',     595, 17.0, 21.2, 53.8,  9.3, 8.95, false, true, false, false),
-- Pantry and condiments
('soy sauce',             'condiment',  53, 8.1,  4.9,  0.6,  0.8, 1.50, false, false, true,  false),
('honey',                 'condiment', 304, 0.3, 82.4,  0.0,  0.2, 0.40, false, false, true,  false),
('salsa',                 'condiment',  36, 1.5,  6.6,  0.2,  1.9, 0.40, false, false, false, false),
('balsamic vinegar',      'condiment',  88, 0.5, 17.0,  0.0,  0.0, 0.70, false, false, false, false),
('coconut milk',          'pantry',    230, 2.3,  5.5, 23.8,  2.2, 1.60, false, false, false, false),
('vegetable broth',       'pantry',      6, 0.2,  1.0,  0.1,  0.0, 0.10, false, false, true,  false),
('chicken broth',         'pantry',      7, 0.6,  0.4,  0.2,  0.0, 0.20, false, false, false, false),
('dark chocolate',        'pantry',    598, 7.8, 45.9, 42.6, 10.9, 11.90, false, false, false, false),
-- Spices
('cumin',                 'spice',     375, 17.8, 44.2, 22.3, 10.5, 66.40, false, false, false, false),
('paprika',               'spice',     282, 14.1, 54.0, 12.9, 34.9, 21.10, false, false, false, false),
('curry powder',          'spice',     325, 14.3, 55.8, 14.0, 53.2, 19.10, false, false, false, false),
('turmeric',              'spice',     312,  9.7, 67.1,  3.3, 22.7, 55.00, false, false, false, false),
('cinnamon',              'spice',     247,  4.0, 80.6,  1.2, 53.1,  8.30, false, false, false, false),
('dried oregano',         'spice',     265,  9.0, 68.9,  4.3, 42.5, 36.80, false, false, false, false),
('black pepper',          'spice',     251, 10.4, 64.0,  3.3, 25.3,  9.70, false, false, false, true),
('salt',                  'spice',       0,  0.0,  0.0,  0.0,  0.0,  0.30, false, false, false, true),
('water',                 'pantry',      0,  0.0,  0.0,  0.0,  0.0,  0.00, false, false, false, true);

INSERT INTO ingredient_aliases (alias, ingredient_id)
SELECT a.alias, i.id
FROM (VALUES
    ('chicken', 'chicken breast'), ('chicken breasts', 'chicken breast'),
    ('chicken thighs', 'chicken thigh'), ('turkey', 'ground turkey'),
    ('beef', 'ground beef'), ('minced beef', 'ground beef'), ('mince', 'ground beef'),
    ('steak', 'sirloin steak'), ('tuna', 'canned tuna'), ('sardines', 'canned sardines'),
    ('prawns', 'shrimp'), ('egg', 'eggs'), ('tofu', 'firm tofu'),
    ('lentils', 'red lentils'), ('garbanzo beans', 'chickpeas'), ('chick peas', 'chickpeas'),
    ('yogurt', 'greek yogurt'), ('yoghurt', 'greek yogurt'), ('greek yoghurt', 'greek yogurt'),
    ('cheese', 'cheddar'), ('cheddar cheese', 'cheddar'), ('feta cheese', 'feta'),
    ('mozzarella cheese', 'mozzarella'), ('parmigiano', 'parmesan'),
    ('baby spinach', 'spinach'), ('bell peppers', 'bell pepper'), ('red pepper', 'bell pepper'),
    ('green pepper', 'bell pepper'), ('capsicum', 'bell pepper'), ('peppers', 'bell pepper'),
    ('tomatoes', 'tomato'), ('cherry tomatoes', 'tomato'), ('diced tomatoes', 'canned tomatoes'),
    ('onions', 'onion'), ('red onion', 'onion'), ('yellow onion', 'onion'),
    ('carrots', 'carrot'), ('courgette', 'zucchini'), ('mushroom', 'mushrooms'),
    ('lettuce', 'romaine lettuce'), ('romaine', 'romaine lettuce'), ('rocket', 'arugula'),
    ('peas', 'frozen peas'), ('green peas', 'frozen peas'), ('sweet potatoes', 'sweet potato'),
    ('potatoes', 'potato'), ('aubergine', 'eggplant'), ('pak choi', 'bok choy'),
    ('green onions', 'scallions'), ('spring onions', 'scallions'), ('beetroot', 'beets'),
    ('coriander', 'cilantro'), ('lemons', 'lemon'), ('limes', 'lime'), ('bananas', 'banana'),
    ('apples', 'apple'), ('oats', 'rolled oats'), ('oatmeal', 'rolled oats'), ('rice', 'white rice'),
    ('spaghetti', 'pasta'), ('penne', 'pasta'), ('bread', 'whole wheat bread'),
    ('tortillas', 'whole wheat tortillas'), ('flour tortillas', 'whole wheat tortillas'),
    ('flaxseed', 'ground flaxseed'), ('flax seeds', 'ground flaxseed'), ('pepitas', 'pumpkin seeds'),
    ('broth', 'vegetable broth'), ('stock', 'vegetable broth'), ('oregano', 'dried oregano'),
    ('chocolate', 'dark chocolate'), ('jalapenos', 'jalapeno'), ('sweetcorn', 'corn')
) AS a(alias, ingredient_name)
JOIN ingredients i ON i.name = a.ingredient_name;

-- Allergen map. Conservative on purpose: when a common product usually
-- contains an allergen (soy sauce -> wheat, dark chocolate -> milk/soy,
-- hummus -> sesame), it is flagged.
CREATE TEMP TABLE staging_allergens (ingredient TEXT, allergen allergen);
INSERT INTO staging_allergens VALUES
    ('milk', 'dairy'), ('greek yogurt', 'dairy'), ('cottage cheese', 'dairy'), ('feta', 'dairy'),
    ('cheddar', 'dairy'), ('mozzarella', 'dairy'), ('parmesan', 'dairy'), ('butter', 'dairy'),
    ('dark chocolate', 'dairy'),
    ('eggs', 'eggs'),
    ('peanut butter', 'peanuts'),
    ('almonds', 'tree_nuts'), ('walnuts', 'tree_nuts'), ('cashews', 'tree_nuts'),
    ('firm tofu', 'soy'), ('tempeh', 'soy'), ('edamame', 'soy'), ('soy sauce', 'soy'),
    ('dark chocolate', 'soy'),
    ('pasta', 'gluten'), ('whole wheat pasta', 'gluten'), ('whole wheat bread', 'gluten'),
    ('whole wheat tortillas', 'gluten'), ('couscous', 'gluten'), ('soy sauce', 'gluten'),
    ('rolled oats', 'gluten'),
    ('salmon', 'fish'), ('canned tuna', 'fish'), ('canned sardines', 'fish'), ('cod', 'fish'),
    ('shrimp', 'shellfish'),
    ('sesame oil', 'sesame'), ('tahini', 'sesame'), ('hummus', 'sesame');

DO $$
DECLARE bad TEXT;
BEGIN
    SELECT string_agg(s.ingredient, ', ') INTO bad
    FROM staging_allergens s LEFT JOIN ingredients i ON i.name = s.ingredient
    WHERE i.id IS NULL;
    IF bad IS NOT NULL THEN
        RAISE EXCEPTION 'Unknown ingredients in allergen map: %', bad;
    END IF;
END $$;

INSERT INTO ingredient_allergens (ingredient_id, allergen)
SELECT i.id, s.allergen FROM staging_allergens s JOIN ingredients i ON i.name = s.ingredient;
DROP TABLE staging_allergens;
