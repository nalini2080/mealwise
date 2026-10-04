-- Recipes. Ingredients are written by name in a staging table, then resolved to
-- ids; the DO block aborts the seed if any name fails to resolve (typo guard).

INSERT INTO recipes (title, description, meal_type, servings, total_minutes, steps) VALUES
-- Breakfast
('Spinach & Feta Scramble', 'Soft-scrambled eggs folded with wilted spinach and salty feta.', 'breakfast', 1, 10,
 ARRAY['Wilt the spinach in olive oil over medium heat, about 1 minute.',
       'Whisk the eggs with salt and pepper, pour into the pan and stir gently until just set.',
       'Crumble the feta over the top and serve.']),
('Berry Chia Overnight Oats', 'Make-ahead oats with chia, yogurt and blueberries.', 'breakfast', 1, 5,
 ARRAY['Stir the oats, chia seeds, yogurt and milk together in a jar.',
       'Top with blueberries and honey.',
       'Refrigerate overnight (or at least 4 hours) and eat cold.']),
('Greek Yogurt Walnut Parfait', 'Layers of Greek yogurt, strawberries, walnuts and flax.', 'breakfast', 1, 5,
 ARRAY['Slice the strawberries.',
       'Layer yogurt, strawberries, walnuts and flaxseed in a glass.',
       'Drizzle with honey.']),
('Peanut Butter Banana Oatmeal', 'Creamy stovetop oats topped with banana and peanut butter.', 'breakfast', 1, 10,
 ARRAY['Simmer the oats in milk with the cinnamon for 5 minutes, stirring often.',
       'Slice the banana on top and add a spoon of peanut butter.']),
('Veggie Egg Muffins', 'Grab-and-go baked egg cups loaded with peppers and spinach.', 'breakfast', 4, 30,
 ARRAY['Heat the oven to 180°C / 350°F and grease a 12-cup muffin tin.',
       'Dice the pepper and onion and chop the spinach; divide between the cups.',
       'Whisk the eggs with salt and pepper, pour over the vegetables and top with cheddar.',
       'Bake 20 minutes until set. Keeps 4 days in the fridge.']),
('Avocado Egg Toast', 'Smashed avocado on whole wheat toast with a fried egg and seeds.', 'breakfast', 1, 10,
 ARRAY['Toast the bread.',
       'Mash the avocado with lemon juice, salt and pepper and spread on the toast.',
       'Fry the eggs and place on top; finish with pumpkin seeds.']),
('Turmeric Tofu Scramble', 'A plant-based scramble with peppers, spinach and turmeric.', 'breakfast', 2, 15,
 ARRAY['Sauté the diced onion and pepper in olive oil for 4 minutes.',
       'Crumble in the tofu, add turmeric and salt, and cook 4 minutes.',
       'Stir in the spinach until wilted.']),
('Cottage Cheese Berry Bowl', 'High-protein cottage cheese with berries, almonds and chia.', 'breakfast', 1, 5,
 ARRAY['Spoon the cottage cheese into a bowl.',
       'Top with blueberries, chopped almonds and chia seeds.']),
('Black Bean Breakfast Burritos', 'Eggs, black beans, salsa and cheddar wrapped to go.', 'breakfast', 2, 15,
 ARRAY['Warm the black beans in a pan.',
       'Scramble the eggs and fold in the spinach.',
       'Fill the tortillas with eggs, beans, salsa and cheddar, then roll up.']),
('Green Protein Smoothie', 'Spinach, banana, yogurt and peanut butter blended smooth.', 'breakfast', 1, 5,
 ARRAY['Add everything to a blender.',
       'Blend until completely smooth, adding more milk if it is too thick.']),
('Mango Chia Pudding', 'Chia pudding layered with fresh mango.', 'breakfast', 2, 5,
 ARRAY['Whisk the chia seeds into the milk with the honey.',
       'Rest 10 minutes, whisk again, then refrigerate at least 2 hours.',
       'Top with diced mango.']),
('Shakshuka', 'Eggs poached in a spiced tomato and pepper sauce.', 'breakfast', 2, 25,
 ARRAY['Sauté the onion and pepper in olive oil for 5 minutes, then add garlic, cumin and paprika.',
       'Add the canned tomatoes and simmer 10 minutes.',
       'Make wells, crack in the eggs, cover and cook 5–7 minutes.',
       'Top with feta and parsley; serve with bread if you have it.']),
-- Lunch
('Red Lentil Soup', 'A hearty, iron-rich soup with carrots, tomatoes and cumin.', 'lunch', 4, 40,
 ARRAY['Sauté the onion, carrot and celery in olive oil for 6 minutes; add garlic and cumin.',
       'Add the lentils, canned tomatoes and broth; simmer 20 minutes.',
       'Stir in the spinach and lemon juice, and season with salt.']),
