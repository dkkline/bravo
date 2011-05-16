from __future__ import division

from itertools import product
from random import randint, random

from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks
from twisted.internet.task import LoopingCall
from zope.interface import implements

from bravo.blocks import blocks
from bravo.ibravo import IAutomaton, IDigHook
from bravo.terrain.trees import ConeTree, NormalTree, RoundTree

from bravo.parameters import factory

class Trees(object):
    """
    Turn saplings into trees.
    """

    implements(IAutomaton)

    blocks = (blocks["sapling"].slot,)
    grow_step_min = 15
    grow_step_max = 60

    def __init__(self):
        self.trees = [
            NormalTree,
            ConeTree,
            RoundTree,
            NormalTree,
        ]

    @inlineCallbacks
    def process(self, coords):
        metadata = yield factory.world.get_metadata(coords)
        # Is this sapling ready to grow into a big tree? We use a bit-trick to
        # check.
        if metadata >= 12:
            # Tree time!
            tree = self.trees[metadata % 4](pos=coords)
            tree.prepare(factory.world)
            tree.make_trunk(factory.world)
            tree.make_foliage(factory.world)
            # We can't easily tell how many chunks were modified, so we have
            # to flush all of them.
            factory.flush_all_chunks()
        else:
            # Increment metadata.
            metadata += 4
            factory.world.set_metadata(coords, metadata)
            reactor.callLater(randint(self.grow_step_min, self.grow_step_max),
                self.process, coords)

    def feed(self, coords):
        reactor.callLater(randint(self.grow_step_min, self.grow_step_max),
            self.process, coords)

    name = "trees"

class Grass(object):

    implements(IAutomaton, IDigHook)

    blocks = (blocks["dirt"].slot,)

    @property
    def step(self):
        """
        Get the step.
        """

        if not self.tracked:
            return 5
        else:
            return max(1 / 20, 5 / len(self.tracked))

    def __init__(self):
        self.tracked = set()
        self.loop = LoopingCall(self.process)
        self.schedule()

    def schedule(self):
        if self.loop.running:
            self.loop.stop()
        self.loop.start(self.step, now=False)

    @inlineCallbacks
    def process(self):
        if not self.tracked:
            self.schedule()
            return

        # Effectively stop tracking this block. We'll add it back in if we're
        # not finished with it.
        coords = self.tracked.pop()

        current = yield factory.world.get_block(coords)
        if current == blocks["dirt"].slot:
            # Yep, it's still dirt. Let's look around and see whether it
            # should be grassy.
            # Our general strategy is as follows: We look at the blocks
            # nearby. If at least eight of them are grass, grassiness is
            # guaranteed, but if none of them are grass, grassiness just won't
            # happen.
            x, y, z = coords

            # First things first: Grass can't grow if there's things on top of
            # it, so check that first.
            above = yield factory.world.get_block((x, y + 1, z))
            if above:
                return

            # The number of grassy neighbors.
            grasses = 0
            # Intentional shadow.
            for x, y, z in product(xrange(x - 1, x + 2), xrange(y - 1, y + 4),
                xrange(z - 1, z + 2)):
                # Early-exit to avoid block lookup if we finish early.
                if grasses >= 8:
                    break
                block = yield factory.world.get_block((x, y, z))
                if block == blocks["grass"].slot:
                    grasses += 1

            # Randomly determine whether we are finished.
            if grasses / 8 >= random():
                # Hey, let's make some grass.
                factory.world.set_block(coords, blocks["grass"].slot)
                # XXX goddammit
                factory.flush_all_chunks()
            else:
                # Not yet; add it back to the list.
                self.tracked.add(coords)

        # And call ourselves later.
        self.schedule()

    def feed(self, coords):
        self.tracked.add(coords)

    def dig_hook(self, chunk, x, y, z, block):
        if y > 0:
            block = chunk.get_block((x, y - 1, z))
            if block in self.blocks:
                # Track it now.
                coords = (chunk.x * 16 + x, y - 1, chunk.z * 16 + z)

                self.tracked.add(coords)

    name = "grass"

    before = tuple()
    after = tuple()

trees = Trees()
grass = Grass()
