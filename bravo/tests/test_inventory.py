import unittest

import bravo.blocks
import bravo.inventory

class TestInventoryInternals(unittest.TestCase):

    def setUp(self):
        self.i = bravo.inventory.Inventory(0, 45)

    def test_trivial(self):
        pass

    def test_add_to_inventory(self):
        self.assertEqual(self.i.holdables, [None] * 9)
        self.assertTrue(self.i.add(2, 1))
        self.assertEqual(self.i.holdables[0], (2, 0, 1))

    def test_add_to_inventory_sequential(self):
        self.assertEqual(self.i.holdables, [None] * 9)
        self.assertTrue(self.i.add(2, 1))
        self.assertEqual(self.i.holdables[0], (2, 0, 1))
        self.assertTrue(self.i.add(2, 1))
        self.assertEqual(self.i.holdables[0], (2, 0, 2))
        self.assertEqual(self.i.holdables[1], None)

    def test_select_stack(self):
        self.i.holdables[0] = (2, 0, 1)
        self.i.holdables[1] = (2, 0, 1)
        self.i.select(37)
        self.i.select(36)
        self.assertEqual(self.i.holdables[0], (2, 0, 2))
        self.assertEqual(self.i.holdables[1], None)

    def test_select_switch(self):
        self.i.holdables[0] = (2, 0, 1)
        self.i.holdables[1] = (3, 0, 1)
        self.i.select(36)
        self.i.select(37)
        self.i.select(36)
        self.assertEqual(self.i.holdables[0], (3, 0, 1))
        self.assertEqual(self.i.holdables[1], (2, 0, 1))

class TestCrafting(unittest.TestCase):

    def setUp(self):
        self.i = bravo.inventory.Inventory(0, 45)

    def test_trivial(self):
        pass

    def test_crafting_wood(self):
        self.i.crafting[0] = (bravo.blocks.blocks["log"].slot, 0, 1)
        self.assertEqual(bravo.inventory.check_recipes(self.i.crafting),
            (bravo.blocks.blocks["wood"].slot, 4))

class TestInventoryIntegration(unittest.TestCase):

    def setUp(self):
        self.i = bravo.inventory.Inventory(0, 45)

    def test_trivial(self):
        pass

    def test_craft_wood_from_log(self):
        self.i.add(bravo.blocks.blocks["log"].slot, 1)
        # Select log from holdables.
        self.i.select(36)
        # Select log into crafting.
        self.i.select(1)
        # Select wood from crafted.
        self.i.select(0)
        # And select wood into holdables.
        self.i.select(36)
        self.assertEqual(self.i.holdables[0],
            (bravo.blocks.blocks["wood"].slot, 0, 4))
        self.assertEqual(self.i.crafting[0], None)
        self.assertEqual(self.i.crafted[0], None)