('Quinoa Chickpea Power Salad', 'Quinoa, chickpeas, crunchy veg and feta in a lemon dressing.', 'lunch', 2, 25,
 ARRAY['Cook the quinoa according to the package and let it cool.',
       'Chop the cucumber and tomato.',
       'Toss everything with olive oil, lemon juice and salt.']),
('Tuna Lettuce Wraps', 'Light tuna salad made with Greek yogurt, in crisp lettuce cups.', 'lunch', 2, 10,
 ARRAY['Mix the tuna, yogurt, diced celery, lemon juice and pepper.',
       'Spoon into romaine leaves.']),
('Black Bean Burrito Bowl', 'Brown rice, black beans, corn, peppers, salsa and avocado.', 'lunch', 2, 25,
 ARRAY['Cook the rice.',
       'Warm the beans and corn with the cumin.',
       'Build bowls with rice, lettuce, beans, corn, pepper, salsa, avocado and lime.']),
('Mediterranean Hummus Wrap', 'Hummus, crunchy veg and feta in a whole wheat wrap.', 'lunch', 1, 10,
 ARRAY['Spread the hummus over the tortilla.',
       'Layer the spinach, sliced cucumber, tomato and feta.',
       'Roll up tightly and slice in half.']),
('Chicken Kale Caesar', 'Massaged kale, grilled chicken and a yogurt Caesar dressing.', 'lunch', 2, 25,
 ARRAY['Season and grill the chicken, about 6 minutes per side; slice.',
       'Whisk the yogurt, lemon, grated garlic, olive oil and half the parmesan.',
       'Massage the kale with the dressing, then top with chicken, toasted bread cubes and the rest of the parmesan.']),
('Egg Fried Rice with Peas', 'Quick fried rice with eggs, peas and carrots.', 'lunch', 2, 20,
 ARRAY['Cook the rice (day-old rice works best).',
       'Scramble the eggs in sesame oil and set aside.',
       'Stir-fry the garlic, carrot and peas for 3 minutes, add the rice and soy sauce, and fold in the eggs and scallions.']),
('Mushroom Spinach Quesadillas', 'Crispy quesadillas filled with mushrooms, spinach and beans.', 'lunch', 2, 15,
 ARRAY['Sauté the mushrooms in olive oil for 5 minutes, then add the spinach to wilt.',
       'Fill the tortillas with the veg, black beans and mozzarella.',
       'Cook in a dry pan until golden on both sides.']),
('Greek Chicken Salad', 'Chicken, cucumber, tomato and feta with oregano dressing.', 'lunch', 2, 25,
 ARRAY['Season the chicken with oregano and cook through; slice.',
       'Chop the romaine, cucumber and tomato.',
       'Toss with olive oil and lemon and top with the chicken and feta.']),
('Sesame Edamame Bowl', 'Quinoa with edamame, crunchy cabbage and avocado.', 'lunch', 2, 20,
 ARRAY['Cook the quinoa.',
       'Shred the cabbage and carrot and slice the cucumber.',
       'Toss with the edamame, soy sauce and sesame oil, and top with avocado.']),
('Beet & Lentil Salad', 'Earthy beets, lentils, arugula, walnuts and feta.', 'lunch', 2, 15,
 ARRAY['Dice the cooked beets.',
       'Toss the lentils, beets and arugula with olive oil and balsamic.',
       'Top with walnuts and crumbled feta.']),
('Minestrone', 'Classic Italian vegetable and bean soup.', 'lunch', 6, 45,
 ARRAY['Sauté the onion, carrot and celery in olive oil; add garlic and oregano.',
       'Add the tomatoes, broth, zucchini and green beans; simmer 15 minutes.',
       'Add the pasta and beans and cook until tender; stir in the spinach.',
       'Serve with parmesan.']),
('Chicken & Kale Soup', 'Comforting chicken soup with kale and potatoes.', 'lunch', 4, 40,
 ARRAY['Sauté the onion, carrot and celery; add garlic.',
       'Add the broth, diced potato and whole chicken breasts; simmer 20 minutes.',
       'Shred the chicken, return it to the pot with the kale, and finish with parsley.']),
-- Dinner
('Chickpea Spinach Curry', 'Creamy coconut chickpea curry loaded with spinach.', 'dinner', 4, 30,
 ARRAY['Sauté the onion, then add garlic, ginger and curry powder for 1 minute.',
       'Add the chickpeas, tomatoes and coconut milk; simmer 15 minutes.',
       'Stir in the spinach and serve over rice.']),
('Turkey Bean Chili', 'Lean turkey chili with kidney beans and peppers.', 'dinner', 4, 45,
 ARRAY['Brown the turkey with the onion and pepper in olive oil.',
       'Add garlic, cumin and paprika, then the tomatoes and beans.',
       'Simmer 25 minutes and season with salt.']),
('Shrimp Veggie Stir-Fry', 'Garlicky shrimp with broccoli and peppers over brown rice.', 'dinner', 2, 20,
 ARRAY['Cook the rice.',
       'Stir-fry the broccoli and pepper in sesame oil for 4 minutes.',
       'Add the shrimp, garlic and ginger; cook 3 minutes, then add the soy sauce and honey.']),
('Sheet Pan Salmon & Sweet Potato', 'Lemon salmon roasted with asparagus and sweet potato.', 'dinner', 2, 35,
 ARRAY['Heat the oven to 220°C / 425°F. Roast the cubed sweet potato in oil for 15 minutes.',
       'Add the asparagus and salmon, season with garlic, lemon and salt.',
       'Roast another 12 minutes.']),
('Beef & Broccoli', 'Takeout-style beef and broccoli with a ginger soy glaze.', 'dinner', 3, 25,
 ARRAY['Cook the rice.',
       'Sear the thinly sliced steak in sesame oil and set it aside.',
       'Stir-fry the broccoli, add garlic, ginger, soy sauce and honey, then return the beef.']),
('Sheet Pan Paprika Chicken', 'Crispy paprika chicken thighs with Brussels sprouts and carrots.', 'dinner', 3, 40,
 ARRAY['Heat the oven to 220°C / 425°F.',
       'Toss the chicken, halved sprouts, carrots and onion with oil, paprika and salt.',
       'Roast 30–35 minutes until the chicken is cooked through.']),
('Veggie-Loaded Bolognese', 'Beef ragù packed with carrots and celery over whole wheat pasta.', 'dinner', 4, 40,
 ARRAY['Sauté the finely diced onion, carrot and celery in olive oil for 8 minutes.',
       'Add the beef and garlic and brown them.',
       'Add the tomatoes and oregano and simmer 20 minutes.',
       'Toss with the cooked pasta and top with parmesan.']),
('Peanut Tofu Noodles', 'Rice noodles and crispy tofu in a lime peanut sauce.', 'dinner', 2, 25,
 ARRAY['Cook the noodles and press and cube the tofu.',
       'Pan-fry the tofu until golden.',
       'Whisk the peanut butter, soy sauce, lime, honey and sesame oil with a splash of water.',
       'Toss the noodles, tofu, shredded cabbage and carrot with the sauce, and top with scallions.']),
('Lemony Sardine Pasta', 'Pantry pasta with sardines, kale, garlic and lemon.', 'dinner', 2, 20,
 ARRAY['Cook the pasta, adding the kale for the last 2 minutes.',
       'Warm the garlic in olive oil, then add the sardines and break them up.',
       'Toss with the pasta, lemon, parsley and parmesan.']),
('Black Bean Stuffed Sweet Potatoes', 'Baked sweet potatoes topped with beans, salsa and yogurt.', 'dinner', 2, 45,
 ARRAY['Bake the sweet potatoes at 200°C / 400°F for 40 minutes.',
       'Warm the beans with the cumin.',
       'Split the potatoes and top with beans, salsa, yogurt, avocado and cilantro.']),
('Beef & Bean Tacos', 'Spiced beef and black bean tacos with crunchy cabbage.', 'dinner', 3, 25,
 ARRAY['Brown the beef with the cumin and paprika, then stir in the beans.',
       'Warm the tortillas.',
       'Fill with the beef, shredded cabbage, salsa, avocado and lime.']),
('Baked Cod with Tomatoes & Green Beans', 'Flaky cod roasted with tomatoes, green beans and basil.', 'dinner', 2, 25,
 ARRAY['Heat the oven to 200°C / 400°F.',
       'Toss the green beans and tomatoes with oil and garlic in a dish and nestle in the cod.',
       'Bake 15 minutes, then finish with lemon and basil.']),
('Chicken Fajita Bowl', 'Smoky chicken and peppers over brown rice.', 'dinner', 3, 30,
 ARRAY['Cook the rice.',
       'Slice the chicken, pepper and onion and toss with cumin, paprika and oil.',
       'Sear in a hot pan for 8–10 minutes and serve over rice with salsa and lime.']),
('Coconut Red Lentil Dal', 'Golden lentil dal with coconut, turmeric and spinach.', 'dinner', 4, 35,
 ARRAY['Sauté the onion, garlic and ginger, then add the turmeric and cumin.',
       'Add the lentils, tomatoes, coconut milk and broth; simmer 20 minutes.',
       'Stir in the spinach. Serve with rice if you like.']),
('Roasted Veg & Chickpea Couscous', 'Roasted zucchini, eggplant and peppers with chickpeas and herbs.', 'dinner', 3, 35,
 ARRAY['Roast the chopped zucchini, eggplant, pepper and onion with oil and cumin at 220°C / 425°F for 25 minutes.',
       'Prepare the couscous with boiling water.',
       'Toss with the chickpeas, lemon and parsley.']),
('Turkey Stuffed Peppers', 'Peppers stuffed with turkey, rice and tomato, topped with mozzarella.', 'dinner', 4, 50,
 ARRAY['Cook the rice. Brown the turkey with the onion, garlic and oregano.',
       'Stir in the tomatoes and rice and fill the halved peppers.',
       'Top with mozzarella and bake at 190°C / 375°F for 25 minutes.']),
('Garlic Butter Shrimp & Zoodles', 'Shrimp in garlic butter over zucchini noodles.', 'dinner', 2, 20,
 ARRAY['Spiralize the zucchini.',
       'Cook the shrimp in butter with garlic for 3 minutes and remove.',
       'Toss the zoodles in the pan for 2 minutes, then return the shrimp with lemon and parsley.']),
('Steak with Garlic Spinach & Potatoes', 'Seared steak with crispy potatoes and garlicky spinach.', 'dinner', 2, 30,
 ARRAY['Roast or pan-fry the cubed potatoes in oil until crisp, about 20 minutes.',
       'Sear the steak 3–4 minutes per side and rest it.',
       'Wilt the spinach with garlic and butter.']),
('Ginger Tofu & Bok Choy', 'Crispy tofu with bok choy and mushrooms in a ginger soy sauce.', 'dinner', 2, 20,
 ARRAY['Cook the rice.',
       'Pan-fry the cubed tofu in sesame oil until golden.',
       'Add the mushrooms, bok choy, garlic and ginger; cook 4 minutes and add the soy sauce.']),
-- Snacks
('Apple & Peanut Butter', 'The classic: crisp apple slices with peanut butter.', 'snack', 1, 2,
 ARRAY['Slice the apple and serve with the peanut butter.']),
('Hummus & Veggie Sticks', 'Crunchy veg sticks with hummus for dipping.', 'snack', 1, 5,
 ARRAY['Cut the carrot, cucumber and pepper into sticks.', 'Serve with the hummus.']),
('No-Bake Energy Bites', 'Oat, peanut butter and dark chocolate bites with seeds.', 'snack', 6, 15,
 ARRAY['Mix everything in a bowl.',
       'Roll into 18 balls and chill 30 minutes.']),
('Dark Chocolate, Almonds & Berries', 'A snack plate that is surprisingly rich in iron.', 'snack', 1, 2,
 ARRAY['Arrange the chocolate, almonds and strawberries on a plate.']),
('Crispy Roasted Chickpeas', 'Crunchy smoky chickpeas.', 'snack', 2, 35,
 ARRAY['Pat the chickpeas dry and toss with oil, paprika, cumin and salt.',
       'Roast at 200°C / 400°F for 30 minutes, shaking halfway.']),
('Sea Salt Edamame', 'Steamed edamame with flaky salt.', 'snack', 1, 5,
 ARRAY['Steam or microwave the edamame and sprinkle with salt.']);

CREATE TEMP TABLE staging_recipe_ingredients (
    recipe TEXT, ingredient TEXT, grams NUMERIC, is_optional BOOLEAN DEFAULT false
);

INSERT INTO staging_recipe_ingredients (recipe, ingredient, grams) VALUES
('Spinach & Feta Scramble','eggs',150),('Spinach & Feta Scramble','spinach',60),('Spinach & Feta Scramble','feta',30),
('Spinach & Feta Scramble','olive oil',5),('Spinach & Feta Scramble','salt',1),('Spinach & Feta Scramble','black pepper',1),

('Berry Chia Overnight Oats','rolled oats',50),('Berry Chia Overnight Oats','chia seeds',15),('Berry Chia Overnight Oats','greek yogurt',100),
('Berry Chia Overnight Oats','milk',120),('Berry Chia Overnight Oats','blueberries',75),('Berry Chia Overnight Oats','honey',10),

('Greek Yogurt Walnut Parfait','greek yogurt',200),('Greek Yogurt Walnut Parfait','strawberries',100),('Greek Yogurt Walnut Parfait','walnuts',20),
('Greek Yogurt Walnut Parfait','ground flaxseed',10),('Greek Yogurt Walnut Parfait','honey',10),

('Peanut Butter Banana Oatmeal','rolled oats',50),('Peanut Butter Banana Oatmeal','milk',200),('Peanut Butter Banana Oatmeal','banana',100),
('Peanut Butter Banana Oatmeal','peanut butter',16),('Peanut Butter Banana Oatmeal','cinnamon',1),

('Veggie Egg Muffins','eggs',400),('Veggie Egg Muffins','bell pepper',120),('Veggie Egg Muffins','spinach',60),('Veggie Egg Muffins','onion',60),
('Veggie Egg Muffins','cheddar',60),('Veggie Egg Muffins','salt',2),('Veggie Egg Muffins','black pepper',1),

('Avocado Egg Toast','whole wheat bread',70),('Avocado Egg Toast','avocado',70),('Avocado Egg Toast','eggs',100),('Avocado Egg Toast','lemon',5),
('Avocado Egg Toast','pumpkin seeds',10),('Avocado Egg Toast','salt',1),('Avocado Egg Toast','black pepper',1),

('Turmeric Tofu Scramble','firm tofu',300),('Turmeric Tofu Scramble','spinach',60),('Turmeric Tofu Scramble','bell pepper',100),
('Turmeric Tofu Scramble','onion',60),('Turmeric Tofu Scramble','turmeric',2),('Turmeric Tofu Scramble','olive oil',10),('Turmeric Tofu Scramble','salt',2),

('Cottage Cheese Berry Bowl','cottage cheese',200),('Cottage Cheese Berry Bowl','blueberries',75),('Cottage Cheese Berry Bowl','almonds',15),
('Cottage Cheese Berry Bowl','chia seeds',10),

('Black Bean Breakfast Burritos','whole wheat tortillas',120),('Black Bean Breakfast Burritos','eggs',200),('Black Bean Breakfast Burritos','black beans',120),
('Black Bean Breakfast Burritos','salsa',60),('Black Bean Breakfast Burritos','cheddar',40),('Black Bean Breakfast Burritos','spinach',40),

('Green Protein Smoothie','spinach',60),('Green Protein Smoothie','banana',100),('Green Protein Smoothie','greek yogurt',150),
('Green Protein Smoothie','peanut butter',16),('Green Protein Smoothie','milk',200),

('Mango Chia Pudding','chia seeds',50),('Mango Chia Pudding','milk',400),('Mango Chia Pudding','mango',200),('Mango Chia Pudding','honey',15),

('Shakshuka','eggs',200),('Shakshuka','canned tomatoes',400),('Shakshuka','bell pepper',150),('Shakshuka','onion',100),('Shakshuka','garlic',6),
('Shakshuka','cumin',3),('Shakshuka','paprika',3),('Shakshuka','olive oil',15),('Shakshuka','feta',40),('Shakshuka','parsley',5),

('Red Lentil Soup','red lentils',250),('Red Lentil Soup','carrot',150),('Red Lentil Soup','celery',100),('Red Lentil Soup','onion',150),
('Red Lentil Soup','garlic',10),('Red Lentil Soup','canned tomatoes',400),('Red Lentil Soup','vegetable broth',1000),('Red Lentil Soup','cumin',4),
('Red Lentil Soup','olive oil',15),('Red Lentil Soup','spinach',100),('Red Lentil Soup','lemon',20),('Red Lentil Soup','salt',4),

('Quinoa Chickpea Power Salad','quinoa',120),('Quinoa Chickpea Power Salad','chickpeas',240),('Quinoa Chickpea Power Salad','cucumber',150),
('Quinoa Chickpea Power Salad','tomato',150),('Quinoa Chickpea Power Salad','feta',60),('Quinoa Chickpea Power Salad','spinach',60),
('Quinoa Chickpea Power Salad','olive oil',20),('Quinoa Chickpea Power Salad','lemon',30),('Quinoa Chickpea Power Salad','salt',2),

('Tuna Lettuce Wraps','canned tuna',240),('Tuna Lettuce Wraps','greek yogurt',80),('Tuna Lettuce Wraps','celery',60),
('Tuna Lettuce Wraps','romaine lettuce',150),('Tuna Lettuce Wraps','lemon',15),('Tuna Lettuce Wraps','black pepper',1),

('Black Bean Burrito Bowl','brown rice',150),('Black Bean Burrito Bowl','black beans',240),('Black Bean Burrito Bowl','corn',150),
('Black Bean Burrito Bowl','bell pepper',120),('Black Bean Burrito Bowl','salsa',100),('Black Bean Burrito Bowl','avocado',140),
('Black Bean Burrito Bowl','lime',20),('Black Bean Burrito Bowl','cumin',3),('Black Bean Burrito Bowl','romaine lettuce',100),

('Mediterranean Hummus Wrap','whole wheat tortillas',60),('Mediterranean Hummus Wrap','hummus',60),('Mediterranean Hummus Wrap','cucumber',80),
('Mediterranean Hummus Wrap','tomato',80),('Mediterranean Hummus Wrap','spinach',30),('Mediterranean Hummus Wrap','feta',30),

('Chicken Kale Caesar','chicken breast',300),('Chicken Kale Caesar','kale',150),('Chicken Kale Caesar','parmesan',30),
('Chicken Kale Caesar','greek yogurt',60),('Chicken Kale Caesar','lemon',20),('Chicken Kale Caesar','garlic',5),
('Chicken Kale Caesar','olive oil',15),('Chicken Kale Caesar','whole wheat bread',60),

('Egg Fried Rice with Peas','white rice',150),('Egg Fried Rice with Peas','eggs',150),('Egg Fried Rice with Peas','frozen peas',150),
('Egg Fried Rice with Peas','carrot',100),('Egg Fried Rice with Peas','scallions',30),('Egg Fried Rice with Peas','soy sauce',30),
('Egg Fried Rice with Peas','sesame oil',10),('Egg Fried Rice with Peas','garlic',6),

('Mushroom Spinach Quesadillas','whole wheat tortillas',120),('Mushroom Spinach Quesadillas','mushrooms',200),('Mushroom Spinach Quesadillas','spinach',100),
('Mushroom Spinach Quesadillas','mozzarella',100),('Mushroom Spinach Quesadillas','olive oil',5),('Mushroom Spinach Quesadillas','black beans',120),

('Greek Chicken Salad','chicken breast',300),('Greek Chicken Salad','romaine lettuce',150),('Greek Chicken Salad','cucumber',150),
('Greek Chicken Salad','tomato',150),('Greek Chicken Salad','feta',60),('Greek Chicken Salad','olive oil',20),('Greek Chicken Salad','lemon',20),
('Greek Chicken Salad','dried oregano',2),

('Sesame Edamame Bowl','quinoa',120),('Sesame Edamame Bowl','edamame',200),('Sesame Edamame Bowl','carrot',100),('Sesame Edamame Bowl','cabbage',150),
('Sesame Edamame Bowl','cucumber',100),('Sesame Edamame Bowl','soy sauce',25),('Sesame Edamame Bowl','sesame oil',10),('Sesame Edamame Bowl','avocado',100),

('Beet & Lentil Salad','cooked lentils',300),('Beet & Lentil Salad','beets',200),('Beet & Lentil Salad','arugula',80),('Beet & Lentil Salad','walnuts',30),
('Beet & Lentil Salad','feta',60),('Beet & Lentil Salad','olive oil',15),('Beet & Lentil Salad','balsamic vinegar',15),

('Minestrone','pasta',120),('Minestrone','kidney beans',400),('Minestrone','canned tomatoes',800),('Minestrone','carrot',150),('Minestrone','celery',100),
('Minestrone','zucchini',200),('Minestrone','onion',150),('Minestrone','garlic',10),('Minestrone','green beans',150),('Minestrone','spinach',100),
('Minestrone','vegetable broth',1500),('Minestrone','olive oil',20),('Minestrone','parmesan',40),('Minestrone','dried oregano',3),

('Chicken & Kale Soup','chicken breast',400),('Chicken & Kale Soup','carrot',150),('Chicken & Kale Soup','celery',100),('Chicken & Kale Soup','onion',150),
('Chicken & Kale Soup','garlic',8),('Chicken & Kale Soup','chicken broth',1500),('Chicken & Kale Soup','kale',100),('Chicken & Kale Soup','potato',200),
('Chicken & Kale Soup','parsley',5),

('Chickpea Spinach Curry','chickpeas',480),('Chickpea Spinach Curry','spinach',200),('Chickpea Spinach Curry','canned tomatoes',400),
('Chickpea Spinach Curry','coconut milk',200),('Chickpea Spinach Curry','onion',150),('Chickpea Spinach Curry','garlic',10),
('Chickpea Spinach Curry','ginger',10),('Chickpea Spinach Curry','curry powder',10),('Chickpea Spinach Curry','olive oil',15),
('Chickpea Spinach Curry','brown rice',200),('Chickpea Spinach Curry','salt',3),

('Turkey Bean Chili','ground turkey',450),('Turkey Bean Chili','kidney beans',400),('Turkey Bean Chili','canned tomatoes',800),('Turkey Bean Chili','onion',150),
('Turkey Bean Chili','bell pepper',150),('Turkey Bean Chili','garlic',10),('Turkey Bean Chili','cumin',6),('Turkey Bean Chili','paprika',6),
('Turkey Bean Chili','olive oil',15),('Turkey Bean Chili','salt',4),

('Shrimp Veggie Stir-Fry','shrimp',300),('Shrimp Veggie Stir-Fry','broccoli',200),('Shrimp Veggie Stir-Fry','bell pepper',150),('Shrimp Veggie Stir-Fry','garlic',8),
('Shrimp Veggie Stir-Fry','ginger',10),('Shrimp Veggie Stir-Fry','soy sauce',30),('Shrimp Veggie Stir-Fry','sesame oil',10),('Shrimp Veggie Stir-Fry','brown rice',150),
('Shrimp Veggie Stir-Fry','honey',10),

('Sheet Pan Salmon & Sweet Potato','salmon',300),('Sheet Pan Salmon & Sweet Potato','asparagus',250),('Sheet Pan Salmon & Sweet Potato','sweet potato',300),
('Sheet Pan Salmon & Sweet Potato','olive oil',20),('Sheet Pan Salmon & Sweet Potato','lemon',30),('Sheet Pan Salmon & Sweet Potato','garlic',6),
('Sheet Pan Salmon & Sweet Potato','salt',2),

('Beef & Broccoli','sirloin steak',400),('Beef & Broccoli','broccoli',300),('Beef & Broccoli','soy sauce',45),('Beef & Broccoli','garlic',10),
('Beef & Broccoli','ginger',10),('Beef & Broccoli','honey',15),('Beef & Broccoli','sesame oil',10),('Beef & Broccoli','white rice',200),

('Sheet Pan Paprika Chicken','chicken thigh',500),('Sheet Pan Paprika Chicken','brussels sprouts',300),('Sheet Pan Paprika Chicken','carrot',200),
('Sheet Pan Paprika Chicken','onion',150),('Sheet Pan Paprika Chicken','olive oil',25),('Sheet Pan Paprika Chicken','paprika',4),('Sheet Pan Paprika Chicken','salt',3),

('Veggie-Loaded Bolognese','whole wheat pasta',320),('Veggie-Loaded Bolognese','ground beef',400),('Veggie-Loaded Bolognese','canned tomatoes',800),
('Veggie-Loaded Bolognese','carrot',100),('Veggie-Loaded Bolognese','celery',80),('Veggie-Loaded Bolognese','onion',150),('Veggie-Loaded Bolognese','garlic',10),
('Veggie-Loaded Bolognese','olive oil',15),('Veggie-Loaded Bolognese','parmesan',40),('Veggie-Loaded Bolognese','dried oregano',3),

('Peanut Tofu Noodles','rice noodles',150),('Peanut Tofu Noodles','firm tofu',300),('Peanut Tofu Noodles','peanut butter',40),('Peanut Tofu Noodles','soy sauce',30),
('Peanut Tofu Noodles','lime',20),('Peanut Tofu Noodles','cabbage',150),('Peanut Tofu Noodles','carrot',100),('Peanut Tofu Noodles','scallions',20),
('Peanut Tofu Noodles','sesame oil',5),('Peanut Tofu Noodles','honey',10),

('Lemony Sardine Pasta','pasta',180),('Lemony Sardine Pasta','canned sardines',180),('Lemony Sardine Pasta','kale',150),('Lemony Sardine Pasta','garlic',8),
('Lemony Sardine Pasta','lemon',30),('Lemony Sardine Pasta','olive oil',15),('Lemony Sardine Pasta','parsley',10),('Lemony Sardine Pasta','parmesan',20),

('Black Bean Stuffed Sweet Potatoes','sweet potato',500),('Black Bean Stuffed Sweet Potatoes','black beans',240),('Black Bean Stuffed Sweet Potatoes','greek yogurt',80),
('Black Bean Stuffed Sweet Potatoes','salsa',80),('Black Bean Stuffed Sweet Potatoes','avocado',100),('Black Bean Stuffed Sweet Potatoes','cilantro',5),
('Black Bean Stuffed Sweet Potatoes','cumin',2),

('Beef & Bean Tacos','ground beef',400),('Beef & Bean Tacos','black beans',200),('Beef & Bean Tacos','corn tortillas',180),('Beef & Bean Tacos','cabbage',150),
('Beef & Bean Tacos','salsa',100),('Beef & Bean Tacos','avocado',100),('Beef & Bean Tacos','lime',15),('Beef & Bean Tacos','cumin',4),('Beef & Bean Tacos','paprika',3),

('Baked Cod with Tomatoes & Green Beans','cod',350),('Baked Cod with Tomatoes & Green Beans','tomato',250),('Baked Cod with Tomatoes & Green Beans','green beans',250),
('Baked Cod with Tomatoes & Green Beans','garlic',6),('Baked Cod with Tomatoes & Green Beans','olive oil',15),('Baked Cod with Tomatoes & Green Beans','lemon',20),
('Baked Cod with Tomatoes & Green Beans','basil',5),

('Chicken Fajita Bowl','chicken breast',450),('Chicken Fajita Bowl','bell pepper',300),('Chicken Fajita Bowl','onion',150),('Chicken Fajita Bowl','brown rice',200),
('Chicken Fajita Bowl','salsa',100),('Chicken Fajita Bowl','lime',20),('Chicken Fajita Bowl','cumin',4),('Chicken Fajita Bowl','paprika',4),('Chicken Fajita Bowl','olive oil',15),

('Coconut Red Lentil Dal','red lentils',300),('Coconut Red Lentil Dal','coconut milk',200),('Coconut Red Lentil Dal','canned tomatoes',400),
('Coconut Red Lentil Dal','onion',150),('Coconut Red Lentil Dal','garlic',10),('Coconut Red Lentil Dal','ginger',15),('Coconut Red Lentil Dal','turmeric',4),
('Coconut Red Lentil Dal','cumin',4),('Coconut Red Lentil Dal','spinach',150),('Coconut Red Lentil Dal','vegetable broth',750),

('Roasted Veg & Chickpea Couscous','couscous',180),('Roasted Veg & Chickpea Couscous','chickpeas',240),('Roasted Veg & Chickpea Couscous','zucchini',200),
('Roasted Veg & Chickpea Couscous','eggplant',200),('Roasted Veg & Chickpea Couscous','bell pepper',150),('Roasted Veg & Chickpea Couscous','onion',100),
('Roasted Veg & Chickpea Couscous','olive oil',25),('Roasted Veg & Chickpea Couscous','cumin',3),('Roasted Veg & Chickpea Couscous','lemon',20),
('Roasted Veg & Chickpea Couscous','parsley',10),

('Turkey Stuffed Peppers','bell pepper',600),('Turkey Stuffed Peppers','ground turkey',450),('Turkey Stuffed Peppers','brown rice',120),
('Turkey Stuffed Peppers','canned tomatoes',400),('Turkey Stuffed Peppers','onion',100),('Turkey Stuffed Peppers','garlic',6),
('Turkey Stuffed Peppers','mozzarella',80),('Turkey Stuffed Peppers','dried oregano',3),

('Garlic Butter Shrimp & Zoodles','shrimp',350),('Garlic Butter Shrimp & Zoodles','zucchini',500),('Garlic Butter Shrimp & Zoodles','garlic',12),
('Garlic Butter Shrimp & Zoodles','butter',20),('Garlic Butter Shrimp & Zoodles','lemon',20),('Garlic Butter Shrimp & Zoodles','parsley',8),

('Steak with Garlic Spinach & Potatoes','sirloin steak',350),('Steak with Garlic Spinach & Potatoes','potato',400),('Steak with Garlic Spinach & Potatoes','spinach',200),
('Steak with Garlic Spinach & Potatoes','garlic',6),('Steak with Garlic Spinach & Potatoes','olive oil',20),('Steak with Garlic Spinach & Potatoes','butter',10),

('Ginger Tofu & Bok Choy','firm tofu',400),('Ginger Tofu & Bok Choy','bok choy',300),('Ginger Tofu & Bok Choy','mushrooms',150),('Ginger Tofu & Bok Choy','garlic',8),
('Ginger Tofu & Bok Choy','ginger',10),('Ginger Tofu & Bok Choy','soy sauce',30),('Ginger Tofu & Bok Choy','sesame oil',10),('Ginger Tofu & Bok Choy','white rice',150),

('Apple & Peanut Butter','apple',180),('Apple & Peanut Butter','peanut butter',32),

('Hummus & Veggie Sticks','hummus',80),('Hummus & Veggie Sticks','carrot',100),('Hummus & Veggie Sticks','cucumber',100),('Hummus & Veggie Sticks','bell pepper',80),

('No-Bake Energy Bites','rolled oats',100),('No-Bake Energy Bites','peanut butter',120),('No-Bake Energy Bites','honey',60),('No-Bake Energy Bites','dark chocolate',40),
('No-Bake Energy Bites','ground flaxseed',20),('No-Bake Energy Bites','pumpkin seeds',30),

('Dark Chocolate, Almonds & Berries','dark chocolate',20),('Dark Chocolate, Almonds & Berries','almonds',20),('Dark Chocolate, Almonds & Berries','strawberries',100),

('Crispy Roasted Chickpeas','chickpeas',240),('Crispy Roasted Chickpeas','olive oil',10),('Crispy Roasted Chickpeas','paprika',3),
('Crispy Roasted Chickpeas','cumin',2),('Crispy Roasted Chickpeas','salt',2),

('Sea Salt Edamame','edamame',150),('Sea Salt Edamame','salt',1);

-- Optional extras: nice to have, never counted as "missing".
INSERT INTO staging_recipe_ingredients (recipe, ingredient, grams, is_optional) VALUES
('Shakshuka','whole wheat bread',80,true),
('Coconut Red Lentil Dal','brown rice',200,true),
('Chicken & Kale Soup','lemon',15,true),
('Tuna Lettuce Wraps','avocado',70,true);

DO $$
DECLARE bad TEXT;
BEGIN
    SELECT string_agg(DISTINCT format('%s -> %s', s.recipe, s.ingredient), ', ') INTO bad
    FROM staging_recipe_ingredients s
    LEFT JOIN recipes r     ON r.title = s.recipe
    LEFT JOIN ingredients i ON i.name  = s.ingredient
    WHERE r.id IS NULL OR i.id IS NULL;
    IF bad IS NOT NULL THEN
        RAISE EXCEPTION 'Unresolved recipe ingredients: %', bad;
    END IF;
END $$;

INSERT INTO recipe_ingredients (recipe_id, ingredient_id, grams, is_optional)
SELECT r.id, i.id, s.grams, s.is_optional
FROM staging_recipe_ingredients s
JOIN recipes r     ON r.title = s.recipe
JOIN ingredients i ON i.name  = s.ingredient;


DROP TABLE staging_recipe_ingredients;
